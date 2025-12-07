# Design Document: Automation API

## Overview

Automation APIは、Kiro Hook、MCP、自動化スクリプト専用のAPIエンドポイントです。ユーザー認証（OAuth2）とは完全に分離された固定API Key認証を採用し、セキュリティを保ちながら自動化を実現します。

**Context7参照**: `/fastapi/fastapi` - APIRouter with dependencies, APIKeyHeader, Security

---

## Architecture

### システムアーキテクチャ

```
┌─────────────────────────────────────────────────────────────────┐
│                      NecoKeeper Application                      │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌────────────────────────┐      ┌─────────────────────────┐   │
│  │   User-Facing API      │      │   Automation API        │   │
│  │   /api/v1/*            │      │   /api/automation/*     │   │
│  ├────────────────────────┤      ├─────────────────────────┤   │
│  │ Authentication:        │      │ Authentication:         │   │
│  │ - OAuth2 Password Flow │      │ - API Key (Fixed)       │   │
│  │ - JWT Token            │      │ - X-Automation-Key      │   │
│  │ - HTTPOnly Cookie      │      │                         │   │
│  ├────────────────────────┤      ├─────────────────────────┤   │
│  │ Authorization:         │      │ Authorization:          │   │
│  │ - User Roles           │      │ - Limited Operations    │   │
│  │ - RBAC                 │      │ - No User Management    │   │
│  ├────────────────────────┤      ├─────────────────────────┤   │
│  │ Audit:                 │      │ Audit:                  │   │
│  │ - user_id recorded     │      │ - recorder_id = None    │   │
│  │ - User actions logged  │      │ - device_tag recorded   │   │
│  └────────────────────────┘      └─────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                  Shared Business Logic                   │   │
│  │  - animal_service.py                                     │   │
│  │  - care_log_service.py                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                    Database Layer                        │   │
│  │  - SQLAlchemy Models                                     │   │
│  │  - SQLite / PostgreSQL                                   │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
```

### 認証フロー比較

#### User-Facing API (OAuth2)

```
┌────────┐                ┌────────┐                ┌──────────┐
│ Client │                │ API    │                │ Database │
└───┬────┘                └───┬────┘                └────┬─────┘
    │                         │                          │
    │ POST /api/v1/auth/token │                          │
    │ {email, password}       │                          │
    ├────────────────────────>│                          │
    │                         │ Verify credentials       │
    │                         ├─────────────────────────>│
    │                         │<─────────────────────────┤
    │                         │ Generate JWT             │
    │<────────────────────────┤                          │
    │ {access_token}          │                          │
    │                         │                          │
    │ POST /api/v1/animals    │                          │
    │ Authorization: Bearer   │                          │
    ├────────────────────────>│ Decode JWT               │
    │                         │ Get user from DB         │
    │                         ├─────────────────────────>│
    │                         │<─────────────────────────┤
    │                         │ Check permissions        │
    │                         │ Create animal            │
    │                         ├─────────────────────────>│
    │<────────────────────────┤                          │
    │ {animal}                │                          │
```

#### Automation API (API Key)

```
┌────────┐                ┌────────┐                ┌──────────┐
│ Hook   │                │ API    │                │ Database │
└───┬────┘                └───┬────┘                └────┬─────┘
    │                         │                          │
    │ POST /automation/animals│                          │
    │ X-Automation-Key: xxx   │                          │
    ├────────────────────────>│ Verify API Key           │
    │                         │ (from env var)           │
    │                         │ Create animal            │
    │                         ├─────────────────────────>│
    │<────────────────────────┤                          │
    │ {animal}                │                          │
```

---

## Component Design

### 1. API Key認証モジュール

**ファイル**: `app/auth/api_key.py`

**責務**:
- API Keyの検証
- 環境変数からのAPI Key読み込み
- エラーハンドリング

**依存関係**:
- `fastapi.security.APIKeyHeader`
- `app.config.Settings`

**公開インターフェース**:
```python
async def get_automation_api_key(
    api_key: str | None = Security(automation_api_key_header)
) -> str:
    """API Keyを検証して返す"""

async def verify_automation_api_key_optional(
    api_key: str | None = Security(automation_api_key_header)
) -> str | None:
    """API Keyをオプショナルで検証"""
```

