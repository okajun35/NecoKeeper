"""
デモ機能・管理画面パスのテスト

環境変数で表示/ルーティングが切り替わる挙動を検証する。
"""

from __future__ import annotations

import importlib

import pytest
from fastapi.testclient import TestClient

import app.api.v1.admin_pages as admin_pages
import app.config as config
import app.main as main


@pytest.fixture
def client_factory(monkeypatch):
    """環境変数を反映したTestClientを作成し、後処理で設定を戻す"""

    def _make(env: dict[str, str]) -> TestClient:
        for key, value in env.items():
            monkeypatch.setenv(key, value)

        config.get_settings.cache_clear()
        importlib.reload(config)
        importlib.reload(admin_pages)
        importlib.reload(main)
        return TestClient(main.app)

    yield _make

    monkeypatch.delenv("DEMO_FEATURES", raising=False)
    monkeypatch.delenv("ADMIN_PATH", raising=False)
    config.get_settings.cache_clear()
    importlib.reload(config)
    importlib.reload(admin_pages)
    importlib.reload(main)


def test_root_returns_404_when_demo_features_disabled(client_factory) -> None:
    """
    正常系: DEMO_FEATURES=false の場合はルートが404

    Given: DEMO_FEATURES=false
    When: / にアクセス
    Then: 404が返る
    """
    client = client_factory({"DEMO_FEATURES": "false"})

    response = client.get("/")

    assert response.status_code == 404


def test_root_includes_theme_css_when_demo_features_enabled(client_factory) -> None:
    """
    正常系: DEMO_FEATURES=true の場合、ランディングページで theme.css を読み込む

    Given: DEMO_FEATURES=true
    When: / にアクセス
    Then: theme.css のリンクが含まれる
    """
    client = client_factory({"DEMO_FEATURES": "true"})

    response = client.get("/")

    assert response.status_code == 200
    assert "/static/css/theme.css" in response.text


def test_login_page_hides_dev_account_when_demo_features_disabled(
    client_factory,
) -> None:
    """
    正常系: DEMO_FEATURES=false の場合は開発用アカウント表示が非表示

    Given: DEMO_FEATURES=false
    When: /admin/login にアクセス
    Then: 開発用アカウントの文言が含まれない
    """
    client = client_factory({"DEMO_FEATURES": "false"})

    response = client.get("/admin/login")

    assert response.status_code == 200
    assert "開発用アカウント" not in response.text
    assert "admin123" not in response.text


def test_admin_path_customization_changes_routes(client_factory) -> None:
    """
    正常系: ADMIN_PATH を変更すると /admin は404になる

    Given: ADMIN_PATH=secret-admin
    When: /admin と /secret-admin/login にアクセス
    Then: /admin は404、/secret-admin/login は200
    """
    client = client_factory({"ADMIN_PATH": "secret-admin"})

    response_legacy = client.get("/admin")
    response_login = client.get("/secret-admin/login")

    assert response_legacy.status_code == 404
    assert response_login.status_code == 200


def test_admin_path_rejects_invalid_characters(client_factory) -> None:
    """
    異常系: ADMIN_PATH に不正な文字が含まれる場合は起動失敗

    Given: ADMIN_PATH=admin/test (スラッシュ含む)
    When: アプリケーション起動
    Then: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="must contain only alphanumeric"):
        client_factory({"ADMIN_PATH": "admin/test"})


def test_admin_path_rejects_reserved_words(client_factory) -> None:
    """
    異常系: ADMIN_PATH に予約語を使用すると起動失敗

    Given: ADMIN_PATH=api
    When: アプリケーション起動
    Then: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="cannot be a reserved path"):
        client_factory({"ADMIN_PATH": "api"})


def test_admin_path_rejects_empty_string(client_factory) -> None:
    """
    異常系: ADMIN_PATH が空文字列の場合は起動失敗

    Given: ADMIN_PATH=""
    When: アプリケーション起動
    Then: ValueErrorが発生
    """
    with pytest.raises(ValueError, match="must not be empty"):
        client_factory({"ADMIN_PATH": ""})
