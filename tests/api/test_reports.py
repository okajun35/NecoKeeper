"""
帳票エクスポートAPIエンドポイントのテスト（多言語対応）

Requirements: Requirement 9, Requirement 25
"""

from __future__ import annotations

from datetime import datetime

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.medical_action import MedicalAction
from app.models.medical_record import MedicalRecord


class TestReportExportEndpoint:
    """帳票エクスポートエンドポイントのテスト"""

    def test_export_daily_report_csv_japanese(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 日本語で日報CSVをエクスポートできる"""
        # Given: テスト用ケアログを作成
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            memo="テスト記録",
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "report_daily" in response.headers["content-disposition"]
        # 日本語ヘッダーの確認
        content = response.content.decode("utf-8-sig")
        assert "記録日時" in content
        assert "猫名" in content

    def test_export_daily_report_csv_english(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 英語で日報CSVをエクスポートできる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="Test User",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            memo="Test record",
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "en",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        # 英語ヘッダーの確認
        content = response.content.decode("utf-8-sig")
        assert "Created At" in content
        assert "Animal Name" in content

    def test_export_weekly_report_excel_japanese(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 日本語で週報Excelをエクスポートできる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="テストユーザー",
            appetite=0.5,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "weekly",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "excel",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
        assert "report_weekly" in response.headers["content-disposition"]

    def test_export_medical_summary_csv_japanese(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_user,
        test_db: Session,
    ):
        """正常系: 日本語で診療帳票（利益計算用）CSVをエクスポートできる"""
        # Given: 診療行為マスタ + 診療記録
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
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert "text/csv" in response.headers["content-type"]
        assert "report_medical_summary" in response.headers["content-disposition"]

        content = response.content.decode("utf-8-sig")
        # ヘッダー（日本語）
        assert "診療記録ID" in content
        assert "診療日" in content
        assert "請求額" in content
        # 金額計算: (3000*2)+500 = 6500
        assert ",6500," in content or "6500" in content

    def test_export_medical_summary_excel_english(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_user,
        test_db: Session,
    ):
        """正常系: 英語で診療帳票（利益計算用）Excelをエクスポートできる"""
        # Given
        action = MedicalAction(
            name="Test Action",
            valid_from=datetime(2024, 1, 1).date(),
            valid_to=None,
            cost_price=10,
            selling_price=30,
            procedure_fee=5,
            currency="USD",
            unit="ml",
        )
        test_db.add(action)
        test_db.commit()
        test_db.refresh(action)

        record = MedicalRecord(
            animal_id=test_animal.id,
            vet_id=test_user.id,
            date=datetime(2024, 11, 15).date(),
            symptoms="Test",
            medical_action_id=action.id,
            dosage=1,
        )
        test_db.add(record)
        test_db.commit()

        request_data = {
            "report_type": "medical_summary",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "excel",
            "locale": "en",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert "spreadsheetml" in response.headers["content-type"]
        assert "report_medical_summary" in response.headers["content-disposition"]

    def test_export_weekly_report_excel_english(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 英語で週報Excelをエクスポートできる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="noon",
            recorder_name="Test User",
            appetite=1.0,
            energy=3,
            urination=False,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 12, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "weekly",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "excel",
            "locale": "en",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200

    def test_export_monthly_report_csv(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 月次集計CSVをエクスポートできる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="evening",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 18, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "monthly",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200

    def test_export_individual_report_csv_with_animal(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 個別帳票CSVをエクスポートできる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "individual",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "animal_id": test_animal.id,
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200

    def test_export_report_invalid_type(self, test_client: TestClient, auth_token: str):
        """異常系: 不正な帳票種別で400エラー"""
        # Given
        request_data = {
            "report_type": "invalid",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 400

    def test_export_report_invalid_format(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 不正な出力形式で400エラー"""
        # Given
        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "invalid",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 400

    def test_export_individual_report_missing_animal_id(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 個別帳票で猫ID未指定で400エラー"""
        # Given
        request_data = {
            "report_type": "individual",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post(
            "/api/v1/reports/export",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 400

    def test_export_report_unauthorized(self, test_client: TestClient):
        """異常系: 認証なしで401エラー"""
        # Given
        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "format": "csv",
            "locale": "ja",
        }

        # When
        response = test_client.post("/api/v1/reports/export", json=request_data)

        # Then
        assert response.status_code == 401


class TestReportPDFEndpoint:
    """帳票PDF生成エンドポイントのテスト"""

    def test_generate_daily_report_pdf_japanese(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 日本語で日報PDFを生成できる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "daily",
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
        assert "report_daily" in response.headers["content-disposition"]
        assert response.content.startswith(b"%PDF")

    def test_generate_daily_report_pdf_english(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 英語で日報PDFを生成できる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="noon",
            recorder_name="Test User",
            appetite=0.5,
            energy=3,
            urination=False,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 12, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "locale": "en",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/report",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert response.content.startswith(b"%PDF")

    def test_generate_weekly_report_pdf_japanese(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 日本語で週報PDFを生成できる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="evening",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 18, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "weekly",
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
        assert response.content.startswith(b"%PDF")

    def test_generate_monthly_report_pdf_english(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 英語で月次集計PDFを生成できる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="morning",
            recorder_name="Test User",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=False,
            created_at=datetime(2024, 11, 15, 9, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "monthly",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "locale": "en",
        }

        # When
        response = test_client.post(
            "/api/v1/pdf/report",
            json=request_data,
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200

    def test_generate_individual_report_pdf_with_animal(
        self,
        test_client: TestClient,
        auth_token: str,
        test_animal: Animal,
        test_db: Session,
    ):
        """正常系: 個別帳票PDFを生成できる"""
        # Given
        care_log = CareLog(
            animal_id=test_animal.id,
            time_slot="evening",
            recorder_name="テストユーザー",
            appetite=1.0,
            energy=3,
            urination=True,
            cleaning=True,
            created_at=datetime(2024, 11, 15, 18, 0, 0),
        )
        test_db.add(care_log)
        test_db.commit()

        request_data = {
            "report_type": "individual",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "animal_id": test_animal.id,
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

    def test_generate_report_pdf_invalid_type(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 不正な帳票種別で400エラー"""
        # Given
        request_data = {
            "report_type": "invalid",
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
        assert response.status_code == 400

    def test_generate_individual_report_pdf_missing_animal_id(
        self, test_client: TestClient, auth_token: str
    ):
        """異常系: 個別帳票で猫ID未指定で400エラー"""
        # Given
        request_data = {
            "report_type": "individual",
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
        assert response.status_code == 400

    def test_generate_report_pdf_unauthorized(self, test_client: TestClient):
        """異常系: 認証なしで401エラー"""
        # Given
        request_data = {
            "report_type": "daily",
            "start_date": "2024-11-01",
            "end_date": "2024-11-30",
            "locale": "ja",
        }

        # When
        response = test_client.post("/api/v1/pdf/report", json=request_data)

        # Then
        assert response.status_code == 401
