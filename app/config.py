"""
アプリケーション設定管理モジュール

環境変数からアプリケーション設定を読み込み、型安全な設定管理を提供します。
Pydantic Settingsを使用して環境変数の検証と型変換を行います。
"""

from functools import lru_cache
from typing import Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    アプリケーション設定クラス

    環境変数または.envファイルから設定を読み込みます。
    すべての設定は型安全で、Pydanticによって検証されます。
    """

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    # アプリケーション基本設定
    app_name: str = Field(default="NecoKeeper", description="アプリケーション名")
    app_version: str = Field(default="0.1.0", description="アプリケーションバージョン")
    debug: bool = Field(default=False, description="デバッグモード")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="実行環境"
    )

    # サーバー設定
    host: str = Field(default="0.0.0.0", description="サーバーホスト")
    port: int = Field(default=8000, description="サーバーポート", ge=1, le=65535)

    # セキュリティ設定
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="セッション暗号化用の秘密鍵",
        min_length=32,
    )
    session_cookie_name: str = Field(
        default="necokeeper_session", description="セッションCookie名"
    )
    session_max_age: int = Field(
        default=86400,  # 24時間
        description="セッション有効期限（秒）",
        gt=0,
    )

    # データベース設定
    database_url: str = Field(
        default="sqlite:///./data/necokeeper.db", description="データベース接続URL"
    )
    database_echo: bool = Field(default=False, description="SQLクエリのログ出力")

    # ファイルストレージ設定
    media_dir: str = Field(
        default="./media", description="メディアファイル保存ディレクトリ"
    )
    backup_dir: str = Field(
        default="./backups", description="バックアップファイル保存ディレクトリ"
    )
    max_upload_size: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="最大アップロードサイズ（バイト）",
        gt=0,
    )

    # ログ設定
    log_level: Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"] = Field(
        default="INFO", description="ログレベル"
    )
    log_file: str = Field(default="./logs/app.log", description="ログファイルパス")
    log_max_bytes: int = Field(
        default=10 * 1024 * 1024,  # 10MB
        description="ログファイル最大サイズ（バイト）",
        gt=0,
    )
    log_backup_count: int = Field(
        default=5, description="ログファイルバックアップ数", ge=0
    )

    # PDF生成設定
    pdf_dpi: int = Field(default=300, description="PDF生成時のDPI", ge=72, le=600)
    qr_code_size: int = Field(default=10, description="QRコードのサイズ", ge=1, le=40)

    # バックアップ設定
    backup_enabled: bool = Field(default=True, description="自動バックアップの有効化")
    backup_schedule_hour: int = Field(
        default=3, description="バックアップ実行時刻（時）", ge=0, le=23
    )
    backup_retention_days: int = Field(
        default=30, description="バックアップ保持日数", ge=1
    )

    # CORS設定
    cors_origins: list[str] = Field(
        default=["http://localhost:3000", "http://localhost:8000"],
        description="CORS許可オリジン",
    )

    # 管理者設定
    admin_email: str = Field(
        default="admin@example.com", description="管理者メールアドレス"
    )

    @field_validator("secret_key")
    @classmethod
    def validate_secret_key(cls, v: str) -> str:
        """
        本番環境でデフォルトの秘密鍵が使用されていないことを確認
        """
        import os

        # テスト環境では警告を出さない
        is_testing = os.environ.get("PYTEST_CURRENT_TEST") is not None

        if v == "your-secret-key-change-in-production" and not is_testing:
            import warnings

            warnings.warn(
                "デフォルトのSECRET_KEYが使用されています。本番環境では必ず変更してください。",
                UserWarning,
                stacklevel=2,
            )
        return v

    @field_validator("database_url")
    @classmethod
    def validate_database_url(cls, v: str) -> str:
        """
        データベースURLの基本的な検証
        """
        if not v:
            raise ValueError("DATABASE_URLは必須です")
        return v


@lru_cache
def get_settings() -> Settings:
    """
    設定インスタンスを取得（キャッシュ付き）

    @lru_cache()デコレータにより、初回呼び出し時のみSettingsインスタンスを作成し、
    以降の呼び出しではキャッシュされたインスタンスを返します。
    これにより、環境変数の読み込みが1回のみ実行され、パフォーマンスが向上します。

    Returns:
        Settings: アプリケーション設定インスタンス
    """
    return Settings()


# 設定インスタンスをエクスポート（便利のため）
settings = get_settings()
