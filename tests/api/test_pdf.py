"""
PDF生成APIエンドポイントのテスト

Requirements: Requirement 2, Requirement 7, Requirement 9
"""

from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.config import settings
from app.models.animal import Animal


class TestQRCardEndpoint:
    """QRカードPDF生成エンドポイントのテスト"""

    def test_generate_qr_card_success(
        self, test_client: TestClient, auth_token: str, test_animal: Animal
    ):
        """正常系: QRカードPDFを生成できる"""
        # Given
        request_data = {
            "animal_id": test_animal.id,
            "base_url": "https://test.example.com",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/qr-card",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        expected_filename = "necro_tag" if settings.kiroween_mode else "qr_card"
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert expected_filename in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_generate_qr_card_unauthorized(
        self, test_client: TestClient, test_animal: Animal
    ):
        """異常系: 認証なしで401エラー"""
        # Given
        request_data = {"animal_id": test_animal.id}

        # When
        response = test_client.post("/api/v1/pdf/qr-card", json=request_data)

        # Then
        assert response.status_code == 401

    def test_generate_qr_card_nonexistent_animal(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given
        request_data = {"animal_id": 99999}

        # When
        response = test_client.post(
            "/api/v1/pdf/qr-card",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 404


class TestQRCardGridEndpoint:
    """面付けQRカードPDF生成エンドポイントのテスト"""

    def test_generate_qr_card_grid_success(
        self, test_client: TestClient, auth_token: str, test_animals_bulk: list[Animal]
    ):
        """正常系: 面付けQRカードPDFを生成できる"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:5]]
        request_data = {
            "animal_ids": animal_ids,
            "base_url": "https://test.example.com",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/qr-card-grid",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        expected_filename = (
            "necro_tags_grid" if settings.kiroween_mode else "qr_card_grid"
        )
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert expected_filename in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_generate_qr_card_grid_exceeds_limit(
        self, test_client: TestClient, auth_token: str, test_animals_bulk: list[Animal]
    ):
        """異常系: 11枚以上のQRカードで422エラー（Pydanticバリデーション）"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:11]]
        request_data = {"animal_ids": animal_ids}

        # When
        response = test_client.post(
            "/api/v1/pdf/qr-card-grid",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 422
        assert "animal_ids" in response.json()["detail"][0]["loc"]


class TestPaperFormEndpoint:
    """紙記録フォームPDF生成エンドポイントのテスト"""

    def test_generate_paper_form_success(
        self, test_client: TestClient, auth_token: str, test_animal: Animal
    ):
        """正常系: 紙記録フォームPDFを生成できる"""
        # Given
        request_data = {
            "animal_id": test_animal.id,
            "year": 2024,
            "month": 11,
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/paper-form",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert "paper_form" in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_generate_paper_form_invalid_month(
        self, test_client: TestClient, auth_token: str, test_animal: Animal
    ):
        """異常系: 不正な月で422エラー"""
        # Given
        request_data = {
            "animal_id": test_animal.id,
            "year": 2024,
            "month": 13,  # 不正な月
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/paper-form",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 422


class TestMedicalDetailEndpoint:
    """診療明細PDF生成エンドポイントのテスト"""

    def test_generate_medical_detail_not_implemented(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 診療記録機能が未実装で501エラー"""
        # Given
        request_data = {"medical_record_id": 1}

        # When
        response = test_client.post(
            "/api/v1/pdf/medical-detail",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 501


class TestReportEndpoint:
    """帳票PDF生成エンドポイントのテスト"""

    def test_generate_report_success(self, test_client: TestClient, auth_token: str):
        """正常系: 帳票PDF生成が成功"""
        # Given
        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/report",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"

    def test_generate_report_medical_summary_success(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_user,
        test_db: Session,
    ):
        """正常系: 診療帳票（利益計算用）PDF生成が成功"""
        # Given
        from app.models.medical_action import MedicalAction
        from app.models.medical_record import MedicalRecord

        action = MedicalAction(
            name="ワクチン",
            valid_from=datetime(2024, 1, 1).date(),
            valid_to=None,
            cost_price=1000,
            selling_price=3000,
            procedure_fee=500,
            currency="JPY",
            unit="回",
        )
        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        record = MedicalRecord(
            animal_id=test_animal.id,
            vet_id=test_user.id,
            date=datetime(2024, 11, 15).date(),
            symptoms="テスト",
            medical_action_id=action.id,
            dosage=2,
        )
        test_db.add(record)
        test_db.commit()

        request_data = {
            "report_type": "medical_summary",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/report",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert response.headers["content-type"] == "application/pdf"
        assert response.content.startswith(b"%PDF")
