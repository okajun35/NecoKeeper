"""
ユーザーサービス

ユーザーのCRUD操作を提供します。
"""

from __future__ import annotations

import logging

from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserListResponse

logger = logging.getLogger(__name__)


def list_users(
    db: Session,
    page: int = 1,
    page_size: int = 100,
    role: str | None = None,
    is_active: bool | None = None,
) -> UserListResponse:
    """
    ユーザー一覧を取得（ページネーション付き）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        role: ロールフィルター（admin, vet, staff）
        is_active: アクティブ状態フィルター

    Returns:
        UserListResponse: ユーザー一覧とページネーション情報

    Example:
        >>> users = list_users(db, page=1, role="vet")
    """
    # クエリを構築
    query = db.query(User)

    # フィルター
    if role:
        query = query.filter(User.role == role)

    if is_active is not None:
        query = query.filter(User.is_active == is_active)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * page_size
    users = query.order_by(User.name.asc()).offset(offset).limit(page_size).all()

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return UserListResponse(
        items=users,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
