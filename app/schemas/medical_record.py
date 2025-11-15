"""
診療記録（MedicalRecord）関連のPydanticスキーマ

診療記録のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel, ConfigDict, field_validator


class MedicalRecordBase(BaseModel):
    """診療記録の基本情報スキーマ"""

    animal_id: int
    date: date
    time_slot: Optional[str] = None
    weight: Decimal
    temperature: Optional[Decimal] = None
    symptoms: str
    medical_action_id: Optional[int] = None
    dosage: Optional[int] = None
    other: Optional[str] = None
    comment: Optional[str] = None

    @field_validator("weight")
    @classmethod
    def validate_weight(cls, v: Decimal) -> Decimal:
        """体重は正の数でなければならない"""
        if v <= 0:
            raise ValueError("体重は正の数でなければなりません")
        return v

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: Optional[Decimal]) -> Optional[Decimal]:
        """体温は35.0〜42.0の範囲でなければならない"""
        if v is not None and (v < Decimal("35.0") or v > Decimal("42.0")):
            raise ValueError("体温は35.0〜42.0の範囲でなければなりません")
        return v


class MedicalRecordCreate(MedicalRecordBase):
    """診療記録登録リクエストスキーマ"""

    vet_id: int


class MedicalRecordUpdate(BaseModel):
    """診療記録更新リクエストスキーマ（全フィールド任意）"""

    date: Optional[date] = None
    time_slot: Optional[str] = None
    weight: Optional[Decimal] = None
    temperature: Optional[Decimal] = None
    symptoms: Optional[str] = None
    medical_action_id: Optional[int] = None
    dosage: Optional[int] = None
    other: Optional[str] = None
    comment: Optional[str] = None


class MedicalRecordResponse(MedicalRecordBase):
    """診療記録レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    vet_id: int
    created_at: datetime
    updated_at: datetime
    last_updated_at: datetime
    last_updated_by: Optional[int]


class MedicalRecordListResponse(BaseModel):
    """診療記録一覧レスポンススキーマ"""

    items: list[MedicalRecordResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
