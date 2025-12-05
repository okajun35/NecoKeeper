"""
タイムゾーンユーティリティ

JSTとUTCの変換、現在時刻の取得を提供します。
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

import pytz

# タイムゾーン定義
JST = pytz.timezone("Asia/Tokyo")
UTC = pytz.utc


def get_jst_now() -> datetime:
    """
    JST現在時刻を取得（タイムゾーン情報なし）

    Returns:
        datetime: JST現在時刻（naive datetime）

    Example:
        >>> now = get_jst_now()
        >>> print(now)
        2025-12-03 20:30:00
    """
    return datetime.now(JST).replace(tzinfo=None)


def get_jst_date() -> date_type:
    """
    JST現在日付を取得

    Returns:
        date: JST現在日付

    Example:
        >>> today = get_jst_date()
        >>> print(today)
        2025-12-03
    """
    return datetime.now(JST).date()


def utc_to_jst(dt: datetime) -> datetime:
    """
    UTC時刻をJST時刻に変換

    Args:
        dt: UTC時刻（naive または aware datetime）

    Returns:
        datetime: JST時刻（naive datetime）

    Example:
        >>> utc_time = datetime(2025, 12, 1, 17, 25, 28)
        >>> jst_time = utc_to_jst(utc_time)
        >>> print(jst_time)
        2025-12-02 02:25:28
    """
    if dt is None:
        return None

    # タイムゾーン情報がない場合はUTCとして扱う
    if dt.tzinfo is None:
        dt = UTC.localize(dt)

    # JSTに変換してタイムゾーン情報を削除
    return dt.astimezone(JST).replace(tzinfo=None)


def jst_to_utc(dt: datetime) -> datetime:
    """
    JST時刻をUTC時刻に変換

    Args:
        dt: JST時刻（naive または aware datetime）

    Returns:
        datetime: UTC時刻（naive datetime）

    Example:
        >>> jst_time = datetime(2025, 12, 2, 2, 25, 28)
        >>> utc_time = jst_to_utc(jst_time)
        >>> print(utc_time)
        2025-12-01 17:25:28
    """
    if dt is None:
        return None

    # タイムゾーン情報がない場合はJSTとして扱う
    if dt.tzinfo is None:
        dt = JST.localize(dt)

    # UTCに変換してタイムゾーン情報を削除
    return dt.astimezone(UTC).replace(tzinfo=None)
