"""
API Key認証のテスト

Automation API専用のAPI Key認証機能をテストします。

Context7参照: /pytest-dev/pytest (Trust Score: 9.5)
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5
"""

from __future__ import annotations

import pytest
from fastapi import HTTPException
from sqlalchemy.orm import Session


class TestGetAutomationApiKey:
    """get_automation_api_key のテスト"""

    def test_valid_api_key_success(self, test_db: Session, monkeypatch):
        """
        正常系: 有効なAPI Keyで認証成功

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 正しいAPI Keyでget_automation_api_keyを呼び出す
        Then: API Keyが返される

        Requirements: 1.1, 1.2, 1.6
        """
        # Given
        from app.auth.api_key import get_automation_api_key
        from app.config import get_settings

        # 環境変数を設定
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-32-characters-long")

        # 設定をリロード
        get_settings.cache_clear()

        # When
        result = get_automation_api_key(api_key="test-api-key-32-characters-long")

        # Then
        assert result == "test-api-key-32-characters-long"

        # クリーンアップ
        get_settings.cache_clear()

    def test_invalid_api_key_returns_403(self, test_db: Session, monkeypatch):
        """
        異常系: 無効なAPI Keyで403エラー

        Given: Automation APIが有効で、API Keyが設定されている
        When: 間違ったAPI Keyでget_automation_api_keyを呼び出す
        Then: 403 Forbiddenエラーが発生する

        Requirements: 1.2, 1.4
        """
        # Given
        from app.auth.api_key import get_automation_api_key
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "correct-api-key")

        get_settings.cache_clear()

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            get_automation_api_key(api_key="wrong-api-key")

        assert exc_info.value.status_code == 403
        assert exc_info.value.detail == "Invalid Automation API Key"
        assert exc_info.value.headers == {"WWW-Authenticate": "ApiKey"}

        # クリーンアップ
        get_settings.cache_clear()

    def test_missing_api_key_returns_401(self, test_db: Session, monkeypatch):
        """
        異常系: API Key未設定で401エラー

        Given: Automation APIが有効で、API Keyが設定されている
        When: API Keyなしでget_automation_api_keyを呼び出す
        Then: 401 Unauthorizedエラーが発生する

        Requirements: 1.3
        """
        # Given
        from app.auth.api_key import get_automation_api_key
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")

        get_settings.cache_clear()

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            get_automation_api_key(api_key=None)

        assert exc_info.value.status_code == 401
        assert exc_info.value.detail == "X-Automation-Key header is required"
        assert exc_info.value.headers == {"WWW-Authenticate": "ApiKey"}

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_disabled_returns_503(self, test_db: Session, monkeypatch):
        """
        異常系: Automation API無効で503エラー

        Given: Automation APIが無効
        When: get_automation_api_keyを呼び出す
        Then: 503 Service Unavailableエラーが発生する

        Requirements: 1.5
        """
        # Given
        from app.auth.api_key import get_automation_api_key
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")

        get_settings.cache_clear()

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            get_automation_api_key(api_key="any-key")

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Automation API is disabled"
        assert exc_info.value.headers == {"WWW-Authenticate": "ApiKey"}

        # クリーンアップ
        get_settings.cache_clear()

    def test_api_key_not_configured_returns_503(self, test_db: Session, monkeypatch):
        """
        異常系: API Key未設定（空文字列）で503エラー

        Given: Automation APIが有効だが、API Keyが空文字列
        When: get_automation_api_keyを呼び出す
        Then: 503 Service Unavailableエラーが発生する

        Requirements: 1.5
        """
        # Given
        from app.auth.api_key import get_automation_api_key
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        # 空文字列を設定してAPI Keyが未設定の状態をシミュレート
        monkeypatch.setenv("AUTOMATION_API_KEY", "")

        get_settings.cache_clear()

        # When / Then
        with pytest.raises(HTTPException) as exc_info:
            get_automation_api_key(api_key="any-key")

        assert exc_info.value.status_code == 503
        assert exc_info.value.detail == "Automation API Key is not configured"
        assert exc_info.value.headers == {"WWW-Authenticate": "ApiKey"}

        # クリーンアップ
        get_settings.cache_clear()


