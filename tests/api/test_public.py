"""
Public APIエンドポイントのテスト

認証不要の世話記録入力フォーム用APIのテスト。
"""

from __future__ import annotations

from datetime import date

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
            "log_date": "2025-11-15",
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

    def test_create_care_log_public_with_defecation_and_stool_condition_success(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 排便あり+便状態ありで登録できる"""
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
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "defecation": True,
            "stool_condition": 2,
            "cleaning": True,
            "memo": "元気です",
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["defecation"] is True
        assert data["stool_condition"] == 2

    def test_create_care_log_public_defecation_true_without_stool_condition_returns_422(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """異常系: defecation=true で stool_condition 未指定は422"""
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
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "defecation": True,
            "cleaning": True,
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 422

    def test_create_care_log_public_accepts_notes_alias_and_returns_memo(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 入力はnotesでも受理し、レスポンスはmemoで返す"""
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
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "cleaning": True,
            "notes": "notesでもOK",
        }

        # When
        response = test_client.post("/api/v1/public/care-logs", json=care_log_data)

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["memo"] == "notesでもOK"
        assert "notes" not in data

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
            "log_date": "2025-11-15",
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
            "log_date": "2025-11-15",
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
            "log_date": "2025-11-15",
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
            defecation=True,
            stool_condition=2,
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


