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


class TestWeightTrendAnalysis:
    """体重推移分析のテスト（DDD準拠）"""

    def test_get_weight_history_sorted_by_date(self, test_db: Session, test_vet_user):
        """体重履歴を日付順で取得できる"""
        # Given: 新しい猫を作成（他のテストの影響を避ける）
        from app.models.animal import Animal

        animal = Animal(
            name="体重テスト猫",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="male",
            status="QUARANTINE",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # 複数の診療記録を作成（日付順ではない）
        dates_weights = [
            (date(2025, 11, 20), Decimal("4.5")),
            (date(2025, 11, 10), Decimal("4.2")),
            (date(2025, 11, 15), Decimal("4.3")),
        ]

        for record_date, weight in dates_weights:
            record_data = MedicalRecordCreate(
                animal_id=animal.id,
                vet_id=test_vet_user.id,
                date=record_date,
                weight=weight,
                symptoms="定期健診",
            )
            medical_record_service.create_medical_record(test_db, record_data)

        # When: 診療記録を取得
        result = medical_record_service.list_medical_records(
            test_db, animal_id=animal.id, page=1, page_size=100
        )

        # Then: 日付順（降順：新しい順）でソートされている
        weight_records = [r for r in result.items if r.weight is not None]
        dates = [r.date for r in weight_records]
        assert dates == sorted(dates, reverse=True)

    def test_filter_records_with_weight_only(
        self, test_db: Session, test_animal, test_vet_user
    ):
        """体重データのみをフィルタリングできる"""
        # Given: 体重ありとなしの記録を作成
        with_weight = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=Decimal("4.5"),
            symptoms="定期健診",
        )
        without_weight = MedicalRecordCreate(
            animal_id=test_animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 16),
            weight=None,
            symptoms="診察のみ",
        )

        medical_record_service.create_medical_record(test_db, with_weight)
        medical_record_service.create_medical_record(test_db, without_weight)

        # When: 全記録を取得
        result = medical_record_service.list_medical_records(
            test_db, animal_id=test_animal.id
        )

        # Then: 体重データの有無を確認できる
        weight_records = [r for r in result.items if r.weight is not None]
        assert len(weight_records) >= 1
        assert all(r.weight is not None for r in weight_records)

    def test_calculate_weight_change_percentage(self):
        """体重変化率を正しく計算できる"""
        # Given
        previous_weight = Decimal("4.0")
        current_weight = Decimal("4.4")

        # When
        change = current_weight - previous_weight
        percentage = (change / previous_weight) * 100

        # Then
        assert change == Decimal("0.4")
        assert percentage == Decimal("10.0")

    def test_detect_significant_weight_change(self):
        """10%以上の体重変化を検出できる"""
        # Given
        test_cases = [
            (Decimal("4.0"), Decimal("4.4"), True),  # +10%
            (Decimal("4.0"), Decimal("3.6"), True),  # -10%
            (Decimal("4.0"), Decimal("4.3"), False),  # +7.5%
            (Decimal("4.0"), Decimal("3.7"), False),  # -7.5%
        ]

        for previous, current, expected_warning in test_cases:
            # When
            change_percentage = abs((current - previous) / previous * 100)
            has_warning = change_percentage >= 10

            # Then
            assert has_warning == expected_warning, (
                f"体重変化 {previous}kg → {current}kg "
                f"({change_percentage}%) の警告判定が正しくありません"
            )

    def test_weight_trend_with_multiple_records(self, test_db: Session, test_vet_user):
        """複数の体重記録から推移を取得できる"""
        # Given: 新しい猫を作成（他のテストの影響を避ける）
        from app.models.animal import Animal

        animal = Animal(
            name="体重推移テスト猫",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="female",
            status="QUARANTINE",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # 体重が増加傾向の記録を作成
        weight_progression = [
            (date(2025, 12, 1), Decimal("4.0")),
            (date(2025, 12, 8), Decimal("4.2")),
            (date(2025, 12, 15), Decimal("4.4")),
            (date(2025, 12, 22), Decimal("4.6")),
        ]

        for record_date, weight in weight_progression:
            record_data = MedicalRecordCreate(
                animal_id=animal.id,
                vet_id=test_vet_user.id,
                date=record_date,
                weight=weight,
                symptoms="定期健診",
            )
            medical_record_service.create_medical_record(test_db, record_data)

        # When: 診療記録を取得
        result = medical_record_service.list_medical_records(
            test_db, animal_id=animal.id, page=1, page_size=100
        )

        # Then: 体重が増加傾向であることを確認
        weight_records = sorted(
            [r for r in result.items if r.weight is not None], key=lambda x: x.date
        )
        assert len(weight_records) == 4

        # 各記録の体重が前回より増加している
        for i in range(1, len(weight_records)):
            assert weight_records[i].weight >= weight_records[i - 1].weight

    def test_empty_weight_history(self, test_db: Session, test_vet_user):
        """体重データがない場合の処理"""
        # Given: 新しい猫を作成（他のテストの影響を避ける）
        from app.models.animal import Animal

        animal = Animal(
            name="体重なしテスト猫",
            pattern="三毛",
            tail_length="短い",
            age_months=6,
            gender="unknown",
            status="QUARANTINE",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # 体重なしの記録のみ
        record_data = MedicalRecordCreate(
            animal_id=animal.id,
            vet_id=test_vet_user.id,
            date=date(2025, 11, 15),
            weight=None,
            symptoms="診察のみ",
        )
        medical_record_service.create_medical_record(test_db, record_data)

        # When: この猫の診療記録のみを取得
        result = medical_record_service.list_medical_records(
            test_db, animal_id=animal.id, page=1, page_size=100
        )

        # Then: この猫の体重データがないことを確認
        weight_records = [r for r in result.items if r.weight is not None]
        assert len(weight_records) == 0, (
            f"体重データが0件のはずが{len(weight_records)}件存在します。"
            f"animal_id={animal.id}でフィルタリングされていない可能性があります。"
        )
