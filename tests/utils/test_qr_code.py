"""
QRコード生成ユーティリティのテスト

Requirements: Requirement 2.3
"""

from __future__ import annotations

import pytest

from app.utils import qr_code


class TestGenerateQRCode:
    """QRコード生成のテスト"""

    def test_generate_qr_code_success(self):
        """正常系: QRコードを生成できる"""
        # Given
        data = "https://example.com/test"

        # When
        img = qr_code.generate_qr_code(data)

        # Then
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0

    def test_generate_qr_code_empty_data(self):
        """異常系: 空のデータでエラー"""
        # When/Then
        with pytest.raises(ValueError, match="QRコードに埋め込むデータが空です"):
            qr_code.generate_qr_code("")

    def test_generate_qr_code_custom_size(self):
        """正常系: カスタムサイズでQRコードを生成できる"""
        # Given
        data = "https://example.com/test"

        # When
        img = qr_code.generate_qr_code(data, box_size=20, border=2)

        # Then
        assert img is not None
        assert img.size[0] > 0


class TestGenerateQRCodeBytes:
    """QRコードバイト列生成のテスト"""

    def test_generate_qr_code_bytes_success(self):
        """正常系: QRコードをバイト列として生成できる"""
        # Given
        data = "https://example.com/test"

        # When
        qr_bytes = qr_code.generate_qr_code_bytes(data)

        # Then
        assert qr_bytes is not None
        assert isinstance(qr_bytes, bytes)
        assert len(qr_bytes) > 0
        # PNGヘッダーの確認
        assert qr_bytes.startswith(b"\x89PNG")

    def test_generate_qr_code_bytes_empty_data(self):
        """異常系: 空のデータでエラー"""
        # When/Then
        with pytest.raises(ValueError, match="QRコードに埋め込むデータが空です"):
            qr_code.generate_qr_code_bytes("")


class TestGenerateAnimalQRURL:
    """猫のQR URL生成のテスト"""

    def test_generate_animal_qr_url_success(self):
        """正常系: 猫のQR URLを生成できる"""
        # Given
        base_url = "https://necokeeper.example.com"
        animal_id = 123

        # When
        url = qr_code.generate_animal_qr_url(base_url, animal_id)

        # Then
        assert url == "https://necokeeper.example.com/public/care?animal_id=123"

    def test_generate_animal_qr_url_with_trailing_slash(self):
        """正常系: 末尾のスラッシュを削除してURLを生成できる"""
        # Given
        base_url = "https://necokeeper.example.com/"
        animal_id = 123

        # When
        url = qr_code.generate_animal_qr_url(base_url, animal_id)

        # Then
        assert url == "https://necokeeper.example.com/public/care?animal_id=123"


class TestGenerateAnimalQRCode:
    """猫のQRコード生成のテスト"""

    def test_generate_animal_qr_code_success(self):
        """正常系: 猫のQRコードを生成できる"""
        # Given
        base_url = "https://necokeeper.example.com"
        animal_id = 123

        # When
        img = qr_code.generate_animal_qr_code(base_url, animal_id)

        # Then
        assert img is not None
        assert img.size[0] > 0
        assert img.size[1] > 0


class TestGenerateAnimalQRCodeBytes:
    """猫のQRコードバイト列生成のテスト"""

    def test_generate_animal_qr_code_bytes_success(self):
        """正常系: 猫のQRコードをバイト列として生成できる"""
        # Given
        base_url = "https://necokeeper.example.com"
        animal_id = 123

        # When
        qr_bytes = qr_code.generate_animal_qr_code_bytes(base_url, animal_id)

        # Then
        assert qr_bytes is not None
        assert isinstance(qr_bytes, bytes)
        assert len(qr_bytes) > 0
        assert qr_bytes.startswith(b"\x89PNG")
