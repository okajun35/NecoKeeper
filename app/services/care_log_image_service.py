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

HEIC_MIME_TYPES = {
    "image/heic",
    "image/heif",
}

ALLOWED_CARE_IMAGE_FORMATS = {
    "JPEG",
    "PNG",
    "WEBP",
}

COMPRESSION_QUALITY_STEPS = (75, 65, 55, 45)

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


def _compress_webp(image: Image.Image, long_edge: int, quality: int) -> bytes:
    """指定長辺・品質で WebP へ圧縮する（アスペクト比維持）。"""
    working = image.copy()
    working.thumbnail((long_edge, long_edge), Image.Resampling.LANCZOS)
    output = io.BytesIO()
    working.save(
        output,
        format="WEBP",
        quality=quality,
        method=6,
    )
    return output.getvalue()


def _compress_with_ladder(image: Image.Image) -> bytes:
    """
    受信画像を段階圧縮し、保存上限内のバイト列を返す。

    試行順:
    1. 長辺=max_long_edge, quality=75→65→55→45
    2. 長辺=fallback_long_edge, quality=75→65→55→45
    """
    long_edges = [settings.care_log_image_max_long_edge]
    if settings.care_log_image_fallback_long_edge not in long_edges:
        long_edges.append(settings.care_log_image_fallback_long_edge)

    max_size = settings.care_log_image_max_size_bytes
    for long_edge in long_edges:
        for quality in COMPRESSION_QUALITY_STEPS:
            optimized = _compress_webp(image, long_edge=long_edge, quality=quality)
            if len(optimized) <= max_size:
                return optimized

    raise HTTPException(
        status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
        detail="画像を2MB以下にできませんでした。別の画像で再投稿してください。",
    )


def save_care_log_image(file: UploadFile) -> tuple[str, str]:
    """
    世話記録画像を保存する。

    Returns:
        tuple[str, str]: (保存キー, media_type)
    """
    content_type = (file.content_type or "").lower()
    if content_type in HEIC_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="HEICは非対応です。JPEGで再投稿してください。",
        )
    if content_type not in ALLOWED_CARE_IMAGE_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="画像は JPEG/PNG/WebP のみ対応しています",
        )

    validate_image_file(file, max_size=settings.care_log_image_receive_max_size_bytes)

    try:
        file.file.seek(0)
        raw = file.file.read()

        with Image.open(io.BytesIO(raw)) as image:
            detected_format = (image.format or "").upper()
            if detected_format in {"HEIC", "HEIF"}:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="HEICは非対応です。JPEGで再投稿してください。",
                )
            if detected_format not in ALLOWED_CARE_IMAGE_FORMATS:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="画像は JPEG/PNG/WebP のみ対応しています",
                )

            image = ImageOps.exif_transpose(image)
            if image.mode != "RGB":
                image = image.convert("RGB")

            optimized = _compress_with_ladder(image)
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
