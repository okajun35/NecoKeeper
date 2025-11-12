"""
世話記録サービス

世話記録のCRUD操作とCSVエクスポートを提供します。
"""

import csv
import io
from datetime import date, datetime

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.care_log import CareLog
from app.schemas.care_log import CareLogCreate, CareLogListResponse, CareLogUpdate


def create_care_log(db: Session, care_log_data: CareLogCreate) -> CareLog:
    """
    世話記録を登録

    Args:
        db: データベースセッション
        care_log_data: 世話記録データ

    Returns:
        CareLog: 登録された世話記録
    """
    care_log = CareLog(**care_log_data.model_dump())
    db.add(care_log)
    db.commit()
    db.refresh(care_log)

    return care_log


def get_care_log(db: Session, care_log_id: int) -> CareLog:
    """
    世話記録の詳細を取得

    Args:
        db: データベースセッション
        care_log_id: 世話記録ID

    Returns:
        CareLog: 世話記録

    Raises:
        HTTPException: 世話記録が見つからない場合
    """
    care_log = db.query(CareLog).filter(CareLog.id == care_log_id).first()

    if not care_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {care_log_id} の世話記録が見つかりません",
        )

    return care_log


def update_care_log(
    db: Session, care_log_id: int, care_log_data: CareLogUpdate, user_id: int
) -> CareLog:
    """
    世話記録を更新

    Args:
        db: データベースセッション
        care_log_id: 世話記録ID
        care_log_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        CareLog: 更新された世話記録

    Raises:
        HTTPException: 世話記録が見つからない場合
    """
    care_log = get_care_log(db, care_log_id)

    # 世話記録を更新
    update_dict = care_log_data.model_dump(exclude_unset=True)
    for key, value in update_dict.items():
        setattr(care_log, key, value)

    # 更新者を記録
    care_log.last_updated_by = user_id

    db.commit()
    db.refresh(care_log)

    return care_log


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

    return CareLogListResponse(
        items=care_logs,
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
        .order_by(CareLog.created_at.desc())
        .first()
    )
