# Automation API ガイド

## 概要

Automation APIは、Kiro Hook、MCP、自動化スクリプト専用のAPIエンドポイントです。ユーザー認証（OAuth2）とは完全に分離された固定API Key認証を採用し、セキュリティを保ちながら自動化を実現します。

**主な特徴**:
- 🔐 **固定API Key認証**: 環境変数で管理される安全な認証方式
- 🔄 **完全分離アーキテクチャ**: ユーザーAPIと独立した認証・認可
- 📝 **限定操作**: 猫登録と世話記録登録のみを許可
- 📊 **監査可能**: すべての操作をログ記録

---

## 目次

1. [デュアル認証アーキテクチャ](#デュアル認証アーキテクチャ)
2. [セットアップ](#セットアップ)
3. [API Key生成](#api-key生成)
4. [エンドポイント一覧](#エンドポイント一覧)
5. [使用例](#使用例)
6. [セキュリティ考慮事項](#セキュリティ考慮事項)
7. [トラブルシューティング](#トラブルシューティング)

---

## デュアル認証アーキテクチャ

NecoKeeperは、2つの独立した認証方式を並行運用しています。

### アーキテクチャ図

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
└─────────────────────────────────────────────────────────────────┘
```

### 認証方式の比較

| 項目 | User-Facing API | Automation API |
|------|----------------|----------------|
| **エンドポイント** | `/api/v1/*` | `/api/automation/*` |
| **認証方式** | OAuth2 + JWT | API Key (固定) |
| **認証ヘッダー** | `Authorization: Bearer <token>` | `X-Automation-Key: <key>` |
| **対象ユーザー** | 管理画面ユーザー | Hook/MCP/スクリプト |
| **権限** | ユーザーロールベース | 限定操作のみ |
| **監査ログ** | `user_id`記録 | `recorder_id=null` |

### セキュリティ境界

**完全分離の原則**:
1. **エンドポイント分離**: 異なるURLパスで完全に分離
2. **認証方式分離**: OAuth2とAPI Keyは互換性なし
3. **権限分離**: Automation APIは限定操作のみ許可
4. **監査分離**: 操作元を明確に識別可能

---

## セットアップ

### 1. 環境変数の設定

`.env`ファイルに以下を追加します：

```bash
# Automation API設定
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=<生成したAPI Key>
```

### 2. API Keyの生成

次のセクションを参照してください。

### 3. アプリケーションの再起動

```bash
# 開発環境
uvicorn app.main:app --reload

# 本番環境（Docker）
docker-compose restart
```

---

## API Key生成

### 推奨方法: Pythonスクリプト

**32文字以上の強力なAPI Keyを生成**:

```bash
python -c "import secrets; print('AUTOMATION_API_KEY=' + secrets.token_urlsafe(32))"
```

**出力例**:
```
AUTOMATION_API_KEY=xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d
```

### 本番環境での要件

- ✅ **最小長**: 32文字以上（必須）
- ✅ **ランダム性**: `secrets.token_urlsafe()`を使用
- ✅ **保存場所**: 環境変数のみ（コードに含めない）
- ✅ **HTTPS**: 本番環境では必須

### 開発環境での設定

開発環境では短いキーも許可されますが、本番環境と同じ形式を推奨：

```bash
# 開発環境用（推奨しない）
AUTOMATION_API_KEY=dev-test-key

# 開発環境用（推奨）
AUTOMATION_API_KEY=dev-xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM
```

---

## エンドポイント一覧

### 1. 猫登録 API

**エンドポイント**: `POST /api/automation/animals`

**説明**: 新しい猫を登録します。

**リクエストヘッダー**:
```
X-Automation-Key: <your-api-key>
Content-Type: application/json
```

**リクエストボディ**:
```json
{
  "name": "たま",
  "pattern": "キジトラ",
  "status": "保護中",
  "gender": "male",
  "estimated_age": 2,
  "description": "人懐っこい性格"
}
```

**レスポンス** (201 Created):
```json
{
  "id": 13,
  "name": "たま",
  "pattern": "キジトラ",
  "status": "保護中",
  "gender": "male",
  "estimated_age": 2,
  "description": "人懐っこい性格",
  "created_at": "2025-11-24T10:00:00Z"
}
```

### 2. 猫情報取得 API

**エンドポイント**: `GET /api/automation/animals/{animal_id}`

**説明**: 指定したIDの猫情報を取得します。

**リクエストヘッダー**:
```
X-Automation-Key: <your-api-key>
```

**レスポンス** (200 OK):
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

### 3. 世話記録登録 API

**エンドポイント**: `POST /api/automation/care-logs`

**説明**: 世話記録を登録します（OCR Import用に最適化）。

**リクエストヘッダー**:
```
X-Automation-Key: <your-api-key>
Content-Type: application/json
```

**リクエストボディ**:
```json
{
  "animal_id": 12,
  "log_date": "2025-11-24",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": true,
  "defecation": true,
  "cleaning": false,
  "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
  "recorder_name": "OCR自動取込",
  "from_paper": true,
  "device_tag": "OCR-Import"
}
```

**レスポンス** (201 Created):
```json
{
  "id": 178,
  "animal_id": 12,
  "log_date": "2025-11-24",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": true,
  "defecation": true,
  "cleaning": false,
  "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
  "recorder_name": "OCR自動取込",
  "recorder_id": null,
  "from_paper": true,
  "device_tag": "OCR-Import",
  "created_at": "2025-11-24T10:00:00Z"
}
```

### エラーレスポンス

#### 401 Unauthorized
```json
{
  "detail": "X-Automation-Key header is required"
}
```

#### 403 Forbidden
```json
{
  "detail": "Invalid Automation API Key"
}
```

#### 404 Not Found
```json
{
  "detail": "Animal not found"
}
```

#### 503 Service Unavailable
```json
{
  "detail": "Automation API is disabled"
}
```

---

## 使用例

### curl コマンド例

#### 1. 猫を登録

```bash
curl -X POST "http://localhost:8000/api/automation/animals" \
  -H "X-Automation-Key: xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "たま",
    "pattern": "キジトラ",
    "status": "保護中",
    "gender": "male",
    "estimated_age": 2
  }'
```

#### 2. 猫情報を取得

```bash
curl -X GET "http://localhost:8000/api/automation/animals/13" \
  -H "X-Automation-Key: xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d"
```

#### 3. 世話記録を登録

```bash
curl -X POST "http://localhost:8000/api/automation/care-logs" \
  -H "X-Automation-Key: xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d" \
  -H "Content-Type: application/json" \
  -d '{
    "animal_id": 12,
    "log_date": "2025-11-24",
    "time_slot": "morning",
    "appetite": 5,
    "energy": 5,
    "urination": true,
    "defecation": true,
    "cleaning": false,
    "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
    "recorder_name": "OCR自動取込",
    "from_paper": true,
    "device_tag": "OCR-Import"
  }'
```

### Python コード例

#### 基本的な使用方法

```python
import os
import requests
from datetime import date

# 環境変数からAPI Keyを取得
API_KEY = os.getenv("AUTOMATION_API_KEY")
BASE_URL = "http://localhost:8000/api/automation"

# 共通ヘッダー
headers = {
    "X-Automation-Key": API_KEY,
    "Content-Type": "application/json"
}

# 1. 猫を登録
def create_animal(name: str, pattern: str, status: str = "保護中"):
    """猫を登録"""
    response = requests.post(
        f"{BASE_URL}/animals",
        headers=headers,
        json={
            "name": name,
            "pattern": pattern,
            "status": status,
            "gender": "unknown",
            "estimated_age": 0
        }
    )
    response.raise_for_status()
    return response.json()

# 2. 猫情報を取得
def get_animal(animal_id: int):
    """猫情報を取得"""
    response = requests.get(
        f"{BASE_URL}/animals/{animal_id}",
        headers=headers
    )
    response.raise_for_status()
    return response.json()

# 3. 世話記録を登録
def create_care_log(animal_id: int, log_date: date, **kwargs):
    """世話記録を登録"""
    response = requests.post(
        f"{BASE_URL}/care-logs",
        headers=headers,
        json={
            "animal_id": animal_id,
            "log_date": log_date.isoformat(),
            "time_slot": kwargs.get("time_slot", "morning"),
            "appetite": kwargs.get("appetite", 5),
            "energy": kwargs.get("energy", 5),
            "urination": kwargs.get("urination", False),
            "defecation": kwargs.get("defecation", False),
            "cleaning": kwargs.get("cleaning", False),
            "memo": kwargs.get("memo", ""),
            "recorder_name": kwargs.get("recorder_name", "自動登録"),
            "from_paper": kwargs.get("from_paper", False),
            "device_tag": kwargs.get("device_tag", "Python-Script")
        }
    )
    response.raise_for_status()
    return response.json()

# 使用例
if __name__ == "__main__":
    # 猫を登録
    animal = create_animal("たま", "キジトラ")
    print(f"Created animal: {animal['id']}")

    # 世話記録を登録
    care_log = create_care_log(
        animal_id=animal["id"],
        log_date=date.today(),
        appetite=5,
        energy=5,
        urination=True,
        memo="元気です"
    )
    print(f"Created care log: {care_log['id']}")
```

#### エラーハンドリング付き

```python
import os
import requests
from typing import Dict, Any

class AutomationAPIClient:
    """Automation API クライアント"""

    def __init__(self, base_url: str = "http://localhost:8000/api/automation"):
        self.base_url = base_url
        self.api_key = os.getenv("AUTOMATION_API_KEY")

        if not self.api_key:
            raise ValueError("AUTOMATION_API_KEY environment variable is not set")

        self.headers = {
            "X-Automation-Key": self.api_key,
            "Content-Type": "application/json"
        }

    def _handle_response(self, response: requests.Response) -> Dict[Any, Any]:
        """レスポンスを処理"""
        try:
            response.raise_for_status()
            return response.json()
        except requests.exceptions.HTTPError as e:
            if response.status_code == 401:
                raise Exception("API Key is missing or invalid (401)")
            elif response.status_code == 403:
                raise Exception("API Key is invalid (403)")
            elif response.status_code == 404:
                raise Exception("Resource not found (404)")
            elif response.status_code == 503:
                raise Exception("Automation API is disabled (503)")
            else:
                raise Exception(f"HTTP Error: {e}")

    def create_animal(self, data: Dict[str, Any]) -> Dict[Any, Any]:
        """猫を登録"""
        response = requests.post(
            f"{self.base_url}/animals",
            headers=self.headers,
            json=data
        )
        return self._handle_response(response)

    def get_animal(self, animal_id: int) -> Dict[Any, Any]:
        """猫情報を取得"""
        response = requests.get(
            f"{self.base_url}/animals/{animal_id}",
            headers=self.headers
        )
        return self._handle_response(response)

    def create_care_log(self, data: Dict[str, Any]) -> Dict[Any, Any]:
        """世話記録を登録"""
        response = requests.post(
            f"{self.base_url}/care-logs",
            headers=self.headers,
            json=data
        )
        return self._handle_response(response)

# 使用例
if __name__ == "__main__":
    try:
        client = AutomationAPIClient()

        # 猫を登録
        animal = client.create_animal({
            "name": "たま",
            "pattern": "キジトラ",
            "status": "保護中",
            "gender": "male",
            "estimated_age": 2
        })
        print(f"✅ Created animal: {animal['id']}")

        # 世話記録を登録
        care_log = client.create_care_log({
            "animal_id": animal["id"],
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": True,
            "recorder_name": "Python Script",
            "device_tag": "automation-script"
        })
        print(f"✅ Created care log: {care_log['id']}")

    except Exception as e:
        print(f"❌ Error: {e}")
```

#### Kiro Hook での使用例

```python
#!/usr/bin/env python3
"""
Kiro Hook: 世話記録を一括登録

使用方法:
  python register_care_logs.py <json_file>
"""

import os
import sys
import json
import requests
from pathlib import Path

def register_care_logs(json_file: Path):
    """JSONファイルから世話記録を一括登録"""

    # API Key取得
    api_key = os.getenv("AUTOMATION_API_KEY")
    if not api_key:
        print("❌ Error: AUTOMATION_API_KEY is not set")
        print("Please set the environment variable:")
        print("  export AUTOMATION_API_KEY=<your-api-key>")
        sys.exit(1)

    # JSONファイル読み込み
    with open(json_file) as f:
        care_logs = json.load(f)

    # API設定
    base_url = os.getenv("API_BASE_URL", "http://localhost:8000")
    headers = {
        "X-Automation-Key": api_key,
        "Content-Type": "application/json"
    }

    # 一括登録
    success_count = 0
    error_count = 0

    for log in care_logs:
        try:
            response = requests.post(
                f"{base_url}/api/automation/care-logs",
                headers=headers,
                json=log
            )
            response.raise_for_status()
            success_count += 1
            print(f"✅ Registered: {log['animal_id']} - {log['log_date']}")
        except Exception as e:
            error_count += 1
            print(f"❌ Failed: {log['animal_id']} - {log['log_date']}: {e}")

    # 結果表示
    print(f"\n📊 Results: {success_count} success, {error_count} errors")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python register_care_logs.py <json_file>")
        sys.exit(1)

    json_file = Path(sys.argv[1])
    if not json_file.exists():
        print(f"❌ Error: File not found: {json_file}")
        sys.exit(1)

    register_care_logs(json_file)
```

---

## セキュリティ考慮事項

### 1. API Key管理

#### ✅ 推奨事項

- **環境変数で管理**: `.env`ファイルまたはシステム環境変数
- **Gitignore**: `.env`ファイルは必ずgitignoreに追加
- **強力なキー**: 32文字以上のランダム文字列
- **定期的なローテーション**: 3-6ヶ月ごとにキーを更新

#### ❌ 禁止事項

- **コードに埋め込み**: ソースコードに直接記述しない
- **公開リポジトリ**: GitHubなどに誤ってプッシュしない
- **短いキー**: 開発環境でも強力なキーを使用
- **共有**: API Keyを複数人で共有しない

### 2. ネットワークセキュリティ

#### 本番環境

- ✅ **HTTPS必須**: すべての通信をHTTPSで暗号化
- ✅ **ファイアウォール**: 必要なポートのみ開放
- ✅ **IP制限**: 可能であればアクセス元IPを制限

#### 開発環境

- ⚠️ **HTTP許可**: ローカル開発のみ
- ⚠️ **localhost**: 外部からアクセスできないように設定

### 3. 権限管理

#### Automation APIの制限

- ✅ **限定操作**: 猫登録と世話記録登録のみ
- ✅ **ユーザー管理不可**: ユーザー情報の取得・変更は不可
- ✅ **削除操作不可**: データの削除は不可

#### 監査ログ

- ✅ **操作記録**: すべての操作をログに記録
- ✅ **識別可能**: `recorder_id=null`で自動化操作を識別
- ✅ **device_tag**: 操作元デバイスを記録

### 4. エラーハンドリング

#### セキュアなエラーメッセージ

```python
# ✅ 推奨: 詳細を隠す
{
  "detail": "Invalid Automation API Key"
}

# ❌ 非推奨: 詳細を露出
{
  "detail": "API Key 'abc123' does not match expected key 'xyz789'"
}
```

### 5. Rate Limiting（オプション）

将来的な実装推奨：

```python
# slowapi を使用したRate Limiting
from slowapi import Limiter
from slowapi.util import get_remote_address

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/automation/care-logs")
@limiter.limit("100/minute")
def create_care_log(...):
  pass
```

---

## トラブルシューティング

### 1. 401 Unauthorized エラー

**症状**:
```json
{
  "detail": "X-Automation-Key header is required"
}
```

**原因**:
- API Keyヘッダーが送信されていない

**解決方法**:
```bash
# ヘッダーを追加
curl -H "X-Automation-Key: <your-key>" ...
```

### 2. 403 Forbidden エラー

**症状**:
```json
{
  "detail": "Invalid Automation API Key"
}
```

**原因**:
- API Keyが間違っている
- 環境変数が設定されていない

**解決方法**:
```bash
# 環境変数を確認
echo $AUTOMATION_API_KEY

# 環境変数を設定
export AUTOMATION_API_KEY=<your-key>

# アプリケーションを再起動
uvicorn app.main:app --reload
```

### 3. 503 Service Unavailable エラー

**症状**:
```json
{
  "detail": "Automation API is disabled"
}
```

**原因**:
- `ENABLE_AUTOMATION_API`が`false`または未設定

**解決方法**:
```bash
# .envファイルに追加
echo "ENABLE_AUTOMATION_API=true" >> .env

# アプリケーションを再起動
uvicorn app.main:app --reload
```

### 4. 本番環境でAPI Keyが短すぎるエラー

**症状**:
```
ValueError: Automation API Key must be at least 32 characters in production
```

**原因**:
- 本番環境でAPI Keyが32文字未満

**解決方法**:
```bash
# 強力なAPI Keyを生成
python -c "import secrets; print(secrets.token_urlsafe(32))"

# 環境変数を更新
export AUTOMATION_API_KEY=<generated-key>
```

### 5. Kiro Hookで環境変数が読み込まれない

**症状**:
- `AUTOMATION_API_KEY is not set`エラー

**原因**:
- Kiro Hookの実行環境で環境変数が設定されていない

**解決方法**:

#### 方法1: .envファイルを使用

```python
from dotenv import load_dotenv
load_dotenv()

api_key = os.getenv("AUTOMATION_API_KEY")
```

#### 方法2: Kiro設定で環境変数を設定

`.kiro/hooks/config.json`:
```json
{
  "hooks": {
    "register_care_logs": {
      "env": {
        "AUTOMATION_API_KEY": "${AUTOMATION_API_KEY}"
      }
    }
  }
}
```

### 6. CORS エラー（ブラウザから直接アクセス）

**症状**:
```
Access to fetch at 'http://localhost:8000/api/automation/animals' from origin 'http://localhost:3000' has been blocked by CORS policy
```

**原因**:
- Automation APIはブラウザからの直接アクセスを想定していない

**解決方法**:
- サーバーサイドスクリプトから呼び出す
- または、CORSを有効化（非推奨）

### 7. デバッグモード

**詳細なログを有効化**:

```bash
# ログレベルを設定
export LOG_LEVEL=DEBUG

# アプリケーションを起動
uvicorn app.main:app --reload --log-level debug
```

**ログ確認**:
```bash
# リアルタイムでログを確認
tail -f logs/app.log

# エラーログのみ確認
grep "ERROR" logs/app.log
```

---

## よくある質問（FAQ）

### Q1: User-Facing APIとAutomation APIの違いは？

**A**: 認証方式と対象ユーザーが異なります。

- **User-Facing API**: OAuth2認証、管理画面ユーザー向け
- **Automation API**: API Key認証、Hook/MCP/スクリプト向け

### Q2: API Keyを複数発行できますか？

**A**: 現在のバージョンでは1つのAPI Keyのみサポートしています。将来的に複数キー対応を予定しています。

### Q3: API Keyの有効期限はありますか？

**A**: 現在のバージョンでは有効期限はありません。定期的な手動ローテーションを推奨します。

### Q4: Rate Limitingは実装されていますか？

**A**: 現在のバージョンでは未実装です。Phase 3で実装予定です。

### Q5: Automation APIで削除操作はできますか？

**A**: セキュリティ上の理由から、削除操作は許可していません。

---

## 次のステップ

1. **API Keyを生成**: [API Key生成](#api-key生成)を参照
2. **環境変数を設定**: `.env`ファイルに追加
3. **テスト実行**: curlコマンドで動作確認
4. **Kiro Hookに統合**: Pythonスクリプトを作成
5. **本番環境デプロイ**: セキュリティチェックリストを確認

---

## 関連ドキュメント

- [OCR Import Guide](./ocr-import-guide.md) - OCR自動取込の詳細
- [API Reference](../app/api/automation/) - APIソースコード
- [Requirements](../.kiro/specs/automation-api/requirements.md) - 要件定義
- [Design](../.kiro/specs/automation-api/design.md) - 設計書

---

**最終更新**: 2025-11-24
**バージョン**: 1.0.0
**Context7参照**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
