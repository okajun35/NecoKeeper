"""
ユーザー管理APIエンドポイント

ユーザーのCRUD操作を提供するAPIエンドポイントです。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.user import User
from app.schemas.user import UserListResponse
from app.services import user_service

router = APIRouter(prefix="/users", tags=["users"])


@router.get("", response_model=UserListResponse)
def list_users(
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(100, ge=1, le=100, description="1ページあたりの件数"),
    role: str | None = Query(None, description="ロールフィルター（admin, vet, staff）"),
    is_active: bool | None = Query(None, description="アクティブ状態フィルター"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
) -> UserListResponse:
    """
    ユーザー一覧を取得

    Args:
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        role: ロールフィルター
        is_active: アクティブ状態フィルター
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        UserListResponse: ユーザー一覧とページネーション情報
    """
    return user_service.list_users(
        db=db,
        page=page,
        page_size=page_size,
        role=role,
        is_active=is_active,
    )
