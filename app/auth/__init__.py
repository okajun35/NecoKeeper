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
    "create_access_token",
    "decode_access_token",
    "get_current_active_user",
    "get_current_user",
    "has_permission",
    "hash_password",
    "oauth2_scheme",
    "require_permission",
    "require_role",
    "validate_password_policy",
    "verify_password",
]
