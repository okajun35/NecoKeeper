"""
世話記録（CareLog）関連のPydanticスキーマ

世話記録のリクエスト・レスポンススキーマを定義します。
"""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CareLogBase(BaseModel):
    """世話記録の基本情報スキーマ"""

    animal_id: int = Field(..., description="猫ID")
    recorder_name: str = Field(..., max_length=100, description="記録者名")
    time_slot: str = Field(..., description="時点（morning/noon/evening）")
    appetite: int = Field(3, ge=1, le=5, description="食欲（1〜5段階、5が最良）")
    energy: int = Field(3, ge=1, le=5, description="元気（1〜5段階、5が最良）")
    urination: bool = Field(False, description="排尿有無")
    cleaning: bool = Field(False, description="清掃済み")
    memo: str | None = Field(None, description="メモ")
    from_paper: bool = Field(False, description="紙記録からの転記フラグ")

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot(cls, v: str) -> str:
        """時点の検証"""
        allowed = ["morning", "noon", "evening"]
        if v not in allowed:
            raise ValueError(
                f"時点は {', '.join(allowed)} のいずれかである必要があります"
            )
        return v


class CareLogCreate(CareLogBase):
    """世話記録登録リクエストスキーマ"""

    recorder_id: int | None = Field(
        None, description="記録者ID（ボランティアテーブル）"
    )
    ip_address: str | None = Field(None, max_length=45, description="IPアドレス")
    user_agent: str | None = Field(
        None, max_length=255, description="ユーザーエージェント"
    )
    device_tag: str | None = Field(None, max_length=100, description="デバイスタグ")


class CareLogUpdate(BaseModel):
    """世話記録更新リクエストスキーマ（全フィールド任意）"""

    recorder_name: str | None = Field(None, max_length=100)
    time_slot: str | None = None
    appetite: int | None = Field(None, ge=1, le=5)
    energy: int | None = Field(None, ge=1, le=5)
    urination: bool | None = None
    cleaning: bool | None = None
    memo: str | None = None
    from_paper: bool | None = None

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot(cls, v: str | None) -> str | None:
        """時点の検証"""
        if v is not None:
            allowed = ["morning", "noon", "evening"]
            if v not in allowed:
                raise ValueError(
                    f"時点は {', '.join(allowed)} のいずれかである必要があります"
                )
        return v


class CareLogResponse(CareLogBase):
    """世話記録レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recorder_id: int | None
    ip_address: str | None
    user_agent: str | None
    device_tag: str | None
    created_at: datetime
    last_updated_at: datetime
    last_updated_by: int | None


class CareLogListResponse(BaseModel):
    """世話記録一覧レスポンススキーマ"""

    items: list[CareLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
