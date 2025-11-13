"""
ボランティア管理サービス

ボランティア記録者のCRUD操作を提供します。
"""

from __future__ import annotations

import logging
from collections.abc import Sequence

from fastapi import HTTPException, status
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.care_log import CareLog
from app.models.volunteer import Volunteer
from app.schemas.volunteer import (
    VolunteerCreate,
    VolunteerListResponse,
    VolunteerUpdate,
)

logger = logging.getLogger(__name__)


def create_volunteer(db: Session, volunteer_data: VolunteerCreate) -> Volunteer:
    """
    ボランティアを登録

    Args:
        db: データベースセッション
        volunteer_data: ボランティア登録データ

    Returns:
        Volunteer: 登録されたボランティア

    Raises:
        HTTPException: データベースエラーが発生した場合

    Example:
        >>> volunteer_data = VolunteerCreate(name="田中太郎", contact="090-1234-5678")
        >>> volunteer = create_volunteer(db, volunteer_data)
        >>> print(volunteer.name)
        田中太郎
    """
    try:
        volunteer = Volunteer(**volunteer_data.model_dump())
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)

        logger.info(
            f"ボランティアを登録しました: ID={volunteer.id}, 名前={volunteer.name}"
        )
        return volunteer

    except Exception as e:
        db.rollback()
        logger.error(f"ボランティアの登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ボランティアの登録に失敗しました",
        ) from e


def get_volunteer(db: Session, volunteer_id: int) -> Volunteer:
    """
    ボランティアの詳細を取得

    Args:
        db: データベースセッション
        volunteer_id: ボランティアID

    Returns:
        Volunteer: ボランティア情報

    Raises:
        HTTPException: ボランティアが見つからない場合

    Example:
        >>> volunteer = get_volunteer(db, 1)
        >>> print(volunteer.name)
        田中太郎
    """
    try:
        volunteer = db.query(Volunteer).filter(Volunteer.id == volunteer_id).first()

        if not volunteer:
            logger.warning(f"ボランティアが見つかりません: ID={volunteer_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {volunteer_id} のボランティアが見つかりません",
            )

        return volunteer

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"ボランティアの取得に失敗しました: ID={volunteer_id}, エラー={e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ボランティアの取得に失敗しました",
        ) from e


def list_volunteers(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    status_filter: str | None = None,
) -> VolunteerListResponse:
    """
    ボランティア一覧を取得（ページネーション付き）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        status_filter: ステータスフィルター（active/inactive）

    Returns:
        VolunteerListResponse: ボランティア一覧とページネーション情報

    Raises:
        HTTPException: データベースエラーが発生した場合

    Example:
        >>> response = list_volunteers(db, page=1, page_size=10, status_filter="active")
        >>> print(f"総件数: {response.total}")
        総件数: 5
    """
    try:
        query = db.query(Volunteer)

        # ステータスフィルター
        if status_filter:
            query = query.filter(Volunteer.status == status_filter)

        # 総件数を取得
        total = query.count()

        # ページネーション
        offset = (page - 1) * page_size
        volunteers: Sequence[Volunteer] = (
            query.order_by(Volunteer.name).offset(offset).limit(page_size).all()
        )

        # 総ページ数を計算
        total_pages = (total + page_size - 1) // page_size

        return VolunteerListResponse(
            items=volunteers,
            total=total,
            page=page,
            page_size=page_size,
            total_pages=total_pages,
        )

    except Exception as e:
        logger.error(f"ボランティア一覧の取得に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ボランティア一覧の取得に失敗しました",
        ) from e


def update_volunteer(
    db: Session, volunteer_id: int, volunteer_data: VolunteerUpdate
) -> Volunteer:
    """
    ボランティア情報を更新

    Args:
        db: データベースセッション
        volunteer_id: ボランティアID
        volunteer_data: 更新データ

    Returns:
        Volunteer: 更新されたボランティア

    Raises:
        HTTPException: ボランティアが見つからない場合、またはデータベースエラーが発生した場合

    Example:
        >>> update_data = VolunteerUpdate(status="inactive")
        >>> volunteer = update_volunteer(db, 1, update_data)
        >>> print(volunteer.status)
        inactive
    """
    try:
        volunteer = get_volunteer(db, volunteer_id)

        # ボランティア情報を更新
        update_dict = volunteer_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(volunteer, key, value)

        db.commit()
        db.refresh(volunteer)

        logger.info(f"ボランティア情報を更新しました: ID={volunteer.id}")
        return volunteer

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"ボランティア情報の更新に失敗しました: ID={volunteer_id}, エラー={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="ボランティア情報の更新に失敗しました",
        ) from e


def get_activity_history(db: Session, volunteer_id: int) -> dict[str, int | str | None]:
    """
    ボランティアの活動履歴を取得

    Args:
        db: データベースセッション
        volunteer_id: ボランティアID

    Returns:
        dict: 活動履歴（記録回数、最終記録日）

    Raises:
        HTTPException: ボランティアが見つからない場合、またはデータベースエラーが発生した場合

    Example:
        >>> history = get_activity_history(db, 1)
        >>> print(f"記録回数: {history['record_count']}")
        記録回数: 25
    """
    try:
        # ボランティアの存在確認
        volunteer = get_volunteer(db, volunteer_id)

        # 記録回数を取得
        record_count: int = (
            db.query(func.count(CareLog.id))
            .filter(CareLog.recorder_id == volunteer_id)
            .scalar()
            or 0
        )

        # 最終記録日を取得
        last_record = (
            db.query(func.max(CareLog.created_at))
            .filter(CareLog.recorder_id == volunteer_id)
            .scalar()
        )

        last_record_date: str | None = (
            last_record.strftime("%Y-%m-%d %H:%M:%S") if last_record else None
        )

        return {
            "volunteer_id": volunteer.id,
            "volunteer_name": volunteer.name,
            "record_count": record_count,
            "last_record_date": last_record_date,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"活動履歴の取得に失敗しました: volunteer_id={volunteer_id}, エラー={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="活動履歴の取得に失敗しました",
        ) from e


def get_active_volunteers(db: Session) -> Sequence[Volunteer]:
    """
    アクティブなボランティア一覧を取得

    Publicフォームの記録者選択リスト用。

    Args:
        db: データベースセッション

    Returns:
        Sequence[Volunteer]: アクティブなボランティアのリスト

    Raises:
        HTTPException: データベースエラーが発生した場合

    Example:
        >>> volunteers = get_active_volunteers(db)
        >>> print(f"アクティブなボランティア数: {len(volunteers)}")
        アクティブなボランティア数: 5
    """
    try:
        volunteers: Sequence[Volunteer] = (
            db.query(Volunteer)
            .filter(Volunteer.status == "active")
            .order_by(Volunteer.name)
            .all()
        )

        return volunteers

    except Exception as e:
        logger.error(f"アクティブなボランティア一覧の取得に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="アクティブなボランティア一覧の取得に失敗しました",
        ) from e
