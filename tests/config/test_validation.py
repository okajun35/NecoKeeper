"""
設定バリデーションのテスト

app.config.Settings のバリデーション機能を検証する。
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.config import Settings


class TestAdminPathValidation:
    """ADMIN_PATHバリデーションのテスト"""

    def test_valid_admin_path_alphanumeric(self) -> None:
        """
        正常系: 英数字のみの ADMIN_PATH

        Given: ADMIN_PATH=admin123
        When: Settings を初期化
        Then: 正常に設定される
        """
        settings = Settings(admin_path="admin123")
        assert settings.admin_path == "admin123"
        assert settings.admin_base_path == "/admin123"

    def test_valid_admin_path_with_hyphens(self) -> None:
        """
        正常系: ハイフンを含む ADMIN_PATH

        Given: ADMIN_PATH=secret-admin-2024
        When: Settings を初期化
        Then: 正常に設定される
        """
        settings = Settings(admin_path="secret-admin-2024")
        assert settings.admin_path == "secret-admin-2024"

    def test_admin_path_strips_slashes(self) -> None:
        """
        正常系: 前後のスラッシュが除去される

        Given: ADMIN_PATH=/admin/
        When: Settings を初期化
        Then: admin に正規化される
        """
        settings = Settings(admin_path="/admin/")
        assert settings.admin_path == "admin"
        assert settings.admin_base_path == "/admin"

    def test_admin_path_rejects_empty_string(self) -> None:
        """
        異常系: 空文字列は拒否

        Given: ADMIN_PATH=""
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(ValidationError, match="must not be empty"):
            Settings(admin_path="")

    def test_admin_path_rejects_only_slashes(self) -> None:
        """
        異常系: スラッシュのみは拒否

        Given: ADMIN_PATH="///"
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(ValidationError, match="must not be empty"):
            Settings(admin_path="///")

    def test_admin_path_rejects_special_characters(self) -> None:
        """
        異常系: 特殊文字は拒否

        Given: ADMIN_PATH=admin@123
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(
            ValidationError,
            match="must contain only alphanumeric characters and hyphens",
        ):
            Settings(admin_path="admin@123")

    def test_admin_path_rejects_spaces(self) -> None:
        """
        異常系: スペースは拒否

        Given: ADMIN_PATH="admin panel"
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(
            ValidationError,
            match="must contain only alphanumeric characters and hyphens",
        ):
            Settings(admin_path="admin panel")

    def test_admin_path_rejects_path_traversal(self) -> None:
        """
        異常系: パストラバーサルは拒否

        Given: ADMIN_PATH="../admin"
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(
            ValidationError,
            match="must contain only alphanumeric characters and hyphens",
        ):
            Settings(admin_path="../admin")

    @pytest.mark.parametrize(
        "reserved_word",
        ["api", "static", "public", "docs", "redoc", "media", "API", "Static", "DOCS"],
    )
    def test_admin_path_rejects_reserved_words(self, reserved_word: str) -> None:
        """
        異常系: 予約語は拒否（大文字小文字区別なし）

        Given: ADMIN_PATH=<予約語>
        When: Settings を初期化
        Then: ValidationError
        """
        with pytest.raises(ValidationError, match="cannot be a reserved path"):
            Settings(admin_path=reserved_word)

    def test_admin_path_allows_reserved_as_substring(self) -> None:
        """
        正常系: 予約語を含むが完全一致でない場合は許可

        Given: ADMIN_PATH=my-api-admin
        When: Settings を初期化
        Then: 正常に設定される
        """
        settings = Settings(admin_path="my-api-admin")
        assert settings.admin_path == "my-api-admin"
