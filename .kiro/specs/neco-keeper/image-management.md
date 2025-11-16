# 画像管理仕様

## 概要

NecoKeeperの画像管理機能は、猫のプロフィール画像と画像ギャラリーの2つの機能を提供します。

### 設計原則

1. **ストレージ効率**: 画像サイズ制限とファイル数制限
2. **パフォーマンス**: 画像の遅延読み込みとキャッシュ
3. **ユーザビリティ**: ドラッグ&ドロップ、プレビュー表示
4. **セキュリティ**: ファイル形式検証、サイズ制限

## データモデル

### AnimalImages（猫画像ギャラリー）

| カラム名 | 型 | NULL | デフォルト | 説明 |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | 主キー |
| animal_id | INTEGER | NO | - | 猫ID（FK） |
| image_path | VARCHAR(255) | NO | - | 画像パス（相対パス） |
| taken_at | DATE | YES | NULL | 撮影日 |
| description | TEXT | YES | NULL | 説明 |
| file_size | INTEGER | NO | 0 | ファイルサイズ（bytes） |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | 作成日時 |

**インデックス**: animal_id, taken_at

### Animals.photo（プロフィール画像）

- **型**: VARCHAR(255)
- **NULL**: YES（任意項目）
- **デフォルト**: NULL
- **説明**: プロフィール画像パス（絶対パスまたは相対パス）

**画像パスの優先順位**:
1. `Animals.photo`（プロフィール画像）
2. `AnimalImages`の最新画像（created_at降順）
3. デフォルト画像（`/static/images/default-cat.svg`）

## ストレージ構造

### ディレクトリ構成

```
media/
└── animals/
    └── {animal_id}/
        ├── profile/                    # プロフィール画像（1枚のみ）
        │   └── {uuid}.{ext}
        └── gallery/                    # 画像ギャラリー
            ├── {uuid}.{ext}
            ├── {uuid}.{ext}
            └── ...
```

### ファイル命名規則

- **形式**: `{uuid}.{ext}`
- **UUID**: UUID4（ハイフンなし、32文字）
- **拡張子**: `jpg`, `jpeg`, `png`, `webp`

**例**:
- `f4b3679d97474a6dbe89d7275c8e71db.png`
- `a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.jpg`

## 画像制限

### デフォルト設定

| 項目 | 値 | 説明 |
|-----|-----|------|
| 最大画像枚数（1猫あたり） | 20枚 | Settingsテーブルで変更可能 |
| 最大ファイルサイズ | 5MB | Settingsテーブルで変更可能 |
| 対応形式 | JPEG, PNG, WebP | - |
| 最小サイズ | 100x100px | - |
| 最大サイズ | 4000x4000px | - |

### Settings設定

```json
{
  "key": "image_limits",
  "value": {
    "max_images_per_animal": 20,
    "max_image_size_bytes": 5242880,
    "allowed_formats": ["image/jpeg", "image/png", "image/webp"],
    "min_width": 100,
    "min_height": 100,
    "max_width": 4000,
    "max_height": 4000
  }
}
```

## API仕様

### 画像アップロード

#### プロフィール画像アップロード（新規）

```http
POST /api/v1/animals/{animal_id}/profile-image
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
```

**レスポンス**:
```json
{
  "image_path": "/media/animals/1/profile/f4b3679d97474a6dbe89d7275c8e71db.png"
}
```

#### プロフィール画像変更

```http
PUT /api/v1/animals/{animal_id}/profile-image
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
```

**レスポンス**:
```json
{
  "image_path": "/media/animals/1/profile/a1b2c3d4e5f6g7h8i9j0k1l2m3n4o5p6.jpg"
}
```

#### ギャラリーからプロフィール画像を選択

```http
PUT /api/v1/animals/{animal_id}/profile-image/from-gallery/{image_id}
Content-Type: application/json
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "image_path": "/media/animals/1/gallery/f4b3679d97474a6dbe89d7275c8e71db.png"
}
```

#### 画像ギャラリーにアップロード

