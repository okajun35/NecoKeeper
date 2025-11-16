"""
里親管理サービスのテスト

里親希望者と譲渡プロセスのビジネスロジックをテストします。
"""

from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException

from app.models.adoption_record import AdoptionRecord
from app.models.animal import Animal
from app.models.applicant import Applicant
from app.models.status_history import StatusHistory
from app.schemas.adoption import (
    AdoptionRecordCreate,
    AdoptionRecordUpdate,
    ApplicantCreate,
    ApplicantUpdate,
)
from app.services import adoption_service

# ========================================
# Applicant（里親希望者）テスト
# ========================================


class TestCreateApplicant:
    """里親希望者登録のテスト"""

    def test_create_applicant_with_valid_data_success(self, test_db, test_user):
        """正常系: 有効なデータで里親希望者を登録できる"""
        # Given
        applicant_data = ApplicantCreate(
            name="山田太郎",
            contact="090-1234-5678",
            address="東京都渋谷区",
            family="夫婦2人",
            environment="マンション、ペット可",
            conditions="成猫希望",
        )

        # When
        result = adoption_service.create_applicant(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert result.id is not None
        assert result.name == "山田太郎"
        assert result.contact == "090-1234-5678"
        assert result.address == "東京都渋谷区"
        assert result.created_at is not None

    def test_create_applicant_with_minimal_data_success(self, test_db, test_user):
        """正常系: 必須項目のみで里親希望者を登録できる"""
        # Given
        applicant_data = ApplicantCreate(
            name="佐藤花子",
            contact="sato@example.com",
        )

        # When
        result = adoption_service.create_applicant(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert result.id is not None
        assert result.name == "佐藤花子"
        assert result.contact == "sato@example.com"
        assert result.address is None
        assert result.family is None


class TestGetApplicant:
    """里親希望者取得のテスト"""

    def test_get_applicant_with_valid_id_success(self, test_db, test_user):
        """正常系: 有効なIDで里親希望者を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        # When
        result = adoption_service.get_applicant(test_db, applicant.id)

        # Then
        assert result.id == applicant.id
        assert result.name == "山田太郎"

    def test_get_applicant_with_nonexistent_id_raises_404(self, test_db):
        """異常系: 存在しないIDで404エラー"""
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.get_applicant(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestListApplicants:
    """里親希望者一覧取得のテスト"""

    def test_list_applicants_returns_all_applicants(self, test_db):
        """正常系: 全ての里親希望者を取得できる"""
        # Given
        applicants_data = [
            Applicant(name=f"希望者{i}", contact=f"contact{i}@example.com")
            for i in range(5)
        ]
        test_db.add_all(applicants_data)
        test_db.commit()

        # When
        result = adoption_service.list_applicants(test_db)

        # Then
        assert len(result) == 5

    def test_list_applicants_with_pagination(self, test_db):
        """正常系: ページネーションが機能する"""
        # Given
        applicants_data = [
            Applicant(name=f"希望者{i}", contact=f"contact{i}@example.com")
            for i in range(10)
        ]
        test_db.add_all(applicants_data)
        test_db.commit()

        # When
        result = adoption_service.list_applicants(test_db, skip=2, limit=3)

        # Then
        assert len(result) == 3


class TestUpdateApplicant:
    """里親希望者更新のテスト"""

    def test_update_applicant_with_valid_data_success(self, test_db, test_user):
        """正常系: 有効なデータで里親希望者を更新できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        update_data = ApplicantUpdate(contact="090-9876-5432", address="大阪府大阪市")

        # When
        result = adoption_service.update_applicant(
            test_db, applicant.id, update_data, user_id=test_user.id
        )

        # Then
        assert result.contact == "090-9876-5432"
        assert result.address == "大阪府大阪市"
        assert result.name == "山田太郎"  # 変更されていない

    def test_update_applicant_with_nonexistent_id_raises_404(self, test_db, test_user):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = ApplicantUpdate(contact="090-9876-5432")

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.update_applicant(
                test_db, 99999, update_data, user_id=test_user.id
            )
        assert exc_info.value.status_code == 404


# ========================================
# AdoptionRecord（譲渡記録）テスト
# ========================================


class TestCreateInterviewRecord:
    """面談記録登録のテスト"""

    def test_create_interview_record_with_valid_data_success(
        self, test_db, test_animal, test_user
    ):
        """正常系: 有効なデータで面談記録を登録できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record_data = AdoptionRecordCreate(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            interview_date=date(2025, 11, 15),
            interview_note="面談実施。飼育環境良好。",
            decision="pending",
        )

        # When
        result = adoption_service.create_interview_record(
            test_db, record_data, user_id=test_user.id
        )

        # Then
        assert result.id is not None
        assert result.animal_id == test_animal.id
        assert result.applicant_id == applicant.id
        assert result.interview_date == date(2025, 11, 15)
        assert result.decision == "pending"

    def test_create_interview_record_with_nonexistent_animal_raises_404(
        self, test_db, test_user
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record_data = AdoptionRecordCreate(
            animal_id=99999,
            applicant_id=applicant.id,
            interview_date=date(2025, 11, 15),
            decision="pending",
        )

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.create_interview_record(
                test_db, record_data, user_id=test_user.id
            )
        assert exc_info.value.status_code == 404

    def test_create_interview_record_with_nonexistent_applicant_raises_404(
        self, test_db, test_animal, test_user
    ):
        """異常系: 存在しない里親希望者IDで404エラー"""
        # Given
        record_data = AdoptionRecordCreate(
            animal_id=test_animal.id,
            applicant_id=99999,
            interview_date=date(2025, 11, 15),
            decision="pending",
        )

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.create_interview_record(
                test_db, record_data, user_id=test_user.id
            )
        assert exc_info.value.status_code == 404


class TestCreateAdoptionRecord:
    """譲渡記録登録のテスト"""

    def test_create_adoption_record_updates_animal_status(
        self, test_db, test_animal, test_user
    ):
        """正常系: 譲渡記録登録時に猫のステータスが「譲渡済み」に更新される"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        old_status = test_animal.status

        # When
        result = adoption_service.create_adoption_record(
            test_db,
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            adoption_date=date(2025, 11, 20),
            user_id=test_user.id,
        )

        # Then
        assert result.id is not None
        assert result.adoption_date == date(2025, 11, 20)
        assert result.decision == "approved"

        # 猫のステータスが更新されている
        test_db.refresh(test_animal)
        assert test_animal.status == "譲渡済み"

        # ステータス変更履歴が記録されている
        history = (
            test_db.query(StatusHistory)
            .filter(StatusHistory.animal_id == test_animal.id)
            .order_by(StatusHistory.changed_at.desc())
            .first()
        )
        assert history is not None
        assert history.old_status == old_status
        assert history.new_status == "譲渡済み"
        assert history.changed_by == test_user.id

    def test_create_adoption_record_with_nonexistent_animal_raises_404(
        self, test_db, test_user
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.create_adoption_record(
                test_db,
                animal_id=99999,
                applicant_id=applicant.id,
                adoption_date=date(2025, 11, 20),
                user_id=test_user.id,
            )
        assert exc_info.value.status_code == 404


class TestUpdateAdoptionRecord:
    """譲渡記録更新のテスト"""

    def test_update_adoption_record_with_valid_data_success(
        self, test_db, test_animal, test_user
    ):
        """正常系: 有効なデータで譲渡記録を更新できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            adoption_date=date(2025, 11, 20),
            decision="approved",
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        update_data = AdoptionRecordUpdate(follow_up="譲渡後1週間経過。問題なし。")

        # When
        result = adoption_service.update_adoption_record(
            test_db, record.id, update_data, user_id=test_user.id
        )

        # Then
        assert result.follow_up == "譲渡後1週間経過。問題なし。"
        assert result.adoption_date == date(2025, 11, 20)  # 変更されていない

    def test_update_adoption_record_with_nonexistent_id_raises_404(
        self, test_db, test_user
    ):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = AdoptionRecordUpdate(follow_up="フォロー内容")

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.update_adoption_record(
                test_db, 99999, update_data, user_id=test_user.id
            )
        assert exc_info.value.status_code == 404


class TestGetAdoptionRecord:
    """譲渡記録取得のテスト"""

    def test_get_adoption_record_with_valid_id_success(self, test_db, test_animal):
        """正常系: 有効なIDで譲渡記録を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        record = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            adoption_date=date(2025, 11, 20),
            decision="approved",
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        # When
        result = adoption_service.get_adoption_record(test_db, record.id)

        # Then
        assert result.id == record.id
        assert result.decision == "approved"

    def test_get_adoption_record_with_nonexistent_id_raises_404(self, test_db):
        """異常系: 存在しないIDで404エラー"""
        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            adoption_service.get_adoption_record(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestListAdoptionRecords:
    """譲渡記録一覧取得のテスト"""

    def test_list_adoption_records_returns_all_records(self, test_db, test_animal):
        """正常系: 全ての譲渡記録を取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        records_data = [
            AdoptionRecord(
                animal_id=test_animal.id,
                applicant_id=applicant.id,
                interview_date=date(2025, 11, i + 1),
                decision="pending",
            )
            for i in range(3)
        ]
        test_db.add_all(records_data)
        test_db.commit()

        # When
        result = adoption_service.list_adoption_records(test_db)

        # Then
        assert len(result) == 3

    def test_list_adoption_records_filtered_by_animal_id(self, test_db, test_animal):
        """正常系: 特定の猫の譲渡記録のみを取得できる"""
        # Given
        applicant = Applicant(name="山田太郎", contact="090-1234-5678")
        test_db.add(applicant)
        test_db.commit()
        test_db.refresh(applicant)

        # 別の猫を作成
        another_animal = Animal(
            name="別の猫",
            pattern="キジトラ",
            tail_length="長い",
            age="成猫",
            gender="female",
            status="保護中",
        )
        test_db.add(another_animal)
        test_db.commit()
        test_db.refresh(another_animal)

        # test_animalの記録を2件作成
        record1 = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            decision="pending",
        )
        record2 = AdoptionRecord(
            animal_id=test_animal.id,
            applicant_id=applicant.id,
            decision="approved",
        )
        # another_animalの記録を1件作成
        record3 = AdoptionRecord(
            animal_id=another_animal.id,
            applicant_id=applicant.id,
            decision="pending",
        )
        test_db.add_all([record1, record2, record3])
        test_db.commit()

        # When
        result = adoption_service.list_adoption_records(
            test_db, animal_id=test_animal.id
        )

        # Then
        assert len(result) == 2
        assert all(r.animal_id == test_animal.id for r in result)
