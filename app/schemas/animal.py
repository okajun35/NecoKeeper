"""
猫（Animal）関連のPydanticスキーマ

猫の個体情報のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class AnimalBase(BaseModel):
    """猫の基本情報スキーマ"""

    name: str | None = Field(None, max_length=100, description="猫の名前")
    photo: str | None = Field(
        None, max_length=255, description="プロフィール画像のファイルパス（任意）"
    )
    pattern: str = Field(
        ..., max_length=100, description="柄・色（例: キジトラ、三毛、黒猫）"
    )
    tail_length: str = Field(
        ..., max_length=50, description="尻尾の長さ（例: 長い、短い、なし）"
    )
    collar: str | None = Field(None, max_length=100, description="首輪の有無と色")
    age: str = Field(
        ..., max_length=50, description="年齢・大きさ（例: 子猫、成猫、老猫）"
    )
    gender: str = Field(..., max_length=10, description="性別（male/female/unknown）")
    ear_cut: bool = Field(False, description="耳カットの有無（TNR済みの印）")
    features: str | None = Field(None, description="外傷・特徴・性格（自由記述）")
    status: str = Field("保護中", max_length=20, description="ステータス")
    protected_at: date_type = Field(
        default_factory=date_type.today, description="保護日"
    )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """性別の検証"""
        allowed = ["male", "female", "unknown"]
        if v not in allowed:
            raise ValueError(
                f"性別は {', '.join(allowed)} のいずれかである必要があります"
            )
        return v


class AnimalCreate(AnimalBase):
    """猫登録リクエストスキーマ"""

    pass


class AnimalUpdate(BaseModel):
    """猫更新リクエストスキーマ（全フィールド任意）"""

    name: str | None = Field(None, max_length=100)
    photo: str | None = Field(None, max_length=255)
    pattern: str | None = Field(None, max_length=100)
    tail_length: str | None = Field(None, max_length=50)
    collar: str | None = Field(None, max_length=100)
    age: str | None = Field(None, max_length=50)
    gender: str | None = Field(None, max_length=10)
    ear_cut: bool | None = None
    features: str | None = None
    status: str | None = Field(None, max_length=20)
    protected_at: date_type | None = None

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        """性別の検証"""
        if v is not None:
            allowed = ["male", "female", "unknown"]
            if v not in allowed:
                raise ValueError(
                    f"性別は {', '.join(allowed)} のいずれかである必要があります"
                )
        return v


class AnimalResponse(AnimalBase):
    """猫レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AnimalListResponse(BaseModel):
    """猫一覧レスポンススキーマ"""

    items: list[AnimalResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
