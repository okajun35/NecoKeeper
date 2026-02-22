"""
猫管理APIエンドポイント

猫の個体情報のCRUD操作を提供します。
"""

from __future__ import annotations

import logging
from datetime import datetime
from io import BytesIO
from typing import Annotated

import qrcode  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, status
from fastapi.responses import Response
from pydantic import BaseModel, ConfigDict
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.config import get_settings
from app.database import get_db
from app.models.animal import Animal
from app.models.user import User
from app.schemas.animal import (
    AnimalCreate,
    AnimalListResponse,
    AnimalResponse,
    AnimalStatusUpdate,
    AnimalUpdate,
    ConfirmationErrorResponse,
)
from app.services import animal_service

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/animals", tags=["猫管理"])


@router.get("", response_model=AnimalListResponse)
def list_animals(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: str | None = Query(
        None, description="ステータスフィルター（ACTIVE=活動中）"
    ),
    gender: str | None = Query(None, description="性別フィルター"),
    fiv: str | None = Query(
        None, description="FIV検査結果（positive/negative/unknown）"
    ),
    felv: str | None = Query(
        None, description="FeLV検査結果（positive/negative/unknown）"
    ),
    is_sterilized: str | None = Query(
        None, description="避妊・去勢状態（true/false/unknown）"
    ),
    location_type: str | None = Query(None, description="場所タイプ"),
    is_ready_for_adoption: str | None = Query(
        None, description="譲渡可能（true=IN_CARE or TRIAL）"
    ),
) -> AnimalListResponse:
    """
    猫一覧を取得

    ページネーション付きで猫の一覧を取得します。
    各種条件でフィルタリングすることも可能です。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）
        status: ステータスフィルター（ACTIVE=保護中+在籍中+トライアル中）
        gender: 性別フィルター（male/female/unknown）
        fiv: FIV検査結果（positive/negative/unknown）
        felv: FeLV検査結果（positive/negative/unknown）
        is_sterilized: 避妊・去勢状態（true/false/unknown）
        location_type: 場所タイプ（FACILITY/FOSTER_HOME/ADOPTER_HOME）
        is_ready_for_adoption: 譲渡可能フィルター（true=IN_CARE or TRIAL）

    Returns:
        AnimalListResponse: 猫一覧とページネーション情報
    """
    return animal_service.list_animals(
        db=db,
        page=page,
        page_size=page_size,
        status_filter=status,
        gender=gender,
        fiv=fiv,
        felv=felv,
        is_sterilized=is_sterilized,
        location_type=location_type,
        is_ready_for_adoption=is_ready_for_adoption,
    )


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
def create_animal(
    animal_data: AnimalCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
) -> Animal:
    """
    猫を登録

    新しい猫の個体情報を登録します。
    登録時にステータス履歴も自動的に作成されます。

    Args:
        animal_data: 猫登録データ
        db: データベースセッション
        current_user: 現在のユーザー（animal:write権限が必要）

    Returns:
        AnimalResponse: 登録された猫の情報

    Raises:
        HTTPException: マイクロチップ番号が重複している場合（409）
    """
    try:
        return animal_service.create_animal(
            db=db, animal_data=animal_data, user_id=current_user.id
        )
    except IntegrityError as e:
        if "microchip_number" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このマイクロチップ番号は既に登録されています",
            ) from e
        raise


