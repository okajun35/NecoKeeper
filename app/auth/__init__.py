"""
認証・認可モジュール

JWT + OAuth2 Password Flowによる認証システムを提供します。
"""

from app.auth.dependencies import (
    get_current_active_user,
    get_current_user,
    oauth2_scheme,
)
from app.auth.jwt import create_access_token, decode_access_token
from app.auth.password import hash_password, validate_password_policy, verify_password
from app.auth.permissions import has_permission, require_permission, require_role

__all__ = [
    # Dependencies
    "oauth2_scheme",
    "get_current_user",
    "get_current_active_user",
    # JWT
    "create_access_token",
    "decode_access_token",
    # Password
    "hash_password",
    "verify_password",
    "validate_password_policy",
    # Permissions
    "has_permission",
    "require_role",
    "require_permission",
]
