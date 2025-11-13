"""
Public APIエンドポイントのテスト

認証不要の世話記録入力フォーム用APIのテスト。
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.volunteer import Volunteer


class TestGetAnimalInfo:
    """猫情報取得エンドポイントのテスト"""

    def test_get_animal_info_success(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: 猫情報を取得できる"""
        # When
        response = test_client.get(f"/api/v1/public/animals/{test_animal.id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_animal.id
        assert data["name"] == test_animal.name
        assert data["photo"] == test_animal.photo

    def test_get_animal_info_not_found(self, test_client: TestClient):
        """異常系: 存在しない猫IDで404エラー"""
        # When
        response = test_client.get("/api/v1/public/animals/99999")

        # Then
        assert response.status_code == 404
        assert "見つかりません" in response.json()["detail"]


class TestGetActiveVolunteers:
    """アクティブボランティア一覧取得エンドポイントのテスト"""

    def test_get_active_volunteers_success(
        self, test_client: TestClient, test_db: Session
    ):
        """正常系: アクティブなボランティア一覧を取得できる"""
        # Given
        active_volunteer = Volunteer(
            name="アクティブボランティア",
            contact="090-1111-1111",
            status="active",
        )
        inactive_volunteer = Volunteer(
            name="非アクティブボランティア",
            contact="090-2222-2222",
            status="inactive",
        )
        test_db.add(active_volunteer)
        test_db.add(inactive_volunteer)
        test_db.commit()

        # When
        response = test_client.get("/api/v1/public/volunteers")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 1
        assert data[0]["name"] == "アクティブボランティア"
        assert data[0]["status"] == "active"

    def test_get_active_volunteers_empty(self, test_client: TestClient):
        """正常系: アクティブなボランティアがいない場合は空リスト"""
        # When
        response = test_client.get("/api/v1/public/volunteers")

        # Then
        assert response.status_code == 200
        assert response.json() == []


class TestCreateCareLogPublic:
    """世話記録登録エンドポイント（Public）のテスト"""

    def test_create_care_log_public_success(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 世話記録を登録できる（認証不要）"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": "テストボランティア",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "cleaning": True,
            "memo": "元気です",
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["recorder_id"] == volunteer.id
        assert data["time_slot"] == "morning"
        assert data["appetite"] == 5
        assert data["energy"] == 5
        assert data["urination"] is True
        assert data["cleaning"] is True
        assert data["memo"] == "元気です"
        assert data["ip_address"] is not None  # IPアドレスが記録される
        assert data["user_agent"] is not None  # User-Agentが記録される

    def test_create_care_log_public_minimal_fields(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 最小限のフィールドで登録できる"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": "テストボランティア",
            "time_slot": "morning",
            "appetite": 3,
            "energy": 3,
            "urination": False,
            "cleaning": False,
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["memo"] is None

    def test_create_care_log_public_nonexistent_animal(
        self, test_client: TestClient, test_db: Session
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        care_log_data = {
            "animal_id": 99999,
            "recorder_id": volunteer.id,
            "recorder_name": "テストボランティア",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "cleaning": True,
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 404
        assert "見つかりません" in response.json()["detail"]

    def test_create_care_log_public_invalid_time_slot(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """異常系: 不正な時点で422エラー"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": volunteer.id,
            "recorder_name": "テストボランティア",
            "time_slot": "深夜",  # 不正な時点
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "cleaning": True,
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 422


class TestGetLatestCareLog:
    """最新世話記録取得エンドポイントのテスト"""

    def test_get_latest_care_log_success(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 最新の世話記録を取得できる"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        # 古い記録
        old_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
        )
        test_db.add(old_log)
        test_db.commit()

        # 新しい記録
        new_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            time_slot="noon",
            appetite=5,
            energy=5,
            urination=False,
            cleaning=False,
            memo="最新の記録",
        )
        test_db.add(new_log)
        test_db.commit()
        test_db.refresh(new_log)

        # When
        response = test_client.get(f"/api/v1/public/care-logs/latest/{test_animal.id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == new_log.id
        assert data["time_slot"] == "noon"
        assert data["appetite"] == 5
        assert data["energy"] == 5
        assert data["memo"] == "最新の記録"

    def test_get_latest_care_log_no_records(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: 記録がない場合はnullを返す"""
        # When
        response = test_client.get(f"/api/v1/public/care-logs/latest/{test_animal.id}")

        # Then
        assert response.status_code == 200
        assert response.json() is None

    def test_get_latest_care_log_multiple_animals(
        self, test_client: TestClient, test_db: Session
    ):
        """正常系: 複数の猫がいる場合、指定した猫の記録のみ取得"""
        # Given
        animal1 = Animal(
            name="猫1",
            photo="cat1.jpg",
            pattern="キジトラ",
            tail_length="長い",
            age="成猫",
            gender="female",
            status="保護中",
        )
        animal2 = Animal(
            name="猫2",
            photo="cat2.jpg",
            pattern="三毛",
            tail_length="短い",
            age="成猫",
            gender="male",
            status="保護中",
        )
        test_db.add(animal1)
        test_db.add(animal2)
        test_db.commit()
        test_db.refresh(animal1)
        test_db.refresh(animal2)

        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        # 猫1の記録
        log1 = CareLog(
            animal_id=animal1.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            time_slot="morning",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
            memo="猫1の記録",
        )
        # 猫2の記録
        log2 = CareLog(
            animal_id=animal2.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            time_slot="noon",
            appetite=3,
            energy=3,
            urination=False,
            cleaning=False,
            memo="猫2の記録",
        )
        test_db.add(log1)
        test_db.add(log2)
        test_db.commit()
        test_db.refresh(log1)

        # When
        response = test_client.get(f"/api/v1/public/care-logs/latest/{animal1.id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == log1.id
        assert data["memo"] == "猫1の記録"
