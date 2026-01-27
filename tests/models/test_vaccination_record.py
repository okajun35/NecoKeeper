"""
VaccinationRecord モデルのテスト

Issue #83: プロフィールに医療情報を追加
TDD: テスト先行で実装
"""

from datetime import date, datetime

from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.vaccination_record import VaccinationRecord
from app.utils.enums import VaccineCategoryEnum


class TestVaccinationRecordModel:
    """VaccinationRecord モデルのテストクラス"""

    def test_create_vaccination_record(self, test_db: Session) -> None:
        """ワクチン接種記録を作成できること"""
        # 先に猫を作成
        animal = Animal(
            coat_color="キジトラ",
            tail_length="長い",
            gender="male",
        )
        test_db.add(animal)
        test_db.commit()

        # ワクチン記録を作成
        record = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE.value,
            administered_on=date(2026, 1, 15),
        )
        test_db.add(record)
        test_db.commit()

        assert record.id is not None
        assert record.animal_id == animal.id
        assert record.vaccine_category == "3core"
        assert record.administered_on == date(2026, 1, 15)
        assert record.next_due_on is None
        assert record.memo is None

    def test_create_vaccination_record_with_optional_fields(
        self, test_db: Session
    ) -> None:
        """オプションフィールド付きでワクチン記録を作成できること"""
        animal = Animal(
            coat_color="黒",
            tail_length="短い",
            gender="female",
        )
        test_db.add(animal)
        test_db.commit()

        record = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_4CORE.value,
            administered_on=date(2026, 1, 10),
            next_due_on=date(2027, 1, 10),
            memo="ロット番号: ABC123",
        )
        test_db.add(record)
        test_db.commit()

        assert record.next_due_on == date(2027, 1, 10)
        assert record.memo == "ロット番号: ABC123"

    def test_vaccination_record_relationship(self, test_db: Session) -> None:
        """Animal とのリレーションが正しく設定されること"""
        animal = Animal(
            name="リレーションテスト猫",
            coat_color="三毛",
            tail_length="長い",
            gender="female",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        record = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_5CORE.value,
            administered_on=date(2026, 1, 20),
        )
        test_db.add(record)
        test_db.commit()
        test_db.refresh(animal)

        # リレーションを通じてアクセス
        assert record.animal.name == "リレーションテスト猫"
        # この猫固有のレコード数を確認
        own_records = [r for r in animal.vaccination_records if r.id == record.id]
        assert len(own_records) == 1
        assert own_records[0].vaccine_category == "5core"

    def test_multiple_vaccination_records(self, test_db: Session) -> None:
        """同じ猫に複数のワクチン記録を追加できること"""
        animal = Animal(
            name="複数ワクチンテスト猫",
            coat_color="白",
            tail_length="長い",
            gender="male",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # このテスト開始時点のレコード数を記録
        initial_count = len(animal.vaccination_records)

        # 1回目
        record1 = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE.value,
            administered_on=date(2025, 6, 1),
        )
        # 2回目
        record2 = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE.value,
            administered_on=date(2026, 1, 1),
        )
        test_db.add_all([record1, record2])
        test_db.commit()
        test_db.refresh(animal)

        # 2件追加されたことを確認
        assert len(animal.vaccination_records) == initial_count + 2

    def test_cascade_delete(self, test_db: Session) -> None:
        """猫を削除するとワクチン記録も削除されること"""
        animal = Animal(
            coat_color="茶トラ",
            tail_length="短い",
            gender="male",
        )
        test_db.add(animal)
        test_db.commit()

        record = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE.value,
            administered_on=date(2026, 1, 15),
        )
        test_db.add(record)
        test_db.commit()

        record_id = record.id

        # 猫を削除
        test_db.delete(animal)
        test_db.commit()

        # ワクチン記録も削除されていること
        deleted_record = test_db.get(VaccinationRecord, record_id)
        assert deleted_record is None

    def test_timestamps(self, test_db: Session) -> None:
        """created_at と updated_at が自動設定されること"""
        animal = Animal(
            coat_color="グレー",
            tail_length="長い",
            gender="unknown",
        )
        test_db.add(animal)
        test_db.commit()

        record = VaccinationRecord(
            animal_id=animal.id,
            vaccine_category=VaccineCategoryEnum.VACCINE_3CORE.value,
            administered_on=date(2026, 1, 15),
        )
        test_db.add(record)
        test_db.commit()

        assert record.created_at is not None
        assert record.updated_at is not None
        assert isinstance(record.created_at, datetime)
        assert isinstance(record.updated_at, datetime)


class TestAnimalMedicalFields:
    """Animal モデルの医療情報フィールドのテスト"""

    def test_fiv_felv_fields_default_none(self, test_db: Session) -> None:
        """FIV/FeLV フィールドがデフォルトで None であること"""
        animal = Animal(
            coat_color="キジトラ",
            tail_length="長い",
            gender="male",
        )
        test_db.add(animal)
        test_db.commit()

        assert animal.fiv_positive is None
        assert animal.felv_positive is None

    def test_fiv_felv_positive(self, test_db: Session) -> None:
        """FIV/FeLV 陽性を設定できること"""
        animal = Animal(
            coat_color="黒",
            tail_length="長い",
            gender="male",
            fiv_positive=True,
            felv_positive=False,
        )
        test_db.add(animal)
        test_db.commit()

        assert animal.fiv_positive is True
        assert animal.felv_positive is False

    def test_sterilization_fields_default_none(self, test_db: Session) -> None:
        """避妊・去勢フィールドがデフォルトで None であること"""
        animal = Animal(
            coat_color="白",
            tail_length="短い",
            gender="female",
        )
        test_db.add(animal)
        test_db.commit()

        assert animal.is_sterilized is None
        assert animal.sterilized_on is None

    def test_sterilization_done(self, test_db: Session) -> None:
        """避妊・去勢済みを設定できること"""
        animal = Animal(
            coat_color="三毛",
            tail_length="長い",
            gender="female",
            is_sterilized=True,
            sterilized_on=date(2025, 12, 1),
        )
        test_db.add(animal)
        test_db.commit()

        assert animal.is_sterilized is True
        assert animal.sterilized_on == date(2025, 12, 1)

    def test_sterilization_not_done(self, test_db: Session) -> None:
        """避妊・去勢未実施を設定できること"""
        animal = Animal(
            coat_color="茶トラ",
            tail_length="長い",
            gender="male",
            is_sterilized=False,
        )
        test_db.add(animal)
        test_db.commit()

        assert animal.is_sterilized is False
        assert animal.sterilized_on is None
