# NecoKeeper Automation API

このディレクトリには、Kiro Hook、MCP、自動化スクリプト専用のAutomation APIエンドポイントが含まれています。

## 概要

Automation APIは、外部システムやAIアシスタント（Claude）がNecoKeeperと連携するための専用APIです。通常のWeb UIとは異なり、API Key認証を使用してプログラマティックなアクセスを提供します。

### 主な特徴

- **API Key認証**: `X-Automation-Key`ヘッダーによるシンプルな認証
- **トークン不要**: JWTトークンの管理が不要
- **自動化向け**: スクリプトやMCPツールからの利用に最適化
- **完全なCRUD**: 猫の登録、取得、画像アップロード、PDF生成

## 目次

- [認証](#認証)
- [利用可能なエンドポイント](#利用可能なエンドポイント)
- [使用例](#使用例)
- [エラーハンドリング](#エラーハンドリング)
- [セキュリティ](#セキュリティ)
- [開発](#開発)

## 認証

### API Keyの生成

```bash
# セキュアな32文字のAPI Keyを生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 出力例:
# xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ
```

### 環境変数の設定

`.env`ファイルに以下を追加：

```bash
# Automation API Keyを設定
AUTOMATION_API_KEY=xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ

# Automation APIを有効化
ENABLE_AUTOMATION_API=true
```

### 認証方法

すべてのリクエストに`X-Automation-Key`ヘッダーを含める：

```bash
curl -X POST http://localhost:8000/api/automation/animals \
  -H "X-Automation-Key: xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ" \
  -H "Content-Type: application/json" \
  -d '{"name": "たま", "gender": "male", "pattern": "キジトラ", "tail_length": "長い", "age_months": 12, "age_is_estimated": false}'
```

## 利用可能なエンドポイント

### 1. 猫の登録

**エンドポイント**: `POST /api/automation/animals`

**説明**: 新しい猫をシステムに登録します。

**リクエストボディ**:
```json
{
  "name": "たま",
  "gender": "male",
  "pattern": "キジトラ",
  "tail_length": "長い",
  "age_months": 12,
  "age_is_estimated": false,
  "status": "保護中",
  "collar": "赤い首輪",
  "ear_cut": false,
  "features": "人懐っこい性格",
  "protected_at": "2024-11-29"
}
```

**必須フィールド**:
- `name`: 猫の名前（1-100文字）
- `gender`: 性別（`male`, `female`, `unknown`）
- `pattern`: 柄・模様
- `tail_length`: 尻尾の長さ

**任意フィールド**:
- `age_months`: 月齢（null=不明）
- `age_is_estimated`: 推定月齢フラグ（`true`でも`age_months`がnullなら年齢不明扱い）

**レスポンス** (201 Created):
```json
{
  "id": 42,
  "name": "たま",
  "photo": null,
  "pattern": "キジトラ",
  "tail_length": "長い",
  "collar": "赤い首輪",
  "age_months": 12,
  "age_is_estimated": false,
  "gender": "male",
  "ear_cut": false,
  "features": "人懐っこい性格",
  "status": "保護中",
  "protected_at": "2024-11-29",
  "created_at": "2024-11-29T10:00:00Z",
  "updated_at": "2024-11-29T10:00:00Z"
}
```

### 2. 猫情報の取得

**エンドポイント**: `GET /api/automation/animals/{animal_id}`

**説明**: 指定されたIDの猫情報を取得します。

**パスパラメータ**:
- `animal_id`: 猫のID（整数）

**レスポンス** (200 OK):
```json
{
  "id": 42,
  "name": "たま",
  "pattern": "キジトラ",
  "status": "保護中",
  ...
}
```

**エラーレスポンス** (404 Not Found):
```json
{
  "detail": "ID 999 の猫が見つかりません"
}
```

### 3. 猫の画像アップロード

**エンドポイント**: `POST /api/automation/animals/{animal_id}/images`

**説明**: 猫のプロフィール画像をアップロードします。画像は`media/animals/{animal_id}/gallery/`にUUIDベースのファイル名で保存されます。

**パスパラメータ**:
- `animal_id`: 猫のID（整数）

**リクエスト**: `multipart/form-data`
- `file`: 画像ファイル（JPEG、PNG、WebP対応）

**制限**:
- 最大ファイルサイズ: 5MB（デフォルト）
- 最大画像枚数: 20枚/猫（デフォルト）
- 対応形式: JPEG、PNG、WebP

**レスポンス** (201 Created):
```json
{
  "id": 1,
  "animal_id": 42,
  "image_path": "animals/42/gallery/550e8400-e29b-41d4-a716-446655440000.jpg",
  "file_size": 102400,
  "taken_at": null,
  "description": null,
  "created_at": "2024-11-29T10:00:00Z"
}
```

**エラーレスポンス**:

- **400 Bad Request** - 不正なファイル形式:
  ```json
  {
    "detail": "サポートされていないファイル形式です。JPEG、PNG、WebPのみ対応しています"
  }
  ```

- **400 Bad Request** - ファイルサイズ超過:
  ```json
  {
    "detail": "ファイルサイズが上限（5MB）を超えています"
  }
  ```

- **400 Bad Request** - 画像枚数上限:
  ```json
  {
    "detail": "画像枚数が上限（20枚）に達しています"
  }
  ```

- **404 Not Found** - 猫が存在しない:
  ```json
  {
    "detail": "猫ID 999 が見つかりません"
  }
  ```

### 4. QR付きPDFの生成

**エンドポイント**: `POST /api/automation/pdf/qr-card-grid`

**説明**: 指定された猫のQRコード付きPDFを生成します。

**リクエストボディ**:
```json
{
  "animal_ids": [42, 43, 44]
}
```

**レスポンス**: PDFファイル（`application/pdf`）

## 使用例

### Python (httpx)

```python
import httpx
from pathlib import Path

# API設定
API_URL = "http://localhost:8000"
API_KEY = "xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ"

# HTTPクライアント作成
client = httpx.Client(
    base_url=API_URL,
    headers={"X-Automation-Key": API_KEY}
)

# 1. 猫を登録
response = client.post("/api/automation/animals", json={
    "name": "たま",
    "gender": "male",
    "pattern": "キジトラ",
    "tail_length": "長い",
    "age_months": 12,
    "age_is_estimated": False,
    "status": "保護中"
})
animal = response.json()
animal_id = animal["id"]
print(f"登録完了: ID={animal_id}, 名前={animal['name']}")

# 2. 画像をアップロード
with open("tama.jpg", "rb") as f:
    response = client.post(
        f"/api/automation/animals/{animal_id}/images",
        files={"file": ("tama.jpg", f, "image/jpeg")}
    )
image = response.json()
print(f"画像アップロード完了: {image['image_path']}")

# 3. QR PDFを生成
response = client.post("/api/automation/pdf/qr-card-grid", json={
    "animal_ids": [animal_id]
})
pdf_path = Path(f"qr_{animal_id}.pdf")
pdf_path.write_bytes(response.content)
print(f"PDF生成完了: {pdf_path}")
```

### cURL

```bash
# 1. 猫を登録
curl -X POST http://localhost:8000/api/automation/animals \
  -H "X-Automation-Key: xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "たま",
    "gender": "male",
    "pattern": "キジトラ",
    "tail_length": "長い",
    "age_months": 12,
    "age_is_estimated": false
  }'

# 2. 猫情報を取得
curl -X GET http://localhost:8000/api/automation/animals/42 \
  -H "X-Automation-Key: xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ"

# 3. 画像をアップロード
curl -X POST http://localhost:8000/api/automation/animals/42/images \
  -H "X-Automation-Key: xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ" \
  -F "file=@tama.jpg"

# 4. QR PDFを生成
curl -X POST http://localhost:8000/api/automation/pdf/qr-card-grid \
  -H "X-Automation-Key: xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ" \
  -H "Content-Type: application/json" \
  -d '{"animal_ids": [42]}' \
  --output qr_42.pdf
```

### JavaScript (fetch)

```javascript
const API_URL = 'http://localhost:8000';
const API_KEY = 'xK9mP2nQ4rS6tU8vW0yZ1aB3cD5eF7gH9iJ';

// 1. 猫を登録
const response = await fetch(`${API_URL}/api/automation/animals`, {
  method: 'POST',
  headers: {
    'X-Automation-Key': API_KEY,
    'Content-Type': 'application/json'
  },
  body: JSON.stringify({
    name: 'たま',
    gender: 'male',
    pattern: 'キジトラ',
    tail_length: '長い',
    age_months: 12,
    age_is_estimated: false
  })
});
const animal = await response.json();
console.log(`登録完了: ID=${animal.id}`);

// 2. 画像をアップロード
const formData = new FormData();
formData.append('file', fileInput.files[0]);

const imageResponse = await fetch(
  `${API_URL}/api/automation/animals/${animal.id}/images`,
  {
    method: 'POST',
    headers: {
      'X-Automation-Key': API_KEY
    },
    body: formData
  }
);
const image = await imageResponse.json();
console.log(`画像アップロード完了: ${image.image_path}`);
```

## エラーハンドリング

### HTTPステータスコード

| コード | 説明 | 対処方法 |
|--------|------|----------|
| 200 | 成功 | - |
| 201 | 作成成功 | - |
| 400 | リクエストが不正 | リクエストボディを確認 |
| 401 | 認証失敗（API Key未設定） | `X-Automation-Key`ヘッダーを追加 |
| 403 | 認証失敗（API Key不正） | API Keyを確認 |
| 404 | リソースが見つからない | IDを確認 |
| 500 | サーバーエラー | ログを確認、管理者に連絡 |

### エラーレスポンス形式

すべてのエラーは以下の形式で返されます：

```json
{
  "detail": "エラーメッセージ"
}
```

### エラーハンドリングの例

```python
import httpx

try:
    response = client.post("/api/automation/animals", json=data)
    response.raise_for_status()
    animal = response.json()
except httpx.HTTPStatusError as e:
    if e.response.status_code == 401:
        print("認証エラー: API Keyを確認してください")
    elif e.response.status_code == 400:
        print(f"リクエストエラー: {e.response.json()['detail']}")
    elif e.response.status_code == 404:
        print("猫が見つかりません")
    else:
        print(f"エラー: {e.response.status_code}")
except httpx.RequestError as e:
    print(f"接続エラー: {e}")
```

## セキュリティ

### ベストプラクティス

1. **API Keyの管理**
   - ✅ 環境変数に保存
   - ✅ `.env`ファイルを使用（`.gitignore`に追加）
   - ❌ ソースコードにハードコードしない
   - ❌ バージョン管理にコミットしない

2. **API Keyの生成**
   - 暗号学的に安全な乱数生成を使用
   - 最低32文字
   - `secrets.token_urlsafe()`を使用

3. **通信の保護**
   - 本番環境ではHTTPSを使用
   - API Keyは`X-Automation-Key`ヘッダーで送信
   - API Keyをログに記録しない

4. **ファイルアップロードの検証**
   - ファイル形式の検証
   - ファイルサイズの制限
   - ディレクトリトラバーサル攻撃の防止

### セキュリティチェックリスト

本番環境デプロイ前に確認：

- [ ] API Keyは環境変数に保存されている
- [ ] HTTPSが有効化されている
- [ ] ファイルアップロードの検証が実装されている
- [ ] エラーメッセージに機密情報が含まれていない
- [ ] ログが適切に保護されている
- [ ] API Keyのローテーションポリシーが確立されている

## 開発

### プロジェクト構造

```
app/api/automation/
├── __init__.py       # ルーター登録
├── animals.py        # 猫関連エンドポイント
├── care_logs.py      # ケアログエンドポイント
├── pdf.py            # PDF生成エンドポイント
└── README.md         # このファイル
```

### テストの実行

```bash
# すべてのAutomation APIテストを実行
pytest tests/api/automation/ -v

# カバレッジ付きで実行
pytest tests/api/automation/ --cov=app/api/automation --cov-report=html

# 特定のテストファイルを実行
pytest tests/api/automation/test_animals_images.py -v
```

### コード品質チェック

```bash
# コードフォーマット
ruff format app/api/automation/

# Lintチェック
ruff check app/api/automation/ --fix

# 型チェック
mypy app/api/automation/

# すべてのチェックを実行
make check
```

### 開発ステータス

#### 実装済み機能
- ✅ 猫の登録（POST /api/automation/animals）
- ✅ 猫情報の取得（GET /api/automation/animals/{id}）
- ✅ 画像アップロード（POST /api/automation/animals/{id}/images）
- ✅ QR PDF生成（POST /api/automation/pdf/qr-card-grid）
- ✅ API Key認証
- ✅ エラーハンドリング
- ✅ 包括的なテスト

#### 今後の拡張予定
- [ ] 猫情報の更新（PUT /api/automation/animals/{id}）
- [ ] 猫の削除（DELETE /api/automation/animals/{id}）
- [ ] 猫の検索（GET /api/automation/animals?query=...）
- [ ] バッチ登録（POST /api/automation/animals/batch）
- [ ] Webhookサポート

## 関連ドキュメント

### 内部ドキュメント
- **MCP Server**: `app/mcp/README.md` - MCPツールからの利用方法
- **Design Document**: `.kiro/specs/claude-mcp-integration/design.md`
- **Requirements**: `.kiro/specs/claude-mcp-integration/requirements.md`

### 外部リソース
- **FastAPI Documentation**: [fastapi.tiangolo.com](https://fastapi.tiangolo.com/)
- **OpenAPI Specification**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## ライセンス

NecoKeeperプロジェクトの一部です。

---

**最終更新**: 2024-11-29
**バージョン**: 1.0.0
**ステータス**: 本番環境対応
