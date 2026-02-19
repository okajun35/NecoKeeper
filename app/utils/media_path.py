"""
Media path helper utilities.

DB保存値（`/media/...` と `animals/...` の混在）を安全に扱うための
共通ヘルパーを提供します。
"""

from __future__ import annotations

from pathlib import Path

from app.config import get_settings


def normalize_media_path(path: str | None) -> str | None:
    """
    DB上の画像パスを正規化して相対パスに変換する。

    Examples:
        "/media/animals/1/a.jpg" -> "animals/1/a.jpg"
        "animals/1/a.jpg" -> "animals/1/a.jpg"
    """
    if path is None:
        return None

    normalized = path.strip().replace("\\", "/")
    if not normalized:
        return None

    normalized = normalized.split("?", maxsplit=1)[0]
    normalized = normalized.split("#", maxsplit=1)[0]

    while normalized.startswith("/"):
        normalized = normalized[1:]
    while normalized.startswith("./"):
        normalized = normalized[2:]

    if normalized.startswith("media/"):
        normalized = normalized.removeprefix("media/")

    return normalized or None


def build_media_url(path: str | None) -> str | None:
    """画像パスを `/media/...` 形式のURLに変換する。"""
    normalized = normalize_media_path(path)
    if normalized is None:
        return None
    return f"/media/{normalized}"


def resolve_media_file_path(path: str, media_dir: str | Path | None = None) -> Path:
    """
    画像パスを `MEDIA_DIR` 配下の実ファイルパスへ安全に解決する。

    Raises:
        ValueError: パスが不正、または media_dir 外を指している場合
    """
    normalized = normalize_media_path(path)
    if normalized is None:
        raise ValueError("image path is empty")

    if media_dir is None:
        media_dir = get_settings().media_dir

    media_root = Path(media_dir).resolve()
    resolved = (media_root / normalized).resolve()

    if not resolved.is_relative_to(media_root):
        raise ValueError("image path points outside media directory")

    return resolved
