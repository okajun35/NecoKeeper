"""
世話記録サービス

世話記録のCRUD操作とCSVエクスポートを提供します。
"""

from __future__ import annotations

import csv
import io
import logging
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.care_log import CareLog
from app.schemas.care_log import (
    CareLogCreate,
    CareLogListResponse,
    CareLogResponse,
    CareLogUpdate,
)

logger = logging.getLogger(__name__)


def _validate_defecation_fields(defecation: bool, stool_condition: int | None) -> None:
    if defecation is False and stool_condition is not None:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="defecation=false の場合、stool_condition は null である必要があります",
        )
    if defecation is True:
        if stool_condition is None:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="defecation=true の場合、stool_condition は必須です",
            )
        if not (1 <= stool_condition <= 5):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="stool_condition は 1〜5 の範囲である必要があります",
            )


def create_care_log(db: Session, care_log_data: CareLogCreate) -> CareLog:
    """
    世話記録を登録

    Args:
        db: データベースセッション
        care_log_data: 世話記録データ

    Returns:
        CareLog: 登録された世話記録

    Raises:
        HTTPException: データベースエラーが発生した場合
    """
    try:
        _validate_defecation_fields(
            care_log_data.defecation,
            None
            if care_log_data.stool_condition is None
            else int(care_log_data.stool_condition),
        )

        care_log = CareLog(**care_log_data.model_dump())
        db.add(care_log)
        db.commit()
        db.refresh(care_log)

        logger.info(
            f"世話記録を登録しました: ID={care_log.id}, 猫ID={care_log.animal_id}"
        )
        return care_log

    except HTTPException:
        raise

    except Exception as e:
        db.rollback()
        logger.error(f"世話記録の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="世話記録の登録に失敗しました",
        ) from e


def get_care_log(db: Session, care_log_id: int) -> CareLogResponse:
    """
    世話記録の詳細を取得

    Args:
        db: データベースセッション
        care_log_id: 世話記録ID

    Returns:
        CareLogResponse: 世話記録（猫の名前を含む）

    Raises:
        HTTPException: 世話記録が見つからない場合
    """
    try:
        care_log = db.query(CareLog).filter(CareLog.id == care_log_id).first()

        if not care_log:
            logger.warning(f"世話記録が見つかりません: ID={care_log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {care_log_id} の世話記録が見つかりません",
            )

        # 猫名を取得
        animal_name = None
        if care_log.animal:
            animal_name = care_log.animal.name or f"ID:{care_log.animal_id}"

        # CareLogResponseを作成
        return CareLogResponse(
            id=care_log.id,
            animal_id=care_log.animal_id,
            animal_name=animal_name,
            recorder_id=care_log.recorder_id,
            recorder_name=care_log.recorder_name,
            log_date=care_log.log_date,
            time_slot=care_log.time_slot,
            appetite=care_log.appetite,
            energy=care_log.energy,
            urination=care_log.urination,
            defecation=care_log.defecation,
            stool_condition=care_log.stool_condition,
            cleaning=care_log.cleaning,
            memo=care_log.memo,
            from_paper=care_log.from_paper,
            ip_address=care_log.ip_address,
            user_agent=care_log.user_agent,
            device_tag=care_log.device_tag,
            created_at=care_log.created_at,
            last_updated_at=care_log.last_updated_at,
            last_updated_by=care_log.last_updated_by,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"世話記録の取得に失敗しました: ID={care_log_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="世話記録の取得に失敗しました",
        ) from e