```http
POST /api/v1/animals/{animal_id}/images
Content-Type: multipart/form-data
Authorization: Bearer {token}

file: (binary)
taken_at: 2025-11-15 (optional)
description: かわいい写真 (optional)
```

**レスポンス**:
```json
{
  "id": 123,
  "animal_id": 1,
  "image_path": "animals/1/gallery/f4b3679d97474a6dbe89d7275c8e71db.png",
  "taken_at": "2025-11-15",
  "description": "かわいい写真",
  "file_size": 1234567,
  "created_at": "2025-11-15T10:30:00"
}
```

### 画像一覧取得

```http
GET /api/v1/animals/{animal_id}/images?sort_by=created_at&ascending=false
Authorization: Bearer {token}
```

**レスポンス**:
```json
[
  {
    "id": 123,
    "animal_id": 1,
    "image_path": "animals/1/gallery/f4b3679d97474a6dbe89d7275c8e71db.png",
    "taken_at": "2025-11-15",
    "description": "かわいい写真",
    "file_size": 1234567,
    "created_at": "2025-11-15T10:30:00"
  },
  ...
]
```

**クエリパラメータ**:
- `sort_by`: ソート基準（`created_at` または `taken_at`）
- `ascending`: 昇順（`true`）または降順（`false`）

### 画像削除

```http
DELETE /api/v1/images/{image_id}
Authorization: Bearer {token}
```

**レスポンス**: 204 No Content

### 画像制限情報取得

```http
GET /api/v1/animals/{animal_id}/images/limits
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "max_images_per_animal": 20,
  "max_image_size_mb": 5.0,
  "current_count": 8,
  "remaining_count": 12
}
```

### 表示用画像パス取得

```http
GET /api/v1/animals/{animal_id}/display-image
Authorization: Bearer {token}
```

**レスポンス**:
```json
{
  "image_path": "/media/animals/1/profile/f4b3679d97474a6dbe89d7275c8e71db.png"
}
```

## フロントエンド実装

### 管理画面（猫詳細ページ）

#### プロフィール画像変更モーダル

```html
<!-- モーダル構造 -->
<div id="profileImageModal" class="modal">
  <div class="modal-content">
    <h3>プロフィール画像を変更</h3>

    <!-- タブ -->
    <div class="tabs">
      <button id="tab-upload" class="tab active">新しい画像をアップロード</button>
      <button id="tab-gallery" class="tab">ギャラリーから選択</button>
    </div>

    <!-- アップロードタブ -->
    <div id="content-upload" class="tab-content">
      <input type="file" id="modal-file-input" accept="image/*">
      <div id="modal-preview-container" class="hidden">
        <img id="modal-preview" src="" alt="プレビュー">
      </div>
      <button id="uploadBtn" disabled>アップロード</button>
    </div>

    <!-- ギャラリータブ -->
    <div id="content-gallery" class="tab-content hidden">
      <div id="gallery-grid" class="grid">
        <!-- 画像グリッド -->
      </div>
      <div id="gallery-empty" class="hidden">
        <p>画像がありません</p>
      </div>
    </div>

    <button id="cancelUploadBtn">キャンセル</button>
  </div>
</div>
```

#### JavaScript実装

```javascript
// プロフィール画像アップロード
async function uploadProfileImage(animalId, file) {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${API_BASE}/animals/${animalId}/profile-image`, {
    method: 'PUT',
    headers: {
      Authorization: `Bearer ${getToken()}`,
    },
    body: formData,
  });

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'アップロードに失敗しました');
  }

  const result = await response.json();

  // プロフィール画像を更新
  document.getElementById('animalPhoto').src = result.image_path;

  showAlert('success', 'プロフィール画像を更新しました');
}

