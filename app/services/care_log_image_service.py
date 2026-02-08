"""
世話記録画像サービス

Publicの世話記録に添付される画像を非公開ストレージへ保存し、
管理画面の認証済みAPI経由でのみ配信するためのユーティリティを提供する。
"""

from __future__ import annotations

import io
import logging
import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError

from app.config import get_settings
from app.utils.image import validate_image_file
from app.utils.timezone import get_jst_now

settings = get_settings()
logger = logging.getLogger(__name__)

ALLOWED_CARE_IMAGE_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/webp",
}

CARE_IMAGE_MEDIA_TYPES = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}


def _care_log_image_root() -> Path:
    root = Path(settings.care_log_image_dir)
    root.mkdir(parents=True, exist_ok=True)
    return root


def _safe_resolved_path(image_key: str) -> Path:
    root = _care_log_image_root().resolve()
    resolved = (root / image_key).resolve()
    if resolved != root and root not in resolved.parents:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="不正な画像キーです",
        )
    return resolved


def save_care_log_image(file: UploadFile) -> tuple[str, str]:
    """
    世話記録画像を保存する。

    Returns:
        tuple[str, str]: (保存キー, media_type)
    """
    if file.content_type not in ALLOWED_CARE_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像は JPEG/PNG/WebP のみ対応しています",
        )

    validate_image_file(file, max_size=settings.care_log_image_max_size_bytes)

    try:
        file.file.seek(0)
        raw = file.file.read()

        with Image.open(io.BytesIO(raw)) as image:
            image = ImageOps.exif_transpose(image)
            if image.mode != "RGB":
                image = image.convert("RGB")

            max_edge = settings.care_log_image_max_long_edge
            image.thumbnail((max_edge, max_edge), Image.Resampling.LANCZOS)

            output = io.BytesIO()
            image.save(
                output,
                format="WEBP",
                quality=settings.care_log_image_quality,
                method=6,
            )
            optimized = output.getvalue()
    except UnidentifiedImageError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像の読み取りに失敗しました",
        ) from exc
    except HTTPException:
        raise
    except Exception as exc:  # pragma: no cover - 想定外の防御
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像処理に失敗しました",
        ) from exc

    if len(optimized) > settings.care_log_image_max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=(
                f"画像サイズが大きすぎます。"
                f"最大 {settings.care_log_image_max_size_mb:.1f}MB です"
            ),
        )

    now = get_jst_now()
    image_key = f"{now:%Y/%m}/{uuid.uuid4().hex}.webp"
    save_path = _safe_resolved_path(image_key)
    save_path.parent.mkdir(parents=True, exist_ok=True)
    save_path.write_bytes(optimized)

    return image_key, "image/webp"


def remove_care_log_image(image_key: str | None) -> None:
    """保存済みの世話記録画像を削除する（存在しない場合は無視）。"""
    if not image_key:
        return
    try:
        path = _safe_resolved_path(image_key)
    except HTTPException:
        return
    path.unlink(missing_ok=True)


def get_care_log_image_path(image_key: str) -> Path:
    """画像キーから絶対パスを解決し、存在チェックを行う。"""
    path = _safe_resolved_path(image_key)
    if not path.exists() or not path.is_file():
        logger.warning(
            "Care log image file not found (image_key=%s, resolved_path=%s)",
            image_key,
            path,
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="画像が見つかりません",
        )
    return path


def get_care_log_image_media_type(image_key: str) -> str:
    """画像キーからレスポンス用 media_type を推定する。"""
    suffix = Path(image_key).suffix.lower()
    return CARE_IMAGE_MEDIA_TYPES.get(suffix, "application/octet-stream")