def update_care_log(
    db: Session,
    care_log_id: int,
    care_log_data: CareLogUpdate,
    user_id: int | None,
    expected_animal_id: int | None = None,
    enforce_time_slot: str | None = None,
    care_log: CareLog | None = None,
) -> CareLogResponse:
    """
    世話記録を更新

    Args:
        db: データベースセッション
        care_log_id: 世話記録ID
        care_log_data: 更新データ
        user_id: 更新者のユーザーID
        care_log: 既に取得済みのCareLogオブジェクト（指定時はDBクエリをスキップ。IDはcare_log_idと一致する必要がある）

    Returns:
        CareLogResponse: 更新された世話記録（猫の名前を含む）

    Raises:
        HTTPException: 世話記録が見つからない場合、またはデータベースエラーが発生した場合
        ValueError: care_logのIDがcare_log_idと一致しない場合
    """
    try:
        # CareLogオブジェクトを取得（未指定の場合のみDBから取得）
        if care_log is None:
            care_log = db.query(CareLog).filter(CareLog.id == care_log_id).first()
        elif care_log.id != care_log_id:
            # 提供されたcare_logのIDが一致しない場合はエラー
            raise ValueError(
                f"Provided care_log.id ({care_log.id}) does not match care_log_id ({care_log_id})"
            )

        if not care_log:
            logger.warning(f"世話記録が見つかりません: ID={care_log_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {care_log_id} の世話記録が見つかりません",
            )

        if expected_animal_id is not None and care_log.animal_id != expected_animal_id:
            logger.warning(
                "世話記録の猫IDが一致しません: care_log_id=%s, expected=%s, actual=%s",
                care_log_id,
                expected_animal_id,
                care_log.animal_id,
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {care_log_id} の世話記録が見つかりません",
            )

        update_dict = care_log_data.model_dump(exclude_unset=True)

        if (
            enforce_time_slot
            and "time_slot" in update_dict
            and update_dict["time_slot"] != enforce_time_slot
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail="この記録の時点は変更できません",
            )

        # defecation=False に変更する場合、stool_condition が明示的に指定されていなければ自動的にクリアする。
        # ただし defecation=False と同時に stool_condition に値が指定された場合は不整合として弾く。
        if "defecation" in update_dict and update_dict["defecation"] is False:
            if "stool_condition" not in update_dict:
                update_dict["stool_condition"] = None
            elif update_dict["stool_condition"] is not None:
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                    detail="defecation=false の場合、stool_condition は null である必要があります",
                )

        proposed_defecation = update_dict.get("defecation", care_log.defecation)
        proposed_stool_condition = update_dict.get(
            "stool_condition", care_log.stool_condition
        )

        _validate_defecation_fields(
            bool(proposed_defecation),
            None if proposed_stool_condition is None else int(proposed_stool_condition),
        )

        for key, value in update_dict.items():
            setattr(care_log, key, value)

        if user_id is not None:
            care_log.last_updated_by = user_id

        db.commit()
        db.refresh(care_log)

        logger.info(f"世話記録を更新しました: ID={care_log_id}")

        # 猫名を取得してCareLogResponseを返す
        animal_name = None
        if care_log.animal:
            animal_name = care_log.animal.name or f"ID:{care_log.animal_id}"

        return CareLogResponse(
            id=care_log.id,
            animal_id=care_log.animal_id,
            animal_name=animal_name,
            recorder_id=care_log.recorder_id,
            recorder_name=care_log.recorder_name,
            log_date=care_log.log_date,
            time_slot=care_log.time_slot,
            appetite=care_log.appetite,
            energy=care_log.energy,
            urination=care_log.urination,
            defecation=care_log.defecation,
            stool_condition=care_log.stool_condition,
            cleaning=care_log.cleaning,
            memo=care_log.memo,
            from_paper=care_log.from_paper,
            ip_address=care_log.ip_address,
            user_agent=care_log.user_agent,
            device_tag=care_log.device_tag,
            created_at=care_log.created_at,
            last_updated_at=care_log.last_updated_at,
            last_updated_by=care_log.last_updated_by,
        )

    except HTTPException:
        raise
    except ValueError as e:
        # プログラミングエラー（care_logとcare_log_idの不一致）
        logger.error(f"無効なパラメータ: {e}")
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(f"世話記録の更新に失敗しました: ID={care_log_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="世話記録の更新に失敗しました",
        ) from e


