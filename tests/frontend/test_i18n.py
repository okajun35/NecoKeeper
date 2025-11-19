"""
i18n (国際化) 機能のテスト

Phase 1 & 2の実装をテスト:
- 名前空間の読み込み
- 言語切り替え
- キャッシュ機能
- FastAPI依存性注入
"""

from __future__ import annotations

import json
from pathlib import Path

from fastapi import Request
from fastapi.testclient import TestClient

from app.main import app
from app.utils.i18n import get_locale, get_translations


class TestI18nTranslationFiles:
    """翻訳ファイルのテスト"""

    def test_japanese_common_translation_file_exists(self) -> None:
        """日本語の共通翻訳ファイルが存在する"""
        file_path = Path("app/static/i18n/ja/common.json")
        assert file_path.exists()

    def test_english_common_translation_file_exists(self) -> None:
        """英語の共通翻訳ファイルが存在する"""
        file_path = Path("app/static/i18n/en/common.json")
        assert file_path.exists()

    def test_japanese_dashboard_translation_file_exists(self) -> None:
        """日本語のダッシュボード翻訳ファイルが存在する"""
        file_path = Path("app/static/i18n/ja/dashboard.json")
        assert file_path.exists()

    def test_english_dashboard_translation_file_exists(self) -> None:
        """英語のダッシュボード翻訳ファイルが存在する"""
        file_path = Path("app/static/i18n/en/dashboard.json")
        assert file_path.exists()

    def test_japanese_common_translation_content(self) -> None:
        """日本語の共通翻訳ファイルの内容が正しい"""
        file_path = Path("app/static/i18n/ja/common.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        assert "app_name" in translations
        assert translations["app_name"] == "NecoKeeper"
        assert "save" in translations
        assert translations["save"] == "保存"

    def test_english_common_translation_content(self) -> None:
        """英語の共通翻訳ファイルの内容が正しい"""
        file_path = Path("app/static/i18n/en/common.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        assert "app_name" in translations
        assert translations["app_name"] == "NecoKeeper"
        assert "save" in translations
        assert translations["save"] == "Save"


class TestI18nBackendIntegration:
    """バックエンドi18n統合のテスト"""

    def test_get_locale_from_cookie(self) -> None:
        """Cookieから言語を取得"""
        # Mockリクエストを作成
        from unittest.mock import Mock

        request = Mock(spec=Request)
        request.cookies = {"language": "en"}
        request.headers = {}

        locale = get_locale(request, None)
        assert locale == "en"

    def test_get_locale_from_accept_language_header(self) -> None:
        """Accept-Languageヘッダーから言語を取得"""
        from unittest.mock import Mock

        request = Mock(spec=Request)
        request.cookies = {}
        request.headers = {}

        locale = get_locale(request, "ja-JP,ja;q=0.9,en;q=0.8")
        assert locale == "ja"

    def test_get_locale_default(self) -> None:
        """デフォルト言語を取得"""
        from unittest.mock import Mock

        request = Mock(spec=Request)
        request.cookies = {}
        request.headers = {}

        locale = get_locale(request, None)
        assert locale == "ja"

    def test_get_translations_japanese(self) -> None:
        """日本語の翻訳カタログを取得"""
        translations = get_translations("ja")
        assert translations is not None

    def test_get_translations_english(self) -> None:
        """英語の翻訳カタログを取得"""
        translations = get_translations("en")
        assert translations is not None


class TestI18nAPIEndpoints:
    """i18n APIエンドポイントのテスト"""

    def test_set_language_to_english(self) -> None:
        """言語を英語に設定"""
        client = TestClient(app)
        response = client.post("/api/v1/language/set", json={"language": "en"})

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "en"
        assert "message" in data

    def test_set_language_to_japanese(self) -> None:
        """言語を日本語に設定"""
        client = TestClient(app)
        response = client.post("/api/v1/language/set", json={"language": "ja"})

        assert response.status_code == 200
        data = response.json()
        assert data["language"] == "ja"
        assert "message" in data

    def test_set_language_invalid(self) -> None:
        """無効な言語コードでエラー"""
        client = TestClient(app)
        response = client.post("/api/v1/language/set", json={"language": "invalid"})

        assert response.status_code == 422  # Validation error


class TestI18nNamespaces:
    """名前空間のテスト"""

    def test_all_namespaces_exist_for_japanese(self) -> None:
        """日本語の全名前空間ファイルが存在する"""
        namespaces = ["common", "dashboard", "animals", "care_logs", "medical_records"]
        for ns in namespaces:
            file_path = Path(f"app/static/i18n/ja/{ns}.json")
            assert file_path.exists(), f"Missing: {file_path}"

    def test_all_namespaces_exist_for_english(self) -> None:
        """英語の全名前空間ファイルが存在する"""
        namespaces = ["common", "dashboard", "animals", "care_logs", "medical_records"]
        for ns in namespaces:
            file_path = Path(f"app/static/i18n/en/{ns}.json")
            assert file_path.exists(), f"Missing: {file_path}"

    def test_dashboard_namespace_structure(self) -> None:
        """ダッシュボード名前空間の構造が正しい"""
        file_path = Path("app/static/i18n/ja/dashboard.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        assert "title" in translations
        assert "description" in translations
        assert "stats" in translations
        assert "protected" in translations["stats"]
        assert "adoptable" in translations["stats"]

    def test_medical_records_namespace_structure_japanese(self) -> None:
        """日本語の医療記録名前空間の構造が正しい"""
        file_path = Path("app/static/i18n/ja/medical_records.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        # 基本的なキーの確認
        assert "title" in translations
        assert "list_title" in translations
        assert "description" in translations
        assert "add_new" in translations
        assert "edit" in translations

        # フィールドの確認
        assert "fields" in translations
        assert "animal" in translations["fields"]
        assert "vet" in translations["fields"]
        assert "date" in translations["fields"]
        assert "weight" in translations["fields"]
        assert "temperature" in translations["fields"]
        assert "symptoms" in translations["fields"]

        # ラベルの確認
        assert "labels" in translations
        assert "animal" in translations["labels"]
        assert "vet" in translations["labels"]
        assert "weight" in translations["labels"]

        # プレースホルダーの確認
        assert "placeholders" in translations
        assert "select" in translations["placeholders"]
        assert "weight" in translations["placeholders"]

        # 時間帯の確認
        assert "time_slots" in translations
        assert "morning" in translations["time_slots"]
        assert "afternoon" in translations["time_slots"]
        assert "evening" in translations["time_slots"]

        # ボタンの確認
        assert "buttons" in translations
        assert "submit" in translations["buttons"]
        assert "cancel" in translations["buttons"]

    def test_medical_records_namespace_structure_english(self) -> None:
        """英語の医療記録名前空間の構造が正しい"""
        file_path = Path("app/static/i18n/en/medical_records.json")
        with file_path.open(encoding="utf-8") as f:
            translations = json.load(f)

        # 基本的なキーの確認
        assert "title" in translations
        assert translations["title"] == "Medical Records"
        assert "list_title" in translations
        assert "description" in translations
        assert "add_new" in translations

        # フィールドの確認
        assert "fields" in translations
        assert "animal" in translations["fields"]
        assert translations["fields"]["animal"] == "Cat"

        # ラベルの確認
        assert "labels" in translations
        assert "animal" in translations["labels"]
        assert translations["labels"]["animal"] == "Cat"

        # 時間帯の確認
        assert "time_slots" in translations
        assert translations["time_slots"]["morning"] == "Morning"
        assert translations["time_slots"]["afternoon"] == "Afternoon"
        assert translations["time_slots"]["evening"] == "Evening"


class TestI18nBabelIntegration:
    """Babel統合のテスト"""

    def test_babel_config_exists(self) -> None:
        """babel.cfgが存在する"""
        file_path = Path("babel.cfg")
        assert file_path.exists()

    def test_babel_locales_directory_exists(self) -> None:
        """app/locales/ディレクトリが存在する"""
        dir_path = Path("app/locales")
        assert dir_path.exists()
        assert dir_path.is_dir()

    def test_japanese_po_file_exists(self) -> None:
        """日本語の.poファイルが存在する"""
        file_path = Path("app/locales/ja/LC_MESSAGES/messages.po")
        assert file_path.exists()

    def test_english_po_file_exists(self) -> None:
        """英語の.poファイルが存在する"""
        file_path = Path("app/locales/en/LC_MESSAGES/messages.po")
        assert file_path.exists()

    def test_japanese_mo_file_exists(self) -> None:
        """日本語の.moファイルが存在する"""
        file_path = Path("app/locales/ja/LC_MESSAGES/messages.mo")
        assert file_path.exists()

    def test_english_mo_file_exists(self) -> None:
        """英語の.moファイルが存在する"""
        file_path = Path("app/locales/en/LC_MESSAGES/messages.mo")
        assert file_path.exists()
