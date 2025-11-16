"""
診療記録機能のテスト

診療記録のCRUD操作とバリデーションをテストします。
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

import pytest
from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.schemas.medical_record import MedicalRecordCreate, MedicalRecordUpdate
from app.services import medical_record_service


class TestMedicalRecordService:
    """診療記録サービスのテスト"""

    def test_create_medical_record(self, test_db: Session, test_animal, test_vet_user):
        """診療記録を登録できる"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            temperature=Decimal("38.5"),
            symptoms="食欲不振、元気がない",
            comment="経過観察が必要",
        )

        # When
        result = medical_record_service.create_medical_record(test_db, record_data)

        # Then
        assert result.id is not None
        assert result.animal_id == test_animal.id
        assert result.vet_id == test_vet_user.id
        assert result.weight == Decimal("4.5")
        assert result.temperature == Decimal("38.5")
        assert result.symptoms == "食欲不振、元気がない"

    def test_create_medical_record_without_weight(
        self, test_db: Session, test_animal, test_vet_user
    ):
        """体重なしで診療記録を登録できる"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=None,  # 体重なし
            temperature=Decimal("38.5"),
            symptoms="定期健診",
            comment="体重測定なし",
        )

        # When
        result = medical_record_service.create_medical_record(test_db, record_data)

        # Then
        assert result.id is not None
        assert result.animal_id == test_animal.id
        assert result.weight is None
        assert result.temperature == Decimal("38.5")

    def test_get_medical_record(self, test_db: Session, test_animal, test_vet_user):
        """診療記録を取得できる"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        created = medical_record_service.create_medical_record(test_db, record_data)

        # When
        result = medical_record_service.get_medical_record(test_db, created.id)

        # Then
        assert result.id == created.id
        assert result.animal_id == test_animal.id

    def test_get_nonexistent_medical_record(self, test_db: Session):
        """存在しない診療記録を取得すると404エラー"""
        # When/Then
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            medical_record_service.get_medical_record(test_db, 99999)
        assert exc_info.value.status_code == 404

    def test_list_medical_records(self, test_db: Session, test_animal, test_vet_user):
        """診療記録一覧を取得できる"""
        # Given
        for i in range(3):
            record_data = MedicalRecordCreate(
                animal_id=test_animal.id,
                vet_id=test_vet_user.id,
                date=date(2025, 11, 15 + i),
                weight=Decimal(f"4.{i}"),
                symptoms=f"症状{i}",
            )
            medical_record_service.create_medical_record(test_db, record_data)

        # When
        result = medical_record_service.list_medical_records(
            test_db, page=1, page_size=10
        )

        # Then
        assert result.total >= 3
        assert len(result.items) >= 3
        assert result.page == 1

    def test_list_medical_records_with_animal_filter(
        self, test_db: Session, test_animal, test_vet_user
    ):
        """猫IDでフィルターして診療記録を取得できる"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        medical_record_service.create_medical_record(test_db, record_data)

        # When
        result = medical_record_service.list_medical_records(
            test_db, animal_id=test_animal.id
        )

        # Then
        assert result.total >= 1
        assert all(item.animal_id == test_animal.id for item in result.items)

    def test_update_medical_record(self, test_db: Session, test_animal, test_vet_user):
        """診療記録を更新できる"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        created = medical_record_service.create_medical_record(test_db, record_data)

        # When
        update_data = MedicalRecordUpdate(
            weight=Decimal("4.6"), comment="体重が増加しました"
        )
        result = medical_record_service.update_medical_record(
            test_db, created.id, update_data, test_vet_user.id
        )

        # Then
        assert result.weight == Decimal("4.6")
        assert result.comment == "体重が増加しました"
        assert result.last_updated_by == test_vet_user.id


class TestMedicalRecordAPI:
    """診療記録APIのテスト"""

    def test_create_medical_record_api(
        self, test_client: TestClient, vet_auth_token: str, test_animal, test_vet_user
    ):
        """診療記録登録APIが正常に動作する"""
        # Given
        data = {
            "animal_id": test_animal.id,
            "vet_id": test_vet_user.id,
            "date": "2025-11-15",
            "weight": 4.5,
            "temperature": 38.5,
            "symptoms": "食欲不振",
        }
        headers = {"Authorization": f"Bearer {vet_auth_token}"}

        # When
        response = test_client.post(
            "/api/v1/medical-records", json=data, headers=headers
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        result = response.json()
        assert result["animal_id"] == test_animal.id
        assert result["weight"] == "4.50"

    def test_get_medical_record_api(
        self,
        test_client: TestClient,
        auth_token: str,
        test_db: Session,
        test_animal,
        test_vet_user,
    ):
        """診療記録取得APIが正常に動作する"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        created = medical_record_service.create_medical_record(test_db, record_data)
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When
        response = test_client.get(
            f"/api/v1/medical-records/{created.id}", headers=headers
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["id"] == created.id

    def test_list_medical_records_api(self, test_client: TestClient, auth_token: str):
        """診療記録一覧取得APIが正常に動作する"""
        # Given
        headers = {"Authorization": f"Bearer {auth_token}"}

        # When
        response = test_client.get("/api/v1/medical-records", headers=headers)

        # Then
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert "items" in result
        assert "total" in result
        assert "page" in result

    def test_update_medical_record_api(
        self,
        test_client: TestClient,
        vet_auth_token: str,
        test_db: Session,
        test_animal,
        test_vet_user,
    ):
        """診療記録更新APIが正常に動作する"""
        # Given
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        created = medical_record_service.create_medical_record(test_db, record_data)
        headers = {"Authorization": f"Bearer {vet_auth_token}"}

        # When
        update_data = {"weight": 4.6, "comment": "体重増加"}
        response = test_client.put(
            f"/api/v1/medical-records/{created.id}",
            json=update_data,
            headers=headers,
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        result = response.json()
        assert result["weight"] == "4.60"
        assert result["comment"] == "体重増加"


class TestMedicalRecordValidation:
    """診療記録のバリデーションテスト"""

    def test_weight_must_be_positive(self, test_animal, test_vet_user):
        """体重は正の数でなければならない"""
        # Given/When/Then
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            MedicalRecordCreate(
                animal_id=test_animal.id,
                vet_id=test_vet_user.id,
                date=date(2025, 11, 15),
                weight=Decimal("-1.0"),  # 負の値
                symptoms="定期健診",
            )
        assert "体重は正の数でなければなりません" in str(exc_info.value)

    def test_weight_can_be_none(self, test_animal, test_vet_user):
        """体重はNoneでも良い（任意項目）"""
        # Given/When
        record_data = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=None,  # Noneは許可
            symptoms="定期健診",
        )

        # Then
        assert record_data.weight is None

    def test_temperature_range_validation(self, test_animal, test_vet_user):
        """体温は35.0〜42.0の範囲でなければならない"""
        # Given/When/Then
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            MedicalRecordCreate(
                animal_id=test_animal.id,
                vet_id=test_vet_user.id,
                date=date(2025, 11, 15),
                weight=Decimal("4.5"),
                temperature=Decimal("50.0"),  # 範囲外
                symptoms="定期健診",
            )
        assert "体温は35.0〜42.0の範囲でなければなりません" in str(exc_info.value)
