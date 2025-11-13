"""
画像ギャラリーサービスのテスト

t-wada準拠のテスト設計:
- ドメインロジックの検証
- 境界値テスト
- エラーハンドリングの検証
- 副作用の検証（ファイル保存、データベース記録など）
"""

from __future__ import annotations

import io
from datetime import date, datetime, timedelta
from pathlib import Path

import pytest
from fastapi import HTTPException, UploadFile
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_image import AnimalImage
from app.models.setting import Setting
from app.services import image_service


@pytest.fixture
def mock_image_file() -> UploadFile:
    """モック画像ファイルを作成"""
    # 小さなPNG画像データ（1x1ピクセルの透明PNG）
    png_data = (
        b"\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01"
        b"\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\nIDATx\x9cc\x00\x01"
        b"\x00\x00\x05\x00\x01\r\n-\xb4\x00\x00\x00\x00IEND\xaeB`\x82"
    )
    file = io.BytesIO(png_data)
    # headers引数でcontent_typeを設定
    upload_file = UploadFile(
        filename="test.png", file=file, headers={"content-type": "image/png"}
    )
    return upload_file


class TestGetImageLimits:
    """画像制限設定取得のテスト"""

    def test_get_default_limits(self, test_db: Session):
        """正常系: デフォルト設定を取得できる"""
        # When
        max_images, max_size = image_service.get_image_limits(test_db)

        # Then
        assert max_images == 20  # デフォルト値
        assert max_size == 5 * 1024 * 1024  # 5MB

    def test_get_custom_limits(self, test_db: Session):
        """正常系: カスタム設定を取得できる"""
        # Given
        setting1 = Setting(
            key="max_images_per_animal",
            value="30",
            description="最大画像枚数",
        )
        setting2 = Setting(
            key="max_image_size_mb",
            value="10.0",
            description="最大ファイルサイズ",
        )
        test_db.add(setting1)
        test_db.add(setting2)
        test_db.commit()

        # When
        max_images, max_size = image_service.get_image_limits(test_db)

        # Then
        assert max_images == 30
        assert max_size == 10 * 1024 * 1024  # 10MB

    def test_get_limits_with_invalid_value(self, test_db: Session):
        """異常系: 不正な設定値の場合はデフォルト値を返す"""
        # Given: 既存の設定を削除してから追加
        test_db.query(Setting).filter(Setting.key == "max_images_per_animal").delete()
        test_db.commit()

        setting = Setting(
            key="max_images_per_animal",
            value="invalid",
            description="不正な値",
        )
        test_db.add(setting)
        test_db.commit()

        # When
        max_images, max_size = image_service.get_image_limits(test_db)

        # Then
        assert max_images == 20  # デフォルト値にフォールバック


class TestCountAnimalImages:
    """画像枚数カウントのテスト"""

    def test_count_zero_images(self, test_db: Session, test_animal: Animal):
        """正常系: 画像が0枚の場合"""
        # When
        count = image_service.count_animal_images(test_db, test_animal.id)

        # Then
        assert count == 0

    def test_count_multiple_images(self, test_db: Session, test_animal: Animal):
        """正常系: 複数の画像がある場合"""
        # Given
        for i in range(3):
            image = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"test_{i}.jpg",
                file_size=1024,
            )
            test_db.add(image)
        test_db.commit()

        # When
        count = image_service.count_animal_images(test_db, test_animal.id)

        # Then
        assert count == 3


