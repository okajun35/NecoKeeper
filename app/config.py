"""
アプリケーション設定管理モジュール

環境変数からアプリケーション設定を読み込み、型安全な設定管理を提供します。
Pydantic Settingsを使用して環境変数の検証と型変換を行います。
"""

import json
import os
from datetime import datetime
from functools import lru_cache
from typing import Any, Literal

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """
    アプリケーション設定クラス

    環境変数または.envファイルから設定を読み込みます。
    すべての設定は型安全で、Pydanticによって検証されます。
    """

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # アプリケーション基本設定
    app_name: str = Field(default="NecoKeeper", description="アプリケーション名")
    app_version: str = Field(default="0.1.0", description="アプリケーションバージョン")
    debug: bool = Field(default=False, description="デバッグモード")
    environment: Literal["development", "staging", "production"] = Field(
        default="development", description="実行環境"
    )
    default_language: Literal["ja", "en"] = Field(
        default="ja", description="既定の表示言語（ja/en）"
    )

    # サーバー設定
    host: str = Field(default="0.0.0.0", description="サーバーホスト")
    port: int = Field(default=8000, description="サーバーポート", ge=1, le=65535)
    use_proxy_headers: bool = Field(
        default=True,
        description="リバースプロキシ配下で X-Forwarded-* ヘッダーを信頼するか",
    )

    # セキュリティ設定
    secret_key: str = Field(
        default="your-secret-key-change-in-production",
        description="セッション暗号化用の秘密鍵",
        min_length=32,
    )
    jwt_algorithm: Literal[
        "HS256",
        "HS384",
        "HS512",
        "ES256",
        "ES384",
        "ES512",
    ] = Field(default="HS256", description="JWT署名アルゴリズム")
    jwt_access_token_expire_minutes: int = Field(
        default=120, description="JWTアクセストークンの有効期限（分）", gt=0
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
    max_image_count: int = Field(
        default=20,
        description="1猫あたりの最大画像枚数（設定が存在しない場合のデフォルト）",
        ge=1,
        le=100,
    )
    max_image_size_mb: float = Field(
        default=5.0,
        description="1画像あたりの最大ファイルサイズ（MB）",
        gt=0,
        le=100.0,
    )
    care_log_image_dir: str = Field(
        default="./data/private/care_log_images",
        description="世話記録画像（非公開）保存ディレクトリ",
    )
    care_log_image_max_size_mb: float = Field(
        default=2.0,
        description="世話記録画像の最大ファイルサイズ（MB）",
        gt=0,
        le=20.0,
    )
    care_log_image_receive_max_size_mb: float = Field(
        default=10.0,
        description="世話記録画像の受信時最大ファイルサイズ（MB）",
        gt=0,
        le=50.0,
    )
    care_log_image_max_long_edge: int = Field(
        default=1920,
        description="世話記録画像の長辺最大ピクセル",
        ge=640,
        le=4096,
    )
    care_log_image_fallback_long_edge: int = Field(
        default=1280,
        description="世話記録画像圧縮失敗時の再試行長辺ピクセル",
        ge=640,
        le=4096,
    )
    care_log_image_quality: int = Field(
        default=82,
        description="世話記録画像の圧縮品質（WebP/JPEG）",
        ge=50,
        le=95,
    )

    # ログ設定
    log_level: Literal[
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    ] = Field(default="INFO", description="ログレベル")
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
    pdf_font_family: str = Field(
        default="IPAGothic",
        description="PDF生成時に使用するフォントファミリー（カンマ区切りで複数指定可能）",
    )

    # バックアップ設定
    auto_backup_enabled: bool = Field(
        default=True, description="自動バックアップ機能の有効化"
    )
    backup_schedule: str = Field(
        default="0 2 * * *", description="自動バックアップの実行スケジュール（cron式）"
    )
    backup_retention_days: int = Field(
        default=30, description="バックアップ保持日数", ge=1
    )

    # CORS設定
    cors_origins: list[str] = Field(
        default_factory=lambda: [
            "http://localhost:3000",
            "http://localhost:8000",
        ],
        description="CORS許可オリジン",
    )

    # 管理者設定
    admin_email: str = Field(
        default="admin@example.com", description="管理者メールアドレス"
    )
    admin_path: str = Field(
        default="admin",
        description="管理画面のパス（先頭/末尾の/は不要）",
    )

    # デモ機能設定
    demo_features: bool = Field(
        default=False,
        description="LP等のデモ表示・デモ導線の有効化",
    )

    # アプリケーションURL設定
    base_url: str = Field(
        default="http://localhost:8000", description="アプリケーションのベースURL"
    )

    # ランディングページ設定
    github_repo_url: str = Field(
        default="https://github.com/okajun35/NecoKeeper",
        description="GitHubリポジトリURL",
    )
    demo_video_id: str = Field(
        default="K5GZoW2HnA0", description="YouTube ID for demo video"
    )

    # Cookie設定（認証用）
    cookie_secure: bool = Field(
        default=True,
        description="Cookie Secureフラグ（本番環境ではTrue、開発環境ではFalse）",
    )
    cookie_samesite: Literal["lax", "strict", "none"] = Field(
        default="lax", description="Cookie SameSite属性（CSRF対策）"
    )
    cookie_max_age: int = Field(
        default=7200,  # 2時間
        description="Cookie有効期限（秒）",
        gt=0,
    )

    # OCR Import設定
    ocr_temp_dir: str = Field(
        default="tmp/images", description="OCR一時ファイル保存ディレクトリ"
    )
    ocr_log_file: str = Field(
        default="logs/ocr-import.log", description="OCRログファイルパス"
    )
    necokeeper_api_url: str = Field(
        default="http://localhost:8000", description="NecoKeeper API URL"
    )
    necokeeper_admin_username: str = Field(
        default="admin", description="NecoKeeper管理者ユーザー名"
    )
    necokeeper_admin_password: str = Field(
        default="", description="NecoKeeper管理者パスワード"
    )

    # Automation API設定
    enable_automation_api: bool = Field(
        default=False, description="Automation APIの有効化"
    )
    automation_api_key: str | None = Field(
        default=None, description="Automation API用の固定API Key"
    )

    # Kiroween Theme設定
    kiroween_mode: bool = Field(
        default=False,
        description="Kiroween Mode（Necro-Terminal Theme）の有効化。"
        "Trueの場合、サイバーパンク/ホラーテーマのUIが適用されます。",
    )

    # 静的ファイルキャッシュバスティング設定
    @property
    def static_version(self) -> str:
        """
        静的ファイルのキャッシュバスティング用バージョン文字列

        サーバー起動時のタイムスタンプを使用して、サーバー再起動時に
        自動的にブラウザキャッシュを無効化します。

        Returns:
            str: YYYYMMDDHHMMフォーマットのバージョン文字列

        Example:
            <script
                src="/static/js/app.js?v={{ settings.static_version }}"
            ></script>
            # → /static/js/app.js?v=202412011430
        """
        return datetime.now().strftime("%Y%m%d%H%M")

    @property
    def admin_base_path(self) -> str:
        """管理画面のベースパス（先頭/付き）"""

        return f"/{self.admin_path}"

    @property
    def is_automation_api_secure(self) -> bool:
        """
        Automation APIのセキュリティ検証

        本番環境でAutomation APIが有効な場合、API Keyが設定され、
        かつ32文字以上であることを確認します。

        Returns:
            bool: セキュリティ要件を満たしている場合True

        Example:
            settings = get_settings()
            is_secure = settings.is_automation_api_secure
            if settings.enable_automation_api and not is_secure:
                raise ValueError("Automation API Key is not secure")
        """
        if not self.enable_automation_api:
            return True

        if self.automation_api_key is None:
            return False

        # 本番環境では32文字以上を要求
        if self.environment == "production":
            return len(self.automation_api_key) >= 32

        return True

    @property
    def max_image_size_bytes(self) -> int:
        """画像アップロード制限（バイト）"""

        return int(self.max_image_size_mb * 1024 * 1024)

    @property
    def max_upload_size(self) -> int:
        """後方互換性のためのエイリアス"""

        return self.max_image_size_bytes

    @property
    def care_log_image_max_size_bytes(self) -> int:
        """世話記録画像アップロード制限（バイト）"""

        return int(self.care_log_image_max_size_mb * 1024 * 1024)

    @property
    def care_log_image_receive_max_size_bytes(self) -> int:
        """世話記録画像受信時の制限（バイト）"""

        return int(self.care_log_image_receive_max_size_mb * 1024 * 1024)

    @field_validator("cors_origins", mode="before")
    @classmethod
    def parse_cors_origins(cls, value: Any) -> list[str]:
        """文字列で定義されたCORS_ORIGINSをリストに変換"""

        if isinstance(value, str):
            raw = value.strip()
            if not raw:
                return []
            if raw.startswith("["):
                try:
                    parsed = json.loads(raw)
                except json.JSONDecodeError as exc:
                    raise ValueError("CORS_ORIGINS must be valid JSON array") from exc
                if not isinstance(parsed, list):
                    raise ValueError("CORS_ORIGINS JSON must be a list")
                return [str(origin).strip() for origin in parsed if str(origin).strip()]
            return [origin.strip() for origin in raw.split(",") if origin.strip()]
        if isinstance(value, list):
            return [str(origin).strip() for origin in value if str(origin).strip()]
        if value is None:
            return []
        raise ValueError("CORS_ORIGINS must be a string, JSON array, or list")

    @field_validator("admin_path")
    @classmethod
    def normalize_admin_path(cls, value: str) -> str:
        """
        ADMIN_PATHを正規化してバリデーション

        - 前後のスラッシュを除去
        - 英数字とハイフンのみ許可
        - 予約語をチェック
        """
        import re

        normalized = value.strip().strip("/")

        # 空文字チェック
        if not normalized:
            raise ValueError("ADMIN_PATH must not be empty")

        # 英数字とハイフンのみ許可
        if not re.match(r"^[a-zA-Z0-9-]+$", normalized):
            raise ValueError(
                "ADMIN_PATH must contain only alphanumeric characters and hyphens"
            )

        # 予約語チェック
        reserved = {"api", "static", "public", "docs", "redoc", "media"}
        if normalized.lower() in reserved:
            raise ValueError(
                f"ADMIN_PATH cannot be a reserved path: {', '.join(sorted(reserved))}"
            )

        return normalized

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

    def model_post_init(self, __context: Any) -> None:
        """
        モデル初期化後の検証

        すべてのフィールドが設定された後に実行されるため、
        フィールド間の依存関係を検証できます。

        Requirements: 2.3, 2.4, 2.5
        """
        # テスト環境では検証をスキップ
        is_testing = os.environ.get("PYTEST_CURRENT_TEST") is not None
        if is_testing:
            return

        # Automation APIが無効な場合は検証不要
        if not self.enable_automation_api:
            return

        # Automation APIが有効な場合、API Keyが必須
        if self.automation_api_key is None or self.automation_api_key == "":
            raise ValueError(
                "AUTOMATION_API_KEY is required when ENABLE_AUTOMATION_API is true"
            )

        # 本番環境では32文字以上を要求
        is_prod = self.environment == "production"
        has_short_key = len(self.automation_api_key) < 32
        if is_prod and has_short_key:
            raise ValueError(
                "AUTOMATION_API_KEY must be at least 32 characters "
                "in production. Generate a secure key with: "
                "python -c 'import secrets; print(secrets.token_urlsafe(32))'"
            )


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