class TestUpdateCareLogPublic:
    """世話記録更新エンドポイント（Public）のテスト"""

    def _make_volunteer(self, db: Session) -> Volunteer:
        volunteer = Volunteer(
            name="更新テストボランティア", contact="090-9999-9999", status="active"
        )
        db.add(volunteer)
        db.commit()
        db.refresh(volunteer)
        return volunteer

    def _make_care_log(
        self, db: Session, animal: Animal, volunteer: Volunteer
    ) -> CareLog:
        care_log = CareLog(
            animal_id=animal.id,
            recorder_id=volunteer.id,
            recorder_name=volunteer.name,
            log_date=date(2025, 11, 20),
            time_slot="morning",
            appetite=3,
            energy=3,
            urination=True,
            cleaning=True,
            memo="初期メモ",
        )
        db.add(care_log)
        db.commit()
        db.refresh(care_log)
        return care_log

    def test_update_care_log_public_success(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """正常系: 既存記録を更新でき、猫ID/時点は維持される"""
        volunteer = self._make_volunteer(test_db)
        care_log = self._make_care_log(test_db, test_animal, volunteer)

        payload = {"memo": "更新しました", "energy": 4, "cleaning": False}

        response = test_client.put(
            f"/api/v1/public/care-logs/animal/{test_animal.id}/{care_log.id}",
            json=payload,
            headers={"User-Agent": "pytest-agent"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["memo"] == "更新しました"
        assert data["energy"] == 4
        assert data["cleaning"] is False
        assert data["animal_id"] == test_animal.id
        assert data["time_slot"] == "morning"  # 時点は変更不可

        test_db.refresh(care_log)
        assert care_log.memo == "更新しました"
        assert care_log.ip_address is not None
        assert care_log.user_agent == "pytest-agent"

    def test_update_care_log_public_reject_time_slot_change(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """異常系: 時点変更を含む更新は422"""
        volunteer = self._make_volunteer(test_db)
        care_log = self._make_care_log(test_db, test_animal, volunteer)

        response = test_client.put(
            f"/api/v1/public/care-logs/animal/{test_animal.id}/{care_log.id}",
            json={"time_slot": "evening"},
        )

        assert response.status_code == 422

    def test_update_care_log_public_wrong_animal_returns_404(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """異常系: 猫ID不一致で404を返す"""
        volunteer = self._make_volunteer(test_db)
        care_log = self._make_care_log(test_db, test_animal, volunteer)

        another_animal = Animal(
            name="別猫",
            photo="",
            pattern="",
            tail_length="",
            age_months=None,
            gender="",
        )
        test_db.add(another_animal)
        test_db.commit()
        test_db.refresh(another_animal)

        response = test_client.put(
            f"/api/v1/public/care-logs/animal/{another_animal.id}/{care_log.id}",
            json={"memo": "should fail"},
        )

        assert response.status_code == 404

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
            age_months=12,
            gender="female",
            status="保護中",
        )
        animal2 = Animal(
            name="猫2",
            photo="cat2.jpg",
            pattern="三毛",
            tail_length="短い",
            age_months=12,
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


class TestGetAnimalCareLogsList:
    """個別猫の記録一覧取得エンドポイントのテスト"""

    def test_get_animal_care_logs_success(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 個別猫の記録一覧を取得できる"""
        from datetime import date, timedelta

        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        today = date.today()

        # 当日の記録（朝・夕）
        morning_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today,
            time_slot="morning",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
        )
        evening_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today,
            time_slot="evening",
            appetite=4,
            energy=4,
            urination=True,
            cleaning=False,
        )

        # 過去の記録
        past_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today - timedelta(days=3),
            time_slot="noon",
            appetite=3,
            energy=3,
            urination=False,
            cleaning=True,
        )

        test_db.add(morning_log)
        test_db.add(evening_log)
        test_db.add(past_log)
        test_db.commit()

        # When
        response = test_client.get(f"/api/v1/public/care-logs/animal/{test_animal.id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["animal_name"] == test_animal.name
        assert data["animal_photo"] == test_animal.photo

        # 当日の記録状況
        assert data["today_status"]["morning"] is True
        assert data["today_status"]["noon"] is False
        assert data["today_status"]["evening"] is True

        # 直近7日間の記録
        assert len(data["recent_logs"]) == 3

    def test_get_animal_care_logs_no_records(
        self, test_client: TestClient, test_animal: Animal
    ):
        """正常系: 記録がない場合は空リスト"""
        # When
        response = test_client.get(f"/api/v1/public/care-logs/animal/{test_animal.id}")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["today_status"]["morning"] is False
        assert data["today_status"]["noon"] is False
        assert data["today_status"]["evening"] is False
        assert len(data["recent_logs"]) == 0

    def test_get_animal_care_logs_not_found(self, test_client: TestClient):
        """異常系: 存在しない猫IDで404エラー"""
        # When
        response = test_client.get("/api/v1/public/care-logs/animal/99999")

        # Then
        assert response.status_code == 404
        assert "見つかりません" in response.json()["detail"]


class TestGetCareLogDetail:
    """特定記録の詳細取得エンドポイントのテスト"""

    def test_get_care_log_detail_success(
        self, test_client: TestClient, test_animal: Animal, test_db: Session
    ):
        """正常系: 特定記録の詳細を取得できる"""
        # Given
        volunteer = Volunteer(
            name="テストボランティア",
            contact="090-1234-5678",
            status="active",
        )
        test_db.add(volunteer)
        test_db.commit()
        test_db.refresh(volunteer)

        care_log = CareLog(
            animal_id=test_animal.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            time_slot="morning",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
            memo="詳細テスト",
        )
        test_db.add(care_log)
        test_db.commit()
        test_db.refresh(care_log)

        # When
        response = test_client.get(
            f"/api/v1/public/care-logs/animal/{test_animal.id}/{care_log.id}"
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == care_log.id
        assert data["animal_id"] == test_animal.id
        assert data["time_slot"] == "morning"
        assert data["appetite"] == 5
        assert data["energy"] == 5
        assert data["urination"] is True
        assert data["cleaning"] is True
        assert data["memo"] == "詳細テスト"

    def test_get_care_log_detail_not_found_animal(self, test_client: TestClient):
        """異常系: 存在しない猫IDで404エラー"""
        # When
        response = test_client.get("/api/v1/public/care-logs/animal/99999/1")

        # Then
        assert response.status_code == 404
        assert "見つかりません" in response.json()["detail"]

    def test_get_care_log_detail_not_found_log(
        self, test_client: TestClient, test_animal: Animal
    ):
        """異常系: 存在しない記録IDで404エラー"""
        # When
        response = test_client.get(
            f"/api/v1/public/care-logs/animal/{test_animal.id}/99999"
        )

        # Then
        assert response.status_code == 404
        assert "見つかりません" in response.json()["detail"]


class TestGetAllAnimalsStatusToday:
    """全猫の当日記録状況一覧取得エンドポイントのテスト"""

    def test_get_all_animals_status_today_success(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """正常系: 全猫の当日記録状況を取得できる"""
        from datetime import date

        # Given
        # test_animalのステータスを譲渡済みに変更（表示されないようにする）
        test_animal.status = "譲渡済み"
        test_db.commit()

        animal1 = Animal(
            name="猫1",
            photo="cat1.jpg",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="female",
            status="保護中",
        )
        animal2 = Animal(
            name="猫2",
            photo="cat2.jpg",
            pattern="三毛",
            tail_length="短い",
            age_months=12,
            gender="male",
            status="治療中",
        )
        animal3 = Animal(
            name="猫3",
            photo="cat3.jpg",
            pattern="白",
            tail_length="長い",
            age_months=12,
            gender="female",
            status="譲渡済み",  # 譲渡済みは表示されない
        )
        test_db.add(animal1)
        test_db.add(animal2)
        test_db.add(animal3)
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

        today = date.today()

        # 猫1の記録（朝・夕）
        log1_morning = CareLog(
            animal_id=animal1.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today,
            time_slot="morning",
            appetite=5,
            energy=5,
            urination=True,
            cleaning=True,
        )
        log1_evening = CareLog(
            animal_id=animal1.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today,
            time_slot="evening",
            appetite=4,
            energy=4,
            urination=True,
            cleaning=False,
        )

        # 猫2の記録（昼のみ）
        log2_noon = CareLog(
            animal_id=animal2.id,
            recorder_id=volunteer.id,
            recorder_name="テストボランティア",
            log_date=today,
            time_slot="noon",
            appetite=3,
            energy=3,
            urination=False,
            cleaning=True,
        )

        test_db.add(log1_morning)
        test_db.add(log1_evening)
        test_db.add(log2_noon)
        test_db.commit()

        # When
        response = test_client.get("/api/v1/public/care-logs/status/today")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["target_date"] == today.isoformat()
        assert len(data["animals"]) == 2  # 譲渡済みは除外

        # 猫1の記録状況
        animal1_status = next(
            a for a in data["animals"] if a["animal_id"] == animal1.id
        )
        assert animal1_status["animal_name"] == "猫1"
        assert animal1_status["morning_recorded"] is True
        assert animal1_status["noon_recorded"] is False
        assert animal1_status["evening_recorded"] is True

        # 猫2の記録状況
        animal2_status = next(
            a for a in data["animals"] if a["animal_id"] == animal2.id
        )
        assert animal2_status["animal_name"] == "猫2"
        assert animal2_status["morning_recorded"] is False
        assert animal2_status["noon_recorded"] is True
        assert animal2_status["evening_recorded"] is False

    def test_get_all_animals_status_today_no_records(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """正常系: 記録がない場合は全てFalse"""
        from datetime import date

        # Given
        # test_animalのステータスを譲渡済みに変更（表示されないようにする）
        test_animal.status = "譲渡済み"
        test_db.commit()

        animal = Animal(
            name="猫",
            photo="cat.jpg",
            pattern="キジトラ",
            tail_length="長い",
            age_months=12,
            gender="female",
            status="保護中",
        )
        test_db.add(animal)
        test_db.commit()
        test_db.refresh(animal)

        # When
        response = test_client.get("/api/v1/public/care-logs/status/today")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["target_date"] == date.today().isoformat()
        assert len(data["animals"]) == 1

        animal_status = data["animals"][0]
        assert animal_status["animal_id"] == animal.id
        assert animal_status["morning_recorded"] is False
        assert animal_status["noon_recorded"] is False
        assert animal_status["evening_recorded"] is False

    def test_get_all_animals_status_today_empty(
        self, test_client: TestClient, test_db: Session, test_animal: Animal
    ):
        """正常系: 猫がいない場合は空リスト"""
        from datetime import date

        # Given
        # test_animalのステータスを譲渡済みに変更（表示されないようにする）
        test_animal.status = "譲渡済み"
        test_db.commit()

        # When
        response = test_client.get("/api/v1/public/care-logs/status/today")

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["target_date"] == date.today().isoformat()
        assert len(data["animals"]) == 0