**エラーレスポンス**:
- 401 Unauthorized: API Key未設定
- 403 Forbidden: API Key無効
- 503 Service Unavailable: Automation API無効

### 2. 設定管理モジュール

**ファイル**: `app/config.py`

**追加設定**:
```python
class Settings(BaseSettings):
    # Automation API設定
    enable_automation_api: bool = False
    automation_api_key: str | None = None

    @property
    def is_automation_api_secure(self) -> bool:
        """セキュリティ検証"""
```

**バリデーション**:
- 本番環境: API Key必須、32文字以上
- 開発環境: API Key任意

### 3. Automation APIルーター

**ファイル**: `app/api/automation/__init__.py`

**責務**:
- ルーター設定
- 共通認証の適用
- エラーレスポンス定義

**設定**:
```python
router = APIRouter(
    prefix="/automation",
    tags=["automation"],
    dependencies=[Depends(get_automation_api_key)],  # 全エンドポイントで認証
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        503: {"description": "Service Unavailable"}
    }
)
```

### 4. 猫登録Automation API

**ファイル**: `app/api/automation/animals.py`

**エンドポイント**:
- `POST /api/automation/animals` - 猫登録
- `GET /api/automation/animals/{animal_id}` - 猫情報取得

**特徴**:
- `recorder_id=None` で自動化を示す
- ビジネスロジックは既存サービスを再利用

### 5. 世話記録登録Automation API

**ファイル**: `app/api/automation/care_logs.py`

**エンドポイント**:
- `POST /api/automation/care-logs` - 世話記録登録

**特徴**:
- `recorder_name`, `from_paper`, `device_tag` をリクエストから受け取る
- OCR Import用に最適化

---

## Data Flow

### 世話記録登録フロー（OCR Import）

```
┌──────────────┐
│ PDF Document │
└──────┬───────┘
       │
       │ Phase 1: PDF → Image
       ▼
┌──────────────┐
│ PNG Image    │
└──────┬───────┘
       │
       │ Phase 2: Image → JSON (Kiro Chat)
       ▼
┌──────────────┐
│ JSON File    │
└──────┬───────┘
       │
       │ Phase 3: JSON → Database (Kiro Hook)
       ▼
┌──────────────────────────────────────────────┐
│ Kiro Hook: register_care_logs.py             │
│ - Read JSON file                              │
│ - Get AUTOMATION_API_KEY from env             │
│ - For each record:                            │
│   POST /api/automation/care-logs              │
│   Header: X-Automation-Key: ${API_KEY}        │
│   Body: {animal_id, log_date, ...}           │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ Automation API: /api/automation/care-logs    │
│ - Verify API Key (router-level)              │
│ - Call care_log_service.create_care_log()    │
│ - Return created record                       │
└──────┬───────────────────────────────────────┘
       │
       ▼
┌──────────────────────────────────────────────┐
│ Database: care_log table                     │
│ - animal_id: 12                               │
│ - log_date: 2025-11-24                        │
│ - recorder_name: "OCR自動取込"                │
│ - from_paper: true                            │
│ - device_tag: "OCR-Import"                    │
│ - recorder_id: null (automation indicator)    │
└───────────────────────────────────────────────┘
```

---

## Security Design

### API Key管理

**生成**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**保存**:
- 環境変数: `AUTOMATION_API_KEY`
- `.env`ファイル（gitignore済み）
- 本番環境: Render Dashboard等で設定

**送信**:
- HTTPヘッダー: `X-Automation-Key: ${API_KEY}`
- HTTPS必須（本番環境）

### セキュリティ境界

**分離ポイント**:
1. **エンドポイント分離**: `/api/v1/*` vs `/api/automation/*`
2. **認証方式分離**: OAuth2 vs API Key
3. **権限分離**: ユーザーロール vs 限定操作
4. **監査分離**: user_id vs recorder_id=None

**攻撃対策**:
- API Key漏洩: 環境変数で管理、コードに含めない
- Brute Force: Rate Limiting（オプション）
- MITM: HTTPS必須（本番環境）
- 権限昇格: Automation APIは限定操作のみ

### 監査ログ

**ユーザー操作**:
```json
{
  "action": "create_care_log",
  "user_id": 1,
  "user_email": "admin@example.com",
  "timestamp": "2025-11-24T10:00:00Z"
}
```