// ギャラリーから画像を選択
async function selectGalleryImage(imageId, imagePath) {
  const response = await fetch(
    `${API_BASE}/animals/${animalId}/profile-image/from-gallery/${imageId}`,
    {
      method: 'PUT',
      headers: {
        Authorization: `Bearer ${getToken()}`,
        'Content-Type': 'application/json',
      },
    }
  );

  if (!response.ok) {
    const error = await response.json();
    throw new Error(error.detail || 'プロフィール画像の設定に失敗しました');
  }

  const result = await response.json();

  // プロフィール画像を更新
  document.getElementById('animalPhoto').src = result.image_path;

  showAlert('success', 'プロフィール画像を更新しました');
}
```

#### 画像ギャラリータブ

```html
<!-- 画像ギャラリー -->
<div id="content-gallery" class="tab-content">
  <div class="gallery-header">
    <p>8枚の画像</p>
    <button onclick="openUploadDialog()">画像を追加</button>
  </div>

  <div class="gallery-grid">
    <div class="gallery-item">
      <img src="/media/animals/1/gallery/image1.png" alt="猫の画像">
      <button onclick="deleteImage(123)" class="delete-btn">削除</button>
      <p class="image-date">2025-11-15</p>
      <p class="image-description">かわいい写真</p>
    </div>
    <!-- 他の画像 -->
  </div>
</div>
```

### 新規登録ページ

```html
<!-- プロフィール画像アップロード -->
<div class="form-group">
  <label for="profile-image">プロフィール画像（任意）</label>
  <input type="file" id="profile-image" accept="image/*">
  <img id="profile-preview" src="/static/images/default-cat.svg" alt="プレビュー">
  <p class="help-text">最大5MB、JPEG/PNG/WebP形式</p>
</div>
```

```javascript
// 新規登録時のプロフィール画像アップロード
async function createAnimalWithImage() {
  // 1. 猫の基本情報を登録
  const animal = await apiRequest(`${API_BASE}/animals`, {
    method: 'POST',
    body: JSON.stringify(formData),
  });

  // 2. プロフィール画像がある場合はアップロード
  const fileInput = document.getElementById('profile-image');
  if (fileInput.files.length > 0) {
    await uploadProfileImage(animal.id, fileInput.files[0]);
  }

  // 3. 詳細ページにリダイレクト
  window.location.href = `/admin/animals/${animal.id}`;
}
```

## バックエンド実装

### サービス層（image_service.py）

```python
from __future__ import annotations

import os
import uuid
from pathlib import Path
from typing import BinaryIO

from fastapi import HTTPException, UploadFile, status
from PIL import Image
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.animal_image import AnimalImage
from app.models.setting import Setting

# 画像保存ディレクトリ
MEDIA_ROOT = Path("media")
ANIMALS_DIR = MEDIA_ROOT / "animals"

# 対応形式
ALLOWED_FORMATS = {"image/jpeg", "image/png", "image/webp"}
ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp"}


