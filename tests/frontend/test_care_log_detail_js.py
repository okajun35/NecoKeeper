"""
世話記録詳細JavaScript機能のテスト
Tests for care_log_detail.js functionality
"""

from datetime import date

from app.models.care_log import CareLog


class TestCareLogDetailJSLoad:
    """世話記録詳細の読み込み"""

    def test_load_care_log_detail_success(
        self, test_client, auth_headers, test_db, test_animal, test_user
    ):
        """
        Given: 世話記録が存在する
        When: GET /api/v1/care-logs/{id} をリクエスト
        Then: 200 OK で世話記録詳細が返される
        """
        # Given: 世話記録を作成
        care_log = CareLog(
            animal_id=test_animal.id,
            log_date=date(2024, 11, 20),
            time_slot="morning",
            appetite=0.75,
            energy=5,
            urination=True,
            cleaning=True,
            memo="元気です",
            recorder_id=test_user.id,
            recorder_name=test_user.email,
        )
        test_db.add(care_log)
        test_db.commit()
        care_log_id = care_log.id

        # When: 世話記録詳細をリクエスト
        response = test_client.get(
            f"/api/v1/care-logs/{care_log_id}", headers=auth_headers
        )

        # Then: 成功し、詳細が返される
        assert response.status_code == 200
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert data["log_date"] == "2024-11-20"
        assert data["time_slot"] == "morning"
        assert data["appetite"] == 0.75
        assert data["energy"] == 5
        assert data["urination"] is True
        assert data["cleaning"] is True
        assert data["memo"] == "元気です"

    def test_load_care_log_detail_not_found(self, test_client, auth_headers, test_db):
        """
        Given: 存在しない世話記録ID
        When: GET /api/v1/care-logs/{id} をリクエスト
        Then: 404 Not Found が返される
        """
        # Given: 存在しないID
        non_existent_id = 99999

        # When: 存在しない世話記録をリクエスト
        response = test_client.get(
            f"/api/v1/care-logs/{non_existent_id}", headers=auth_headers
        )

        # Then: 404エラーが返される
        assert response.status_code == 404

    def test_load_care_log_detail_unauthorized(self, test_client, test_db):
        """
        Given: 認証トークンなし
        When: GET /api/v1/care-logs/{id} をリクエスト
        Then: 401 Unauthorized が返される
        """
        # Given: 認証なし
        # When: 世話記録詳細をリクエスト
        response = test_client.get("/api/v1/care-logs/1")

        # Then: 401エラーが返される
        assert response.status_code == 401
