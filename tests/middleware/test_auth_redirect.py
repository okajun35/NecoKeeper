"""
認証リダイレクトミドルウェアのテスト

t-wada氏のテスト駆動開発原則に基づき、Given-When-Then形式でテストを記述します。

Context7参照: /fastapi/fastapi
- Middleware Testing
- TestClient

テスト方針:
1. ドメインロジックテスト（最優先）
   - 401エラー時の正しいリダイレクト
   - APIとページリクエストの区別
2. 境界値テスト
   - ログインページ自体へのアクセス
   - 他のステータスコードの処理
3. エッジケースのテスト
   - 各種パスパターン
"""

from __future__ import annotations

import pytest
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.testclient import TestClient

from app.middleware.auth_redirect import AuthRedirectMiddleware


@pytest.fixture
def test_app() -> FastAPI:
    """
    テスト用のFastAPIアプリケーション

    401エラーを返すダミーエンドポイントを含む
    最小構成のアプリケーションを作成します。
    """
    app = FastAPI()

    # ミドルウェアを追加
    app.add_middleware(AuthRedirectMiddleware)

    # テスト用エンドポイント: 常に401を返す
    @app.get("/api/v1/protected")
    async def api_protected(request: Request) -> JSONResponse:
        """APIエンドポイント（401エラー）"""
        raise HTTPException(status_code=401, detail="Unauthorized")

    @app.get("/admin/dashboard")
    async def admin_dashboard(request: Request) -> dict[str, str]:
        """管理画面エンドポイント（401エラー）"""
        raise HTTPException(status_code=401, detail="Unauthorized")

    @app.get("/admin/login")
    async def admin_login(request: Request) -> dict[str, str]:
        """ログインページ（正常）"""
        return {"page": "login"}

    @app.get("/public/page")
    async def public_page(request: Request) -> dict[str, str]:
        """公開ページ（正常）"""
        return {"page": "public"}

    @app.get("/api/v1/public")
    async def api_public(request: Request) -> dict[str, str]:
        """公開APIエンドポイント（正常）"""
        return {"status": "ok"}

    return app


@pytest.fixture
def test_client(test_app: FastAPI) -> TestClient:
    """テストクライアント"""
    return TestClient(test_app)


