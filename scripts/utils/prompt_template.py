"""
LLM Prompt Template for OCR Care Log Import

This module provides structured prompt templates for instructing multimodal LLMs
to extract care log data from handwritten images.

Requirements: 1.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9
"""

from __future__ import annotations


def generate_ocr_prompt(
    animal_id: int,
    year: int,
    month: int,
) -> str:
    """
    Generate a structured prompt for OCR analysis of care log images.

    This prompt instructs the LLM to:
    1. Extract handwritten care log data from images
    2. Map Japanese field names to English field names
    3. Convert symbols (○/△/×) to appropriate values
    4. Format output as JSON array

    Args:
        animal_id: The ID of the cat for which records are being extracted
        year: The year for date parsing (e.g., 2025)
        month: The month for date parsing (1-12)

    Returns:
        str: Formatted prompt string ready for LLM

    Example:
        >>> prompt = generate_ocr_prompt(animal_id=5, year=2025, month=11)
        >>> # Use prompt with multimodal LLM to analyze image
    """
    prompt = f"""あなたは手書きの猫世話記録表を解析するOCRアシスタントです。

画像から以下の情報を抽出し、JSON形式で出力してください：

【対象猫】
- animal_id: {animal_id}

【対象期間】
- year: {year}
- month: {month}

【抽出する項目】
1. 日付（M/D形式）
2. 時間帯（朝/昼/夕）
3. ごはん（○/△/×）
4. 元気（○/△/×）
5. 排尿（○/×/数字）
6. 排便（○/×）
7. 嘔吐（○/×）
8. 投薬（○/×）
9. 備考（手書きメモ）

【出力形式】
以下のJSON配列形式で出力してください：

[
  {{
    "animal_id": {animal_id},
    "log_date": "YYYY-MM-DD",
    "time_slot": "morning" | "noon" | "evening",
    "appetite": 0.0-1.0,
    "energy": 1-5,
    "urination": true | false,
    "cleaning": false,
    "memo": "排便: あり, 嘔吐: なし, 投薬: なし, 備考: ...",
    "recorder_name": "OCR自動取込",
    "from_paper": true
  }}
]

【マッピングルール】
- ごはん: ○→1.0, △→0.5, ×→0.0
- 元気: ○→5, △→3, ×→1
- 排尿: ○→true, ×→false, 数字→true（回数はmemoに記載）
- 排便/嘔吐/投薬: ○→"あり", ×→"なし"（memoに追記）
- 空欄: デフォルト値を使用
- 朝→morning, 昼→noon, 夕→evening

【注意事項】
- 読み取れない文字は "?" で表記
- 不明確な記号は保守的に解釈
- 日付は {year}-{month:02d}-DD 形式に変換
- 各日付・時間帯ごとに1レコード作成

画像を解析して、上記形式のJSONを出力してください。"""

    return prompt


def get_mapping_rules() -> dict[str, str]:
    """
    Get the mapping rules for handwritten symbols to values.

    Returns:
        dict: Mapping rules documentation

    Example:
        >>> rules = get_mapping_rules()
        >>> print(rules["appetite"])
        '○→1.0, △→0.5, ×→0.0'
    """
    return {
        "appetite": "○→1.0, △→0.5, ×→0.0",
        "energy": "○→5, △→3, ×→1",
        "urination": "○→true, ×→false, 数字→true（回数はmemoに記載）",
        "defecation": "○→'排便あり', ×→'排便なし'（memoに追記）",
        "vomiting": "○→'嘔吐あり', ×→'嘔吐なし'（memoに追記）",
        "medication": "○→'投薬あり', ×→'投薬なし'（memoに追記）",
        "time_slot": "朝→morning, 昼→noon, 夕→evening",
        "empty_cells": "デフォルト値を使用",
    }


def get_output_format_spec() -> dict[str, str | list[str]]:
    """
    Get the JSON output format specification.

    Returns:
        dict: Output format specification with field descriptions

    Example:
        >>> spec = get_output_format_spec()
        >>> print(spec["required_fields"])
        ['animal_id', 'log_date', 'time_slot', ...]
    """
    return {
        "type": "array",
        "description": "Array of care log records",
        "required_fields": [
            "animal_id",
            "log_date",
            "time_slot",
            "appetite",
            "energy",
            "urination",
            "cleaning",
            "recorder_name",
            "from_paper",
        ],
        "optional_fields": [
            "memo",
            "recorder_id",
            "ip_address",
            "user_agent",
            "device_tag",
        ],
        "field_types": {
            "animal_id": "integer",
            "log_date": "string (YYYY-MM-DD)",
            "time_slot": "string (morning|noon|evening)",
            "appetite": "float (0.0-1.0)",
            "energy": "integer (1-5)",
            "urination": "boolean",
            "cleaning": "boolean (always false for OCR)",
            "memo": "string (nullable)",
            "recorder_name": "string (default: 'OCR自動取込')",
            "from_paper": "boolean (always true for OCR)",
        },
    }


def get_default_values() -> dict[str, str | bool | None]:
    """
    Get default values for OCR imports.

    Returns:
        dict: Default values for optional fields

    Example:
        >>> defaults = get_default_values()
        >>> print(defaults["recorder_name"])
        'OCR自動取込'
    """
    return {
        "recorder_name": "OCR自動取込",
        "recorder_id": None,
        "from_paper": True,
        "device_tag": "OCR-Import",
        "cleaning": False,
        "ip_address": None,
        "user_agent": None,
    }
