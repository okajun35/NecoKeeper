"""
猫管理サービス

猫の個体情報のCRUD操作を提供します。
"""

from __future__ import annotations

import logging

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.status_history import StatusHistory
from app.schemas.animal import (
    AnimalCreate,
    AnimalListResponse,
    AnimalStatusUpdate,
    AnimalUpdate,
    ConfirmationResponseData,
)
from app.utils.media_path import build_media_url, resolve_media_file_path

logger = logging.getLogger(__name__)


def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """
    猫を登録

    Args:
        db: データベースセッション
        animal_data: 猫登録データ
        user_id: 登録者のユーザーID

    Returns:
        Animal: 登録された猫

    Raises:
        HTTPException: データベースエラーが発生した場合
    """
    try:
        # 猫を作成
        animal = Animal(**animal_data.model_dump())
        db.add(animal)
        db.flush()  # IDを取得するためにflush

        # ステータス履歴を記録（汎用フォーマット + 互換性カラム）
        status_history = StatusHistory(
            animal_id=animal.id,
            field="status",
            old_value=None,
            new_value=animal.status,
            old_status=None,
            new_status=animal.status,
            changed_by=user_id,
            reason="初回登録",
        )
        db.add(status_history)

        db.commit()
        db.refresh(animal)

        logger.info(f"猫を登録しました: ID={animal.id}, 名前={animal.name}")
        return animal

    except IntegrityError:
        # IntegrityErrorは呼び出し元で処理させる
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"猫の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫の登録に失敗しました",
        ) from e


def get_animal(db: Session, animal_id: int) -> Animal:
    """
    猫の詳細を取得

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        Animal: 猫情報

    Raises:
        HTTPException: 猫が見つからない場合
    """
    try:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()

        if not animal:
            logger.warning(f"猫が見つかりません: ID={animal_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {animal_id} の猫が見つかりません",
            )

        return animal

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"猫の取得に失敗しました: ID={animal_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫の取得に失敗しました",
        ) from e


def update_animal(
    db: Session,
    animal_id: int,
    animal_data: AnimalUpdate | AnimalStatusUpdate,
    user_id: int,
) -> Animal | ConfirmationResponseData:
    """
    猫情報を更新（確認フロー対応）

    ステータス・ロケーション変更時に履歴を自動記録。
    終端ステータス（ADOPTED/DECEASED）から復帰時は確認フローを実行。

    Args:
        db: データベースセッション
        animal_id: 猫ID
        animal_data: 更新データ（status, location_type, confirm, reason を含む可能性）
        user_id: 更新者のユーザーID

    Returns:
        - 通常: Animal（更新済み）
        - 確認要: {"requires_confirmation": true, "warning_code": "...", "message": "..."}

    Raises:
        HTTPException: 猫が見つからない場合、またはデータベースエラーが発生した場合
    """
    try:
        animal = get_animal(db, animal_id)
        update_dict = animal_data.model_dump(exclude_unset=True)

        # 確認フラグと理由を抽出（モデル更新から除外）
        confirm = update_dict.pop("confirm", False)
        reason = update_dict.pop("reason", None)

        # ステータス変更の検出
        status_changed = (
            "status" in update_dict and update_dict["status"] != animal.status
        )
        location_changed = (
            "location_type" in update_dict
            and update_dict["location_type"] != animal.location_type
        )

        # 終端ステータスから復帰かチェック
        if status_changed:
            current_status = animal.status
            target_status = update_dict["status"]
            is_leaving_terminal = (
                _is_terminal_status(current_status) and current_status != target_status
            )

            # 確認が必要かつ未確認の場合は409を返す
            if is_leaving_terminal and not confirm:
                warning_msg = _get_terminal_warning_message(current_status)
                warning_code = f"LEAVE_{current_status}"
                logger.warning(
                    f"終端ステータスからの復帰確認が必要: ID={animal_id}, "
                    f"{current_status} → {target_status}"
                )
                return {
                    "requires_confirmation": True,
                    "warning_code": warning_code,
                    "message": warning_msg,
                }

        # 履歴記録前に旧値を保存
        old_status_val: str | None = animal.status if status_changed else None
        old_location_val: str | None = (
            animal.location_type if location_changed else None
        )

        # 更新実行
        for key, value in update_dict.items():
            if key not in ("confirm", "reason"):
                setattr(animal, key, value)

        # 履歴記録: status 変更
        if status_changed:
            _record_change(
                db,
                animal_id,
                field="status",
                old_value=old_status_val,
                new_value=update_dict["status"],
                user_id=user_id,
                reason=reason,
            )

        # 履歴記録: location_type 変更
        if location_changed:
            _record_change(
                db,
                animal_id,
                field="location_type",
                old_value=old_location_val,
                new_value=update_dict["location_type"],
                user_id=user_id,
                reason=reason,
            )

        db.commit()
        db.refresh(animal)

        logger.info(
            f"猫情報を更新しました: ID={animal.id}, "
            f"status_changed={status_changed}, location_changed={location_changed}"
        )
        return animal

    except IntegrityError:
        db.rollback()
        raise
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"猫情報の更新に失敗しました: ID={animal_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫情報の更新に失敗しました",
        ) from e


