"""
認証APIエンドポイントのテスト
"""


class TestLoginEndpoint:
    """ログインエンドポイントのテストクラス"""

    def test_login_success(self, test_client):
        """正しい認証情報でログインできる"""
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "TestPassword123",
            },
        )

        assert response.status_code == 200
        data = response.json()

        # トークンが返されること
        assert "access_token" in data
        assert "token_type" in data
        assert data["token_type"] == "bearer"
        assert len(data["access_token"]) > 0

    def test_login_wrong_password(self, test_client):
        """間違ったパスワードでログインできない"""
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "WrongPassword",
            },
        )

        assert response.status_code == 401
        data = response.json()
        assert "detail" in data

    def test_login_nonexistent_user(self, test_client):
        """存在しないユーザーでログインできない"""
        response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "nonexistent@example.com",
                "password": "SomePassword123",
            },
        )

        assert response.status_code == 401


class TestCurrentUserEndpoint:
    """現在のユーザー情報取得エンドポイントのテストクラス"""

    def test_get_current_user_with_valid_token(self, test_client):
        """有効なトークンでユーザー情報を取得できる"""
        # まずログインしてトークンを取得
        login_response = test_client.post(
            "/api/v1/auth/token",
            data={
                "username": "test@example.com",
                "password": "TestPassword123",
            },
        )
        token = login_response.json()["access_token"]

        # トークンを使ってユーザー情報を取得
        response = test_client.get(
            "/api/v1/auth/me", headers={"Authorization": f"Bearer {token}"}
        )

        assert response.status_code == 200
        data = response.json()

        # ユーザー情報が返されること
        assert data["email"] == "test@example.com"
        assert data["name"] == "Test User"
        assert data["role"] == "staff"
        assert data["is_active"] is True

    def test_get_current_user_without_token(self, test_client):
        """トークンなしではアクセスできない"""
        response = test_client.get("/api/v1/auth/me")

        assert response.status_code == 401

    def test_get_current_user_with_invalid_token(self, test_client):
        """無効なトークンではアクセスできない"""
        response = test_client.get(
            "/api/v1/auth/me", headers={"Authorization": "Bearer invalid_token"}
        )

        assert response.status_code == 401