**自動化操作**:
```json
{
  "action": "create_care_log",
  "recorder_id": null,
  "recorder_name": "OCR自動取込",
  "device_tag": "OCR-Import",
  "from_paper": true,
  "timestamp": "2025-11-24T10:00:00Z"
}
```

---

## API Specification

### POST /api/automation/animals

**Request**:
```http
POST /api/automation/animals HTTP/1.1
Host: localhost:8000
X-Automation-Key: xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d
Content-Type: application/json

{
  "name": "たま",
  "pattern": "キジトラ",
  "status": "保護中",
  "gender": "male",
  "estimated_age": 2
}
```

**Response (201 Created)**:
```json
{
  "id": 13,
  "name": "たま",
  "pattern": "キジトラ",
  "status": "保護中",
  "gender": "male",
  "estimated_age": 2,
  "created_at": "2025-11-24T10:00:00Z"
}
```

### POST /api/automation/care-logs

**Request**:
```http
POST /api/automation/care-logs HTTP/1.1
Host: localhost:8000
X-Automation-Key: xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d
Content-Type: application/json

{
  "animal_id": 12,
  "log_date": "2025-11-24",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": true,
  "cleaning": false,
  "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
  "recorder_name": "OCR自動取込",
  "from_paper": true,
  "device_tag": "OCR-Import"
}
```

**Response (201 Created)**:
```json
{
  "id": 178,
  "animal_id": 12,
  "log_date": "2025-11-24",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": true,
  "cleaning": false,
  "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
  "recorder_name": "OCR自動取込",
  "recorder_id": null,
  "from_paper": true,
  "device_tag": "OCR-Import",
  "created_at": "2025-11-24T10:00:00Z"
}
```

### Error Responses

**401 Unauthorized**:
```json
{
  "detail": "X-Automation-Key header is required"
}
```

**403 Forbidden**:
```json
{
  "detail": "Invalid Automation API Key"
}
```

**503 Service Unavailable**:
```json
{
  "detail": "Automation API is disabled"
}
```

---

## Testing Strategy

### ユニットテスト

**API Key認証**:
```python
def test_valid_api_key():
    """有効なAPI Keyで認証成功"""

def test_invalid_api_key():
    """無効なAPI Keyで403エラー"""

def test_missing_api_key():
    """API Key未設定で401エラー"""

def test_disabled_automation_api():
    """Automation API無効で503エラー"""
```

**エンドポイント**:
```python
def test_create_animal_automation():
    """猫登録成功"""

def test_create_care_log_automation():
    """世話記録登録成功"""

def test_automation_api_without_auth():
    """認証なしで401エラー"""
```

### 統合テスト

```python
def test_ocr_import_workflow():
    """OCR Import全体フロー"""
    # 1. JSONファイル作成
    # 2. Kiro Hook実行
    # 3. Automation API呼び出し
    # 4. データベース確認
```

### セキュリティテスト

```python
def test_api_key_isolation():
    """API KeyでユーザーAPIにアクセスできないこと"""

def test_oauth2_isolation():
    """OAuth2でAutomation APIにアクセスできないこと"""

def test_production_api_key_validation():
    """本番環境でAPI Key長さ検証"""
```

---

## Deployment Considerations

### 環境変数設定

**開発環境**:
```bash
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=dev-test-key-not-for-production
```

**本番環境（Render）**:
```bash
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=<32文字以上のランダム文字列>
```

### セキュリティチェックリスト

- [ ] API Keyが32文字以上
- [ ] API Keyが環境変数で管理
- [ ] HTTPS接続（本番環境）
- [ ] Rate Limiting設定（オプション）
- [ ] 監査ログ有効化
- [ ] エラーメッセージに機密情報なし

---

## Migration Path

### Phase 1: 実装（POC）
- API Key認証モジュール
- Automation APIルーター
- 世話記録登録エンドポイント
- Kiro Hook更新

### Phase 2: 拡張（本番移行）
- 猫登録エンドポイント
- Rate Limiting
- 詳細な監査ログ
- API使用統計

### Phase 3: 最適化（運用）
- API Key rotation
- 複数API Key対応
- Scope-based permissions
- Webhook通知

---

**最終更新**: 2025-11-24
**Context7参照**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