@router.get("/search", response_model=AnimalListResponse)
def search_animals(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    q: str = Query(..., min_length=1, description="検索クエリ"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
) -> AnimalListResponse:
    """
    猫を検索

    名前、毛色、特徴で部分一致検索を行います。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        q: 検索クエリ（最低1文字）
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）

    Returns:
        AnimalListResponse: 検索結果とページネーション情報
    """
    return animal_service.search_animals(db=db, query=q, page=page, page_size=page_size)


@router.get("/{animal_id}", response_model=AnimalResponse)
def get_animal(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Animal:
    """
    猫の詳細を取得

    指定されたIDの猫の詳細情報を取得します。

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AnimalResponse: 猫の詳細情報

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    return animal_service.get_animal(db=db, animal_id=animal_id)


@router.put(
    "/{animal_id}",
    response_model=AnimalResponse,
    responses={409: {"model": ConfirmationErrorResponse}},
)
def update_animal(
    animal_id: int,
    animal_data: AnimalUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
) -> Animal:
    """
    猫情報を更新

    指定されたIDの猫の情報を更新します。
    ステータスが変更された場合は履歴も自動的に記録されます。

    Args:
        animal_id: 猫ID
        animal_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（animal:write権限が必要）

    Returns:
        AnimalResponse: 更新された猫の情報

    Raises:
        HTTPException: 猫が見つからない場合（404）
        HTTPException: マイクロチップ番号が重複している場合（409）
    """
    try:
        result = animal_service.update_animal(
            db=db, animal_id=animal_id, animal_data=animal_data, user_id=current_user.id
        )

        # 確認フロー発動時は409を返す
        if isinstance(result, dict) and result.get("requires_confirmation"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result,
            )

        if isinstance(result, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="不正な確認レスポンスを検出しました",
            )

        return result
    except IntegrityError as e:
        if "microchip_number" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このマイクロチップ番号は既に登録されています",
            ) from e
        raise


@router.patch(
    "/{animal_id}",
    response_model=AnimalResponse,
    responses={409: {"model": ConfirmationErrorResponse}},
)
def patch_animal(
    animal_id: int,
    animal_data: AnimalStatusUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
) -> Animal:
    """
    猫情報を部分更新（ステータス・ロケーション専用）
    指定されたIDの猫のステータス・ロケーション情報を更新します。
    変更時に履歴を自動記録。

    **終端ステータス（ADOPTED/DECEASED）からの復帰時は確認フローを実行**
    - 初回: confirm なし → 409 Conflict（requires_confirmation=true を返す）
    - 確認後: confirm=true で再送 → 200 OK で更新実行

    Args:
        animal_id: 猫ID
        animal_data: 更新データ（status, location_type, current_location_note, confirm, reason）
        db: データベースセッション
        current_user: 現在のユーザー（animal:write権限が必要）

    Returns:
        - AnimalResponse: 更新された猫の情報
        - HTTP 409: 確認が必要な場合（requires_confirmation=true, warning_code, message）

    Raises:
        HTTPException: 猫が見つからない場合（404）
        HTTPException: バリデーションエラー（400）
    """
    try:
        result = animal_service.update_animal(
            db=db, animal_id=animal_id, animal_data=animal_data, user_id=current_user.id
        )

        # 確認フロー発動時は409を返す
        if isinstance(result, dict) and result.get("requires_confirmation"):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail=result,
            )

        if isinstance(result, dict):
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="不正な確認レスポンスを検出しました",
            )

        return result
    except IntegrityError as e:
        if "microchip_number" in str(e):
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="このマイクロチップ番号は既に登録されています",
            ) from e
        raise


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_animal(  # type: ignore[no-untyped-def]
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:delete"))],
):
    """
    猫を削除

    指定されたIDの猫を削除します（物理削除）。

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー（animal:delete権限が必要）

    Raises:
        HTTPException: 猫が見つからない場合（404）

    Note:
        実際のアプリケーションでは論理削除を推奨
    """
    animal_service.delete_animal(db=db, animal_id=animal_id)


@router.get("/{animal_id}/qr")
def get_animal_qr_code(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """
    猫のQRコード画像を生成

    指定された猫の世話記録入力画面へのQRコードを生成します。
    QRコードをスキャンすると、公開世話記録入力画面が開きます。

    このエンドポイントは認証不要です（QRコードは公開情報のため）。

    Args:
        animal_id: 猫ID
        db: データベースセッション

    Returns:
        Response: QRコード画像（PNG形式）

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    # 猫の存在確認
    animal = animal_service.get_animal(db=db, animal_id=animal_id)

    # 設定から基本URLを取得
    settings = get_settings()
    base_url = (
        settings.base_url if hasattr(settings, "base_url") else "http://localhost:8000"
    )

    # 世話記録入力画面のURL
    care_log_url = f"{base_url}/public/care?animal_id={animal.id}"

    # QRコード生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(care_log_url)
    qr.make(fit=True)

    # 画像生成
    img = qr.make_image(fill_color="black", back_color="white")

    # BytesIOに保存
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return Response(content=img_io.getvalue(), media_type="image/png")


@router.get("/{animal_id}/display-image")
def get_animal_display_image(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    猫の表示用画像パスを取得

    優先順位:
    1. プロフィール画像（animal.photo）
    2. 画像ギャラリーの1枚目
    3. デフォルト画像

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 画像パス {"image_path": "/path/to/image.jpg"}
    """
    image_path = animal_service.get_display_image(db=db, animal_id=animal_id)
    return {"image_path": image_path}


@router.post("/{animal_id}/profile-image")
def upload_profile_image(
    animal_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    プロフィール画像をアップロード

    Args:
        animal_id: 猫ID
        file: 画像ファイル
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: アップロード結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫が見つからない、またはアップロードに失敗した場合
    """
    from app.services import image_service

    # 画像をアップロード（画像ギャラリーに追加）
    image = image_service.upload_image(
        db=db,
        animal_id=animal_id,
        file=file,
        taken_at=None,
        description="プロフィール画像",
    )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}


@router.put("/{animal_id}/profile-image")
def update_profile_image(
    animal_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    プロフィール画像を変更

    Args:
        animal_id: 猫ID
        file: 画像ファイル
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 更新結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫が見つからない、またはアップロードに失敗した場合
    """
    from app.services import image_service

    # 画像をアップロード（画像ギャラリーに追加）
    image = image_service.upload_image(
        db=db,
        animal_id=animal_id,
        file=file,
        taken_at=None,
        description="プロフィール画像",
    )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}


@router.put("/{animal_id}/profile-image/from-gallery/{image_id}")
def set_profile_image_from_gallery(
    animal_id: int,
    image_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    画像ギャラリーからプロフィール画像を選択

    Args:
        animal_id: 猫ID
        image_id: 画像ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 更新結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫または画像が見つからない場合
    """
    from app.services import image_service

    # 画像の存在確認
    image = image_service.get_image(db, image_id)

    # 画像が指定された猫のものか確認
    if image.animal_id != animal_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された画像は別の猫のものです",
        )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}


# === ステータス・ロケーション履歴 API（Issue #85） ===


class StatusHistoryItem(BaseModel):
    """ステータス履歴アイテム"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int
    field: str | None
    old_value: str | None
    new_value: str | None
    reason: str | None
    changed_by: int | None
    changed_at: datetime


class StatusHistoryResponse(BaseModel):
    """ステータス履歴レスポンス（ページネーション）"""

    items: list[StatusHistoryItem]
    total: int
    page: int
    page_size: int
    total_pages: int


@router.get(
    "/{animal_id}/status-history",
    response_model=StatusHistoryResponse,
    summary="ステータス・ロケーション変更履歴を取得",
)
def get_animal_status_history(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:read"))],
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
) -> StatusHistoryResponse:
    """
    動物のステータス・ロケーション変更履歴を取得

    指定されたIDの猫のステータス・ロケーション変更履歴を時系列で取得します。

    Args:
        animal_id: 猫ID
        page: ページ番号（デフォルト: 1）
        page_size: 1ページあたりの件数（デフォルト: 20、最大: 100）
        db: データベースセッション
        current_user: 現在のユーザー（animal:read権限が必要）

    Returns:
        StatusHistoryResponse: 履歴リストとページネーション情報

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    from app.models.status_history import StatusHistory

    try:
        # 猫が存在するか確認
        animal_service.get_animal(db, animal_id)

        # 履歴を取得
        query = db.query(StatusHistory).filter(StatusHistory.animal_id == animal_id)
        total = query.count()

        # ページネーション
        offset = (page - 1) * page_size
        items = (
            query.order_by(StatusHistory.changed_at.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )

        # 総ページ数を計算
        total_pages = (total + page_size - 1) // page_size

        return StatusHistoryResponse(
            items=items,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"ステータス履歴の取得に失敗しました: animal_id={animal_id}, エラー={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ステータス履歴の取得に失敗しました",
        ) from e
