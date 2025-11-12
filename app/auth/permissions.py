"""
権限チェックモジュール

ロールベースのアクセス制御（RBAC）を実装します。

Requirements: Requirement 10.1-10.5
"""

from typing import Annotated, Any

from fastapi import Depends, HTTPException, status

from app.auth.dependencies import get_current_active_user
from app.models.user import User

# ロール別権限マトリクス
PERMISSIONS = {
    "admin": ["*"],  # 全権限
    "vet": [
        "animal:read",
        "animal:write",
        "care:read",
        "care:write",
        "medical:read",
        "medical:write",
        "medical:delete",
        "report:read",
    ],
    "staff": [
        "animal:read",
        "animal:write",
        "care:read",
        "care:write",
        "medical:read",
        "report:read",
        "report:write",
        "csv:import",
        "csv:export",
    ],
    "read_only": [
        "animal:read",
        "care:read",
        "medical:read",
        "report:read",
    ],
}


def has_permission(user: User, permission: str) -> bool:
    """
    ユーザーが指定された権限を持っているかチェック

    Args:
        user: ユーザーオブジェクト
        permission: チェックする権限（例: "animal:write"）

    Returns:
        bool: 権限がある場合True
    """
    user_permissions = PERMISSIONS.get(user.role, [])

    # adminは全権限を持つ
    if "*" in user_permissions:
        return True

    return permission in user_permissions


def require_role(allowed_roles: list[str]) -> Any:
    """
    指定されたロールのいずれかを要求する依存性を生成

    Args:
        allowed_roles: 許可されたロールのリスト

    Returns:
        依存性関数

    Example:
        @app.get("/admin", dependencies=[Depends(require_role(["admin"]))])
        async def admin_only():
            return {"message": "Admin only"}
    """

    async def role_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if current_user.role not in allowed_roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"この操作には {', '.join(allowed_roles)} のいずれかのロールが必要です",
            )
        return current_user

    return role_checker


def require_permission(required_permission: str) -> Any:
    """
    指定された権限を要求する依存性を生成

    Args:
        required_permission: 必要な権限（例: "animal:write"）

    Returns:
        依存性関数

    Example:
        @app.post("/animals", dependencies=[Depends(require_permission("animal:write"))])
        async def create_animal():
            return {"message": "Animal created"}
    """

    async def permission_checker(
        current_user: Annotated[User, Depends(get_current_active_user)],
    ) -> User:
        if not has_permission(current_user, required_permission):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"この操作には '{required_permission}' 権限が必要です",
            )
        return current_user

    return permission_checker
