"""
世話記録登録Automation APIのテスト

Automation API専用の世話記録登録エンドポイントをテストします。

Context7参照: /pytest-dev/pytest (Trust Score: 9.5)
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog


class TestCreateCareLogAutomation:
    """POST /api/automation/care-logs のテスト"""

    def test_create_care_log_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        正常系: 世話記録登録成功

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 有効なデータでPOST /api/automation/care-logsを呼び出す
        Then: 201 Createdが返され、世話記録が登録される

        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-32-characters-long")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
            "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
            "from_paper": True,
            "device_tag": "OCR-Import",
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key-32-characters-long"},
        )

        # Then
        assert response.status_code == 201
        data = response.json()

        # レスポンスの検証
        assert data["animal_id"] == test_animal.id
        assert data["animal_name"] == test_animal.name
        assert data["recorder_id"] is None  # 自動化を示す
        assert data["recorder_name"] == "OCR自動取込"
        assert data["log_date"] == "2025-11-24"
        assert data["time_slot"] == "morning"
        assert data["appetite"] == 1.0
        assert data["energy"] == 5
        assert data["urination"] is True
        assert data["cleaning"] is False
        assert data["memo"] == "排便: あり, 嘔吐: なし, 投薬: なし"
        assert data["from_paper"] is True
        assert data["device_tag"] == "OCR-Import"
        assert "id" in data
        assert "created_at" in data

        # データベースの検証
        care_log = test_db.query(CareLog).filter(CareLog.id == data["id"]).first()
        assert care_log is not None
        assert care_log.animal_id == test_animal.id
        assert care_log.recorder_id is None
        assert care_log.recorder_name == "OCR自動取込"
        assert care_log.from_paper is True
        assert care_log.device_tag == "OCR-Import"

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_missing_api_key_returns_401(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        異常系: API Key未設定で401エラー

        Given: Automation APIが有効
        When: API Keyなしでリクエストを送信
        Then: 401 Unauthorizedが返される

        Requirements: 5.6
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            # API Keyヘッダーなし
        )

        # Then
        assert response.status_code == 401
        assert response.json()["detail"] == "X-Automation-Key header is required"

        # データベースに記録されていないことを確認
        care_log_count = test_db.query(CareLog).count()
        assert care_log_count == 0

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_invalid_api_key_returns_403(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        異常系: API Key無効で403エラー

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 間違ったAPI Keyでリクエストを送信
        Then: 403 Forbiddenが返される

        Requirements: 5.6
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "correct-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "wrong-api-key"},
        )

        # Then
        assert response.status_code == 403
        assert response.json()["detail"] == "Invalid Automation API Key"

        # データベースに記録されていないことを確認
        care_log_count = test_db.query(CareLog).count()
        assert care_log_count == 0

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_invalid_data_returns_400(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        異常系: データ不正で400エラー

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 不正なデータ（無効なtime_slot）でリクエストを送信
        Then: 400 Bad Requestが返される

        Requirements: 5.6
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "invalid_slot",  # 無効な時点
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then
        assert response.status_code == 422  # Pydanticのバリデーションエラー
        assert "detail" in response.json()

        # データベースに記録されていないことを確認
        care_log_count = test_db.query(CareLog).count()
        assert care_log_count == 0

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_nonexistent_animal_returns_404(
        self, test_client: TestClient, test_db: Session, monkeypatch
    ):
        """
        異常系: 猫が存在しない場合に404エラー

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 存在しない猫IDでリクエストを送信
        Then: 404 Not Foundが返される

        Requirements: 5.6
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": 99999,  # 存在しない猫ID
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then
        assert response.status_code == 404
        assert "99999" in response.json()["detail"]
        assert "見つかりません" in response.json()["detail"]

        # データベースに記録されていないことを確認
        care_log_count = test_db.query(CareLog).count()
        assert care_log_count == 0

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_with_all_fields(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        正常系: すべてのフィールドを含む世話記録登録

        Given: Automation APIが有効
        When: すべてのオプショナルフィールドを含むデータでリクエストを送信
        Then: 201 Createdが返され、すべてのフィールドが正しく保存される

        Requirements: 5.1, 5.2, 5.3, 5.4
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_id": None,  # 自動化を示す
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "evening",
            "appetite": 0.75,
            "energy": 3,
            "urination": False,
            "cleaning": True,
            "memo": "特記事項なし",
            "from_paper": True,
            "ip_address": "192.168.1.100",
            "user_agent": "Kiro-Hook/1.0",
            "device_tag": "OCR-Import-Device-01",
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then
        assert response.status_code == 201
        data = response.json()

        # すべてのフィールドの検証
        assert data["animal_id"] == test_animal.id
        assert data["recorder_id"] is None
        assert data["recorder_name"] == "OCR自動取込"
        assert data["log_date"] == "2025-11-24"
        assert data["time_slot"] == "evening"
        assert data["appetite"] == 0.75
        assert data["energy"] == 3
        assert data["urination"] is False
        assert data["cleaning"] is True
        assert data["memo"] == "特記事項なし"
        assert data["from_paper"] is True
        assert data["ip_address"] == "192.168.1.100"
        assert data["user_agent"] == "Kiro-Hook/1.0"
        assert data["device_tag"] == "OCR-Import-Device-01"

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_minimal_fields(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        正常系: 最小限のフィールドで世話記録登録

        Given: Automation APIが有効
        When: 必須フィールドのみでリクエストを送信
        Then: 201 Createdが返され、デフォルト値が適用される

        Requirements: 5.1
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "テストユーザー",
            "log_date": "2025-11-24",
            "time_slot": "noon",
            # appetite, energy, urination, cleaning, from_paperはデフォルト値を使用
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then
        assert response.status_code == 201
        data = response.json()

        # デフォルト値の検証
        assert data["appetite"] == 1.0  # デフォルト
        assert data["energy"] == 3  # デフォルト
        assert data["urination"] is False  # デフォルト
        assert data["cleaning"] is False  # デフォルト
        assert data["from_paper"] is False  # デフォルト

        # クリーンアップ
        get_settings.cache_clear()

    @pytest.mark.parametrize(
        "time_slot",
        ["morning", "noon", "evening"],
        ids=["morning", "noon", "evening"],
    )
    def test_create_care_log_all_time_slots(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
        time_slot: str,
    ):
        """
        正常系: すべての時点（morning/noon/evening）で世話記録登録

        Given: Automation APIが有効
        When: 各時点でリクエストを送信
        Then: 201 Createdが返される

        Requirements: 5.1
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "テストユーザー",
            "log_date": "2025-11-24",
            "time_slot": time_slot,
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": True,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then
        assert response.status_code == 201
        data = response.json()
        assert data["time_slot"] == time_slot

        # クリーンアップ
        get_settings.cache_clear()

    def test_create_care_log_automation_api_disabled_returns_503(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        異常系: Automation API無効で503エラー

        Given: Automation APIが無効
        When: リクエストを送信
        Then: 503 Service Unavailableが返される

        Requirements: 5.6
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")
        get_settings.cache_clear()

        care_log_data = {
            "animal_id": test_animal.id,
            "recorder_name": "OCR自動取込",
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
            "urination": True,
            "cleaning": False,
        }

        # When
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "any-key"},
        )

        # Then
        assert response.status_code == 503
        assert response.json()["detail"] == "Automation API is disabled"

        # データベースに記録されていないことを確認
        care_log_count = test_db.query(CareLog).count()
        assert care_log_count == 0

        # クリーンアップ
        get_settings.cache_clear()
