"""
i18nユーティリティのテスト（JSON翻訳）

Requirements: Requirement 25（多言語対応）
"""

from __future__ import annotations

import pytest

from app.utils.i18n import load_json_translations, tj


class TestLoadJsonTranslations:
    """JSON翻訳ファイル読み込みのテスト"""

    def test_load_json_translations_japanese(self):
        """正常系: 日本語翻訳ファイルを読み込める"""
        # When
        translations = load_json_translations("ja", "reports")

        # Then
        assert translations is not None
        assert isinstance(translations, dict)
        assert "headers" in translations
        assert "time_slots" in translations

    def test_load_json_translations_english(self):
        """正常系: 英語翻訳ファイルを読み込める"""
        # When
        translations = load_json_translations("en", "reports")

        # Then
        assert translations is not None
        assert isinstance(translations, dict)
        assert "headers" in translations
        assert "time_slots" in translations

    def test_load_json_translations_cache(self):
        """正常系: 翻訳ファイルがキャッシュされる"""
        # Given
        translations1 = load_json_translations("ja", "reports")

        # When
        translations2 = load_json_translations("ja", "reports")

        # Then
        # 同じオブジェクトが返される（キャッシュヒット）
        assert translations1 is translations2

    def test_load_json_translations_invalid_locale_fallback(self):
        """境界値: 不正なロケールは日本語にフォールバック"""
        # When
        translations = load_json_translations("invalid", "reports")

        # Then
        assert translations is not None
        # 日本語にフォールバック
        assert translations == load_json_translations("ja", "reports")


class TestTj:
    """JSON翻訳関数のテスト"""

    def test_tj_simple_key_japanese(self):
        """正常系: シンプルなキーで日本語翻訳を取得できる"""
        # When
        result = tj("headers.animal_name", locale="ja")

        # Then
        assert result == "猫名"

    def test_tj_simple_key_english(self):
        """正常系: シンプルなキーで英語翻訳を取得できる"""
        # When
        result = tj("headers.animal_name", locale="en")

        # Then
        assert result == "Animal Name"

    def test_tj_nested_key_japanese(self):
        """正常系: ネストされたキーで日本語翻訳を取得できる"""
        # When
        result = tj("time_slots.morning", locale="ja")

        # Then
        assert result == "朝"

    def test_tj_nested_key_english(self):
        """正常系: ネストされたキーで英語翻訳を取得できる"""
        # When
        result = tj("time_slots.morning", locale="en")

        # Then
        assert result == "Morning"

    def test_tj_with_interpolation_japanese(self):
        """正常系: パラメータ補間で日本語翻訳を取得できる"""
        # When
        result = tj("animal.no_name", locale="ja", id=123)

        # Then
        assert result == "ID:123"

    def test_tj_with_interpolation_english(self):
        """正常系: パラメータ補間で英語翻訳を取得できる"""
        # When
        result = tj("animal.no_name", locale="en", id=456)

        # Then
        assert result == "ID:456"

    def test_tj_missing_key_returns_last_part(self):
        """境界値: 存在しないキーは最後の部分を返す"""
        # When
        result = tj("nonexistent.key.path", locale="ja")

        # Then
        assert result == "path"

    def test_tj_default_locale_japanese(self):
        """正常系: デフォルトロケールは日本語"""
        # When
        result = tj("headers.animal_name")

        # Then
        assert result == "猫名"

    def test_tj_default_namespace_reports(self):
        """正常系: デフォルト名前空間はreports"""
        # When
        result = tj("headers.log_date", locale="ja")

        # Then
        assert result == "記録日"

    def test_tj_boolean_values_japanese(self):
        """正常系: 真偽値の日本語翻訳を取得できる"""
        # When
        yes_result = tj("boolean.yes", locale="ja")
        no_result = tj("boolean.no", locale="ja")

        # Then
        assert yes_result == "○"
        assert no_result == "×"

    def test_tj_boolean_values_english(self):
        """正常系: 真偽値の英語翻訳を取得できる"""
        # When
        yes_result = tj("boolean.yes", locale="en")
        no_result = tj("boolean.no", locale="en")

        # Then
        assert yes_result == "✓"
        assert no_result == "✗"

    @pytest.mark.parametrize(
        "key,locale,expected",
        [
            ("headers.created_at", "ja", "記録日時"),
            ("headers.created_at", "en", "Created At"),
            ("headers.log_date", "ja", "記録日"),
            ("headers.log_date", "en", "Log Date"),
            ("time_slots.noon", "ja", "昼"),
            ("time_slots.noon", "en", "Noon"),
            ("time_slots.evening", "ja", "夕"),
            ("time_slots.evening", "en", "Evening"),
        ],
    )
    def test_tj_parametrized_translations(self, key, locale, expected):
        """パラメータ化テスト: 複数のキー×ロケールで正しく翻訳される"""
        # When
        result = tj(key, locale=locale)

        # Then
        assert result == expected

    def test_tj_sheet_name_japanese(self):
        """正常系: シート名の日本語翻訳を取得できる"""
        # When
        result = tj("sheet_names.care_logs", locale="ja")

        # Then
        assert result == "世話記録"

    def test_tj_sheet_name_english(self):
        """正常系: シート名の英語翻訳を取得できる"""
        # When
        result = tj("sheet_names.care_logs", locale="en")

        # Then
        assert result == "Care Logs"

    def test_tj_report_title_japanese(self):
        """正常系: 帳票タイトルの日本語翻訳を取得できる"""
        # When
        result = tj("report_titles.daily", locale="ja")

        # Then
        assert result == "日報"

    def test_tj_report_title_english(self):
        """正常系: 帳票タイトルの英語翻訳を取得できる"""
        # When
        result = tj("report_titles.daily", locale="en")

        # Then
        assert result == "Daily Report"

    def test_tj_all_time_slots_japanese(self):
        """正常系: 全時点の日本語翻訳を取得できる"""
        # When
        morning = tj("time_slots.morning", locale="ja")
        noon = tj("time_slots.noon", locale="ja")
        evening = tj("time_slots.evening", locale="ja")

        # Then
        assert morning == "朝"
        assert noon == "昼"
        assert evening == "夕"

    def test_tj_all_time_slots_english(self):
        """正常系: 全時点の英語翻訳を取得できる"""
        # When
        morning = tj("time_slots.morning", locale="en")
        noon = tj("time_slots.noon", locale="en")
        evening = tj("time_slots.evening", locale="en")

        # Then
        assert morning == "Morning"
        assert noon == "Noon"
        assert evening == "Evening"