class TestAuthRedirectMiddleware:
    """
    認証リダイレクトミドルウェアのテスト

    t-wada式のテスト駆動開発に基づき、
    ビジネスロジックを中心にテストを構成します。
    """

    # ==========================================
    # ドメインロジックテスト（最優先）
    # ==========================================

    def test_api_401_returns_json_error(self, test_client: TestClient) -> None:
        """
        正常系: API（/api/v1/）への401エラーはJSONレスポンスを返す

        ビジネスルール:
        - APIリクエストは人間向けではないため、JSONエラーを返す
        - リダイレクトは行わない
        """
        # Given: APIエンドポイントへのリクエスト
        # When: 401エラーが発生する
        response = test_client.get("/api/v1/protected")

        # Then: 401ステータスとJSONレスポンスが返される
        assert response.status_code == 401
        assert response.headers["content-type"] == "application/json"
        data = response.json()
        assert "detail" in data
        assert data["detail"] == "認証が必要です。ログインしてください。"
        # WWW-Authenticateヘッダーも含まれる
        assert "www-authenticate" in response.headers

    def test_admin_page_401_redirects_to_login(self, test_client: TestClient) -> None:
        """
        正常系: 管理画面（/admin）への401エラーはログインページにリダイレクト

        ビジネスルール:
        - ユーザー向けページは自動的にログインページへ誘導
        - 302（一時的なリダイレクト）を使用
        """
        # Given: 管理画面エンドポイントへのリクエスト
        # When: 401エラーが発生する
        response = test_client.get("/admin/dashboard", follow_redirects=False)

        # Then: ログインページへの302リダイレクトが返される
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"

    def test_login_page_401_does_not_redirect(self, test_client: TestClient) -> None:
        """
        境界値テスト: ログインページ自体への401はリダイレクトしない

        エッジケース:
        - ログインページ→ログインページの無限ループを防ぐ
        - 401のままレスポンスを返す
        """
        # Given: ログインページが正常に機能している
        # When: ログインページにアクセス
        response = test_client.get("/admin/login")

        # Then: 正常にレスポンスが返される（この場合は200）
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == "login"

    # ==========================================
    # 境界値テスト
    # ==========================================

    def test_non_401_status_codes_pass_through(self, test_client: TestClient) -> None:
        """
        境界値テスト: 401以外のステータスコードはそのまま通過

        境界値:
        - 200, 404, 500などの他のステータスコードは変更しない
        """
        # Given: 正常に動作する公開ページ
        # When: リクエストを送信
        response = test_client.get("/public/page")

        # Then: ステータスコードは変更されない
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == "public"

    def test_public_api_returns_normally(self, test_client: TestClient) -> None:
        """
        正常系: 公開APIエンドポイントは正常に動作

        確認事項:
        - ミドルウェアが正常なリクエストを妨害しない
        """
        # Given: 公開APIエンドポイント
        # When: リクエストを送信
        response = test_client.get("/api/v1/public")

        # Then: 正常なレスポンスが返される
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"

    # ==========================================
    # エッジケーステスト
    # ==========================================

    def test_api_path_exact_prefix_match(self, test_client: TestClient) -> None:
        """
        エッジケーステスト: /api/v1/で始まるパスのみAPIとして扱う

        確認事項:
        - /api/v1で始まるパスのみJSON応答
        - パス判定の正確性
        """
        # Given: /api/v1/で始まるエンドポイント
        # When: 401エラーが発生
        response = test_client.get("/api/v1/protected")

        # Then: JSONエラーレスポンスが返される
        assert response.status_code == 401
        assert "application/json" in response.headers["content-type"]

    def test_admin_path_prefix_match(self, test_client: TestClient) -> None:
        """
        エッジケーステスト: /adminで始まるパスのみリダイレクト

        確認事項:
        - /adminで始まるパスのみリダイレクト
        - パス判定の正確性
        """
        # Given: /adminで始まるエンドポイント
        # When: 401エラーが発生
        response = test_client.get("/admin/dashboard", follow_redirects=False)

        # Then: ログインページへリダイレクトされる
        assert response.status_code == 302
        assert response.headers["location"] == "/admin/login"

    def test_redirect_status_code_is_302(self, test_client: TestClient) -> None:
        """
        仕様確認テスト: リダイレクトのステータスコードは302

        仕様:
        - 一時的なリダイレクトとして302を使用
        - 永続的なリダイレクト（301）ではない
        """
        # Given: 管理画面エンドポイント
        # When: 401エラーが発生
        response = test_client.get("/admin/dashboard", follow_redirects=False)

        # Then: 302（一時的リダイレクト）が返される
        assert response.status_code == 302

    def test_json_response_includes_www_authenticate_header(
        self, test_client: TestClient
    ) -> None:
        """
        仕様確認テスト: API 401レスポンスにWWW-Authenticateヘッダーを含む

        RFC 7235準拠:
        - 401レスポンスにはWWW-Authenticateヘッダーが必要
        - Bearerトークン認証を示す
        """
        # Given: APIエンドポイント
        # When: 401エラーが発生
        response = test_client.get("/api/v1/protected")

        # Then: WWW-Authenticateヘッダーが含まれる
        assert response.status_code == 401
        assert "www-authenticate" in response.headers
        assert response.headers["www-authenticate"] == "Bearer"


class TestAuthRedirectMiddlewareIntegration:
    """
    統合テスト

    実際のアプリケーションフローに近いシナリオをテストします。
    """

    def test_multiple_redirects_scenario(self, test_client: TestClient) -> None:
        """
        統合テスト: 複数の401エラーが連続しても正しく処理される

        シナリオ:
        1. 管理画面へアクセス → ログインページへリダイレクト
        2. APIへアクセス → JSONエラー
        """
        # Scenario 1: 管理画面へのアクセス
        # Given: 認証されていないユーザー
        # When: 管理画面にアクセス
        response1 = test_client.get("/admin/dashboard", follow_redirects=False)

        # Then: ログインページへリダイレクト
        assert response1.status_code == 302
        assert response1.headers["location"] == "/admin/login"

        # Scenario 2: APIへのアクセス
        # When: 保護されたAPIにアクセス
        response2 = test_client.get("/api/v1/protected")

        # Then: JSONエラーが返される
        assert response2.status_code == 401
        assert "application/json" in response2.headers["content-type"]
