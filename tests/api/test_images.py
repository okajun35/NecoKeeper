"""
画像管理APIのテスト

Context7参照: /pytest-dev/pytest (Trust Score: 9.5)
"""

from __future__ import annotations

import io
from datetime import date

from fastapi import status
from fastapi.testclient import TestClient
from PIL import Image
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_image import AnimalImage


class TestImageUpload:
    """画像アップロードのテスト"""

    def test_upload_image_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: 画像をアップロードできる"""
        # Given: テスト用の画像ファイルを作成
        image = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: 画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/images",
            headers=auth_headers,
            files={"file": ("test.png", img_bytes, "image/png")},
        )

        # Then: 201 Createdが返される
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["animal_id"] == test_animal.id
        assert "image_path" in data
        assert data["image_path"].endswith(".png")

    def test_upload_image_with_metadata(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: メタデータ付きで画像をアップロードできる"""
        # Given: テスト用の画像ファイルとメタデータ
        image = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="JPEG")
        img_bytes.seek(0)

        # When: メタデータ付きで画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/images",
            headers=auth_headers,
            files={"file": ("test.jpg", img_bytes, "image/jpeg")},
            data={
                "taken_at": "2024-01-15",
                "description": "かわいい写真",
            },
        )

        # Then: 201 Createdが返される
        assert response.status_code == status.HTTP_201_CREATED
        data = response.json()
        assert data["taken_at"] == "2024-01-15"
        assert data["description"] == "かわいい写真"

    def test_upload_image_nonexistent_animal(
        self,
        test_client: TestClient,
        auth_headers: dict[str, str],
    ):
        """異常系: 存在しない猫IDで404エラー"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="green")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: 存在しない猫IDで画像をアップロード
        response = test_client.post(
            "/api/v1/animals/99999/images",
            headers=auth_headers,
            files={"file": ("test.png", img_bytes, "image/png")},
        )

        # Then: 404 Not Foundが返される
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_upload_image_unauthorized(
        self,
        test_client: TestClient,
        test_animal: Animal,
    ):
        """異常系: 認証なしで401エラー"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="yellow")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: 認証なしで画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/images",
            files={"file": ("test.png", img_bytes, "image/png")},
        )

        # Then: 401 Unauthorizedが返される
        assert response.status_code == status.HTTP_401_UNAUTHORIZED


class TestImageList:
    """画像一覧取得のテスト"""

    def test_list_images_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: 画像一覧を取得できる"""
        # Given: 複数の画像を登録
        for i in range(3):
            img = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"animals/{test_animal.id}/gallery/test{i}.png",
                taken_at=date(2024, 1, i + 1),
            )
            test_db.add(img)
        test_db.commit()

        # When: 画像一覧を取得
        response = test_client.get(
            f"/api/v1/animals/{test_animal.id}/images",
            headers=auth_headers,
        )

        # Then: 200 OKが返される
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3

    def test_list_images_sorted_by_created_at_desc(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: 作成日時の降順でソートされる"""
        # Given: 複数の画像を登録
        images: list[AnimalImage] = []
        for i in range(3):
            img = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"animals/{test_animal.id}/gallery/test{i}.png",
            )
            test_db.add(img)
            images.append(img)
        test_db.commit()

        # When: 作成日時の降順で画像一覧を取得
        response = test_client.get(
            f"/api/v1/animals/{test_animal.id}/images?sort_by=created_at&ascending=false",
            headers=auth_headers,
        )

        # Then: 降順でソートされている
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert len(data) == 3
        # 降順なので最新の画像が最初（IDが大きい方が新しい）
        assert data[0]["id"] > data[1]["id"]
        assert data[1]["id"] > data[2]["id"]


