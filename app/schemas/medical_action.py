"""
診療行為マスター（MedicalAction）関連のPydanticスキーマ

診療行為（薬剤、ワクチン、検査等）のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, field_validator


class MedicalActionBase(BaseModel):
    """診療行為マスターの基本情報スキーマ"""

    name: str = Field(..., max_length=100, description="診療名称")
    valid_from: date = Field(..., description="適用開始日")
    valid_to: date | None = Field(None, description="適用終了日")
    cost_price: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="原価", decimal_places=2
    )
    selling_price: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="請求価格", decimal_places=2
    )
    procedure_fee: Decimal = Field(
        default=Decimal("0.00"), ge=0, description="投薬・処置料金", decimal_places=2
    )
    currency: str = Field(default="JPY", max_length=3, description="通貨単位")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str) -> str:
        """通貨単位はJPYまたはUSDのみ"""
        if v not in ["JPY", "USD"]:
            raise ValueError("通貨単位はJPYまたはUSDのみ指定可能です")
        return v

    @field_validator("valid_to")
    @classmethod
    def validate_valid_to(cls, v: date | None, info: Any) -> date | None:
        """適用終了日は適用開始日より後でなければならない"""
        if v is not None and "valid_from" in info.data:
            valid_from = info.data["valid_from"]
            if v <= valid_from:
                raise ValueError("適用終了日は適用開始日より後でなければなりません")
        return v


class MedicalActionCreate(MedicalActionBase):
    """診療行為マスター登録リクエストスキーマ"""

    pass


class MedicalActionUpdate(BaseModel):
    """診療行為マスター更新リクエストスキーマ（全フィールド任意）"""

    name: str | None = Field(None, max_length=100, description="診療名称")
    valid_from: date | None = Field(None, description="適用開始日")
    valid_to: date | None = Field(None, description="適用終了日")
    cost_price: Decimal | None = Field(None, ge=0, description="原価")
    selling_price: Decimal | None = Field(None, ge=0, description="請求価格")
    procedure_fee: Decimal | None = Field(None, ge=0, description="投薬・処置料金")
    currency: str | None = Field(None, max_length=3, description="通貨単位")

    @field_validator("currency")
    @classmethod
    def validate_currency(cls, v: str | None) -> str | None:
        """通貨単位はJPYまたはUSDのみ"""
        if v is not None and v not in ["JPY", "USD"]:
            raise ValueError("通貨単位はJPYまたはUSDのみ指定可能です")
        return v


class MedicalActionResponse(MedicalActionBase):
    """診療行為マスターレスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime
    last_updated_at: datetime
    last_updated_by: int | None


class MedicalActionListResponse(BaseModel):
    """診療行為マスター一覧レスポンススキーマ"""

    items: list[MedicalActionResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class BillingCalculation(BaseModel):
    """料金計算結果スキーマ"""

    medical_action_id: int
    medical_action_name: str
    dosage: int = Field(default=1, ge=1, description="投薬量・回数")
    selling_price: Decimal = Field(..., description="単価")
    procedure_fee: Decimal = Field(..., description="処置料金")
    subtotal: Decimal = Field(..., description="小計（単価×投薬量）")
    total: Decimal = Field(..., description="合計（小計＋処置料金）")
    currency: str = Field(..., description="通貨単位")