def delete_animal(db: Session, animal_id: int) -> None:
    """
    猫を削除（物理削除）

    Note: 実際のアプリケーションでは論理削除を推奨

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Raises:
        HTTPException: 猫が見つからない場合、またはデータベースエラーが発生した場合
    """
    try:
        animal = get_animal(db, animal_id)
        db.delete(animal)
        db.commit()

        logger.info(f"猫を削除しました: ID={animal_id}")

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"猫の削除に失敗しました: ID={animal_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫の削除に失敗しました",
        ) from e


def list_animals(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
    gender: str | None = None,
    fiv: str | None = None,
    felv: str | None = None,
    is_sterilized: str | None = None,
    location_type: str | None = None,
    is_ready_for_adoption: str | None = None,
) -> AnimalListResponse:
    """
    猫一覧を取得（ページネーション付き）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        status_filter: ステータスフィルター（ACTIVE=保護中+在籍中+トライアル中）
        gender: 性別フィルター
        fiv: FIV検査結果（positive/negative/unknown）
        felv: FeLV検査結果（positive/negative/unknown）
        is_sterilized: 避妊・去勢状態（true/false/unknown）
        location_type: 場所タイプ
        is_ready_for_adoption: 譲渡可能フィルター（true=IN_CARE or TRIAL）

    Returns:
        AnimalListResponse: 猫一覧とページネーション情報
    """
    # クエリを構築
    query = db.query(Animal)

    # ステータスフィルター
    # 注意: is_ready_for_adoptionが指定された場合、
    #       「優先=追加で絞り込む（AND適用）」として扱う
    #       （例: ACTIVE + is_ready_for_adoption=true → IN_CARE/TRIALのみ）
    if status_filter:
        if status_filter == "ACTIVE":
            # ACTIVE = 保護中 + 在籍中 + トライアル中
            query = query.filter(Animal.status.in_(["QUARANTINE", "IN_CARE", "TRIAL"]))
        elif status_filter == "DAILY":
            # DAILY = 日常管理中（保護中 + 在籍中）- トライアル中は除く
            query = query.filter(Animal.status.in_(["QUARANTINE", "IN_CARE"]))
        elif status_filter == "ARCHIVE":
            # ARCHIVE = 譲渡済み + 死亡
            query = query.filter(Animal.status.in_(["ADOPTED", "DECEASED"]))
        else:
            query = query.filter(Animal.status == status_filter)

    # 譲渡可能フィルター（IN_CARE or TRIAL）
    # ※このフィルタはステータスフィルタに追加で絞り込む（AND適用）
    if is_ready_for_adoption == "true":
        query = query.filter(Animal.status.in_(["IN_CARE", "TRIAL"]))
    elif is_ready_for_adoption == "false":
        query = query.filter(Animal.status.notin_(["IN_CARE", "TRIAL"]))

    # 性別フィルター
    if gender:
        query = query.filter(Animal.gender == gender)

    # FIVフィルター
    if fiv:
        if fiv == "positive":
            query = query.filter(Animal.fiv_positive == True)  # noqa: E712
        elif fiv == "negative":
            query = query.filter(Animal.fiv_positive == False)  # noqa: E712
        elif fiv == "unknown":
            query = query.filter(Animal.fiv_positive.is_(None))

    # FeLVフィルター
    if felv:
        if felv == "positive":
            query = query.filter(Animal.felv_positive == True)  # noqa: E712
        elif felv == "negative":
            query = query.filter(Animal.felv_positive == False)  # noqa: E712
        elif felv == "unknown":
            query = query.filter(Animal.felv_positive.is_(None))

    # 避妊・去勢フィルター
    if is_sterilized:
        if is_sterilized == "true":
            query = query.filter(Animal.is_sterilized == True)  # noqa: E712
        elif is_sterilized == "false":
            query = query.filter(Animal.is_sterilized == False)  # noqa: E712
        elif is_sterilized == "unknown":
            query = query.filter(Animal.is_sterilized.is_(None))

    # 場所タイプフィルター
    if location_type:
        query = query.filter(Animal.location_type == location_type)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * page_size
    animals = (
        query.order_by(Animal.created_at.desc()).offset(offset).limit(page_size).all()
    )

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return AnimalListResponse(
        items=animals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def search_animals(
    db: Session, query: str, page: int = 1, page_size: int = 20
) -> AnimalListResponse:
    """
    猫を検索

    名前、毛色、特徴で部分一致検索を行います。

    Args:
        db: データベースセッション
        query: 検索クエリ
        page: ページ番号
        page_size: 1ページあたりの件数

    Returns:
        AnimalListResponse: 検索結果とページネーション情報
    """
    # 検索クエリを構築
    search_query = db.query(Animal).filter(
        or_(
            Animal.name.ilike(f"%{query}%"),
            Animal.coat_color.ilike(f"%{query}%"),
            Animal.coat_color_note.ilike(f"%{query}%"),
            Animal.features.ilike(f"%{query}%"),
        )
    )

    # 総件数を取得
    total = search_query.count()

    # ページネーション
    offset = (page - 1) * page_size
    animals = (
        search_query.order_by(Animal.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return AnimalListResponse(
        items=animals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def get_display_image(db: Session, animal_id: int) -> str:
    """
    表示用の画像パスを取得

    優先順位:
    1. プロフィール画像（animal.photo）
    2. 画像ギャラリーの1枚目（作成日時降順）
    3. デフォルト画像（Kiroween Modeの場合はHalloween画像）

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        str: 画像パス

    Example:
        >>> image_path = get_display_image(db, 1)
        >>> print(image_path)
        '/media/animals/1/profile.jpg'
    """
    from app.config import get_settings

    settings = get_settings()
    default_image = (
        "/static/icons/halloween_logo_2.webp"
        if settings.kiroween_mode
        else "/static/images/default-cat.svg"
    )

    try:
        animal = get_animal(db, animal_id)

        # 1. プロフィール画像が設定されている場合
        if animal.photo:
            try:
                photo_path = resolve_media_file_path(animal.photo, settings.media_dir)
                if photo_path.exists():
                    photo_url = build_media_url(animal.photo)
                    if photo_url:
                        return photo_url
                else:
                    logger.warning(
                        "event=image_file_missing caller=display animal_id=%s "
                        "source=animal.photo db_path=%s resolved_path=%s media_dir=%s",
                        animal_id,
                        animal.photo,
                        str(photo_path),
                        settings.media_dir,
                    )
            except ValueError as exc:
                logger.warning(
                    "event=image_path_invalid caller=display animal_id=%s "
                    "source=animal.photo db_path=%s media_dir=%s error=%s",
                    animal_id,
                    animal.photo,
                    settings.media_dir,
                    str(exc),
                )

        # 2. 画像ギャラリーの1枚目を取得
        from app.services import image_service

        images = image_service.list_images(
            db, animal_id, sort_by="created_at", ascending=False
        )
        for image in images:
            try:
                image_path = resolve_media_file_path(
                    image.image_path, settings.media_dir
                )
                if image_path.exists():
                    image_url = build_media_url(image.image_path)
                    if image_url:
                        return image_url
                else:
                    logger.warning(
                        "event=image_file_missing caller=display animal_id=%s "
                        "source=gallery image_id=%s db_path=%s resolved_path=%s media_dir=%s",
                        animal_id,
                        image.id,
                        image.image_path,
                        str(image_path),
                        settings.media_dir,
                    )
            except ValueError as exc:
                logger.warning(
                    "event=image_path_invalid caller=display animal_id=%s "
                    "source=gallery image_id=%s db_path=%s media_dir=%s error=%s",
                    animal_id,
                    image.id,
                    image.image_path,
                    settings.media_dir,
                    str(exc),
                )

        # 3. デフォルト画像（Kiroween Modeの場合はHalloween画像）
        return default_image

    except HTTPException:
        # 猫が見つからない場合もデフォルト画像を返す
        return default_image
    except Exception as e:
        logger.error(f"画像パスの取得に失敗しました: animal_id={animal_id}, エラー={e}")
        return default_image


# === ヘルパー関数（issue #85: ステータス確認フロー） ===


def _is_terminal_status(status: str) -> bool:
    """
    終端ステータスか判定

    終端ステータス: ADOPTED, DECEASED
    """
    from app.utils.enums import AnimalStatus

    return status in (AnimalStatus.ADOPTED.value, AnimalStatus.DECEASED.value)


def _get_terminal_warning_message(old_status: str) -> str:
    """終端ステータスからの復帰時の警告メッセージを取得"""
    messages = {
        "ADOPTED": "この個体は『譲渡済み』として登録されています。状態を変更しますか？",
        "DECEASED": "この個体は『死亡』として登録されています。状態を変更しますか？",
    }
    return messages.get(old_status, "この個体のステータスを変更しますか？")


def _record_change(
    db: Session,
    animal_id: int,
    field: str,
    old_value: str | None,
    new_value: str,
    user_id: int,
    reason: str | None = None,
) -> StatusHistory:
    """
    変更履歴を記録

    Args:
        db: データベースセッション
        animal_id: 猫ID
        field: 変更フィールド ('status' or 'location_type')
        old_value: 変更前値（初回登録時はNone）
        new_value: 変更後値
        user_id: ユーザーID
        reason: 変更理由（任意）

    Returns:
        StatusHistory: 記録された履歴
    """
    # 互換性のため old_status/new_status も設定
    # (field == "status" の場合のみ、旧カラムも更新)
    old_status_val = old_value if field == "status" else None
    new_status_val = new_value if field == "status" else None

    history = StatusHistory(
        animal_id=animal_id,
        field=field,
        old_value=old_value,
        new_value=new_value,
        old_status=old_status_val,
        new_status=new_status_val,
        reason=reason,
        changed_by=user_id,
    )
    db.add(history)
    logger.debug(
        f"変更履歴を記録: animal_id={animal_id}, field={field}, "
        f"{old_value} → {new_value}"
    )
    return history
