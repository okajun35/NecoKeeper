"""
ボランティア管理サービスのテスト

t-wada準拠のテスト設計:
- ドメインロジックの検証
- 境界値テスト
- エラーハンドリングの検証
- 副作用の検証（活動履歴など）
"""

from __future__ import annotations

from datetime import date

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.volunteer import Volunteer
from app.schemas.volunteer import VolunteerCreate, VolunteerUpdate
from app.services import volunteer_service


class TestCreateVolunteer:
    """ボランティア登録のテスト"""

    def test_create_volunteer_success(self, test_db: Session) -> None:
        """正常系: ボランティアを登録できる"""
        # Given
        volunteer_data = VolunteerCreate(
            name="田中太郎",
            contact="090-1234-5678",
            affiliation="保護猫団体A",
            status="active",
        )

        # When
        result = volunteer_service.create_volunteer(test_db, volunteer_data)

        # Then
        assert result.id is not None
        assert result.name == "田中太郎"
        assert result.contact == "090-1234-5678"
        assert result.affiliation == "保護猫団体A"
        assert result.status == "active"
        assert result.started_at == date.today()

    def test_create_volunteer_with_minimal_fields(self, test_db: Session) -> None:
        """正常系: 必須フィールドのみでボランティアを登録できる"""
        # Given
        volunteer_data = VolunteerCreate(name="佐藤花子")

        # When
        result = volunteer_service.create_volunteer(test_db, volunteer_data)

        # Then
        assert result.id is not None
        assert result.name == "佐藤花子"
        assert result.contact is None
        assert result.affiliation is None
        assert result.status == "active"  # デフォルト値

    def test_create_volunteer_with_inactive_status(self, test_db: Session) -> None:
        """正常系: 非アクティブ状態でボランティアを登録できる"""
        # Given
        volunteer_data = VolunteerCreate(name="山田次郎", status="inactive")

        # When
        result = volunteer_service.create_volunteer(test_db, volunteer_data)

        # Then
        assert result.status == "inactive"


