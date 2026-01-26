"""VaccinationServiceのテスト（Issue #83）."""

from datetime import date

import pytest
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.vaccination_record import VaccinationRecord
from app.schemas.vaccination_record import (
    VaccinationRecordCreate,
    VaccinationRecordUpdate,
)
from app.services.vaccination_service import (
    create_vaccination_record,
    delete_vaccination_record,
    get_vaccination_record,
    list_vaccination_records_by_animal,
    update_vaccination_record,
)
from app.utils.enums import VaccineCategoryEnum


@pytest.fixture
def sample_animal(test_db: Session) -> Animal:
    """テスト用の動物を作成."""
    animal = Animal(
        name="テスト猫",
        coat_color="キジトラ",
        tail_length="長い",
        gender="male",
    )
    test_db.add(animal)
    test_db.commit()
    test_db.refresh(animal)
    return animal


class TestCreateVaccinationRecord:
    """create_vaccination_record関数のテスト."""

    def test_create_minimal(self, test_db: Session, sample_animal: Animal):
        """最小限のデータでワクチン接種記録を作成できる."""
        create_data = VaccinationRecordCreate(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 15),
        )
        record = create_vaccination_record(test_db, create_data)

        assert record.id is not None
        assert record.animal_id == sample_animal.id
        assert record.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE
        assert record.administered_on == date(2025, 1, 15)
        assert record.next_due_on is None
        assert record.memo is None

    def test_create_with_all_fields(self, test_db: Session, sample_animal: Animal):
        """全フィールドを指定してワクチン接種記録を作成できる."""
        create_data = VaccinationRecordCreate(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_5CORE,
            administered_on=date(2025, 1, 15),
            next_due_on=date(2026, 1, 15),
            memo="初回接種、異常なし",
        )
        record = create_vaccination_record(test_db, create_data)

        assert record.vaccine_category == VaccineCategoryEnum.VACCINE_5CORE
        assert record.next_due_on == date(2026, 1, 15)
        assert record.memo == "初回接種、異常なし"


class TestGetVaccinationRecord:
    """get_vaccination_record関数のテスト."""

    def test_get_existing_record(self, test_db: Session, sample_animal: Animal):
        """既存の記録を取得できる."""
        record = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 15),
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        fetched = get_vaccination_record(test_db, record.id)
        assert fetched.id == record.id
        assert fetched.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE

    def test_get_nonexistent_record_raises_error(self, test_db: Session):
        """存在しない記録の取得はエラー."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            get_vaccination_record(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestUpdateVaccinationRecord:
    """update_vaccination_record関数のテスト."""

    def test_update_partial(self, test_db: Session, sample_animal: Animal):
        """部分更新ができる."""
        record = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 15),
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        update_data = VaccinationRecordUpdate(
            memo="追記: 経過良好",
            next_due_on=date(2026, 1, 15),
        )
        updated = update_vaccination_record(test_db, record.id, update_data)

        assert updated.memo == "追記: 経過良好"
        assert updated.next_due_on == date(2026, 1, 15)
        # 更新していないフィールドは変わらない
        assert updated.vaccine_category == VaccineCategoryEnum.VACCINE_3CORE
        assert updated.administered_on == date(2025, 1, 15)

    def test_update_vaccine_category(self, test_db: Session, sample_animal: Animal):
        """ワクチン種別の変更ができる."""
        record = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 15),
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(record)

        update_data = VaccinationRecordUpdate(
            vaccine_category=VaccineCategoryEnum.VACCINE_5CORE
        )
        updated = update_vaccination_record(test_db, record.id, update_data)

        assert updated.vaccine_category == VaccineCategoryEnum.VACCINE_5CORE

    def test_update_nonexistent_raises_error(self, test_db: Session):
        """存在しない記録の更新はエラー."""
        from fastapi import HTTPException

        update_data = VaccinationRecordUpdate(memo="test")
        with pytest.raises(HTTPException) as exc_info:
            update_vaccination_record(test_db, 99999, update_data)
        assert exc_info.value.status_code == 404


class TestDeleteVaccinationRecord:
    """delete_vaccination_record関数のテスト."""

    def test_delete_existing_record(self, test_db: Session, sample_animal: Animal):
        """既存の記録を削除できる."""
        record = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 15),
        )
        test_db.add(record)
        test_db.commit()
        record_id = record.id

        delete_vaccination_record(test_db, record_id)

        # 削除されていることを確認
        deleted = test_db.query(VaccinationRecord).filter_by(id=record_id).first()
        assert deleted is None

    def test_delete_nonexistent_raises_error(self, test_db: Session):
        """存在しない記録の削除はエラー."""
        from fastapi import HTTPException

        with pytest.raises(HTTPException) as exc_info:
            delete_vaccination_record(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestListVaccinationRecordsByAnimal:
    """list_vaccination_records_by_animal関数のテスト."""

    def test_list_returns_only_target_animal_records(
        self, test_db: Session, sample_animal: Animal
    ):
        """対象動物のワクチン接種記録のみを返す."""
        # 初期状態の件数を取得
        initial_count = len(
            list_vaccination_records_by_animal(test_db, sample_animal.id)
        )
        # 記録を1件追加
        record = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 1, 20),
        )
        test_db.add(record)
        test_db.commit()

        records = list_vaccination_records_by_animal(test_db, sample_animal.id)
        assert len(records) == initial_count + 1

    def test_list_multiple_records_sorted_desc(
        self, test_db: Session, sample_animal: Animal
    ):
        """複数の記録を接種日の降順で取得できる."""
        # 日付をユニークにして特定しやすくする
        dates = [
            date(2030, 1, 1),
            date(2030, 6, 1),
            date(2030, 3, 1),
        ]
        record1 = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=dates[0],
        )
        record2 = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_4CORE,
            administered_on=dates[1],
        )
        record3 = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_5CORE,
            administered_on=dates[2],
        )
        test_db.add_all([record1, record2, record3])
        test_db.commit()

        records = list_vaccination_records_by_animal(test_db, sample_animal.id)

        # 追加した3件の日付が降順で含まれていることを確認
        added_dates = [r.administered_on for r in records if r.administered_on in dates]
        assert added_dates == sorted(dates, reverse=True)

    def test_list_filters_by_animal(self, test_db: Session, sample_animal: Animal):
        """指定した動物の記録のみ取得する."""
        # 別の動物
        other_animal = Animal(
            name="別の猫",
            coat_color="三毛",
            tail_length="短い",
            gender="female",
        )
        test_db.add(other_animal)
        test_db.commit()
        test_db.refresh(other_animal)

        initial_count = len(
            list_vaccination_records_by_animal(test_db, sample_animal.id)
        )

        # それぞれに記録を追加
        record1 = VaccinationRecord(
            animal_id=sample_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
            administered_on=date(2025, 7, 1),
        )
        record2 = VaccinationRecord(
            animal_id=other_animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_5CORE,
            administered_on=date(2025, 8, 1),
        )
        test_db.add_all([record1, record2])
        test_db.commit()

        records = list_vaccination_records_by_animal(test_db, sample_animal.id)

        # sample_animalの記録のみ増加（other_animalは含まれない）
        assert len(records) == initial_count + 1
        assert all(r.animal_id == sample_animal.id for r in records)
