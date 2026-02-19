"""
Automation API統合テスト

ユーザーAPIとAutomation APIの分離、認証方式の独立性、
OpenAPIドキュメント生成を検証する統合テストです。

Context7参照: /pytest-dev/pytest (Trust Score: 9.5)
Requirements: 6.1, 6.2, 6.3, 6.4, 6.5
"""

from __future__ import annotations

from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.models.animal import Animal


class TestAutomationAPIIntegration:
    """Automation APIの統合テスト"""

    def test_automation_api_router_is_registered(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: Automation APIルーターが登録されている

        Given: アプリケーションが起動している
        When: /api/automation/care-logsエンドポイントにアクセス
        Then: エンドポイントが存在する（404ではない）

        Requirements: 6.1
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: API Keyなしでアクセス（401が返るはず）
        response = test_client.post("/api/automation/care-logs", json={})

        # Then: 404ではなく401が返る（エンドポイントが存在する）
        assert response.status_code == 401
        assert response.json()["detail"] == "X-Automation-Key header is required"

        # クリーンアップ
        get_settings.cache_clear()

    def test_user_api_router_is_registered(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ):
        """
        統合テスト: ユーザーAPIルーターが登録されている

        Given: アプリケーションが起動している
        When: /api/v1/care-logsエンドポイントにアクセス
        Then: エンドポイントが存在する

        Requirements: 6.2
        """
        # When: OAuth2トークンでアクセス
        response = test_client.get("/api/v1/care-logs", headers=auth_headers)

        # Then: 404ではない（エンドポイントが存在する）
        assert response.status_code in [200, 401, 403]  # 404以外

    def test_automation_api_does_not_accept_oauth2_token(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
        monkeypatch,
    ):
        """
        統合テスト: Automation APIはOAuth2トークンを受け付けない

        Given: Automation APIが有効
        When: OAuth2トークンでAutomation APIにアクセス
        Then: 401 Unauthorizedが返される（API Keyが必要）

        Requirements: 6.3
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
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 3,
            "vomiting": False,
            "urination": True,
            "cleaning": False,
        }

        # When: OAuth2トークンでAutomation APIにアクセス
        response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers=auth_headers,  # OAuth2トークン
        )

        # Then: 401が返される（API Keyが必要）
        assert response.status_code == 401
        assert response.json()["detail"] == "X-Automation-Key header is required"

        # クリーンアップ
        get_settings.cache_clear()

    def test_user_api_does_not_accept_api_key(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        monkeypatch,
    ):
        """
        統合テスト: ユーザーAPIはAPI Keyを受け付けない

        Given: Automation APIが有効
        When: API KeyでユーザーAPIにアクセス
        Then: 401 Unauthorizedが返される（OAuth2トークンが必要）

        Requirements: 6.4
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: API KeyでユーザーAPIにアクセス
        response = test_client.get(
            "/api/v1/care-logs",
            headers={"X-Automation-Key": "test-api-key"},  # API Key
        )

        # Then: 401が返される（OAuth2トークンが必要）
        assert response.status_code == 401

        # クリーンアップ
        get_settings.cache_clear()

    def test_authentication_schemes_are_independent(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
        monkeypatch,
    ):
        """
        統合テスト: 認証方式が独立している

        Given: Automation APIとユーザーAPIが両方有効
        When: 各APIに適切な認証方式でアクセス
        Then: それぞれ独立して動作する

        Requirements: 6.3, 6.4
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
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 3,
            "vomiting": False,
            "urination": True,
            "cleaning": False,
        }

        # When: Automation APIにAPI Keyでアクセス
        automation_response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # When: ユーザーAPIにOAuth2トークンでアクセス
        user_response = test_client.get("/api/v1/care-logs", headers=auth_headers)

        # Then: 両方とも成功する
        assert automation_response.status_code == 201
        assert user_response.status_code == 200

        # クリーンアップ
        get_settings.cache_clear()

    def test_openapi_schema_includes_api_key_security_scheme(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: OpenAPIスキーマにAPI Key認証方式が含まれる

        Given: アプリケーションが起動している
        When: OpenAPIスキーマを取得
        Then: API Keyのセキュリティスキームが定義されている

        Requirements: 6.5
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: OpenAPIスキーマを取得
        response = test_client.get("/openapi.json")

        # Then: スキーマが取得できる
        assert response.status_code == 200
        schema = response.json()

        # セキュリティスキームの検証
        assert "components" in schema
        assert "securitySchemes" in schema["components"]

        security_schemes = schema["components"]["securitySchemes"]

        # API Keyスキームが定義されている
        assert "APIKeyHeader" in security_schemes
        api_key_scheme = security_schemes["APIKeyHeader"]
        assert api_key_scheme["type"] == "apiKey"
        assert api_key_scheme["in"] == "header"
        assert api_key_scheme["name"] == "X-Automation-Key"

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_endpoints_use_api_key_security(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: Automation APIエンドポイントがAPI Key認証を使用

        Given: アプリケーションが起動している
        When: OpenAPIスキーマを取得
        Then: /api/automation/*エンドポイントがAPIKeyHeaderセキュリティを使用

        Requirements: 6.5
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: OpenAPIスキーマを取得
        response = test_client.get("/openapi.json")
        assert response.status_code == 200
        schema = response.json()

        # Then: /api/automation/care-logsエンドポイントを確認
        paths = schema["paths"]
        assert "/api/automation/care-logs" in paths

        care_logs_endpoint = paths["/api/automation/care-logs"]
        assert "post" in care_logs_endpoint

        post_operation = care_logs_endpoint["post"]

        # セキュリティ要件の検証
        assert "security" in post_operation
        security = post_operation["security"]

        # APIKeyHeaderが使用されている
        assert any("APIKeyHeader" in sec for sec in security)

        # クリーンアップ
        get_settings.cache_clear()

    def test_user_api_endpoints_require_authentication(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: ユーザーAPIエンドポイントが認証を要求する

        Given: アプリケーションが起動している
        When: 認証なしでユーザーAPIにアクセス
        Then: 401 Unauthorizedが返される

        Requirements: 6.4
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: 認証なしでユーザーAPIにアクセス
        response = test_client.get("/api/v1/care-logs")

        # Then: 401が返される
        assert response.status_code == 401

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_and_user_api_coexist(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
        monkeypatch,
    ):
        """
        統合テスト: Automation APIとユーザーAPIが共存する

        Given: 両方のAPIが有効
        When: 同じリソース（世話記録）に対して両方のAPIでアクセス
        Then: 両方とも正常に動作し、データが共有される

        Requirements: 6.1, 6.2
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
            "energy": 3,
            "vomiting": False,
            "urination": True,
            "cleaning": False,
            "from_paper": True,
            "device_tag": "OCR-Import",
        }

        # When: Automation APIで世話記録を作成
        automation_response = test_client.post(
            "/api/automation/care-logs",
            json=care_log_data,
            headers={"X-Automation-Key": "test-api-key"},
        )

        # Then: 作成成功
        assert automation_response.status_code == 201
        created_log = automation_response.json()

        # When: ユーザーAPIで世話記録を取得
        user_response = test_client.get("/api/v1/care-logs", headers=auth_headers)

        # Then: Automation APIで作成した記録が取得できる
        assert user_response.status_code == 200
        response_data = user_response.json()

        # レスポンスがページネーション形式の場合
        if isinstance(response_data, dict) and "items" in response_data:
            care_logs = response_data["items"]
        else:
            care_logs = response_data

        # 作成した記録が含まれている
        assert any(log["id"] == created_log["id"] for log in care_logs)

        # from_paperフラグが保持されている
        created_log_from_user_api = next(
            log for log in care_logs if log["id"] == created_log["id"]
        )
        assert created_log_from_user_api["from_paper"] is True
        assert created_log_from_user_api["device_tag"] == "OCR-Import"

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_disabled_does_not_affect_user_api(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
        monkeypatch,
    ):
        """
        統合テスト: Automation API無効時もユーザーAPIは動作する

        Given: Automation APIが無効
        When: ユーザーAPIにアクセス
        Then: ユーザーAPIは正常に動作する

        Requirements: 6.2
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")
        get_settings.cache_clear()

        # When: ユーザーAPIにアクセス
        response = test_client.get("/api/v1/care-logs", headers=auth_headers)

        # Then: 正常に動作する
        assert response.status_code == 200

        # クリーンアップ
        get_settings.cache_clear()


class TestAutomationAPIErrorHandling:
    """Automation APIのエラーハンドリング統合テスト"""

    def test_automation_api_returns_json_errors(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: Automation APIはJSONエラーを返す

        Given: Automation APIが有効
        When: 認証エラーが発生
        Then: JSONフォーマットのエラーが返される（HTMLリダイレクトではない）

        Requirements: 6.3
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: API Keyなしでアクセス
        response = test_client.post("/api/automation/care-logs", json={})

        # Then: JSONエラーが返される
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/json"
        assert "detail" in response.json()

        # HTMLリダイレクトではない
        assert response.status_code != 302
        assert "text/html" not in response.headers.get("content-type", "")

        # クリーンアップ
        get_settings.cache_clear()

    def test_user_api_401_redirects_to_login_for_admin_pages(
        self, test_client: TestClient
    ):
        """
        統合テスト: ユーザーAPIの401エラーは管理画面でリダイレクト

        Given: ユーザーが未認証
        When: 管理画面にアクセス
        Then: ログインページにリダイレクトされる

        Requirements: 6.4
        """
        # When: 未認証で管理画面にアクセス
        response = test_client.get("/admin/animals", follow_redirects=False)

        # Then: ログインページにリダイレクト
        assert response.status_code == 302
        assert "/admin/login" in response.headers["location"]

    def test_automation_api_401_does_not_redirect(
        self, test_client: TestClient, monkeypatch
    ):
        """
        統合テスト: Automation APIの401エラーはリダイレクトしない

        Given: Automation APIが有効
        When: API Keyなしでアクセス
        Then: JSONエラーが返される（リダイレクトしない）

        Requirements: 6.3
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")
        get_settings.cache_clear()

        # When: API Keyなしでアクセス
        response = test_client.post(
            "/api/automation/care-logs", json={}, follow_redirects=False
        )

        # Then: リダイレクトしない
        assert response.status_code == 401
        assert response.status_code != 302

        # JSONエラーが返される
        assert response.headers["content-type"] == "application/json"
        assert "detail" in response.json()

        # クリーンアップ
        get_settings.cache_clear()