class TestGetVolunteer:
    """ボランティア詳細取得のテスト"""

    def test_get_volunteer_success(
        self, test_db: Session, test_volunteer: Volunteer
    ) -> None:
        """正常系: ボランティアを取得できる"""
        # When
        result = volunteer_service.get_volunteer(test_db, test_volunteer.id)

        # Then
        assert result.id == test_volunteer.id
        assert result.name == test_volunteer.name

    def test_get_volunteer_not_found(self, test_db: Session) -> None:
        """異常系: 存在しないIDで404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            volunteer_service.get_volunteer(test_db, 99999)

        assert exc_info.value.status_code == 404
        assert "99999" in exc_info.value.detail


class TestListVolunteers:
    """ボランティア一覧取得のテスト"""

    def test_list_volunteers_success(self, test_db: Session) -> None:
        """正常系: ボランティア一覧を取得できる"""
        # Given: 3人のボランティアを作成
        for i in range(3):
            volunteer = Volunteer(name=f"ボランティア{i}", status="active")
            test_db.add(volunteer)
        test_db.commit()

        # When
        result = volunteer_service.list_volunteers(test_db, page=1, page_size=10)

        # Then
        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1

    def test_list_volunteers_with_pagination(self, test_db: Session) -> None:
        """正常系: ページネーション付きで一覧を取得できる"""
        # Given: 5人のボランティアを作成
        for i in range(5):
            volunteer = Volunteer(name=f"ボランティア{i}", status="active")
            test_db.add(volunteer)
        test_db.commit()

        # When: 1ページ目（2件ずつ）
        result_page1 = volunteer_service.list_volunteers(test_db, page=1, page_size=2)

        # Then
        assert result_page1.total == 5
        assert len(result_page1.items) == 2
        assert result_page1.total_pages == 3

        # When: 2ページ目
        result_page2 = volunteer_service.list_volunteers(test_db, page=2, page_size=2)

        # Then
        assert len(result_page2.items) == 2
        assert result_page2.page == 2

    def test_list_volunteers_with_status_filter(self, test_db: Session) -> None:
        """正常系: ステータスフィルター付きで一覧を取得できる"""
        # Given: アクティブ2人、非アクティブ1人
        for i in range(2):
            volunteer = Volunteer(name=f"アクティブ{i}", status="active")
            test_db.add(volunteer)
        volunteer_inactive = Volunteer(name="非アクティブ", status="inactive")
        test_db.add(volunteer_inactive)
        test_db.commit()

        # When: アクティブのみフィルター
        result = volunteer_service.list_volunteers(
            test_db, page=1, page_size=10, status_filter="active"
        )

        # Then
        assert result.total == 2
        assert all(v.status == "active" for v in result.items)

    def test_list_volunteers_empty(self, test_db: Session) -> None:
        """境界値: ボランティアが0件の場合"""
        # When
        result = volunteer_service.list_volunteers(test_db, page=1, page_size=10)

        # Then
        assert result.total == 0
        assert len(result.items) == 0
        assert result.total_pages == 0


class TestUpdateVolunteer:
    """ボランティア更新のテスト"""

    def test_update_volunteer_success(
        self, test_db: Session, test_volunteer: Volunteer
    ) -> None:
        """正常系: ボランティア情報を更新できる"""
        # Given
        update_data = VolunteerUpdate(
            contact="080-9876-5432", affiliation="保護猫団体B"
        )

        # When
        result = volunteer_service.update_volunteer(
            test_db, test_volunteer.id, update_data
        )

        # Then
        assert result.id == test_volunteer.id
        assert result.contact == "080-9876-5432"
        assert result.affiliation == "保護猫団体B"
        assert result.name == test_volunteer.name  # 変更されていない

    def test_update_volunteer_status(
        self, test_db: Session, test_volunteer: Volunteer
    ) -> None:
        """正常系: ステータスを更新できる"""
        # Given
        update_data = VolunteerUpdate(status="inactive")

        # When
        result = volunteer_service.update_volunteer(
            test_db, test_volunteer.id, update_data
        )

        # Then
        assert result.status == "inactive"

    def test_update_volunteer_not_found(self, test_db: Session) -> None:
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = VolunteerUpdate(status="inactive")

        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            volunteer_service.update_volunteer(test_db, 99999, update_data)

        assert exc_info.value.status_code == 404


class TestGetActivityHistory:
    """活動履歴取得のテスト"""

    def test_get_activity_history_with_records(
        self, test_db: Session, test_volunteer: Volunteer, test_animal: Animal
    ) -> None:
        """正常系: 記録がある場合の活動履歴を取得できる"""
        # Given: 3件の世話記録を作成
        for _i in range(3):
            care_log = CareLog(
                log_date=date.today(),
                animal_id=test_animal.id,
                recorder_id=test_volunteer.id,
                recorder_name=test_volunteer.name,
                time_slot="morning",
                appetite=5,
                energy=5,
            )
            test_db.add(care_log)
        test_db.commit()

        # When
        result = volunteer_service.get_activity_history(test_db, test_volunteer.id)

        # Then
        assert result["volunteer_id"] == test_volunteer.id
        assert result["volunteer_name"] == test_volunteer.name
        assert result["record_count"] == 3
        assert result["last_record_date"] is not None

    def test_get_activity_history_no_records(
        self, test_db: Session, test_volunteer: Volunteer
    ) -> None:
        """正常系: 記録がない場合の活動履歴を取得できる"""
        # When
        result = volunteer_service.get_activity_history(test_db, test_volunteer.id)

        # Then
        assert result["volunteer_id"] == test_volunteer.id
        assert result["record_count"] == 0
        assert result["last_record_date"] is None

    def test_get_activity_history_not_found(self, test_db: Session) -> None:
        """異常系: 存在しないIDで404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            volunteer_service.get_activity_history(test_db, 99999)

        assert exc_info.value.status_code == 404


class TestGetActiveVolunteers:
    """アクティブボランティア取得のテスト"""

    def test_get_active_volunteers_success(self, test_db: Session) -> None:
        """正常系: アクティブなボランティアのみ取得できる"""
        # Given: アクティブ2人、非アクティブ1人
        for i in range(2):
            volunteer = Volunteer(name=f"アクティブ{i}", status="active")
            test_db.add(volunteer)
        volunteer_inactive = Volunteer(name="非アクティブ", status="inactive")
        test_db.add(volunteer_inactive)
        test_db.commit()

        # When
        result = volunteer_service.get_active_volunteers(test_db)

        # Then
        assert len(result) == 2
        assert all(v.status == "active" for v in result)

    def test_get_active_volunteers_empty(self, test_db: Session) -> None:
        """境界値: アクティブなボランティアが0人の場合"""
        # Given: 非アクティブのみ
        volunteer = Volunteer(name="非アクティブ", status="inactive")
        test_db.add(volunteer)
        test_db.commit()

        # When
        result = volunteer_service.get_active_volunteers(test_db)

        # Then
        assert len(result) == 0

    def test_get_active_volunteers_sorted_by_name(self, test_db: Session) -> None:
        """正常系: 名前順でソートされている"""
        # Given: 名前が逆順のボランティアを作成
        for name in ["Charlie", "Alice", "Bob"]:
            volunteer = Volunteer(name=name, status="active")
            test_db.add(volunteer)
        test_db.commit()

        # When
        result = volunteer_service.get_active_volunteers(test_db)

        # Then
        assert len(result) == 3
        assert result[0].name == "Alice"
        assert result[1].name == "Bob"
        assert result[2].name == "Charlie"
