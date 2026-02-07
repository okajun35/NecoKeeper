"""
PDF生成Automation APIのテスト

Requirements: 2.2
"""

from __future__ import annotations

from fastapi import status
from fastapi.testclient import TestClient


class TestGenerateQRCardGridAutomation:
    """面付けQRカードPDF生成Automation APIのテスト"""

    def test_generate_qr_card_grid_success(
        self, test_client: TestClient, test_animals_bulk, automation_api_key: str
    ):
        """
        正常系: QRカードPDF生成成功

        Requirements: 2.2
        """
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:3]]
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert "attachment" in response.headers["content-disposition"]
        assert "qr_card_grid.pdf" in response.headers["content-disposition"]
        assert len(response.content) > 0  # PDFデータが存在する

    def test_generate_qr_card_grid_with_base_url(
        self, test_client: TestClient, test_animals_bulk, automation_api_key: str
    ):
        """
        正常系: カスタムベースURLでQRカードPDF生成

        Requirements: 2.2
        """
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:2]]
        request_data = {
            "animal_ids": animal_ids,
            "base_url": "https://custom.example.com",
        }

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

    def test_generate_qr_card_grid_without_api_key(
        self, test_client: TestClient, test_animals_bulk
    ):
        """
        異常系: API Key未設定（401）

        Requirements: 2.2
        """
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:3]]
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
        )

        # Then
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "X-Automation-Key header is required" in response.json()["detail"]

    def test_generate_qr_card_grid_with_invalid_api_key(
        self, test_client: TestClient, test_animals_bulk
    ):
        """
        異常系: API Key無効（403）

        Requirements: 2.2
        """
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:3]]
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": "invalid-key"},
        )

        # Then
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "Invalid Automation API Key" in response.json()["detail"]

    def test_generate_qr_card_grid_with_nonexistent_animal(
        self, test_client: TestClient, automation_api_key: str
    ):
        """
        異常系: 存在しない猫ID（404）

        Requirements: 2.2
        """
        # Given
        request_data = {"animal_ids": [99999]}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "99999" in response.json()["detail"]

    def test_generate_qr_card_grid_exceeds_limit(
        self, test_client: TestClient, test_animals_bulk, automation_api_key: str
    ):
        """
        異常系: 10枚を超える（422）

        Requirements: 2.2
        """
        # Given: 11枚のIDを指定
        animal_ids = [animal.id for animal in test_animals_bulk[:10]]
        animal_ids.append(99999)  # 11枚目
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: Pydanticバリデーションエラー
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_generate_qr_card_grid_with_empty_list(
        self, test_client: TestClient, automation_api_key: str
    ):
        """
        異常系: 空のIDリスト（422）

        Requirements: 2.2
        """
        # Given
        request_data = {"animal_ids": []}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_generate_qr_card_grid_with_single_animal(
        self, test_client: TestClient, test_animal, automation_api_key: str
    ):
        """
        正常系: 1枚のみ生成

        Requirements: 2.2
        """
        # Given
        request_data = {"animal_ids": [test_animal.id]}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0

    def test_generate_qr_card_grid_with_max_animals(
        self, test_client: TestClient, test_animals_bulk, automation_api_key: str
    ):
        """
        正常系: 最大10枚生成

        Requirements: 2.2
        """
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:10]]
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=request_data,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then
        assert response.status_code == status.HTTP_200_OK
        assert response.headers["content-type"] == "application/pdf"
        assert len(response.content) > 0


class TestPDFAutomationIntegration:
    """PDF生成の統合テスト"""

    def test_create_animal_and_generate_qr(
        self, test_client: TestClient, test_db, automation_api_key: str
    ):
        """
        統合テスト: 猫を登録してQRカードPDFを生成

        Requirements: 2.2
        """
        # Given: 猫を登録
        animal_data = {
            "name": "PDF統合テスト猫",
            "coat_color": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
        }

        create_response = test_client.post(
            "/api/automation/animals",
            json=animal_data,
            headers={"X-Automation-Key": automation_api_key},
        )
        assert create_response.status_code == status.HTTP_201_CREATED
        created_animal = create_response.json()

        # When: 登録した猫のQRカードPDFを生成
        pdf_request = {"animal_ids": [created_animal["id"]]}
        pdf_response = test_client.post(
            "/api/automation/pdf/qr-card-grid",
            json=pdf_request,
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: PDFが生成される
        assert pdf_response.status_code == status.HTTP_200_OK
        assert pdf_response.headers["content-type"] == "application/pdf"
        assert len(pdf_response.content) > 0
