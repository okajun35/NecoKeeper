"""
食欲ラベル変換ユーティリティ
"""

from __future__ import annotations

from app.utils.i18n import tj

APPETITE_VALUE_TO_LEVEL_KEY = {
    1.0: "3",
    0.5: "2",
    0.0: "1",
}


def normalize_appetite_value(value: float | None) -> float | None:
    """食欲の値を小数第2位で丸める。"""
    if value is None:
        return None
    return round(float(value), 2)


def appetite_level_key(value: float | None) -> str | None:
    """食欲の値からレベルキー（1-3）を返す。"""
    normalized = normalize_appetite_value(value)
    if normalized is None:
        return None
    return APPETITE_VALUE_TO_LEVEL_KEY.get(normalized)


def appetite_label(value: float | None, locale: str = "ja") -> str:
    """食欲の表示ラベルを返す。"""
    level_key = appetite_level_key(value)
    if level_key is None:
        return "-"
    return tj(f"appetite_levels.{level_key}", locale=locale)
