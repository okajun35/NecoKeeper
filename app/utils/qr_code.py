"""
QRコード生成ユーティリティ

猫の個体IDとPublicフォームURLを含むQRコードを生成します。

Requirements: Requirement 2.3
Context7: /lincolnloop/python-qrcode
"""

from __future__ import annotations

import io
from typing import BinaryIO

import qrcode
from qrcode.image.pil import PilImage


def generate_qr_code(
    data: str,
    box_size: int = 10,
    border: int = 4,
    error_correction: int = qrcode.constants.ERROR_CORRECT_L,
) -> PilImage:
    """
    QRコード画像を生成

    Args:
        data: QRコードに埋め込むデータ（URL等）
        box_size: QRコードの各ボックスのピクセルサイズ（デフォルト: 10）
        border: QRコードの境界線の幅（デフォルト: 4）
        error_correction: エラー訂正レベル（デフォルト: ERROR_CORRECT_L）

    Returns:
        PilImage: 生成されたQRコード画像

    Raises:
        ValueError: データが空の場合

    Example:
        >>> qr_img = generate_qr_code("https://example.com/care/123")
        >>> qr_img.save("qr_code.png")
    """
    if not data:
        raise ValueError("QRコードに埋め込むデータが空です")

    qr = qrcode.QRCode(
        version=1,
        error_correction=error_correction,
        box_size=box_size,
        border=border,
    )
    qr.add_data(data)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    return img


def generate_qr_code_bytes(
    data: str,
    box_size: int = 10,
    border: int = 4,
    error_correction: int = qrcode.constants.ERROR_CORRECT_L,
    image_format: str = "PNG",
) -> bytes:
    """
    QRコード画像をバイト列として生成

    Args:
        data: QRコードに埋め込むデータ（URL等）
        box_size: QRコードの各ボックスのピクセルサイズ（デフォルト: 10）
        border: QRコードの境界線の幅（デフォルト: 4）
        error_correction: エラー訂正レベル（デフォルト: ERROR_CORRECT_L）
        image_format: 画像フォーマット（デフォルト: PNG）

    Returns:
        bytes: QRコード画像のバイト列

    Raises:
        ValueError: データが空の場合

    Example:
        >>> qr_bytes = generate_qr_code_bytes("https://example.com/care/123")
        >>> with open("qr_code.png", "wb") as f:
        ...     f.write(qr_bytes)
    """
    img = generate_qr_code(data, box_size, border, error_correction)

    # 画像をバイト列に変換
    buffer: BinaryIO = io.BytesIO()
    img.save(buffer, format=image_format)
    buffer.seek(0)

    return buffer.getvalue()


def generate_animal_qr_url(base_url: str, animal_id: int) -> str:
    """
    猫のPublicフォーム用QR URL を生成

    Args:
        base_url: ベースURL（例: "https://necokeeper.example.com"）
        animal_id: 猫のID

    Returns:
        str: PublicフォームのURL

    Example:
        >>> url = generate_animal_qr_url("https://necokeeper.example.com", 123)
        >>> print(url)
        https://necokeeper.example.com/public/care/123
    """
    # URLの末尾のスラッシュを削除
    base_url = base_url.rstrip("/")
    return f"{base_url}/public/care/{animal_id}"


def generate_animal_qr_code(
    base_url: str,
    animal_id: int,
    box_size: int = 10,
    border: int = 4,
) -> PilImage:
    """
    猫のPublicフォーム用QRコードを生成

    Args:
        base_url: ベースURL（例: "https://necokeeper.example.com"）
        animal_id: 猫のID
        box_size: QRコードの各ボックスのピクセルサイズ（デフォルト: 10）
        border: QRコードの境界線の幅（デフォルト: 4）

    Returns:
        PilImage: 生成されたQRコード画像

    Example:
        >>> qr_img = generate_animal_qr_code("https://necokeeper.example.com", 123)
        >>> qr_img.save("animal_123_qr.png")
    """
    url = generate_animal_qr_url(base_url, animal_id)
    return generate_qr_code(url, box_size, border)


def generate_animal_qr_code_bytes(
    base_url: str,
    animal_id: int,
    box_size: int = 10,
    border: int = 4,
    image_format: str = "PNG",
) -> bytes:
    """
    猫のPublicフォーム用QRコードをバイト列として生成

    Args:
        base_url: ベースURL（例: "https://necokeeper.example.com"）
        animal_id: 猫のID
        box_size: QRコードの各ボックスのピクセルサイズ（デフォルト: 10）
        border: QRコードの境界線の幅（デフォルト: 4）
        image_format: 画像フォーマット（デフォルト: PNG）

    Returns:
        bytes: QRコード画像のバイト列

    Example:
        >>> qr_bytes = generate_animal_qr_code_bytes("https://necokeeper.example.com", 123)
        >>> with open("animal_123_qr.png", "wb") as f:
        ...     f.write(qr_bytes)
    """
    url = generate_animal_qr_url(base_url, animal_id)
    return generate_qr_code_bytes(url, box_size, border, image_format=image_format)
