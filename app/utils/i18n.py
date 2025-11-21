"""
i18n (国際化) モジュール - Babel統合版

Context7ベストプラクティスに基づいた実装:
- Babel統合（Gettext形式 .po/.mo）
- Jinja2 Babel拡張
- 遅延評価（LazyProxy）
- FastAPI依存性注入
- 複数形対応（ngettext）

参照: /websites/babel_pocoo-en
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated, Any

from babel.support import LazyProxy, Translations
from fastapi import Depends, Header, Request

# 翻訳カタログのキャッシュ
_translations_cache: dict[str, Translations] = {}

# JSON翻訳データのキャッシュ
_json_translations: dict[str, dict[str, Any]] = {}

# ロケールディレクトリ
LOCALES_DIR = Path(__file__).parent.parent / "locales"


def get_locale(
    request: Request,
    accept_language: Annotated[str | None, Header()] = None,
) -> str:
    """
    リクエストから言語を検出（FastAPI依存性注入）

    優先順位（Context7ベストプラクティス）:
    1. Cookie (language=en)
    2. Accept-Language ヘッダー
    3. デフォルト (ja)

    Args:
        request: FastAPIリクエストオブジェクト
        accept_language: Accept-Languageヘッダー

    Returns:
        str: 言語コード ('ja' or 'en')

    Example:
        >>> # FastAPIエンドポイントで使用
        >>> @router.get("/items")
        >>> async def get_items(locale: Annotated[str, Depends(get_locale)]):
        >>>     return {"locale": locale}
    """
    # 1. Cookie
    if (lang := request.cookies.get("language")) and lang in ("ja", "en"):
        return lang

    # 2. Accept-Language ヘッダー
    if accept_language:
        for lang in accept_language.split(","):
            code = lang.split(";")[0].split("-")[0].strip()
            if code in ("ja", "en"):
                return code

    # 3. デフォルト
    return "ja"


def get_translations(
    locale: Annotated[str, Depends(get_locale)],
) -> Translations:
    """
    翻訳カタログを取得（FastAPI依存性注入）

    Args:
        locale: 言語コード

    Returns:
        Translations: Babel翻訳カタログ

    Example:
        >>> # FastAPIエンドポイントで使用
        >>> @router.get("/items")
        >>> async def get_items(
        >>>     translations: Annotated[Translations, Depends(get_translations)]
        >>> ):
        >>>     _ = translations.gettext
        >>>     return {"message": _("Items list")}
    """
    if locale in _translations_cache:
        cached: Translations = _translations_cache[locale]
        return cached

    translations: Translations = Translations.load(str(LOCALES_DIR), [locale])
    _translations_cache[locale] = translations
    return translations


def lazy_gettext(string: str) -> LazyProxy:
    """
    遅延評価翻訳（リクエストコンテキスト外で使用）

    Args:
        string: 翻訳する文字列

    Returns:
        LazyProxy: 遅延評価プロキシ

    Example:
        >>> # モジュールレベルで定義（リクエストコンテキスト外）
        >>> EMAIL_SUBJECT = lazy_gettext("Welcome to NecoKeeper")
        >>>
        >>> # 実際の評価はリクエスト時
        >>> def send_email(user, translations):
        >>>     subject = str(EMAIL_SUBJECT)  # この時点で翻訳
        >>>     ...
    """
    # TODO: リクエストコンテキストから翻訳を取得する実装
    # 現在は簡易実装（日本語固定）
    return LazyProxy(lambda: string)


def create_jinja2_i18n_functions(
    translations: Translations,
) -> dict[str, Any]:
    """
    Jinja2テンプレート用のi18n関数を作成

    Args:
        translations: Babel翻訳カタログ

    Returns:
        dict: Jinja2テンプレートで使用する関数の辞書

    Example:
        >>> # Jinja2環境に統合
        >>> from jinja2 import Environment
        >>> env = Environment()
        >>> env.globals.update(create_jinja2_i18n_functions(translations))
        >>>
        >>> # テンプレートで使用
        >>> # {{ _('Save') }}
        >>> # {{ ngettext('%(num)d cat', '%(num)d cats', count) }}
    """
    gettext = translations.gettext
    ngettext = translations.ngettext

    return {
        "_": gettext,  # 翻訳関数
        "gettext": gettext,  # エイリアス
        "ngettext": ngettext,  # 複数形対応
    }


# 後方互換性のための関数（既存コードとの互換性）
def get_language_from_request(request: Request) -> str:
    """
    後方互換性のための関数

    新しいコードでは get_locale を使用してください。
    """
    return get_locale(request)


def translate(key: str, language: str = "ja", **kwargs: Any) -> str:
    """
    後方互換性のための関数

    新しいコードでは Translations.gettext を使用してください。
    """
    translations: Translations = Translations.load(str(LOCALES_DIR), [language])
    text: str = translations.gettext(key)

    # 補間処理
    result: str = text
    for param_key, param_value in kwargs.items():
        result = result.replace(f"{{{{{param_key}}}}}", str(param_value))

    return result


def load_json_translations(locale: str, namespace: str) -> dict[str, Any]:
    """
    JSON翻訳ファイルを読み込む

    Args:
        locale: ロケール (ja, en)
        namespace: 名前空間 (reports, など)

    Returns:
        dict: 翻訳データ
    """
    cache_key = f"{locale}:{namespace}"
    if cache_key in _json_translations:
        return _json_translations[cache_key]

    json_path = LOCALES_DIR / locale / f"{namespace}.json"

    if not json_path.exists():
        # フォールバック: 日本語
        json_path = LOCALES_DIR / "ja" / f"{namespace}.json"

    if json_path.exists():
        with json_path.open(encoding="utf-8") as f:
            data: dict[str, Any] = json.load(f)
            _json_translations[cache_key] = data
            return data

    return {}


def tj(key: str, locale: str = "ja", namespace: str = "reports", **kwargs: Any) -> str:
    """
    JSON翻訳キーから翻訳文字列を取得

    Args:
        key: 翻訳キー (例: "headers.animal_name" または "animal_name")
        locale: ロケール (ja, en)
        namespace: 名前空間 (reports, など)
        **kwargs: 補間用のパラメータ

    Returns:
        str: 翻訳された文字列

    Example:
        >>> tj("headers.animal_name", locale="en")
        'Animal Name'
        >>> tj("animal.no_name", locale="ja", id=123)
        'ID:123'
    """
    translations = load_json_translations(locale, namespace)

    # ネストされたキーに対応
    keys = key.split(".")
    value: Any = translations
    for k in keys:
        if isinstance(value, dict):
            value = value.get(k)
        else:
            value = None
            break

    if value is None:
        # キーが見つからない場合は最後のキーをそのまま返す
        return keys[-1]

    # 文字列補間
    if isinstance(value, str) and kwargs:
        try:
            return value.format(**kwargs)
        except (KeyError, ValueError):
            return value

    return str(value)