def list_care_logs(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    animal_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    time_slot: str | None = None,
) -> CareLogListResponse:
    """
    世話記録一覧を取得（ページネーション付き）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        animal_id: 猫IDフィルター
        start_date: 開始日フィルター
        end_date: 終了日フィルター
        time_slot: 時点フィルター

    Returns:
        CareLogListResponse: 世話記録一覧とページネーション情報
    """
    # クエリを構築
    query = db.query(CareLog)

    # フィルター
    if animal_id:
        query = query.filter(CareLog.animal_id == animal_id)

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(CareLog.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(CareLog.created_at <= end_datetime)

    if time_slot:
        query = query.filter(CareLog.time_slot == time_slot)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * page_size
    care_logs = (
        query.order_by(CareLog.created_at.desc()).offset(offset).limit(page_size).all()
    )

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    # レスポンスアイテムを作成（animal_nameを追加）
    items: list[CareLogResponse] = []
    for log in care_logs:
        # 猫名を取得
        animal_name = None
        if log.animal:
            animal_name = log.animal.name or f"ID:{log.animal_id}"

        # CareLogResponseを作成
        log_response = CareLogResponse(
            id=log.id,
            animal_id=log.animal_id,
            animal_name=animal_name,
            recorder_id=log.recorder_id,
            recorder_name=log.recorder_name,
            log_date=log.log_date,
            time_slot=log.time_slot,
            appetite=log.appetite,
            energy=log.energy,
            urination=log.urination,
            defecation=log.defecation,
            stool_condition=log.stool_condition,
            cleaning=log.cleaning,
            memo=log.memo,
            from_paper=log.from_paper,
            ip_address=log.ip_address,
            user_agent=log.user_agent,
            device_tag=log.device_tag,
            created_at=log.created_at,
            last_updated_at=log.last_updated_at,
            last_updated_by=log.last_updated_by,
        )
        items.append(log_response)

    return CareLogListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def export_care_logs_csv(
    db: Session,
    animal_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> str:
    """
    世話記録をCSV形式でエクスポート

    Args:
        db: データベースセッション
        animal_id: 猫IDフィルター
        start_date: 開始日フィルター
        end_date: 終了日フィルター

    Returns:
        str: CSV文字列
    """
    # クエリを構築
    query = db.query(CareLog)

    # フィルター
    if animal_id:
        query = query.filter(CareLog.animal_id == animal_id)

    if start_date:
        start_datetime = datetime.combine(start_date, datetime.min.time())
        query = query.filter(CareLog.created_at >= start_datetime)

    if end_date:
        end_datetime = datetime.combine(end_date, datetime.max.time())
        query = query.filter(CareLog.created_at <= end_datetime)

    # データを取得
    care_logs = query.order_by(CareLog.created_at.desc()).all()

    # CSVを生成
    output = io.StringIO()
    writer = csv.writer(output)

    # ヘッダー
    writer.writerow(
        [
            "ID",
            "猫ID",
            "記録者名",
            "時点",
            "食欲",
            "元気",
            "排尿",
            "清掃",
            "メモ",
            "記録日時",
        ]
    )

    # データ行
    for log in care_logs:
        writer.writerow(
            [
                log.id,
                log.animal_id,
                log.recorder_name,
                log.time_slot,
                log.appetite,
                log.energy,
                "有" if log.urination else "無",
                "済" if log.cleaning else "未",
                log.memo or "",
                log.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            ]
        )

    return output.getvalue()


def get_latest_care_log(db: Session, animal_id: int) -> CareLog | None:
    """
    指定された猫の最新の世話記録を取得

    前回入力値コピー機能で使用します。

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        Optional[CareLog]: 最新の世話記録（存在しない場合はNone）
    """
    return (
        db.query(CareLog)
        .filter(CareLog.animal_id == animal_id)
        .order_by(CareLog.created_at.desc(), CareLog.id.desc())
        .first()
    )


def get_daily_view(
    db: Session,
    animal_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
    page: int = 1,
    page_size: int = 20,
) -> dict[str, object]:
    """
    日次ビュー形式のデータを取得

    Args:
        db: データベースセッション
        animal_id: 猫ID（Noneの場合は全猫）
        start_date: 開始日（デフォルト: 7日前）
        end_date: 終了日（デフォルト: 今日）
        page: ページ番号
        page_size: ページサイズ

    Returns:
        dict: 日次ビュー形式のデータ
            - items: list[dict]
            - total: int
            - page: int
            - page_size: int
            - total_pages: int
    """
    from datetime import timedelta

    from sqlalchemy import and_

    from app.models.animal import Animal

    # デフォルト日付範囲を設定（過去7日間）
    if end_date is None:
        end_date = date.today()
    if start_date is None:
        start_date = end_date - timedelta(days=6)

    # 日付範囲のバリデーション
    if start_date > end_date:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="開始日は終了日以前である必要があります",
        )

    # 対象猫を取得
    animal_query = db.query(Animal)
    if animal_id is not None:
        animal_query = animal_query.filter(Animal.id == animal_id)
    animals = animal_query.all()

    if not animals:
        return {
            "items": [],
            "total": 0,
            "page": page,
            "page_size": page_size,
            "total_pages": 0,
        }

    # 日付×猫の組み合わせを生成
    daily_records = []
    current_date = start_date
    while current_date <= end_date:
        for animal in animals:
            # 各時点の記録を取得
            morning_log = (
                db.query(CareLog)
                .filter(
                    and_(
                        CareLog.animal_id == animal.id,
                        CareLog.log_date == current_date,
                        CareLog.time_slot == "morning",
                    )
                )
                .first()
            )

            noon_log = (
                db.query(CareLog)
                .filter(
                    and_(
                        CareLog.animal_id == animal.id,
                        CareLog.log_date == current_date,
                        CareLog.time_slot == "noon",
                    )
                )
                .first()
            )

            evening_log = (
                db.query(CareLog)
                .filter(
                    and_(
                        CareLog.animal_id == animal.id,
                        CareLog.log_date == current_date,
                        CareLog.time_slot == "evening",
                    )
                )
                .first()
            )

            # 辞書形式で作成
            morning_record = {
                "exists": morning_log is not None,
                "log_id": morning_log.id if morning_log else None,
                "appetite": morning_log.appetite if morning_log else None,
                "energy": morning_log.energy if morning_log else None,
                "urination": morning_log.urination if morning_log else None,
                "cleaning": morning_log.cleaning if morning_log else None,
            }

            noon_record = {
                "exists": noon_log is not None,
                "log_id": noon_log.id if noon_log else None,
                "appetite": noon_log.appetite if noon_log else None,
                "energy": noon_log.energy if noon_log else None,
                "urination": noon_log.urination if noon_log else None,
                "cleaning": noon_log.cleaning if noon_log else None,
            }

            evening_record = {
                "exists": evening_log is not None,
                "log_id": evening_log.id if evening_log else None,
                "appetite": evening_log.appetite if evening_log else None,
                "energy": evening_log.energy if evening_log else None,
                "urination": evening_log.urination if evening_log else None,
                "cleaning": evening_log.cleaning if evening_log else None,
            }

            # 辞書形式で作成
            daily_record = {
                "date": current_date.isoformat(),
                "animal_id": animal.id,
                "animal_name": animal.name if animal.name else f"猫 {animal.id}",
                "morning": morning_record,
                "noon": noon_record,
                "evening": evening_record,
            }

            daily_records.append(daily_record)

        current_date += timedelta(days=1)

    # 日付降順でソート（新しい日付が上）
    daily_records.sort(key=lambda x: str(x["date"]), reverse=True)

    # ページネーション
    total = len(daily_records)
    total_pages = (total + page_size - 1) // page_size if total > 0 else 0

    # ページ番号のバリデーション
    if page < 1:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail="ページ番号は1以上である必要があります",
        )

    start_idx = (page - 1) * page_size
    end_idx = start_idx + page_size
    paginated_records = daily_records[start_idx:end_idx]

    return {
        "items": paginated_records,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
    }