class TestImageDelete:
    """画像削除のテスト"""

    def test_delete_image_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: 画像を削除できる"""
        # Given: 画像を登録
        img = AnimalImage(
            animal_id=test_animal.id,
            image_path=f"animals/{test_animal.id}/gallery/test.png",
        )
        test_db.add(img)
        test_db.commit()
        test_db.refresh(img)

        # When: 画像を削除
        response = test_client.delete(
            f"/api/v1/images/{img.id}",
            headers=auth_headers,
        )

        # Then: 204 No Contentが返される
        assert response.status_code == status.HTTP_204_NO_CONTENT

        # 画像が削除されている
        deleted_img = (
            test_db.query(AnimalImage).filter(AnimalImage.id == img.id).first()
        )
        assert deleted_img is None

    def test_delete_image_nonexistent(
        self,
        test_client: TestClient,
        auth_headers: dict[str, str],
    ):
        """異常系: 存在しない画像IDで404エラー"""
        # When: 存在しない画像IDで削除
        response = test_client.delete(
            "/api/v1/images/99999",
            headers=auth_headers,
        )

        # Then: 404 Not Foundが返される
        assert response.status_code == status.HTTP_404_NOT_FOUND


class TestProfileImage:
    """プロフィール画像のテスト"""

    def test_upload_profile_image_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: プロフィール画像をアップロードできる"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="red")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: プロフィール画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/profile-image",
            headers=auth_headers,
            files={"file": ("profile.png", img_bytes, "image/png")},
        )

        # Then: 200 OKが返される
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "image_path" in data

        # 猫のphotoフィールドが更新されている
        test_db.refresh(test_animal)
        assert test_animal.photo is not None
        assert test_animal.photo == data["image_path"]

    def test_update_profile_image_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: プロフィール画像を変更できる"""
        # Given: 既存のプロフィール画像
        test_animal.photo = "/media/animals/1/old.png"
        test_db.commit()

        # テスト用の新しい画像ファイル
        image = Image.new("RGB", (100, 100), color="blue")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: プロフィール画像を変更
        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}/profile-image",
            headers=auth_headers,
            files={"file": ("new_profile.png", img_bytes, "image/png")},
        )

        # Then: 200 OKが返される
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "image_path" in data

        # 猫のphotoフィールドが更新されている
        test_db.refresh(test_animal)
        assert test_animal.photo != "/media/animals/1/old.png"
        assert test_animal.photo == data["image_path"]

    def test_set_profile_image_from_gallery_success(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """正常系: ギャラリーからプロフィール画像を選択できる"""
        # Given: ギャラリーに画像を登録
        img = AnimalImage(
            animal_id=test_animal.id,
            image_path=f"animals/{test_animal.id}/gallery/test.png",
        )
        test_db.add(img)
        test_db.commit()
        test_db.refresh(img)

        # When: ギャラリーからプロフィール画像を選択
        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}/profile-image/from-gallery/{img.id}",
            headers=auth_headers,
        )

        # Then: 200 OKが返される
        assert response.status_code == status.HTTP_200_OK
        data = response.json()
        assert "image_path" in data

        # 猫のphotoフィールドが更新されている
        test_db.refresh(test_animal)
        assert test_animal.photo == f"/media/{img.image_path}"

    def test_set_profile_image_from_gallery_wrong_animal(
        self,
        test_client: TestClient,
        test_db: Session,
        test_animal: Animal,
        auth_headers: dict[str, str],
    ):
        """異常系: 別の猫の画像を選択すると400エラー"""
        # Given: 別の猫の画像
        other_animal = Animal(
            name="別の猫",
            coat_color="三毛",
            gender="メス",
            tail_length="長い",
            collar="なし",
            age_months=12,  # 必須項目を追加
            status="QUARANTINE",
            protected_at=date.today(),
        )
        test_db.add(other_animal)
        test_db.commit()
        test_db.refresh(other_animal)

        img = AnimalImage(
            animal_id=other_animal.id,
            image_path=f"animals/{other_animal.id}/gallery/test.png",
        )
        test_db.add(img)
        test_db.commit()
        test_db.refresh(img)

        # When: 別の猫の画像を選択
        response = test_client.put(
            f"/api/v1/animals/{test_animal.id}/profile-image/from-gallery/{img.id}",
            headers=auth_headers,
        )

        # Then: 400 Bad Requestが返される
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_profile_image_unauthorized(
        self,
        test_client: TestClient,
        test_animal: Animal,
    ):
        """異常系: 認証なしで401エラー"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="green")
        img_bytes = io.BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: 認証なしでプロフィール画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/profile-image",
            files={"file": ("profile.png", img_bytes, "image/png")},
        )

        # Then: 401 Unauthorizedが返される
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
