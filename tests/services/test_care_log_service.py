"""
世話記録サービスのテスト

t-wada準拠のテスト設計:
- ドメインロジックの検証（サービス層）
- 境界値テスト
- エラーハンドリングの検証
- 副作用の検証
"""

from __future__ import annotations

from datetime import date, datetime, timedelta

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.user import User
from app.schemas.care_log import CareLogCreate, CareLogUpdate
from app.services import care_log_service


class TestCreateCareLog:
    """世話記録登録のテスト"""

    def test_create_care_log_success(self, test_db: Session, test_animal: Animal):
        """正常系: 世話記録を登録できる"""
        # Given
        care_log_data = CareLogCreate(
            animal_id=test_animal.id,
            recorder_name="テスト記録者",
            log_date=date.today(),
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
            memo="元気です",
        )

        # When
        result = care_log_service.create_care_log(test_db, care_log_data)

        # Then
        assert result.id is not None
        assert result.animal_id == test_animal.id
        assert result.recorder_name == "テスト記録者"
        assert result.time_slot == "morning"
        assert result.appetite == 4
        assert result.energy == 5
        assert result.urination is True
        assert result.cleaning is True
        assert result.memo == "元気です"

    def test_create_care_log_minimal_fields(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 最小限のフィールドで世話記録を登録できる"""
        # Given
        care_log_data = CareLogCreate(
            animal_id=test_animal.id,
            recorder_name="記録者",
            log_date=date.today(),
            time_slot="noon",
            appetite=3,
            energy=3,
            urination=False,
            cleaning=False,
        )

        # When
        result = care_log_service.create_care_log(test_db, care_log_data)

        # Then
        assert result.id is not None
        assert result.memo is None

    def test_create_care_log_all_time_slots(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: すべての時点で世話記録を登録できる"""
        # Given
        time_slots = ["morning", "noon", "evening"]

        for time_slot in time_slots:
            care_log_data = CareLogCreate(
                animal_id=test_animal.id,
                recorder_name="記録者",
                log_date=date.today(),
                time_slot=time_slot,
                appetite=3,
                energy=3,
                urination=True,
                cleaning=True,
            )

            # When
            result = care_log_service.create_care_log(test_db, care_log_data)

            # Then
            assert result.time_slot == time_slot

    def test_create_care_log_with_defecation_false_requires_stool_condition_none(
        self, test_db: Session, test_animal: Animal
    ):
        """異常系: defecation=false の場合 stool_condition を指定すると422"""
        # Given
        care_log_data = CareLogCreate(
            animal_id=test_animal.id,
            recorder_name="記録者",
            log_date=date.today(),
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            defecation=False,
            stool_condition=2,
            cleaning=True,
        )

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.create_care_log(test_db, care_log_data)

        assert exc_info.value.status_code == 422

    def test_create_care_log_with_defecation_true_requires_stool_condition(
        self, test_db: Session, test_animal: Animal
    ):
        """異常系: defecation=true の場合 stool_condition 未指定は422"""
        # Given
        care_log_data = CareLogCreate(
            animal_id=test_animal.id,
            recorder_name="記録者",
            log_date=date.today(),
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            defecation=True,
            stool_condition=None,
            cleaning=True,
        )

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.create_care_log(test_db, care_log_data)

        assert exc_info.value.status_code == 422

    @pytest.mark.parametrize("stool_condition", [1, 5])
    def test_create_care_log_with_defecation_true_accepts_boundary_values(
        self,
        test_db: Session,
        test_animal: Animal,
        stool_condition: int,
    ):
        """正常系: defecation=true の場合 stool_condition は1/5を受け入れる"""
        # Given
        care_log_data = CareLogCreate(
            animal_id=test_animal.id,
            recorder_name="記録者",
            log_date=date.today(),
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            defecation=True,
            stool_condition=stool_condition,
            cleaning=True,
        )

        # When
        result = care_log_service.create_care_log(test_db, care_log_data)

        # Then
        assert result.defecation is True
        assert result.stool_condition == stool_condition


class TestGetCareLog:
    """世話記録取得のテスト"""

    def test_get_care_log_success(self, test_db: Session, test_animal: Animal):
        """正常系: 世話記録を取得できる"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        # When
        result = care_log_service.get_care_log(test_db, care_log.id)

        # Then
        assert result.id == care_log.id
        assert result.animal_id == test_animal.id
        assert result.recorder_name == "記録者"

    def test_get_care_log_not_found(self, test_db: Session):
        """異常系: 存在しない世話記録IDを指定した場合"""
        # Given
        non_existent_id = 99999

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.get_care_log(test_db, non_existent_id)

        assert exc_info.value.status_code == 404
        assert (
            f"ID {non_existent_id} の世話記録が見つかりません" in exc_info.value.detail
        )


class TestUpdateCareLog:
    """世話記録更新のテスト"""

    def test_update_care_log_success(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: 世話記録を更新できる"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        update_data = CareLogUpdate(
            appetite=5,
            energy=5,
            memo="更新されました",
        )

        # When
        result = care_log_service.update_care_log(
            test_db, care_log.id, update_data, test_user.id
        )

        # Then
        assert result.appetite == 5
        assert result.energy == 5
        assert result.memo == "更新されました"
        assert result.last_updated_by == test_user.id

    def test_update_care_log_partial_update(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """正常系: 一部のフィールドのみ更新できる"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="noon",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        original_appetite = care_log.appetite
        update_data = CareLogUpdate(energy=5)

        # When
        result = care_log_service.update_care_log(
            test_db, care_log.id, update_data, test_user.id
        )

        # Then
        assert result.energy == 5
        assert result.appetite == original_appetite  # 変更されていない

    def test_update_care_log_defecation_true_without_stool_condition_raises_422(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """異常系: 更新時も defecation=true の場合 stool_condition は必須"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            defecation=False,
            stool_condition=None,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        update_data = CareLogUpdate(defecation=True)

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.update_care_log(
                test_db, care_log.id, update_data, test_user.id
            )

        assert exc_info.value.status_code == 422

    def test_update_care_log_defecation_false_with_stool_condition_raises_422(
        self, test_db: Session, test_animal: Animal, test_user: User
    ):
        """異常系: 更新時も defecation=false の場合 stool_condition はnull必須"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            defecation=True,
            stool_condition=2,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        update_data = CareLogUpdate(defecation=False)

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.update_care_log(
                test_db, care_log.id, update_data, test_user.id
            )

        assert exc_info.value.status_code == 422

    def test_update_care_log_not_found(self, test_db: Session, test_user: User):
        """異常系: 存在しない世話記録を更新しようとした場合"""
        # Given
        non_existent_id = 99999
        update_data = CareLogUpdate(appetite=5)

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            care_log_service.update_care_log(
                test_db, non_existent_id, update_data, test_user.id
            )

        assert exc_info.value.status_code == 404


class TestListCareLogs:
    """世話記録一覧取得のテスト"""

    def test_list_care_logs_default_pagination(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: デフォルトのページネーションで一覧を取得できる"""
        # Given: 複数の世話記録を作成
        for i in range(5):
            care_log = CareLog(
                log_date=date.today(),
                animal_id=test_animal.id,
                recorder_name=f"記録者{i}",
                time_slot="morning",
                appetite=3,
                energy=3,
                urination=True,
                cleaning=True,
            )
            test_db.add(care_log)
        test_db.commit()

        # When
        result = care_log_service.list_care_logs(test_db)

        # Then
        assert len(result.items) <= 20  # デフォルトのpage_size
        assert result.total >= 5
        assert result.page == 1
        assert result.page_size == 20

    def test_list_care_logs_custom_pagination(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: カスタムページネーションで一覧を取得できる"""
        # Given: 複数の世話記録を作成
        for i in range(10):
            care_log = CareLog(
                log_date=date.today(),
                animal_id=test_animal.id,
                recorder_name=f"記録者{i}",
                time_slot="morning",
                appetite=3,
                energy=3,
                urination=True,
                cleaning=True,
            )
            test_db.add(care_log)
        test_db.commit()

        # When
        result = care_log_service.list_care_logs(test_db, page=2, page_size=3)

        # Then
        assert len(result.items) <= 3
        assert result.page == 2
        assert result.page_size == 3

    def test_list_care_logs_filter_by_animal_id(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 猫IDでフィルタリングできる"""
        # Given
        target_animal = test_animals_bulk[0]
        other_animal = test_animals_bulk[1]

        # 対象の猫の記録
        for i in range(3):
            care_log = CareLog(
                log_date=date.today(),
                animal_id=target_animal.id,
                recorder_name=f"記録者{i}",
                time_slot="morning",
                appetite=3,
                energy=3,
                urination=True,
                cleaning=True,
            )
            test_db.add(care_log)

        # 他の猫の記録
        care_log = CareLog(
            log_date=date.today(),
            animal_id=other_animal.id,
            recorder_name="他の記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(care_log)
        test_db.commit()

        # When
        result = care_log_service.list_care_logs(test_db, animal_id=target_animal.id)

        # Then
        assert all(log.animal_id == target_animal.id for log in result.items)
        assert result.total == 3

    def test_list_care_logs_filter_by_date_range(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 日付範囲でフィルタリングできる"""
        # Given
        today = date.today()
        yesterday = today - timedelta(days=1)
        tomorrow = today + timedelta(days=1)

        # 昨日の記録
        old_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="昨日の記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime.combine(yesterday, datetime.min.time()),
        )
        test_db.add(old_log)

        # 今日の記録
        today_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="今日の記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        test_db.add(today_log)
        test_db.commit()

        # When
        result = care_log_service.list_care_logs(
            test_db, start_date=today, end_date=tomorrow
        )

        # Then
        assert result.total == 1
        assert result.items[0].recorder_name == "今日の記録者"

    def test_list_care_logs_filter_by_time_slot(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 時点でフィルタリングできる"""
        # Given
        for time_slot in ["morning", "noon", "evening"]:
            care_log = CareLog(
                log_date=date.today(),
                animal_id=test_animal.id,
                recorder_name=f"{time_slot}の記録者",
                time_slot=time_slot,
                appetite=3,
                energy=3,
                urination=True,
                cleaning=True,
            )
            test_db.add(care_log)
        test_db.commit()

        # When
        result = care_log_service.list_care_logs(test_db, time_slot="morning")

        # Then
        assert all(log.time_slot == "morning" for log in result.items)
        assert result.total == 1

    def test_list_care_logs_empty_result(self, test_db: Session):
        """正常系: 結果が0件の場合"""
        # When
        result = care_log_service.list_care_logs(test_db, animal_id=99999)

        # Then
        assert len(result.items) == 0
        assert result.total == 0
        assert result.total_pages == 0


class TestExportCareLogsCSV:
    """世話記録CSV出力のテスト"""

    def test_export_csv_success(self, test_db: Session, test_animal: Animal):
        """正常系: CSVを出力できる"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="テスト記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
            memo="テストメモ",
        )
        test_db.add(care_log)
        test_db.commit()

        # When
        csv_content = care_log_service.export_care_logs_csv(test_db)

        # Then
        assert "ID" in csv_content
        assert "猫ID" in csv_content
        assert "記録者名" in csv_content
        assert "テスト記録者" in csv_content
        assert "テストメモ" in csv_content

    def test_export_csv_with_animal_filter(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 猫IDでフィルタリングしてCSV出力できる"""
        # Given
        target_animal = test_animals_bulk[0]
        other_animal = test_animals_bulk[1]

        # 対象の猫の記録
        target_log = CareLog(
            log_date=date.today(),
            animal_id=target_animal.id,
            recorder_name="対象記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
        )
        test_db.add(target_log)

        # 他の猫の記録
        other_log = CareLog(
            log_date=date.today(),
            animal_id=other_animal.id,
            recorder_name="他の記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(other_log)
        test_db.commit()

        # When
        csv_content = care_log_service.export_care_logs_csv(
            test_db, animal_id=target_animal.id
        )

        # Then
        assert "対象記録者" in csv_content
        assert "他の記録者" not in csv_content

    def test_export_csv_with_date_filter(self, test_db: Session, test_animal: Animal):
        """正常系: 日付範囲でフィルタリングしてCSV出力できる"""
        # Given
        today = date.today()
        yesterday = today - timedelta(days=1)

        # 昨日の記録
        old_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="昨日の記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime.combine(yesterday, datetime.min.time()),
        )
        test_db.add(old_log)

        # 今日の記録
        today_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="今日の記録者",
            time_slot="morning",
            appetite=4,
            energy=5,
            urination=True,
            cleaning=True,
            created_at=datetime.combine(today, datetime.min.time()),
        )
        test_db.add(today_log)
        test_db.commit()

        # When
        csv_content = care_log_service.export_care_logs_csv(
            test_db, start_date=today, end_date=today
        )

        # Then
        assert "今日の記録者" in csv_content
        assert "昨日の記録者" not in csv_content

    def test_export_csv_empty_result(self, test_db: Session):
        """正常系: 結果が0件の場合でもヘッダーは出力される"""
        # When
        csv_content = care_log_service.export_care_logs_csv(test_db, animal_id=99999)

        # Then
        lines = csv_content.strip().split("\n")
        assert len(lines) == 1  # ヘッダーのみ
        assert "ID" in lines[0]

    def test_export_csv_urination_cleaning_format(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 排尿・清掃のフォーマットが正しい"""
        # Given
        care_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=False,
        )
        test_db.add(care_log)
        test_db.commit()

        # When
        csv_content = care_log_service.export_care_logs_csv(test_db)

        # Then
        assert "有" in csv_content  # 排尿あり
        assert "未" in csv_content  # 清掃未


class TestGetLatestCareLog:
    """最新世話記録取得のテスト"""

    def test_get_latest_care_log_success(self, test_db: Session, test_animal: Animal):
        """正常系: 最新の世話記録を取得できる"""
        # Given
        # 古い記録
        old_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="古い記録者",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime.now() - timedelta(hours=2),
        )
        test_db.add(old_log)
        test_db.flush()

        # 新しい記録
        new_log = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="新しい記録者",
            time_slot="noon",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
            created_at=datetime.now(),
        )
        test_db.add(new_log)
        test_db.commit()

        # When
        result = care_log_service.get_latest_care_log(test_db, test_animal.id)

        # Then
        assert result is not None
        assert result.recorder_name == "新しい記録者"
        assert result.time_slot == "noon"

    def test_get_latest_care_log_no_records(self, test_db: Session):
        """正常系: 世話記録が存在しない場合はNoneを返す"""
        # Given
        non_existent_animal_id = 99999

        # When
        result = care_log_service.get_latest_care_log(test_db, non_existent_animal_id)

        # Then
        assert result is None

    def test_get_latest_care_log_multiple_same_time(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 同じ時刻の記録がある場合はIDが大きい方を返す"""
        # Given
        same_time = datetime.now()

        log1 = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者1",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=same_time,
        )
        test_db.add(log1)
        test_db.flush()

        log2 = CareLog(
            log_date=date.today(),
            animal_id=test_animal.id,
            recorder_name="記録者2",
            time_slot="noon",
            appetite=4,
            energy=4,
            urination=True,
            cleaning=True,
            created_at=same_time,
        )
        test_db.add(log2)
        test_db.commit()
        test_db.refresh(log1)
        test_db.refresh(log2)

        # When
        result = care_log_service.get_latest_care_log(test_db, test_animal.id)

        # Then
        assert result is not None
        assert result.id == max(log1.id, log2.id)
