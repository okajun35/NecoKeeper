"""
ユーザー（User）関連のPydanticスキーマ

ユーザーのリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    """ユーザーの基本情報スキーマ"""

    email: EmailStr
    name: str
    role: str


class UserCreate(UserBase):
    """ユーザー登録リクエストスキーマ"""

    password: str


class UserUpdate(BaseModel):
    """ユーザー更新リクエストスキーマ（全フィールド任意）"""

    email: EmailStr | None = None
    name: str | None = None
    role: str | None = None
    is_active: bool | None = None


class UserResponse(UserBase):
    """ユーザーレスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class UserListResponse(BaseModel):
    """ユーザー一覧レスポンススキーマ"""

    items: list[UserResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