class TestUploadImage:
    """画像アップロードのテスト"""

    @pytest.mark.asyncio
    async def test_upload_image_success(
        self, test_db: Session, test_animal: Animal, mock_image_file: UploadFile
    ):
        """正常系: 画像をアップロードできる"""
        # Given
        taken_at = date(2024, 1, 1)
        description = "元気な様子"

        # When
        result = await image_service.upload_image(
            db=test_db,
            animal_id=test_animal.id,
            file=mock_image_file,
            taken_at=taken_at,
            description=description,
        )

        # Then
        assert result.id is not None
        assert result.animal_id == test_animal.id
        assert result.taken_at == taken_at
        assert result.description == description
        assert result.file_size > 0
        assert result.image_path.startswith(f"animals/{test_animal.id}/gallery/")

    @pytest.mark.asyncio
    async def test_upload_image_without_optional_fields(
        self, test_db: Session, test_animal: Animal, mock_image_file: UploadFile
    ):
        """正常系: オプションフィールドなしで画像をアップロードできる"""
        # When
        result = await image_service.upload_image(
            db=test_db,
            animal_id=test_animal.id,
            file=mock_image_file,
        )

        # Then
        assert result.taken_at is None
        assert result.description is None

    @pytest.mark.asyncio
    async def test_upload_image_nonexistent_animal(
        self, test_db: Session, mock_image_file: UploadFile
    ):
        """異常系: 存在しない猫IDの場合は404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            await image_service.upload_image(
                db=test_db,
                animal_id=99999,
                file=mock_image_file,
            )
        assert exc_info.value.status_code == 404

    @pytest.mark.asyncio
    async def test_upload_image_exceeds_limit(
        self, test_db: Session, test_animal: Animal, mock_image_file: UploadFile
    ):
        """異常系: 枚数制限を超える場合は400エラー"""
        # Given: 最大枚数を2枚に設定
        setting = Setting(
            key="max_images_per_animal",
            value="2",
            description="最大画像枚数",
        )
        test_db.add(setting)
        test_db.commit()

        # 既に2枚の画像を登録
        for i in range(2):
            image = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"test_{i}.jpg",
                file_size=1024,
            )
            test_db.add(image)
        test_db.commit()

        # When/Then: 3枚目をアップロードしようとすると失敗
        with pytest.raises(HTTPException) as exc_info:
            await image_service.upload_image(
                db=test_db,
                animal_id=test_animal.id,
                file=mock_image_file,
            )
        assert exc_info.value.status_code == 400
        assert "上限" in exc_info.value.detail


class TestListImages:
    """画像一覧取得のテスト"""

    def test_list_images_empty(self, test_db: Session, test_animal: Animal):
        """正常系: 画像が0枚の場合は空リストを返す"""
        # When
        images = image_service.list_images(test_db, test_animal.id)

        # Then
        assert len(images) == 0

    def test_list_images_multiple(self, test_db: Session, test_animal: Animal):
        """正常系: 複数の画像を取得できる"""
        # Given
        for i in range(3):
            image = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"test_{i}.jpg",
                file_size=1024,
            )
            test_db.add(image)
        test_db.commit()

        # When
        images = image_service.list_images(test_db, test_animal.id)

        # Then
        assert len(images) == 3

    def test_list_images_sort_by_created_at_desc(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 作成日時の降順でソートできる"""
        # Given: 明示的に異なる作成日時を設定
        now = datetime.now()

        image1 = AnimalImage(
            animal_id=test_animal.id,
            image_path="test_1.jpg",
            file_size=1024,
            created_at=now - timedelta(seconds=10),  # 10秒前
        )
        image2 = AnimalImage(
            animal_id=test_animal.id,
            image_path="test_2.jpg",
            file_size=1024,
            created_at=now,  # 現在
        )
        test_db.add(image1)
        test_db.add(image2)
        test_db.commit()
        test_db.refresh(image1)
        test_db.refresh(image2)

        # When
        images = image_service.list_images(
            test_db, test_animal.id, sort_by="created_at", ascending=False
        )

        # Then
        # 降順なので、後に作成された画像が先に来る
        assert len(images) == 2
        assert images[0].id == image2.id
        assert images[1].id == image1.id

    def test_list_images_nonexistent_animal(self, test_db: Session):
        """異常系: 存在しない猫IDの場合は404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.list_images(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestGetImage:
    """画像取得のテスト"""

    def test_get_image_success(self, test_db: Session, test_animal: Animal):
        """正常系: 画像を取得できる"""
        # Given
        image = AnimalImage(
            animal_id=test_animal.id,
            image_path="test.jpg",
            file_size=1024,
        )
        test_db.add(image)
        test_db.commit()

        # When
        result = image_service.get_image(test_db, image.id)

        # Then
        assert result.id == image.id
        assert result.animal_id == test_animal.id

    def test_get_image_nonexistent(self, test_db: Session):
        """異常系: 存在しない画像IDの場合は404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.get_image(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestDeleteImage:
    """画像削除のテスト"""

    def test_delete_image_success(self, test_db: Session, test_animal: Animal):
        """正常系: 画像を削除できる"""
        # Given
        image = AnimalImage(
            animal_id=test_animal.id,
            image_path="test.jpg",
            file_size=1024,
        )
        test_db.add(image)
        test_db.commit()
        image_id = image.id

        # When
        result = image_service.delete_image(test_db, image_id)

        # Then
        assert result is True
        # データベースから削除されていることを確認
        deleted_image = (
            test_db.query(AnimalImage).filter(AnimalImage.id == image_id).first()
        )
        assert deleted_image is None

    def test_delete_image_nonexistent(self, test_db: Session):
        """異常系: 存在しない画像IDの場合は404エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.delete_image(test_db, 99999)
        assert exc_info.value.status_code == 404


class TestUpdateImageLimits:
    """画像制限設定更新のテスト"""

    def test_update_max_images(self, test_db: Session):
        """正常系: 最大画像枚数を更新できる"""
        # When
        max_images, max_size = image_service.update_image_limits(
            test_db, max_images_per_animal=30
        )

        # Then
        assert max_images == 30
        # データベースに保存されていることを確認
        setting = (
            test_db.query(Setting)
            .filter(Setting.key == "max_images_per_animal")
            .first()
        )
        assert setting is not None
        assert setting.value == "30"

    def test_update_max_size(self, test_db: Session):
        """正常系: 最大ファイルサイズを更新できる"""
        # When
        max_images, max_size = image_service.update_image_limits(
            test_db, max_image_size_mb=10.0
        )

        # Then
        assert max_size == 10 * 1024 * 1024
        # データベースに保存されていることを確認
        setting = (
            test_db.query(Setting).filter(Setting.key == "max_image_size_mb").first()
        )
        assert setting is not None
        assert setting.value == "10.0"

    def test_update_both_limits(self, test_db: Session):
        """正常系: 両方の制限を同時に更新できる"""
        # When
        max_images, max_size = image_service.update_image_limits(
            test_db, max_images_per_animal=25, max_image_size_mb=8.0
        )

        # Then
        assert max_images == 25
        assert max_size == 8 * 1024 * 1024

    def test_update_max_images_out_of_range_low(self, test_db: Session):
        """異常系: 最大画像枚数が範囲外（下限）の場合は400エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.update_image_limits(test_db, max_images_per_animal=0)
        assert exc_info.value.status_code == 400

    def test_update_max_images_out_of_range_high(self, test_db: Session):
        """異常系: 最大画像枚数が範囲外（上限）の場合は400エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.update_image_limits(test_db, max_images_per_animal=101)
        assert exc_info.value.status_code == 400

    def test_update_max_size_out_of_range_low(self, test_db: Session):
        """異常系: 最大ファイルサイズが範囲外（下限）の場合は400エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.update_image_limits(test_db, max_image_size_mb=0.05)
        assert exc_info.value.status_code == 400

    def test_update_max_size_out_of_range_high(self, test_db: Session):
        """異常系: 最大ファイルサイズが範囲外（上限）の場合は400エラー"""
        # When/Then
        with pytest.raises(HTTPException) as exc_info:
            image_service.update_image_limits(test_db, max_image_size_mb=51.0)
        assert exc_info.value.status_code == 400


class TestGetImagePath:
    """画像パス取得のテスト"""

    def test_get_image_path(self, test_animal: Animal):
        """正常系: 画像の絶対パスを取得できる"""
        # Given
        image = AnimalImage(
            animal_id=test_animal.id,
            image_path="animals/1/gallery/test.jpg",
            file_size=1024,
        )

        # When
        path = image_service.get_image_path(image)

        # Then
        assert isinstance(path, Path)
        assert str(path).endswith("animals/1/gallery/test.jpg")