async def upload_image(
    db: Session,
    animal_id: int,
    file: UploadFile,
    taken_at: date | None = None,
    description: str | None = None,
) -> AnimalImage:
    """
    画像をアップロード

    Args:
        db: データベースセッション
        animal_id: 猫ID
        file: 画像ファイル
        taken_at: 撮影日（任意）
        description: 説明（任意）

    Returns:
        AnimalImage: アップロードされた画像情報

    Raises:
        HTTPException: 猫が存在しない、枚数制限超過、ファイルサイズ超過の場合
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Animal {animal_id} not found"
        )

    # 画像制限チェック
    max_images, max_size_bytes = get_image_limits(db)
    current_count = count_animal_images(db, animal_id)

    if current_count >= max_images:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Maximum {max_images} images per animal"
        )

    # ファイル形式チェック
    if file.content_type not in ALLOWED_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format: {file.content_type}"
        )

    # ファイルサイズチェック
    file_content = await file.read()
    file_size = len(file_content)

    if file_size > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"File size exceeds {max_size_bytes / (1024 * 1024):.1f}MB"
        )

    # 画像サイズチェック
    try:
        img = Image.open(BytesIO(file_content))
        width, height = img.size

        if width < 100 or height < 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size must be at least 100x100px"
            )

        if width > 4000 or height > 4000:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image size must not exceed 4000x4000px"
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid image file: {str(e)}"
        )

    # ファイル保存
    file_ext = Path(file.filename).suffix.lower()
    if file_ext not in ALLOWED_EXTENSIONS:
        file_ext = ".jpg"

    filename = f"{uuid.uuid4().hex}{file_ext}"
    save_dir = ANIMALS_DIR / str(animal_id) / "gallery"
    save_dir.mkdir(parents=True, exist_ok=True)

    file_path = save_dir / filename
    with open(file_path, "wb") as f:
        f.write(file_content)

    # データベースに記録
    relative_path = f"animals/{animal_id}/gallery/{filename}"
    image = AnimalImage(
        animal_id=animal_id,
        image_path=relative_path,
        taken_at=taken_at,
        description=description,
        file_size=file_size,
    )
    db.add(image)
    db.commit()
    db.refresh(image)

    return image


def get_image_limits(db: Session) -> tuple[int, int]:
    """
    画像制限設定を取得

    Returns:
        tuple[int, int]: (最大枚数, 最大ファイルサイズ)
    """
    setting = db.query(Setting).filter(Setting.key == "image_limits").first()

    if setting:
        limits = json.loads(setting.value)
        return (
            limits.get("max_images_per_animal", 20),
            limits.get("max_image_size_bytes", 5 * 1024 * 1024)
        )

    return (20, 5 * 1024 * 1024)


def count_animal_images(db: Session, animal_id: int) -> int:
    """
    猫の画像枚数をカウント
    """
    return db.query(AnimalImage).filter(AnimalImage.animal_id == animal_id).count()


def list_images(
    db: Session,
    animal_id: int,
    sort_by: str = "created_at",
    ascending: bool = False,
) -> list[AnimalImage]:
    """
    画像一覧を取得
    """
    query = db.query(AnimalImage).filter(AnimalImage.animal_id == animal_id)

    if sort_by == "taken_at":
        order_column = AnimalImage.taken_at
    else:
        order_column = AnimalImage.created_at

    if ascending:
        query = query.order_by(order_column.asc())
    else:
        query = query.order_by(order_column.desc())

    return query.all()


def delete_image(db: Session, image_id: int) -> None:
    """
    画像を削除
    """
    image = db.query(AnimalImage).filter(AnimalImage.id == image_id).first()
    if not image:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Image {image_id} not found"
        )

    # ファイル削除
    file_path = MEDIA_ROOT / image.image_path
    if file_path.exists():
        file_path.unlink()

    # データベースから削除
    db.delete(image)
    db.commit()
```

### 表示用画像パス取得

```python
def get_display_image(db: Session, animal_id: int) -> str:
    """
    猫の表示用画像パスを取得

    優先順位:
    1. プロフィール画像（animal.photo）
    2. 画像ギャラリーの最新画像
    3. デフォルト画像

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        str: 画像パス
    """
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        return "/static/images/default-cat.svg"

    # 1. プロフィール画像
    if animal.photo:
        return animal.photo

    # 2. 画像ギャラリーの最新画像
    latest_image = (
        db.query(AnimalImage)
        .filter(AnimalImage.animal_id == animal_id)
        .order_by(AnimalImage.created_at.desc())
        .first()
    )

    if latest_image:
        return f"/media/{latest_image.image_path}"

    # 3. デフォルト画像
    return "/static/images/default-cat.svg"
```

## エラーハンドリング

### バリデーションエラー

| エラー | HTTPステータス | メッセージ |
|-------|--------------|-----------|
| 猫が存在しない | 404 | Animal {id} not found |
| 枚数制限超過 | 400 | Maximum {max} images per animal |
| ファイルサイズ超過 | 400 | File size exceeds {max}MB |
| 不正なファイル形式 | 400 | Unsupported file format: {type} |
| 画像サイズ不正 | 400 | Image size must be at least 100x100px |
| 画像が存在しない | 404 | Image {id} not found |

### フロントエンドエラー表示

```javascript
try {
  await uploadImage(file);
  showAlert('success', '画像をアップロードしました');
} catch (error) {
  console.error('Error uploading image:', error);
  showAlert('error', error.message);
}
```

## テスト仕様

### 単体テスト（tests/services/test_image_service.py）

```python
class TestImageUpload:
    """画像アップロードのテスト"""

    def test_upload_image_success(self, test_db, test_animal):
        """正常系: 画像をアップロードできる"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: 画像をアップロード
        result = await image_service.upload_image(
            db=test_db,
            animal_id=test_animal.id,
            file=UploadFile(filename="test.png", file=img_bytes),
        )

        # Then: 画像が保存される
        assert result.animal_id == test_animal.id
        assert result.image_path.endswith(".png")

    def test_upload_image_exceeds_limit(self, test_db, test_animal):
        """異常系: 枚数制限超過"""
        # Given: 既に20枚の画像が登録されている
        for i in range(20):
            image = AnimalImage(
                animal_id=test_animal.id,
                image_path=f"animals/{test_animal.id}/gallery/test{i}.png",
            )
            test_db.add(image)
        test_db.commit()

        # When: 21枚目をアップロード
        # Then: 400エラーが返される
        with pytest.raises(HTTPException) as exc:
            await image_service.upload_image(...)
        assert exc.value.status_code == 400
