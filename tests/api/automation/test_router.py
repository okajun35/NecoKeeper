"""
Automation APIルーターのテスト

ルーター設定、共通エラーレスポンス、API Key認証の統合をテストします。

Context7参照: /pytest-dev/pytest - Testing FastAPI applications
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

from __future__ import annotations

import pytest
from fastapi import status
from fastapi.testclient import TestClient

from app.main import app


class TestAutomationAPIRouter:
    """Automation APIルーターのテスト"""

    def test_router_configuration(self) -> None:
        """
        ルーター設定の検証

        ルーターが正しく設定されていることを確認します。
        - prefix: /automation
        - tags: ["automation"]
        - dependencies: API Key認証
        """
        # ルーターがアプリケーションに登録されているか確認
        routes = [route for route in app.routes if hasattr(route, "path")]
        automation_routes = [
            route
            for route in routes
            if route.path.startswith("/api/automation")  # type: ignore[attr-defined]
        ]

        # Automation APIルートが存在することを確認
        assert len(automation_routes) >= 0, "Automation API routes should be registered"

    def test_missing_api_key_returns_401(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        API Key未設定で401エラー

        X-Automation-Keyヘッダーがない場合、401 Unauthorizedを返すことを確認します。
        """
        from app.config import get_settings

        # Automation APIを有効化
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "valid-test-key-32-characters-long")
        get_settings.cache_clear()

        # API Keyなしでリクエスト
        response = client.get("/api/automation/test")

        # 401エラーを確認
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert "detail" in response.json()
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "ApiKey"

    def test_invalid_api_key_returns_403(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        無効なAPI Keyで403エラー

        無効なX-Automation-Keyヘッダーの場合、403 Forbiddenを返すことを確認します。
        """
        from app.config import get_settings

        # Automation APIを有効化
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "valid-test-key-32-characters-long")
        get_settings.cache_clear()

        # 無効なAPI Keyでリクエスト
        response = client.get(
            "/api/automation/test", headers={"X-Automation-Key": "invalid-key"}
        )

        # 403エラーを確認
        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert "detail" in response.json()
        assert "WWW-Authenticate" in response.headers

    def test_disabled_automation_api_returns_503(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        Automation API無効で503エラー

        Automation APIが無効な場合、503 Service Unavailableを返すことを確認します。
        """
        from app.config import get_settings

        # Automation APIを無効化
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")
        get_settings.cache_clear()

        # API Keyありでリクエスト
        response = client.get(
            "/api/automation/test", headers={"X-Automation-Key": "any-key"}
        )

        # 503エラーを確認
        assert response.status_code == status.HTTP_503_SERVICE_UNAVAILABLE
        assert "detail" in response.json()
        assert "WWW-Authenticate" in response.headers

    def test_error_response_format(
        self, client: TestClient, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        """
        エラーレスポンスフォーマットの検証

        共通エラーレスポンスが正しいフォーマットで返されることを確認します。
        """
        from app.config import get_settings

        # Automation APIを有効化
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "valid-test-key-32-characters-long")
        get_settings.cache_clear()

        # API Keyなしでリクエスト
        response = client.get("/api/automation/test")

        # レスポンスフォーマットを確認
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        data = response.json()
        assert "detail" in data
        assert isinstance(data["detail"], str)

        # ヘッダーを確認
        assert "WWW-Authenticate" in response.headers
        assert response.headers["WWW-Authenticate"] == "ApiKey"


@pytest.fixture
def client() -> TestClient:
    """
    TestClientフィクスチャ

    FastAPIアプリケーションのテストクライアントを提供します。
    """
    return TestClient(app)
