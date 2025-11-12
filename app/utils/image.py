"""
画像処理ユーティリティ

画像のアップロード、検証、最適化を行います。
"""

import uuid
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from PIL import Image

from app.config import get_settings

settings = get_settings()

# 許可される画像拡張子
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".webp"}

# 許可されるMIMEタイプ
ALLOWED_MIME_TYPES = {
    "image/jpeg",
    "image/png",
    "image/gif",
    "image/webp",
}


def validate_image_file(file: UploadFile, max_size: int | None = None) -> None:
    """
    画像ファイルを検証

    Args:
        file: アップロードされたファイル
        max_size: 最大ファイルサイズ（バイト）

    Raises:
        HTTPException: ファイルが無効な場合
    """
    # ファイル名の検証
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="ファイル名が指定されていません",
        )

    # 拡張子の検証
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていないファイル形式です。許可される形式: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    # MIMEタイプの検証
    if file.content_type not in ALLOWED_MIME_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"許可されていないファイルタイプです。許可されるタイプ: {', '.join(ALLOWED_MIME_TYPES)}",
        )

    # ファイルサイズの検証
    if max_size is None:
        max_size = settings.max_upload_size

    # ファイルサイズを取得（ファイルの最後まで読んでサイズを確認）
    file.file.seek(0, 2)  # ファイルの最後に移動
    file_size = file.file.tell()
    file.file.seek(0)  # ファイルの先頭に戻す

    if file_size > max_size:
        max_size_mb = max_size / (1024 * 1024)
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"ファイルサイズが大きすぎます。最大サイズ: {max_size_mb:.1f}MB",
        )


def generate_unique_filename(original_filename: str) -> str:
    """
    ユニークなファイル名を生成

    Args:
        original_filename: 元のファイル名

    Returns:
        str: ユニークなファイル名
    """
    file_ext = Path(original_filename).suffix.lower()
    unique_id = uuid.uuid4().hex
    return f"{unique_id}{file_ext}"


async def save_upload_file(file: UploadFile, destination_dir: str = "animals") -> str:
    """
    アップロードされたファイルを保存

    Args:
        file: アップロードされたファイル
        destination_dir: 保存先ディレクトリ（media_dir内のサブディレクトリ）

    Returns:
        str: 保存されたファイルの相対パス
    """
    # 保存先ディレクトリを作成
    save_dir = Path(settings.media_dir) / destination_dir
    save_dir.mkdir(parents=True, exist_ok=True)

    # ユニークなファイル名を生成
    filename = generate_unique_filename(file.filename)
    file_path = save_dir / filename

    # ファイルを保存
    contents = await file.read()
    with open(file_path, "wb") as f:
        f.write(contents)

    # 相対パスを返す
    return f"{destination_dir}/{filename}"


def optimize_image(
    image_path: Path, max_size: tuple[int, int] = (1920, 1080), quality: int = 85
) -> None:
    """
    画像を最適化（リサイズ、圧縮）

    Args:
        image_path: 画像ファイルのパス
        max_size: 最大サイズ（幅、高さ）
        quality: JPEG品質（1-100）
    """
    try:
        with Image.open(image_path) as img:
            # RGBAをRGBに変換（JPEGはアルファチャンネルをサポートしない）
            if img.mode in ("RGBA", "LA", "P"):
                # 白背景を作成
                background = Image.new("RGB", img.size, (255, 255, 255))
                if img.mode == "P":
                    img = img.convert("RGBA")
                background.paste(
                    img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None
                )
                img = background

            # サイズを調整（アスペクト比を維持）
            img.thumbnail(max_size, Image.Resampling.LANCZOS)

            # 最適化して保存
            img.save(image_path, optimize=True, quality=quality)
    except Exception as e:
        # 最適化に失敗しても元のファイルは残す
        print(f"画像の最適化に失敗しました: {e}")


async def save_and_optimize_image(
    file: UploadFile,
    destination_dir: str = "animals",
    max_size: tuple[int, int] = (1920, 1080),
    quality: int = 85,
) -> str:
    """
    画像を保存して最適化

    Args:
        file: アップロードされたファイル
        destination_dir: 保存先ディレクトリ
        max_size: 最大サイズ（幅、高さ）
        quality: JPEG品質（1-100）

    Returns:
        str: 保存されたファイルの相対パス
    """
    # ファイルを保存
    relative_path = await save_upload_file(file, destination_dir)

    # 絶対パスを取得
    absolute_path = Path(settings.media_dir) / relative_path

    # 画像を最適化
    optimize_image(absolute_path, max_size, quality)

    return relative_path


def delete_image_file(relative_path: str) -> bool:
    """
    画像ファイルを削除

    Args:
        relative_path: 画像ファイルの相対パス

    Returns:
        bool: 削除に成功した場合True
    """
    try:
        file_path = Path(settings.media_dir) / relative_path
        if file_path.exists():
            file_path.unlink()
            return True
        return False
    except Exception as e:
        print(f"画像ファイルの削除に失敗しました: {e}")
        return False