```

### APIテスト（tests/api/test_images.py）

```python
class TestProfileImage:
    """プロフィール画像のテスト"""

    def test_upload_profile_image_success(
        self,
        test_client,
        test_animal,
        auth_headers,
    ):
        """正常系: プロフィール画像をアップロードできる"""
        # Given: テスト用の画像ファイル
        image = Image.new("RGB", (100, 100), color="red")
        img_bytes = BytesIO()
        image.save(img_bytes, format="PNG")
        img_bytes.seek(0)

        # When: プロフィール画像をアップロード
        response = test_client.post(
            f"/api/v1/animals/{test_animal.id}/profile-image",
            headers=auth_headers,
            files={"file": ("profile.png", img_bytes, "image/png")},
        )

        # Then: 200 OKが返される
        assert response.status_code == 200
        data = response.json()
        assert "image_path" in data

        # 猫のphotoフィールドが更新されている
        test_db.refresh(test_animal)
        assert test_animal.photo is not None
```

## セキュリティ考慮事項

### ファイルアップロードセキュリティ

1. **ファイル形式検証**: Content-Typeとファイル拡張子の両方をチェック
2. **ファイルサイズ制限**: 5MB以下に制限
3. **画像サイズ検証**: PIL/Pillowで画像を開いて検証
4. **ファイル名のサニタイズ**: UUIDを使用してファイル名を生成
5. **ディレクトリトラバーサル対策**: Pathオブジェクトを使用

### 認証・認可

- **プロフィール画像アップロード**: 認証済みユーザー（`get_current_active_user`）
- **画像ギャラリーアップロード**: 認証済みユーザー（`get_current_active_user`）
- **画像削除**: 認証済みユーザー（`get_current_active_user`）

## パフォーマンス最適化

### 画像最適化

1. **リサイズ**: 大きすぎる画像は自動的にリサイズ（オプション）
2. **圧縮**: JPEG品質を調整して圧縮（オプション）
3. **WebP変換**: WebP形式に変換してファイルサイズを削減（オプション）

### キャッシュ戦略

1. **ブラウザキャッシュ**: Cache-Controlヘッダーを設定
2. **CDN**: 画像をCDNで配信（本番環境）
3. **遅延読み込み**: Lazy Loadingで初期表示を高速化

## 今後の拡張

### Phase 2以降の機能

1. **画像編集**: トリミング、回転、フィルター
2. **サムネイル生成**: 複数サイズのサムネイルを自動生成
3. **画像検索**: 画像の説明文で検索
4. **画像並び替え**: ドラッグ&ドロップで順序変更
5. **一括アップロード**: 複数画像を一度にアップロード
6. **画像圧縮**: アップロード時に自動圧縮
7. **画像タグ**: タグ付けで分類
