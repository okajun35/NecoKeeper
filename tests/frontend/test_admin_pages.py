"""
管理画面のテスト

HTMLテンプレートを返すエンドポイントのテスト。
テンプレートファイルの存在と基本的なレンダリングを検証。
"""

from __future__ import annotations

from fastapi.testclient import TestClient

from app.config import get_settings

settings = get_settings()


class TestAnimalPages:
    """猫管理画面のテスト"""

    def test_animals_list_page(self, test_client: TestClient, auth_token: str):
        """正常系: 猫一覧ページが表示される"""
        # When
        response = test_client.get(
            "/admin/animals",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "猫管理".encode() in response.content

    def test_animal_new_page(self, test_client: TestClient, auth_token: str):
        """正常系: 猫新規登録ページが表示される"""
        # When
        response = test_client.get(
            "/admin/animals/new",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "猫新規登録".encode() in response.content
        assert b"animal_new.js" in response.content

    def test_animal_detail_page(
        self, test_client: TestClient, auth_token: str, test_animal
    ):
        """正常系: 猫詳細ページが表示される"""
        # When
        response = test_client.get(
            f"/admin/animals/{test_animal.id}",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()

    def test_animal_edit_page(
        self, test_client: TestClient, auth_token: str, test_animal
    ):
        """正常系: 猫編集ページが表示される"""
        # When
        response = test_client.get(
            f"/admin/animals/{test_animal.id}/edit",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "猫情報編集".encode() in response.content
        assert b"animal_edit.js" in response.content


class TestCareLogPages:
    """世話記録管理画面のテスト"""

    def test_care_logs_list_page(
        self, test_client: TestClient, auth_token: str
    ) -> None:
        """正常系: 世話記録一覧ページが表示される"""
        # When
        response = test_client.get(
            "/admin/care-logs",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()


class TestMedicalRecordPages:
    """診療記録管理画面のテスト"""

    def test_medical_records_list_page(
        self, test_client: TestClient, auth_token: str
    ) -> None:
        """正常系: 診療記録一覧ページが表示される"""
        # When
        response = test_client.get(
            "/admin/medical-records",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "診療記録一覧".encode() in response.content

    def test_medical_record_new_page(
        self, test_client: TestClient, auth_token: str
    ) -> None:
        """正常系: 診療記録新規登録ページが表示される"""
        # When
        response = test_client.get(
            "/admin/medical-records/new",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "新しい診療記録を追加".encode() in response.content


class TestVolunteerPages:
    """ボランティア管理画面のテスト"""

    def test_volunteers_list_page(
        self, test_client: TestClient, auth_token: str
    ) -> None:
        """正常系: ボランティア一覧ページが表示される"""
        # When
        response = test_client.get(
            "/admin/volunteers",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()


class TestDashboardPages:
    """ダッシュボード管理画面のテスト"""

    def test_dashboard_page(self, test_client: TestClient, auth_token: str):
        """正常系: ダッシュボードページが表示される"""
        # When
        response = test_client.get(
            "/admin",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()


class TestAuthPages:
    """認証画面のテスト"""

    def test_login_page_accessible_without_auth(self, test_client: TestClient):
        """
        正常系: ログインページは認証なしでアクセス可能

        Given: 認証トークンなし
        When: /admin/login にアクセス
        Then: 200 OK でログインページが表示される
        """
        # When
        response = test_client.get("/admin/login", follow_redirects=False)

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()
        assert "ログイン".encode() in response.content

    def test_login_page_has_i18n_support(self, test_client: TestClient):
        """
        正常系: ログインページに多言語化サポートがある

        Given: 認証トークンなし
        When: /admin/login にアクセス
        Then: i18next と data-i18n 属性が含まれる
        """
        # When
        response = test_client.get("/admin/login", follow_redirects=False)

        # Then
        assert response.status_code == 200
        # i18nextライブラリが読み込まれている
        assert b"i18next" in response.content
        # i18n.jsが読み込まれている
        assert b"/static/js/i18n.js" in response.content
        # data-i18n属性が使用されている
        assert b"data-i18n" in response.content
        assert b'data-i18n-ns="login"' in response.content
        # 言語切り替えボタンは標準テーマのみ
        if settings.kiroween_mode:
            assert b"language-switcher" not in response.content
        else:
            assert b"language-switcher" in response.content

    def test_login_page_redirects_when_authenticated(
        self, test_client: TestClient, auth_token: str
    ):
        """
        正常系: ログイン済みユーザーはダッシュボードにリダイレクト

        Given: 有効な認証トークン
        When: /admin/login にアクセス
        Then: /admin にリダイレクトされる
        """
        # When
        response = test_client.get(
            "/admin/login",
            headers={"Authorization": f"Bearer {auth_token}"},
            follow_redirects=False,
        )

        # Then
        assert response.status_code == 302
        assert response.headers["location"] == "/admin"

    def test_dashboard_requires_authentication(self, test_client: TestClient):
        """
        セキュリティテスト: ダッシュボードは認証必須

        Given: 認証トークンなし
        When: /admin にアクセス
        Then: 401 Unauthorized または /admin/login にリダイレクト
        """
        # When
        response = test_client.get("/admin", follow_redirects=False)

        # Then
        assert response.status_code in [401, 302]

        if response.status_code == 302:
            assert response.headers["location"] == "/admin/login"

    def test_dashboard_accessible_with_valid_token(
        self, test_client: TestClient, auth_token: str
    ):
        """
        正常系: 認証済みユーザーはダッシュボードにアクセス可能

        Given: 有効な認証トークン
        When: /admin にアクセス
        Then: 200 OK でダッシュボードが表示される
        """
        # When
        response = test_client.get(
            "/admin",
            headers={"Authorization": f"Bearer {auth_token}"},
        )

        # Then
        assert response.status_code == 200
        assert b"text/html" in response.headers["content-type"].encode()

    def test_login_page_boot_sequence_in_kiroween_mode(
        self, test_client: TestClient, monkeypatch
    ):
        """
        正常系: Kiroween Modeでログインページにブートシーケンスが表示される

        Given: KIROWEEN_MODE=True
        When: /admin/login にアクセス
        Then: ブートシーケンスオーバーレイが含まれる

        Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
        """
        # Given: Kiroween Modeを有効化
        from app.config import get_settings

        monkeypatch.setenv("KIROWEEN_MODE", "True")
        get_settings.cache_clear()

        # When
        response = test_client.get("/admin/login", follow_redirects=False)

        # Then
        assert response.status_code == 200

        # ブートシーケンスオーバーレイが含まれる (Requirement 3.1)
        assert b'id="boot-sequence"' in response.content
        assert b'class="boot-sequence"' in response.content

        # ターミナルスタイルのテキストが含まれる (Requirement 3.5)
        assert b"INITIALIZING NECRO-TERMINAL" in response.content
        assert b"LOADING GHOST PROTOCOLS" in response.content
        assert b"ESTABLISHING QUANTUM LINK" in response.content
        assert b"SYSTEM READY" in response.content

        # カーソル点滅要素が含まれる (Requirement 3.5)
        assert b'class="cursor-blink"' in response.content

        # glitch-effects.jsが読み込まれる (BootSequenceクラスを含む)
        assert b"/static/js/glitch-effects.js" in response.content

        # Cleanup
        get_settings.cache_clear()

    def test_login_page_no_boot_sequence_in_standard_mode(
        self, test_client: TestClient, monkeypatch
    ):
        """
        正常系: 標準モードではブートシーケンスが表示されない

        Given: KIROWEEN_MODE=False
        When: /admin/login にアクセス
        Then: ブートシーケンスオーバーレイが含まれない
        """
        # Given: 標準モード
        import importlib

        from app.config import get_settings

        monkeypatch.setenv("KIROWEEN_MODE", "False")
        get_settings.cache_clear()

        # Reload the admin_pages module to pick up new settings
        import app.api.v1.admin_pages

        importlib.reload(app.api.v1.admin_pages)

        # When
        response = test_client.get("/admin/login", follow_redirects=False)

        # Then
        assert response.status_code == 200

        # ブートシーケンスオーバーレイが含まれない
        assert b'id="boot-sequence"' not in response.content
        assert b"INITIALIZING NECRO-TERMINAL" not in response.content

        # glitch-effects.jsが読み込まれない
        assert b"/static/js/glitch-effects.js" not in response.content

        # Cleanup
        get_settings.cache_clear()
        importlib.reload(app.api.v1.admin_pages)

    def test_dashboard_rejects_invalid_token(self, test_client: TestClient):
        """
        異常系: 無効なトークンでダッシュボードにアクセス

        Given: 無効な認証トークン
        When: /admin にアクセス
        Then: 401 Unauthorized
        """
        # When
        response = test_client.get(
            "/admin",
            headers={"Authorization": "Bearer invalid-token"},
            follow_redirects=False,
        )

        # Then
        assert response.status_code in [401, 302]