class TestVerifyAutomationApiKeyOptional:
    """verify_automation_api_key_optional のテスト"""

    def test_valid_api_key_returns_key(self, test_db: Session, monkeypatch):
        """
        正常系: 有効なAPI Keyが提供された場合はキーを返す

        Given: Automation APIが有効で、正しいAPI Keyが設定されている
        When: 正しいAPI Keyでverify_automation_api_key_optionalを呼び出す
        Then: API Keyが返される

        Requirements: 1.7
        """
        # Given
        from app.auth.api_key import verify_automation_api_key_optional
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")

        get_settings.cache_clear()

        # When
        result = verify_automation_api_key_optional(api_key="test-api-key")

        # Then
        assert result == "test-api-key"

        # クリーンアップ
        get_settings.cache_clear()

    def test_invalid_api_key_returns_none(self, test_db: Session, monkeypatch):
        """
        正常系: 無効なAPI Keyの場合はNoneを返す（エラーにしない）

        Given: Automation APIが有効で、API Keyが設定されている
        When: 間違ったAPI Keyでverify_automation_api_key_optionalを呼び出す
        Then: Noneが返される（エラーにならない）

        Requirements: 1.7
        """
        # Given
        from app.auth.api_key import verify_automation_api_key_optional
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "correct-api-key")

        get_settings.cache_clear()

        # When
        result = verify_automation_api_key_optional(api_key="wrong-api-key")

        # Then
        assert result is None

        # クリーンアップ
        get_settings.cache_clear()

    def test_missing_api_key_returns_none(self, test_db: Session, monkeypatch):
        """
        正常系: API Key未提供の場合はNoneを返す

        Given: Automation APIが有効
        When: API Keyなしでverify_automation_api_key_optionalを呼び出す
        Then: Noneが返される

        Requirements: 1.7
        """
        # Given
        from app.auth.api_key import verify_automation_api_key_optional
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")

        get_settings.cache_clear()

        # When
        result = verify_automation_api_key_optional(api_key=None)

        # Then
        assert result is None

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_disabled_returns_none(self, test_db: Session, monkeypatch):
        """
        正常系: Automation API無効の場合はNoneを返す

        Given: Automation APIが無効
        When: verify_automation_api_key_optionalを呼び出す
        Then: Noneが返される（エラーにならない）

        Requirements: 1.7
        """
        # Given
        from app.auth.api_key import verify_automation_api_key_optional
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")

        get_settings.cache_clear()

        # When
        result = verify_automation_api_key_optional(api_key="any-key")

        # Then
        assert result is None

        # クリーンアップ
        get_settings.cache_clear()

    def test_api_key_not_configured_returns_none(self, test_db: Session, monkeypatch):
        """
        正常系: API Key未設定の場合はNoneを返す

        Given: Automation APIが有効だが、API Keyが設定されていない
        When: verify_automation_api_key_optionalを呼び出す
        Then: Noneが返される

        Requirements: 1.7
        """
        # Given
        from app.auth.api_key import verify_automation_api_key_optional
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        get_settings.cache_clear()

        # When
        result = verify_automation_api_key_optional(api_key="any-key")

        # Then
        assert result is None

        # クリーンアップ
        get_settings.cache_clear()


class TestConfigValidation:
    """設定管理のバリデーションテスト"""

    def test_production_requires_32_char_api_key(self, monkeypatch):
        """
        異常系: 本番環境でAPI Keyが32文字未満の場合はエラー

        Given: 本番環境でAutomation APIが有効
        When: 32文字未満のAPI Keyを設定
        Then: ValueErrorが発生する

        Requirements: 2.4, 2.5
        """
        # Given
        from app.config import get_settings

        # テスト環境フラグを一時的に削除
        monkeypatch.delenv("PYTEST_CURRENT_TEST", raising=False)

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "short-key")

        get_settings.cache_clear()

        # When / Then
        with pytest.raises(ValueError) as exc_info:
            get_settings()

        assert "must be at least 32 characters" in str(exc_info.value)

        # クリーンアップ
        get_settings.cache_clear()

    def test_production_accepts_32_char_api_key(self, monkeypatch):
        """
        正常系: 本番環境で32文字以上のAPI Keyは受け入れられる

        Given: 本番環境でAutomation APIが有効
        When: 32文字以上のAPI Keyを設定
        Then: 設定が正常に読み込まれる

        Requirements: 2.4, 2.5
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENVIRONMENT", "production")
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)  # 32文字のAPI Key

        get_settings.cache_clear()

        # When
        settings = get_settings()

        # Then
        assert settings.enable_automation_api is True
        assert settings.automation_api_key == "a" * 32
        assert settings.is_automation_api_secure is True

        # クリーンアップ
        get_settings.cache_clear()

    def test_development_accepts_short_api_key(self, monkeypatch):
        """
        正常系: 開発環境では短いAPI Keyも受け入れられる

        Given: 開発環境でAutomation APIが有効
        When: 短いAPI Keyを設定
        Then: 設定が正常に読み込まれる

        Requirements: 2.4
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "short-key")

        get_settings.cache_clear()

        # When
        settings = get_settings()

        # Then
        assert settings.enable_automation_api is True
        assert settings.automation_api_key == "short-key"
        assert settings.is_automation_api_secure is True

        # クリーンアップ
        get_settings.cache_clear()

    def test_automation_api_disabled_no_validation(self, monkeypatch):
        """
        正常系: Automation API無効の場合はAPI Key検証をスキップ

        Given: Automation APIが無効
        When: API Keyが空文字列で設定されている
        Then: エラーが発生しない（APIが無効なので検証されない）

        Requirements: 2.3
        """
        # Given
        from app.config import get_settings

        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")
        # 空文字列を設定（delenvは.envファイルからの値が残る場合がある）
        monkeypatch.setenv("AUTOMATION_API_KEY", "")

        get_settings.cache_clear()

        # When
        settings = get_settings()

        # Then
        assert settings.enable_automation_api is False
        # Note: automation_api_keyは空文字列でも値として保持される（Noneではない）
        # APIが無効の場合、キーの有無は問わない
        assert settings.is_automation_api_secure is True  # 無効なので常にTrue

        # クリーンアップ
        get_settings.cache_clear()

    def test_is_automation_api_secure_property(self, monkeypatch):
        """
        正常系: is_automation_api_secureプロパティの動作確認

        Given: 様々な設定パターン
        When: is_automation_api_secureプロパティを確認
        Then: 正しいセキュリティ状態が返される

        Requirements: 2.6
        """
        # Given
        from app.config import get_settings

        # パターン1: Automation API無効 → 常にTrue
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "false")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.is_automation_api_secure is True

        # パターン2: 開発環境 + 短いキー → True
        monkeypatch.setenv("ENVIRONMENT", "development")
        monkeypatch.setenv("ENABLE_AUTOMATION_API", "true")
        monkeypatch.setenv("AUTOMATION_API_KEY", "short")
        get_settings.cache_clear()
        settings = get_settings()
        assert settings.is_automation_api_secure is True

        # クリーンアップ
        get_settings.cache_clear()
