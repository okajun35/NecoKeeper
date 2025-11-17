"""
i18n (国際化) ヘルパーモジュール

Jinja2テンプレートで使用する翻訳ヘルパー関数を提供します。
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from fastapi import Request

# 翻訳ファイルのキャッシュ
_translations_cache: dict[str, dict[str, Any]] = {}


def load_translations(language: str) -> dict[str, Any]:
    """
    翻訳ファイルを読み込み

    Args:
        language: 言語コード ('ja' or 'en')

    Returns:
        dict: 翻訳データ

    Example:
        >>> translations = load_translations("ja")
        >>> translations["common"]["save"]
        '保存'
    """
    if language in _translations_cache:
        return _translations_cache[language]

    i18n_dir = Path(__file__).parent.parent / "static" / "i18n"
    translation_file = i18n_dir / f"{language}.json"

    if not translation_file.exists():
        # フォールバック: 日本語
        translation_file = i18n_dir / "ja.json"

    with translation_file.open(encoding="utf-8") as f:
        translations = json.load(f)

    _translations_cache[language] = translations
    return translations


def get_language_from_request(request: Request) -> str:
    """
    リクエストから言語設定を取得

    優先順位:
    1. クエリパラメータ (?lang=en)
    2. Cookie (language=en)
    3. Accept-Languageヘッダー
    4. デフォルト (ja)

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        str: 言語コード ('ja' or 'en')

    Example:
        >>> language = get_language_from_request(request)
        'ja'
    """
    # 1. クエリパラメータ
    lang_param = request.query_params.get("lang")
    if lang_param in ("ja", "en"):
        return lang_param

    # 2. Cookie
    lang_cookie = request.cookies.get("language")
    if lang_cookie in ("ja", "en"):
        return lang_cookie

    # 3. Accept-Languageヘッダー
    accept_language = request.headers.get("Accept-Language", "")
    if accept_language:
        # 最初の言語コードを取得 (例: "ja-JP,ja;q=0.9,en;q=0.8" -> "ja")
        primary_lang = accept_language.split(",")[0].split("-")[0].split(";")[0].strip()
        if primary_lang in ("ja", "en"):
            return primary_lang

    # 4. デフォルト
    return "ja"


def translate(key: str, language: str = "ja", **kwargs: Any) -> str:
    """
    翻訳キーから翻訳テキストを取得

    Args:
        key: 翻訳キー (例: 'common.save', 'dashboard.title')
        language: 言語コード ('ja' or 'en')
        **kwargs: 補間用のパラメータ

    Returns:
        str: 翻訳されたテキスト

    Example:
        >>> translate("common.save", "ja")
        '保存'
        >>> translate("validation.required", "ja", field="名前")
        '名前は必須です'
    """
    translations = load_translations(language)

    # ネストされたキーを辿る (例: 'common.save' -> translations['common']['save'])
    keys = key.split(".")
    value: Any = translations

    for k in keys:
        if isinstance(value, dict) and k in value:
            value = value[k]
        else:
            # キーが見つからない場合はキー自体を返す
            return key

    # 文字列でない場合はキーを返す
    if not isinstance(value, str):
        return key

    # 補間処理 ({{variable}} を置換)
    for param_key, param_value in kwargs.items():
        value = value.replace(f"{{{{{param_key}}}}}", str(param_value))

    return value


def create_jinja2_i18n_functions(request: Request) -> dict[str, Any]:
    """
    Jinja2テンプレート用のi18n関数を作成

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        dict: Jinja2テンプレートで使用する関数の辞書

    Example:
        >>> functions = create_jinja2_i18n_functions(request)
        >>> functions["t"]("common.save")
        '保存'
    """
    language = get_language_from_request(request)

    def t(key: str, **kwargs: Any) -> str:
        """翻訳関数"""
        return translate(key, language, **kwargs)

    def get_language() -> str:
        """現在の言語を取得"""
        return language

    return {
        "t": t,
        "_": t,  # エイリアス
        "get_language": get_language,
        "current_language": language,
    }
