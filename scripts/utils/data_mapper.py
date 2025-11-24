"""
Data Mapping Utilities

手書き記録データをCare Logモデルにマッピングするユーティリティモジュール。
記号や時間帯の変換、デフォルト値の適用を行います。

Usage:
    from scripts.utils.data_mapper import map_symbol_to_value, map_time_slot

    appetite = map_symbol_to_value("○")  # 5
    time_slot = map_time_slot("朝")  # "morning"
"""

from __future__ import annotations


def map_symbol_to_value(symbol: str) -> int:
    """
    記号を数値にマッピング（食欲・元気用）

    Args:
        symbol: 記号（○、△、×）

    Returns:
        int: マッピングされた値（1-5）

    Mapping:
        ○ → 5
        △ → 3
        × → 1

    Example:
        >>> map_symbol_to_value("○")
        5
        >>> map_symbol_to_value("△")
        3
    """
    mapping = {
        "○": 5,
        "◯": 5,  # 全角丸の異体字
        "o": 5,  # 小文字o
        "O": 5,  # 大文字O
        "△": 3,
        "▽": 3,  # 逆三角
        "×": 1,
        "x": 1,  # 小文字x
        "X": 1,  # 大文字X
    }

    # 空白を削除して正規化
    normalized = symbol.strip()

    if normalized in mapping:
        return mapping[normalized]

    # デフォルト値（読み取れない場合は中間値）
    return 3


def map_time_slot(time_indicator: str) -> str:
    """
    時間帯の日本語表記を英語にマッピング

    Args:
        time_indicator: 時間帯（朝、昼、夕）

    Returns:
        str: マッピングされた時間帯（morning, noon, evening）

    Mapping:
        朝 → morning
        昼 → noon
        夕 → evening

    Example:
        >>> map_time_slot("朝")
        'morning'
        >>> map_time_slot("夕")
        'evening'
    """
    mapping = {
        "朝": "morning",
        "昼": "noon",
        "夕": "evening",
        "夜": "evening",  # 夜も夕方として扱う
        "午前": "morning",
        "午後": "evening",
        "morning": "morning",  # 既に英語の場合
        "noon": "noon",
        "evening": "evening",
    }

    # 空白を削除して正規化
    normalized = time_indicator.strip()

    if normalized in mapping:
        return mapping[normalized]

    # デフォルト値（不明な場合は朝）
    return "morning"


def map_boolean(symbol: str) -> bool:
    """
    記号をブール値にマッピング

    Args:
        symbol: 記号（○、×）

    Returns:
        bool: マッピングされた値

    Mapping:
        ○ → True
        × → False

    Example:
        >>> map_boolean("○")
        True
        >>> map_boolean("×")
        False
    """
    true_symbols = {"○", "◯", "o", "O", "あり", "有", "true", "True", "TRUE", "1"}
    false_symbols = {"×", "x", "X", "なし", "無", "false", "False", "FALSE", "0"}

    # 空白を削除して正規化
    normalized = symbol.strip()

    if normalized in true_symbols:
        return True
    if normalized in false_symbols:
        return False

    # デフォルト値（不明な場合はFalse）
    return False


def aggregate_memo_fields(
    defecation: str | None = None,
    vomiting: str | None = None,
    medication: str | None = None,
    notes: str | None = None,
) -> str:
    """
    複数のメモフィールドを1つのメモに集約

    Args:
        defecation: 排便情報
        vomiting: 嘔吐情報
        medication: 投薬情報
        notes: その他の備考

    Returns:
        str: 集約されたメモ

    Example:
        >>> aggregate_memo_fields(
        ...     defecation="あり", vomiting="なし", medication="なし", notes="元気です"
        ... )
        '排便: あり, 嘔吐: なし, 投薬: なし, 備考: 元気です'
    """
    parts: list[str] = []

    if defecation:
        parts.append(f"排便: {defecation}")

    if vomiting:
        parts.append(f"嘔吐: {vomiting}")

    if medication:
        parts.append(f"投薬: {medication}")

    if notes:
        parts.append(f"備考: {notes}")

    # カンマ区切りで結合
    return ", ".join(parts) if parts else ""


def apply_ocr_defaults(record: dict[str, object]) -> dict[str, object]:
    """
    OCRインポート用のデフォルト値を適用

    Args:
        record: Care Logレコード

    Returns:
        dict: デフォルト値が適用されたレコード

    Default Values:
        - recorder_name: "OCR自動取込"
        - recorder_id: None
        - from_paper: True
        - device_tag: "OCR-Import"
        - cleaning: False
        - ip_address: None
        - user_agent: None

    Example:
        >>> record = {"animal_id": 1, "log_date": "2025-11-04"}
        >>> apply_ocr_defaults(record)
        {
            "animal_id": 1,
            "log_date": "2025-11-04",
            "recorder_name": "OCR自動取込",
            "from_paper": True,
            ...
        }
    """
    defaults = {
        "recorder_name": "OCR自動取込",
        "recorder_id": None,
        "from_paper": True,
        "device_tag": "OCR-Import",
        "cleaning": False,
        "ip_address": None,
        "user_agent": None,
    }

    # レコードのコピーを作成
    result = record.copy()

    # デフォルト値を適用（既存の値は上書きしない）
    for key, value in defaults.items():
        if key not in result:
            result[key] = value

    return result
