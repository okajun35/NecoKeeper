"""パス関連のユーティリティ関数"""

from __future__ import annotations

from app.config import get_settings


def is_admin_path(path: str) -> bool:
    """
    管理画面のパス判定

    /{ADMIN_PATH} または /{ADMIN_PATH}/... を対象にする。

    Args:
        path: リクエストパス

    Returns:
        bool: 管理画面パスの場合True

    Example:
        >>> is_admin_path("/admin")
        True
        >>> is_admin_path("/admin/animals")
        True
        >>> is_admin_path("/api/v1/animals")
        False
    """
    settings = get_settings()
    admin_base_path = settings.admin_base_path
    return path == admin_base_path or path.startswith(f"{admin_base_path}/")
