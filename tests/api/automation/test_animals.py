"""
猫登録Automation APIのテスト

Requirements: 4.1, 4.2, 4.3, 4.4, 4.5
"""

from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient

from app.models.animal import Animal


class TestCreateAnimalAutomation:
    """猫登録Automation APIのテスト"""

    def test_create_animal_success(
        self, test_client: TestClient, test_db, automation_api_key: str
    ):
        """
        正常系: 猫登録成功

        Requirements: 4.1, 4.2
        """
        # Given
        animal_data = {
            "name": "自動登録猫",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "status": "QUARANTINE",
        }

        # When
        response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["name"] == "自動登録猫"
        assert data["coat_color"] == "キジトラ"
        assert data["tail_length"] == "長い"
        assert data["age_months"] == 12
        assert data["gender"] == "male"
        assert data["status"] == "QUARANTINE"
        assert "id" in data
        assert "created_at" in data
        assert "updated_at" in data

        # データベースに保存されていることを確認
        animal = test_db.query(Animal).filter(Animal.id == data["id"]).first()
        assert animal is not None
        assert animal.name == "自動登録猫"

    def test_create_animal_without_api_key(self, test_client: TestClient):
        """
        異常系: API Key未設定（401）

        Requirements: 4.6
        """
        # Given
        animal_data = {
            "name": "テスト猫",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
        }

        # When
        response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "X-Automation-Key header is required" in response.json()["detail"]

    def test_create_animal_with_invalid_api_key(self, test_client: TestClient):
        """
        異常系: API Key無効（403）

        Requirements: 4.6
        """
        # Given
        animal_data = {
            "name": "テスト猫",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
        }

        # When
        response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": "invalid-key"},
        )

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid Automation API Key" in response.json()["detail"]

    def test_create_animal_with_invalid_gender(
        self, test_client: TestClient, automation_api_key: str
    ):
        """
        異常系: 不正な性別（400）

        Requirements: 4.1
        """
        # Given
        animal_data = {
            "name": "テスト猫",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "invalid",  # 不正な性別
        }

        # When
        response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_create_animal_with_minimal_data(
        self, test_client: TestClient, test_db, automation_api_key: str
    ):
        """
        正常系: 最小限のデータで猫登録

        Requirements: 4.1, 4.2
        """
        # Given
        animal_data = {
            "coat_color": "三毛",
            "tail_length": "短い",
            "age_months": 6,
            "gender": "female",
        }

        # When
        response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["coat_color"] == "三毛"
        assert data["name"] is None  # 名前は任意
        assert "id" in data


class TestGetAnimalAutomation:
    """猫情報取得Automation APIのテスト"""

    def test_get_animal_success(
        self, test_client: TestClient, test_animal, automation_api_key: str
    ):
        """
        正常系: 猫情報取得成功

        Requirements: 4.4
        """
        # When
        response = test_client.get(
            f"/api/automation/animals/{test_animal.id}",
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert data["id"] == test_animal.id
        assert data["name"] == test_animal.name
        assert data["coat_color"] == test_animal.coat_color
        assert data["status"] == test_animal.status

    def test_get_animal_not_found(
        self, test_client: TestClient, automation_api_key: str
    ):
        """
        異常系: 猫が存在しない（404）

        Requirements: 4.5
        """
        # Given
        nonexistent_id = 99999

        # When
        response = test_client.get(
            f"/api/automation/animals/{nonexistent_id}",
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert f"ID {nonexistent_id} の猫が見つかりません" in response.json()["detail"]

    def test_get_animal_without_api_key(self, test_client: TestClient, test_animal):
        """
        異常系: API Key未設定（401）

        Requirements: 4.6
        """
        # When
        response = test_client.get(
            f"/api/automation/animals/{test_animal.id}",
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "X-Automation-Key header is required" in response.json()["detail"]

    def test_get_animal_with_invalid_api_key(
        self, test_client: TestClient, test_animal
    ):
        """
        異常系: API Key無効（403）

        Requirements: 4.6
        """
        # When
        response = test_client.get(
            f"/api/automation/animals/{test_animal.id}",
            headers={"X-Automation-Key": "invalid-key"},
        )

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid Automation API Key" in response.json()["detail"]


class TestAnimalAutomationIntegration:
    """猫登録・取得の統合テスト"""

    def test_create_and_get_animal(
        self, test_client: TestClient, test_db, automation_api_key: str
    ):
        """
        統合テスト: 猫を登録して取得

        Requirements: 4.1, 4.2, 4.4
        """
        # Given: 猫を登録
        animal_data = {
            "name": "統合テスト猫",
            "coat_color": "黒猫",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "female",
            "ear_cut": True,
            "features": "人懐っこい",
        }

        create_response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": automation_api_key},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_animal = create_response.json()

        # When: 登録した猫を取得
        get_response = test_client.get(
            f"/api/automation/animals/{created_animal['id']}",
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 同じデータが取得できる
        assert get_response.status_code == status.HTTP_200_OK
        retrieved_animal = get_response.json()
        assert retrieved_animal["id"] == created_animal["id"]
        assert retrieved_animal["name"] == "統合テスト猫"
        assert retrieved_animal["coat_color"] == "黒猫"
        assert retrieved_animal["ear_cut"] is True
        assert retrieved_animal["features"] == "人懐っこい"
