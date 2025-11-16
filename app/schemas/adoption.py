"""
里親管理（Adoption）Pydanticスキーマ

里親希望者と譲渡記録のバリデーションスキーマです。
"""

from __future__ import annotations

from datetime import date, datetime

from pydantic import BaseModel, ConfigDict, Field

# ========================================
# Applicant（里親希望者）スキーマ
# ========================================


class ApplicantBase(BaseModel):
    """里親希望者の共通フィールド"""

    name: str = Field(..., max_length=100, description="氏名")
    contact: str = Field(..., max_length=255, description="連絡先")
    address: str | None = Field(None, description="住所")
    family: str | None = Field(None, description="家族構成")
    environment: str | None = Field(None, description="飼育環境")
    conditions: str | None = Field(None, description="希望条件")


class ApplicantCreate(ApplicantBase):
    """里親希望者作成用スキーマ"""

    pass


class ApplicantUpdate(BaseModel):
    """里親希望者更新用スキーマ（全フィールド任意）"""

    name: str | None = Field(None, max_length=100, description="氏名")
    contact: str | None = Field(None, max_length=255, description="連絡先")
    address: str | None = Field(None, description="住所")
    family: str | None = Field(None, description="家族構成")
    environment: str | None = Field(None, description="飼育環境")
    conditions: str | None = Field(None, description="希望条件")


class ApplicantResponse(ApplicantBase):
    """里親希望者レスポンススキーマ"""

    id: int = Field(..., description="里親希望者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# ========================================
# AdoptionRecord（譲渡記録）スキーマ
# ========================================


class AdoptionRecordBase(BaseModel):
    """譲渡記録の共通フィールド"""

    animal_id: int = Field(..., description="猫ID")
    applicant_id: int = Field(..., description="里親希望者ID")
    interview_date: date | None = Field(None, description="面談日")
    interview_note: str | None = Field(None, description="面談内容")
    decision: str | None = Field(
        None,
        pattern="^(approved|rejected|pending)$",
        description="判定結果（approved/rejected/pending）",
    )
    adoption_date: date | None = Field(None, description="譲渡日")
    follow_up: str | None = Field(None, description="譲渡後フォロー")


class AdoptionRecordCreate(AdoptionRecordBase):
    """譲渡記録作成用スキーマ"""

    pass


class AdoptionRecordUpdate(BaseModel):
    """譲渡記録更新用スキーマ（全フィールド任意）"""

    interview_date: date | None = Field(None, description="面談日")
    interview_note: str | None = Field(None, description="面談内容")
    decision: str | None = Field(
        None,
        pattern="^(approved|rejected|pending)$",
        description="判定結果（approved/rejected/pending）",
    )
    adoption_date: date | None = Field(None, description="譲渡日")
    follow_up: str | None = Field(None, description="譲渡後フォロー")


class AdoptionRecordResponse(AdoptionRecordBase):
    """譲渡記録レスポンススキーマ"""

    id: int = Field(..., description="譲渡記録ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)
