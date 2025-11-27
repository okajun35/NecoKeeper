"""
common.jsのAPIリクエスト関数のテスト

JavaScriptの動作をPythonで統合テストとして検証します。
実際のブラウザ環境での動作を模擬し、apiRequest関数が
正しく動作することを確認します。

Context7参照: /fastapi/fastapi
- TestClient for API testing
"""

from __future__ import annotations

from fastapi.testclient import TestClient


class TestCommonJSAPIRequest:
    """
    common.jsのapiRequest関数の動作検証

    JavaScriptの関数をPythonのテストで検証するアプローチ:
    1. APIエンドポイントが正しいレスポンスを返すことを確認
    2. エラーハンドリングが正しく動作することを確認
    3. 認証トークンが正しく送信されることを確認
    """

    def test_successful_get_request_returns_json(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """
        正常系: GETリクエストが成功しJSONを返す

        apiRequest('/api/v1/animals')の動作を検証
        """
        # Given: 認証済みユーザー
        # When: 動物一覧APIにGETリクエスト
        response = test_client.get("/api/v1/animals", headers=auth_headers)

        # Then: 200 OKとJSONレスポンスが返される
        assert response.status_code == 200
        assert response.headers["content-type"].startswith("application/json")
        data = response.json()
        assert "items" in data or isinstance(data, list)

    def test_unauthorized_request_returns_401(self, test_client: TestClient) -> None:
        """
        異常系: 認証なしのリクエストは401を返す

        apiRequest関数内で401を検出してlogout()を呼び出す
        """
        # Given: 認証トークンなし
        # When: 認証が必要なAPIにアクセス
        response = test_client.get("/api/v1/animals")

        # Then: 401 Unauthorizedが返される
        # ミドルウェアがJSONレスポンスを返す
        assert response.status_code == 401
        assert "application/json" in response.headers.get("content-type", "")

    def test_invalid_token_returns_401(self, test_client: TestClient) -> None:
        """
        異常系: 無効なトークンでは401を返す
        """
        # Given: 無効な認証トークン
        invalid_headers = {"Authorization": "Bearer invalid_token_12345"}

        # When: APIにアクセス
        response = test_client.get("/api/v1/animals", headers=invalid_headers)

        # Then: 401 Unauthorizedが返される
        assert response.status_code == 401

    def test_not_found_request_returns_404(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """
        異常系: 存在しないリソースは404を返す

        apiRequest関数はresponse.okをチェックしてエラーをthrowする
        """
        # Given: 認証済みユーザー
        # When: 存在しない動物IDでアクセス
        response = test_client.get("/api/v1/animals/99999", headers=auth_headers)

        # Then: 404 Not Foundが返される
        assert response.status_code == 404
        data = response.json()
        assert "detail" in data

    def test_validation_error_returns_422(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """
        異常系: バリデーションエラーは422を返す
        """
        # Given: 認証済みユーザーと不正なデータ
        invalid_data = {
            "name": "",  # 空の名前（バリデーションエラー）
            "species": "invalid_species",
        }

        # Debug: Verify token works for a simple GET first
        check = test_client.get("/api/v1/animals", headers=auth_headers)
        if check.status_code != 200:
            print(f"DEBUG: Pre-check failed with {check.status_code}: {check.text}")

        # When: 動物登録APIにPOSTリクエスト
        response = test_client.post(
            "/api/v1/animals", json=invalid_data, headers=auth_headers
        )

        # Debug output if failure
        if response.status_code != 422:
            print(f"DEBUG: Status {response.status_code}, Body: {response.text}")

        # Then: 422 Unprocessable Entityが返される
        assert response.status_code == 422


class TestCommonJSAuthFunctions:
    """
    common.jsの認証関連関数の動作検証
    """

    def test_get_access_token_with_valid_credentials(
        self, test_client: TestClient
    ) -> None:
        """
        正常系: 正しい認証情報でトークンを取得できる

        getAccessToken()がlocalStorageから取得する値を検証
        """
        # Given: 有効な認証情報
        # When: ログインAPIを呼び出し
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "TestPassword123",
            },
        )

        # Then: トークンが返される
        assert response.status_code == 200
        data = response.json()
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_check_auth_redirects_without_token(self, test_client: TestClient) -> None:
        """
        境界値テスト: トークンなしでcheckAuth()を呼ぶと
        ログインページにリダイレクトされる（想定動作）

        実際にはJavaScriptで window.location.href = '/admin/login'
        が実行されるため、ここではAPIの401応答を確認
        """
        # Given: 認証トークンなし
        # When: 保護されたエンドポイントにアクセス
        response = test_client.get("/api/v1/auth/me")

        # Then: 401が返される（JavaScriptでリダイレクト処理）
        assert response.status_code == 401


class TestCommonJSIntegration:
    """
    統合テスト: 実際の使用パターンを検証
    """

    def test_full_workflow_login_and_api_call(self, test_client: TestClient) -> None:
        """
        統合テスト: ログイン → API呼び出しの完全なフロー
        """
        # Step 1: ログイン
        login_response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "TestPassword123",
            },
        )
        assert login_response.status_code == 200
        token = login_response.json()["access_token"]

        # Step 2: トークンを使ってAPIにアクセス
        headers = {"Authorization": f"Bearer {token}"}
        api_response = test_client.get("/api/v1/animals", headers=headers)

        # Then: 成功する
        assert api_response.status_code == 200
        data = api_response.json()
        assert "items" in data or isinstance(data, list)

    def test_sequential_api_calls_with_same_token(
        self, test_client: TestClient, auth_headers: dict[str, str]
    ) -> None:
        """
        統合テスト: 同じトークンで複数のAPI呼び出し

        実際のフロントエンド使用パターン:
        1. 動物一覧取得
        2. 特定の動物の詳細取得
        3. ケアログ取得
        """
        # Scenario: ダッシュボードでの複数API呼び出し

        # Call 1: 動物一覧
        response1 = test_client.get("/api/v1/animals", headers=auth_headers)
        assert response1.status_code == 200

        # Call 2: ユーザー情報
        response2 = test_client.get("/api/v1/auth/me", headers=auth_headers)
        assert response2.status_code == 200

        # Call 3: ダッシュボード統計
        response3 = test_client.get("/api/v1/dashboard/stats", headers=auth_headers)
        assert response3.status_code == 200

        # Then: すべて成功
        assert all(
            [
                response1.status_code == 200,
                response2.status_code == 200,
                response3.status_code == 200,
            ]
        )
