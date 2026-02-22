"""VaccinationRecordスキーマのテスト（Issue #83）."""

from datetime import date

import pytest
from pydantic import ValidationError

from app.schemas.vaccination_record import (
    VaccinationRecordCreate,
    VaccinationRecordResponse,
    VaccinationRecordUpdate,
)
from app.utils.enums import VaccineCategoryEnum


class TestVaccinationRecordCreate:
    """VaccinationRecordCreateスキーマのテスト."""

    def test_valid_create_minimal(self):
        """最小限の必須フィールドで作成できる."""
        data = {
            "animal_id": 1,
            "vaccine_category": VaccineCategoryEnum.VACCINE_3CORE,
            "administered_on": date(2025, 1, 15),
        }
        schema = VaccinationRecordCreate(**data)
        assert schema.animal_id == 1
        assert schema.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE
        assert schema.administered_on == date(2025, 1, 15)
        assert schema.next_due_on is None
        assert schema.memo is None

    def test_valid_create_full(self):
        """全フィールドを指定して作成できる."""
        data = {
            "animal_id": 2,
            "vaccine_category": VaccineCategoryEnum.VACCINE_5CORE,
            "administered_on": date(2025, 1, 15),
            "next_due_on": date(2026, 1, 15),
            "memo": "初回接種",
        }
        schema = VaccinationRecordCreate(**data)
        assert schema.animal_id == 2
        assert schema.vaccine_category == VaccineCategoryEnum.VACCINE_5CORE
        assert schema.next_due_on == date(2026, 1, 15)
        assert schema.memo == "初回接種"

    def test_missing_animal_id_raises_error(self):
        """animal_idが欠けているとエラー."""
        data = {
            "vaccine_category": VaccineCategoryEnum.VACCINE_3CORE,
            "administered_on": date(2025, 1, 15),
        }
        with pytest.raises(ValidationError) as exc_info:
            VaccinationRecordCreate(**data)
        assert "animal_id" in str(exc_info.value)

    def test_missing_vaccine_category_raises_error(self):
        """vaccine_categoryが欠けているとエラー."""
        data = {
            "animal_id": 1,
            "administered_on": date(2025, 1, 15),
        }
        with pytest.raises(ValidationError) as exc_info:
            VaccinationRecordCreate(**data)
        assert "vaccine_category" in str(exc_info.value)

    def test_missing_administered_on_raises_error(self):
        """administered_onが欠けているとエラー."""
        data = {
            "animal_id": 1,
            "vaccine_category": VaccineCategoryEnum.VACCINE_3CORE,
        }
        with pytest.raises(ValidationError) as exc_info:
            VaccinationRecordCreate(**data)
        assert "administered_on" in str(exc_info.value)

    def test_invalid_vaccine_category_raises_error(self):
        """無効なvaccine_categoryはエラー."""
        data = {
            "animal_id": 1,
            "vaccine_category": "invalid",
            "administered_on": date(2025, 1, 15),
        }
        with pytest.raises(ValidationError):
            VaccinationRecordCreate(**data)

    def test_vaccine_category_from_string(self):
        """文字列からvaccine_categoryを設定できる."""
        data = {
            "animal_id": 1,
            "vaccine_category": "3core",  # Enum値は "3core"
            "administered_on": date(2025, 1, 15),
        }
        schema = VaccinationRecordCreate(**data)
        assert schema.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE


class TestVaccinationRecordUpdate:
    """VaccinationRecordUpdateスキーマのテスト."""

    def test_empty_update_is_valid(self):
        """空の更新データは有効."""
        schema = VaccinationRecordUpdate()
        assert schema.vaccine_category is None
        assert schema.administered_on is None
        assert schema.next_due_on is None
        assert schema.memo is None

    def test_partial_update(self):
        """部分的な更新ができる."""
        schema = VaccinationRecordUpdate(next_due_on=date(2026, 3, 15), memo="追記")
        assert schema.vaccine_category is None
        assert schema.administered_on is None
        assert schema.next_due_on == date(2026, 3, 15)
        assert schema.memo == "追記"

    def test_full_update(self):
        """全フィールドの更新ができる."""
        schema = VaccinationRecordUpdate(
            vaccine_category=VaccineCategoryEnum.VACCINE_4CORE,
            administered_on=date(2025, 2, 1),
            next_due_on=date(2026, 2, 1),
            memo="更新済み",
        )
        assert schema.vaccine_category == VaccineCategoryEnum.VACCINE_4CORE
        assert schema.administered_on == date(2025, 2, 1)
        assert schema.next_due_on == date(2026, 2, 1)
        assert schema.memo == "更新済み"


class TestVaccinationRecordResponse:
    """VaccinationRecordResponseスキーマのテスト."""

    def test_response_with_all_fields(self):
        """全フィールドを含むレスポンス."""
        data = {
            "id": 1,
            "animal_id": 10,
            "vaccine_category": VaccineCategoryEnum.VACCINE_3CORE,
            "administered_on": date(2025, 1, 15),
            "next_due_on": date(2026, 1, 15),
            "memo": "初回",
            "vaccine_category_display": "3種",
        }
        schema = VaccinationRecordResponse(**data)
        assert schema.id == 1
        assert schema.animal_id == 10
        assert schema.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE
        assert schema.vaccine_category_display == "3種"

    def test_response_without_display(self):
        """display名なしのレスポンス."""
        data = {
            "id": 2,
            "animal_id": 20,
            "vaccine_category": VaccineCategoryEnum.VACCINE_5CORE,
            "administered_on": date(2025, 1, 15),
        }
        schema = VaccinationRecordResponse(**data)
        assert schema.id == 2
        assert schema.vaccine_category_display is None
