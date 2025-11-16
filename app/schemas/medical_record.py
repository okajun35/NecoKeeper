"""
診療記録（MedicalRecord）関連のPydanticスキーマ

診療記録のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, field_validator


class MedicalRecordBase(BaseModel):
    """診療記録の基本情報スキーマ"""

    animal_id: int
    date: date_type
    time_slot: str | None = None
    weight: Decimal | None = None
    temperature: Decimal | None = None
    symptoms: str
    medical_action_id: int | None = None
    dosage: int | None = None
    other: str | None = None
    comment: str | None = None

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Decimal | None) -> Decimal | None:
        """体重は正の数でなければならない（入力された場合）"""
        if v is not None and v <= 0:
            raise ValueError("体重は正の数でなければなりません")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Decimal | None) -> Decimal | None:
        """体温は35.0〜42.0の範囲でなければならない"""
        if v is not None and (v < Decimal("35.0") or v > Decimal("42.0")):
            raise ValueError("体温は35.0〜42.0の範囲でなければなりません")
        return v


class MedicalRecordCreate(MedicalRecordBase):
    """診療記録登録リクエストスキーマ"""

    vet_id: int


class MedicalRecordUpdate(BaseModel):
    """診療記録更新リクエストスキーマ（全フィールド任意）"""

    date: date_type | None = None
    time_slot: str | None = None
    weight: Decimal | None = None
    temperature: Decimal | None = None
    symptoms: str | None = None
    medical_action_id: int | None = None
    dosage: int | None = None
    other: str | None = None
    comment: str | None = None


class MedicalRecordResponse(MedicalRecordBase):
    """診療記録レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vet_id: int
    created_at: datetime
    updated_at: datetime
    last_updated_at: datetime
    last_updated_by: int | None
    # リレーション情報
    animal_name: str | None = None
    vet_name: str | None = None
    medical_action_name: str | None = None
    dosage_unit: str | None = None
    # 請求価格情報
    billing_amount: Decimal | None = None


class MedicalRecordListResponse(BaseModel):
    """診療記録一覧レスポンススキーマ"""

    items: list[MedicalRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
