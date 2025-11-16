"""
認証関連のPydanticスキーマ

JWTトークンとユーザー情報のレスポンススキーマを定義します。
"""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict, EmailStr


class Token(BaseModel):
    """
    トークンレスポンススキーマ

    OAuth2仕様に準拠したトークンレスポンス
    """

    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    """
    トークンペイロードスキーマ

    JWTトークンに含まれるデータ
    """

    user_id: int
    role: str


class UserResponse(BaseModel):
    """
    ユーザー情報レスポンススキーマ

    /api/v1/auth/me エンドポイントのレスポンス
    """

    model_config = ConfigDict(from_attributes=True)

    id: int
    email: EmailStr
    name: str
    role: str
    is_active: bool
