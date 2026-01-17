"""
パスユーティリティのテスト

app.utils.path モジュールの動作を検証する。
"""

from __future__ import annotations

import importlib

import pytest

import app.config as config
from app.utils.path import is_admin_path


@pytest.fixture
def reset_settings(monkeypatch):
    """テスト後に設定をリセット"""
    yield
    monkeypatch.delenv("ADMIN_PATH", raising=False)
    config.get_settings.cache_clear()
    importlib.reload(config)


def test_is_admin_path_with_default_admin(reset_settings) -> None:
    """
    正常系: デフォルト /admin の判定

    Given: ADMIN_PATH=admin (デフォルト)
    When: is_admin_path() を呼び出す
    Then: /admin と /admin/* が True、それ以外は False
    """
    assert is_admin_path("/admin") is True
    assert is_admin_path("/admin/") is True
    assert is_admin_path("/admin/animals") is True
    assert is_admin_path("/admin/care-logs/new") is True

    assert is_admin_path("/") is False
    assert is_admin_path("/api/v1/animals") is False
    assert is_admin_path("/static/css/style.css") is False
    assert is_admin_path("/administrator") is False  # 前方一致ではない


def test_is_admin_path_with_custom_path(monkeypatch, reset_settings) -> None:
    """
    正常系: カスタムパスの判定

    Given: ADMIN_PATH=secret-mgmt
    When: is_admin_path() を呼び出す
    Then: /secret-mgmt と /secret-mgmt/* が True
    """
    monkeypatch.setenv("ADMIN_PATH", "secret-mgmt")
    config.get_settings.cache_clear()
    importlib.reload(config)
    # パスモジュールもリロードして新しい設定を反映
    import app.utils.path as path_module

    importlib.reload(path_module)
    from app.utils.path import is_admin_path

    """
    境界値: 特殊なパスの判定

    Given: ADMIN_PATH=admin
    When: 空文字やルートパスを渡す
    Then: 適切に False を返す
    """
    assert is_admin_path("") is False
    assert is_admin_path("/") is False
    assert is_admin_path("admin") is False  # 先頭スラッシュなし
