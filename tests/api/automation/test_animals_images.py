"""
猫画像アップロードAutomation APIのテスト

Requirements: 3.3, 3.4
"""

from __future__ import annotations

import io

from fastapi import status
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_image import AnimalImage


class TestUploadAnimalImageAutomation:
    """猫画像アップロードAutomation APIのテスト"""

    def test_upload_image_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """正常系: 画像を正常にアップロードできる"""
        # Given: 有効な画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # When: 画像をアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 201 Created が返される
        assert response.status_code == status.HTTP_201_CREATED

        # Then: レスポンスに必要なフィールドが含まれる
        data = response.json()
        assert "id" in data
        assert data["animal_id"] == test_animal.id
        assert "image_path" in data
        assert data["image_path"].startswith(f"animals/{test_animal.id}/gallery/")
        assert data["image_path"].endswith(".jpg")
        assert "file_size" in data
        assert data["file_size"] > 0
        assert "created_at" in data

        # Then: データベースに画像レコードが作成される
        image_record = (
            test_db.query(AnimalImage).filter(AnimalImage.id == data["id"]).first()
        )
        assert image_record is not None
        assert image_record.animal_id == test_animal.id

    def test_upload_image_animal_not_found(
        self,
        test_client: TestClient,
        automation_api_key: str,
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given: 有効な画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # When: 存在しない猫IDで画像をアップロード
        response = test_client.post(
            "/api/automation/animals/99999/images",
            files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 404 Not Found が返される
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert "猫ID 99999 が見つかりません" in response.json()["detail"]

    def test_upload_image_invalid_file_type(
        self,
        test_client: TestClient,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """異常系: 不正なファイル形式で400エラー"""
        # Given: テキストファイルを作成
        text_file = io.BytesIO(b"This is not an image")

        # When: テキストファイルをアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.txt", text_file, "text/plain")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 400 Bad Request が返される
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ファイル形式" in response.json()["detail"]

    def test_upload_image_file_too_large(
        self,
        test_client: TestClient,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """異常系: ファイルサイズ超過で400エラー"""
        # Given: 大きすぎるファイルを作成（6MB）
        # デフォルトの制限は5MBなので、6MBのダミーデータを作成
        large_data = b"x" * (6 * 1024 * 1024)  # 6MB
        image_bytes = io.BytesIO(large_data)

        # When: 大きすぎるファイルをアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("large.jpg", image_bytes, "image/jpeg")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 400 Bad Request が返される
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert "ファイルサイズ" in response.json()["detail"]

    def test_upload_image_without_api_key(
        self,
        test_client: TestClient,
        test_animal: Animal,
    ):
        """異常系: API Key なしで401エラー"""
        # Given: 有効な画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # When: API Key なしで画像をアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.jpg", image_bytes, "image/jpeg")},
        )

        # Then: 401 Unauthorized が返される
        assert response.status_code == status.HTTP_401_UNAUTHORIZED

    def test_upload_image_with_invalid_api_key(
        self,
        test_client: TestClient,
        test_animal: Animal,
    ):
        """異常系: 不正なAPI Keyで403エラー"""
        # Given: 有効な画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="red")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="JPEG")
        image_bytes.seek(0)

        # When: 不正なAPI Keyで画像をアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.jpg", image_bytes, "image/jpeg")},
            headers={"X-Automation-Key": "invalid-key"},
        )

        # Then: 403 Forbidden が返される
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_upload_multiple_images(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """正常系: 複数の画像をアップロードできる"""
        # Given: 3つの画像ファイルを作成
        uploaded_ids = []

        for i in range(3):
            image = Image.new("RGB", (100, 100), color=["red", "green", "blue"][i])
            image_bytes = io.BytesIO()
            image.save(image_bytes, format="JPEG")
            image_bytes.seek(0)

            # When: 画像をアップロード
            response = test_client.post(
                f"/api/automation/animals/{test_animal.id}/images",
                files={"file": (f"test{i}.jpg", image_bytes, "image/jpeg")},
                headers={"X-Automation-Key": automation_api_key},
            )

            # Then: 201 Created が返される
            assert response.status_code == status.HTTP_201_CREATED
            uploaded_ids.append(response.json()["id"])

        # Then: データベースに3つの画像レコードが作成される
        images = (
            test_db.query(AnimalImage)
            .filter(AnimalImage.animal_id == test_animal.id)
            .all()
        )
        assert len(images) == 3

        # Then: すべての画像IDが異なる
        assert len(set(uploaded_ids)) == 3

    def test_upload_image_png_format(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """正常系: PNG形式の画像をアップロードできる"""
        # Given: PNG画像ファイルを作成
        image = Image.new("RGBA", (100, 100), color=(255, 0, 0, 128))
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="PNG")
        image_bytes.seek(0)

        # When: PNG画像をアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.png", image_bytes, "image/png")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 201 Created が返される
        assert response.status_code == status.HTTP_201_CREATED

        # Then: 画像パスがPNG形式
        data = response.json()
        assert data["image_path"].endswith(".png")

    def test_upload_image_webp_format(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        automation_api_key: str,
    ):
        """正常系: WebP形式の画像をアップロードできる"""
        # Given: WebP画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="blue")
        image_bytes = io.BytesIO()
        image.save(image_bytes, format="WEBP")
        image_bytes.seek(0)

        # When: WebP画像をアップロード
        response = test_client.post(
            f"/api/automation/animals/{test_animal.id}/images",
            files={"file": ("test.webp", image_bytes, "image/webp")},
            headers={"X-Automation-Key": automation_api_key},
        )

        # Then: 201 Created が返される
        assert response.status_code == status.HTTP_201_CREATED

        # Then: 画像パスがWebP形式
        data = response.json()
        assert data["image_path"].endswith(".webp")
