"""
ボランティア管理APIのテスト

APIエンドポイントの統合テスト
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.volunteer import Volunteer


class TestListVolunteers:
    """ボランティア一覧取得APIのテスト"""

    def test_list_volunteers_success(
        self, test_client: TestClient, auth_token: str, test_db: Session
    ):
        """正常系: ボランティア一覧を取得できる"""
        # Given: 2人のボランティアを作成
        for i in range(2):
            volunteer = Volunteer(name=f"ボランティア{i}", status="active")
            test_db.add(volunteer)
        test_db.commit()

        # When
        response = test_client.get(
            "/api/v1/volunteers",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["total"] == 2
        assert len(data["items"]) == 2

    def test_list_volunteers_unauthorized(self, test_client: TestClient):
        """異常系: 認証なしで401エラー"""
        # When
        response = test_client.get("/api/v1/volunteers")

        # Then
        assert response.status_code == 401


class TestCreateVolunteer:
    """ボランティア登録APIのテスト"""

    def test_create_volunteer_success(self, test_client: TestClient, auth_token: str):
        """正常系: ボランティアを登録できる"""
        # Given
        volunteer_data = {
            "name": "新規ボランティア",
            "contact": "090-1234-5678",
            "affiliation": "保護猫団体A",
            "status": "active",
        }

        # When
        response = test_client.post(
            "/api/v1/volunteers",
            json=volunteer_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "新規ボランティア"
        assert data["contact"] == "090-1234-5678"
        assert data["id"] is not None

    def test_create_volunteer_unauthorized(self, test_client: TestClient):
        """異常系: 認証なしで401エラー"""
        # Given
        volunteer_data = {"name": "新規ボランティア"}

        # When
        response = test_client.post("/api/v1/volunteers", json=volunteer_data)

        # Then
        assert response.status_code == 401


class TestGetVolunteer:
    """ボランティア詳細取得APIのテスト"""

    def test_get_volunteer_success(
        self, test_client: TestClient, auth_token: str, test_volunteer: Volunteer
    ):
        """正常系: ボランティア詳細を取得できる"""
        # When
        response = test_client.get(
            f"/api/v1/volunteers/{test_volunteer.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == test_volunteer.id
        assert data["name"] == test_volunteer.name

    def test_get_volunteer_not_found(self, test_client: TestClient, auth_token: str):
        """異常系: 存在しないIDで404エラー"""
        # When
        response = test_client.get(
            "/api/v1/volunteers/99999",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 404


class TestUpdateVolunteer:
    """ボランティア更新APIのテスト"""

    def test_update_volunteer_success(
        self, test_client: TestClient, auth_token: str, test_volunteer: Volunteer
    ):
        """正常系: ボランティア情報を更新できる"""
        # Given
        update_data = {"contact": "080-9876-5432", "status": "inactive"}

        # When
        response = test_client.put(
            f"/api/v1/volunteers/{test_volunteer.id}",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["contact"] == "080-9876-5432"
        assert data["status"] == "inactive"

    def test_update_volunteer_not_found(self, test_client: TestClient, auth_token: str):
        """異常系: 存在しないIDで404エラー"""
        # Given
        update_data = {"status": "inactive"}

        # When
        response = test_client.put(
            "/api/v1/volunteers/99999",
            json=update_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 404


class TestGetActivityHistory:
    """活動履歴取得APIのテスト"""

    def test_get_activity_history_success(
        self, test_client: TestClient, auth_token: str, test_volunteer: Volunteer
    ):
        """正常系: 活動履歴を取得できる"""
        # When
        response = test_client.get(
            f"/api/v1/volunteers/{test_volunteer.id}/activity",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        data = response.json()
        assert data["volunteer_id"] == test_volunteer.id
        assert data["volunteer_name"] == test_volunteer.name
        assert "record_count" in data
        assert "last_record_date" in data

    def test_get_activity_history_not_found(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 存在しないIDで404エラー"""
        # When
        response = test_client.get(
            "/api/v1/volunteers/99999/activity",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 404
