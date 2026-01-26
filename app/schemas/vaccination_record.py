"""VaccinationRecord Pydanticスキーマ（Issue #83）."""

from datetime import date as date_type

from pydantic import BaseModel, ConfigDict, Field

from app.utils.enums import VaccineCategoryEnum


class VaccinationRecordBase(BaseModel):
    """VaccinationRecord共通フィールド."""

    vaccine_category: VaccineCategoryEnum = Field(
        ..., description="ワクチン種別（3種/4種/5種）"
    )
    administered_on: date_type = Field(..., description="接種日")
    next_due_on: date_type | None = Field(None, description="次回接種予定日")
    memo: str | None = Field(None, max_length=500, description="備考")


class VaccinationRecordCreate(VaccinationRecordBase):
    """VaccinationRecord作成スキーマ."""

    animal_id: int = Field(..., description="対象動物ID")


class VaccinationRecordUpdate(BaseModel):
    """VaccinationRecord更新スキーマ（全フィールドオプショナル）."""

    vaccine_category: VaccineCategoryEnum | None = Field(
        None, description="ワクチン種別（3種/4種/5種）"
    )
    administered_on: date_type | None = Field(None, description="接種日")
    next_due_on: date_type | None = Field(None, description="次回接種予定日")
    memo: str | None = Field(None, max_length=500, description="備考")


class VaccinationRecordResponse(VaccinationRecordBase):
    """VaccinationRecordレスポンススキーマ."""

    model_config = ConfigDict(from_attributes=True)

    id: int
    animal_id: int
    vaccine_category_display: str | None = None

    @classmethod
    def from_orm_with_display(
        cls, obj: "VaccinationRecordResponse", locale: str = "ja"
    ) -> "VaccinationRecordResponse":
        """ORMオブジェクトからdisplay名付きで変換."""
        data = {
            "id": obj.id,
            "animal_id": obj.animal_id,
            "vaccine_category": obj.vaccine_category,
            "administered_on": obj.administered_on,
            "next_due_on": obj.next_due_on,
            "memo": obj.memo,
        }
        if obj.vaccine_category:
            if locale == "ja":
                data["vaccine_category_display"] = (
                    obj.vaccine_category.display_name_ja()
                )
            else:
                data["vaccine_category_display"] = (
                    obj.vaccine_category.display_name_en()
                )
        return cls(**data)
