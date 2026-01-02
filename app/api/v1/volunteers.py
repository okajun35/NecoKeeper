"""
ボランティア管理APIエンドポイント

ボランティア記録者のCRUD操作を提供します。
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.user import User
from app.models.volunteer import Volunteer
from app.schemas.volunteer import (
    VolunteerCreate,
    VolunteerListResponse,
    VolunteerResponse,
    VolunteerUpdate,
)
from app.services import volunteer_service

router = APIRouter(prefix="/volunteers", tags=["ボランティア管理"])


@router.get("", response_model=VolunteerListResponse)
def list_volunteers(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: str | None = Query(
        None, description="ステータスフィルター（active/inactive）"
    ),
) -> VolunteerListResponse:
    """
    ボランティア一覧を取得

    ページネーション付きでボランティアの一覧を取得します。
    ステータスでフィルタリングすることも可能です。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）
        status: ステータスフィルター（active/inactive）

    Returns:
        VolunteerListResponse: ボランティア一覧とページネーション情報
    """
    return volunteer_service.list_volunteers(
        db=db, page=page, page_size=page_size, status_filter=status
    )


@router.post("", response_model=VolunteerResponse, status_code=status.HTTP_201_CREATED)
def create_volunteer(
    volunteer_data: VolunteerCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("volunteer:write"))],
) -> Volunteer:
    """
    ボランティアを登録

    新しいボランティア記録者を登録します。

    Args:
        volunteer_data: ボランティア登録データ
        db: データベースセッション
        current_user: 現在のユーザー（volunteer:write権限が必要）

    Returns:
        VolunteerResponse: 登録されたボランティアの情報
    """
    return volunteer_service.create_volunteer(db=db, volunteer_data=volunteer_data)


@router.get("/{volunteer_id}", response_model=VolunteerResponse)
def get_volunteer(
    volunteer_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Volunteer:
    """
    ボランティア詳細を取得

    指定されたIDのボランティア情報を取得します。

    Args:
        volunteer_id: ボランティアID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        VolunteerResponse: ボランティア情報
    """
    return volunteer_service.get_volunteer(db=db, volunteer_id=volunteer_id)


@router.put("/{volunteer_id}", response_model=VolunteerResponse)
def update_volunteer(
    volunteer_id: int,
    volunteer_data: VolunteerUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("volunteer:write"))],
) -> Volunteer:
    """
    ボランティア情報を更新

    指定されたIDのボランティア情報を更新します。

    Args:
        volunteer_id: ボランティアID
        volunteer_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（volunteer:write権限が必要）

    Returns:
        VolunteerResponse: 更新されたボランティア情報
    """
    return volunteer_service.update_volunteer(
        db=db, volunteer_id=volunteer_id, volunteer_data=volunteer_data
    )


@router.get("/{volunteer_id}/activity", response_model=dict)
def get_activity_history(
    volunteer_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, int | str | None]:
    """
    ボランティアの活動履歴を取得

    指定されたIDのボランティアの活動履歴（記録回数、最終記録日）を取得します。

    Args:
        volunteer_id: ボランティアID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 活動履歴（volunteer_id, volunteer_name, record_count, last_record_date）
    """
    return volunteer_service.get_activity_history(db=db, volunteer_id=volunteer_id)
