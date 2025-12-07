# Requirements Document: Automation API

## Introduction

Kiro Hook、MCP、自動化スクリプト専用のAPIエンドポイントを実装します。ユーザー認証（OAuth2）とは完全に分離された固定API Key認証を採用し、セキュリティを保ちながら自動化を実現します。

**設計原則**:
- **完全分離**: ユーザー認証とAPI Key認証を完全に分離
- **専用エンドポイント**: `/api/automation/*` で独立したAPIルート
- **最小権限**: 猫登録と世話記録登録のみを許可
- **監査可能**: すべての操作をログ記録

**Context7参照**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader

---

## Glossary

- **Automation API**: Kiro Hook、MCP、自動化スクリプト専用のAPIエンドポイント
- **API Key**: 固定の認証キー。環境変数で管理され、ヘッダーで送信される
- **X-Automation-Key**: API Keyを送信するHTTPヘッダー名
- **OAuth2**: ユーザー向けAPIで使用される既存の認証方式
- **デュアル認証**: ユーザー認証とAPI Key認証の2つの認証方式を並行運用
- **最小権限の原則**: API Keyは必要最小限の操作のみを許可

---

## Requirements

### Requirement 1: API Key認証モジュール

**User Story:** As a システム管理者, I want to implement API Key authentication separate from user authentication, so that automation tools can access the API securely without user credentials.

#### Acceptance Criteria

1. WHEN API Key authentication module is created THEN it SHALL use FastAPI's `APIKeyHeader` security scheme
2. WHEN API Key is validated THEN it SHALL check against `AUTOMATION_API_KEY` environment variable
3. WHEN API Key is missing THEN it SHALL return 401 Unauthorized with `WWW-Authenticate: ApiKey` header
4. WHEN API Key is invalid THEN it SHALL return 403 Forbidden
5. WHEN Automation API is disabled THEN it SHALL return 503 Service Unavailable
6. WHEN API Key is validated successfully THEN it SHALL return the validated key string
7. WHEN API Key validation is optional THEN it SHALL return None without raising an exception for invalid keys

### Requirement 2: 設定管理の拡張

**User Story:** As a システム管理者, I want to configure Automation API settings via environment variables, so that I can enable/disable the feature and set secure API keys.

#### Acceptance Criteria

1. WHEN application starts THEN it SHALL load `ENABLE_AUTOMATION_API` environment variable (default: false)
2. WHEN application starts THEN it SHALL load `AUTOMATION_API_KEY` environment variable
3. WHEN Automation API is enabled in production THEN it SHALL validate that `AUTOMATION_API_KEY` is set
4. WHEN Automation API is enabled in production THEN it SHALL validate that `AUTOMATION_API_KEY` is at least 32 characters
5. WHEN API Key validation fails THEN it SHALL raise a ValueError with descriptive message
6. WHEN settings are accessed THEN it SHALL provide `is_automation_api_secure` property for validation

### Requirement 3: Automation APIルーターの作成

**User Story:** As a 開発者, I want to create a dedicated API router for automation endpoints, so that all automation operations are grouped and secured with API Key authentication.

#### Acceptance Criteria

1. WHEN Automation API router is created THEN it SHALL use `/api/automation` prefix
2. WHEN Automation API router is created THEN it SHALL apply API Key authentication to all endpoints via router-level dependencies
3. WHEN Automation API router is created THEN it SHALL be tagged with "automation" for OpenAPI documentation
4. WHEN Automation API router is created THEN it SHALL define custom error responses (401, 403, 503)
5. WHEN Automation API router is included in main app THEN it SHALL be separate from `/api/v1/*` routes

### Requirement 4: 猫登録Automation API

**User Story:** As a Kiro Hook, I want to register a new cat via Automation API, so that I can automate cat registration without user authentication.

#### Acceptance Criteria

1. WHEN POST `/api/automation/animals` is called with valid API Key THEN it SHALL create a new cat record
2. WHEN cat is created via Automation API THEN it SHALL set `recorder_id` to None to indicate automation
3. WHEN cat creation fails THEN it SHALL return 500 Internal Server Error with error details
4. WHEN GET `/api/automation/animals/{animal_id}` is called THEN it SHALL return cat information
5. WHEN cat is not found THEN it SHALL return 404 Not Found
6. WHEN API Key is missing or invalid THEN it SHALL return 401 or 403 before executing business logic

### Requirement 5: 世話記録登録Automation API

**User Story:** As a OCR Import Hook, I want to register care logs via Automation API, so that I can automate care log registration from scanned documents.

#### Acceptance Criteria

1. WHEN POST `/api/automation/care-logs` is called with valid API Key THEN it SHALL create a new care log record
2. WHEN care log is created via Automation API THEN it SHALL accept `recorder_name` from request body (e.g., "OCR自動取込")
3. WHEN care log is created via Automation API THEN it SHALL accept `from_paper` flag from request body
4. WHEN care log is created via Automation API THEN it SHALL accept `device_tag` from request body (e.g., "OCR-Import")
5. WHEN care log creation fails THEN it SHALL return 500 Internal Server Error with error details
6. WHEN API Key is missing or invalid THEN it SHALL return 401 or 403 before executing business logic

### Requirement 6: メインアプリケーションへの統合

**User Story:** As a システム管理者, I want to integrate Automation API into the main application, so that it runs alongside existing user APIs without conflicts.

#### Acceptance Criteria

1. WHEN application starts THEN it SHALL include Automation API router with `/api` prefix
2. WHEN application starts THEN it SHALL maintain existing `/api/v1/*` routes with OAuth2 authentication
3. WHEN application starts THEN it SHALL not apply OAuth2 authentication to `/api/automation/*` routes
4. WHEN application starts THEN it SHALL not apply API Key authentication to `/api/v1/*` routes
5. WHEN OpenAPI documentation is generated THEN it SHALL show both authentication schemes separately

### Requirement 7: セキュリティ対策

**User Story:** As a セキュリティ担当者, I want to ensure Automation API is secure, so that unauthorized access is prevented and all operations are auditable.

#### Acceptance Criteria

1. WHEN API Key is generated THEN it SHALL be at least 32 characters using `secrets.token_urlsafe(32)`
2. WHEN API Key is stored THEN it SHALL be stored in environment variables, not in code
3. WHEN API Key is transmitted THEN it SHALL be sent via HTTPS in production
4. WHEN Automation API operation is performed THEN it SHALL be logged with "automation" indicator
5. WHEN Automation API is enabled in production THEN it SHALL enforce minimum key length validation
6. WHEN Automation API is disabled THEN it SHALL return 503 for all automation endpoints
7. WHEN rate limiting is implemented (optional) THEN it SHALL limit requests per minute per IP address

### Requirement 8: Kiro Hook統合

**User Story:** As a Kiro Hook, I want to use Automation API for care log registration, so that I can register OCR-extracted data without OAuth2 authentication flow.

#### Acceptance Criteria

1. WHEN `register_care_logs.py` is updated THEN it SHALL use `/api/automation/care-logs` endpoint
2. WHEN `register_care_logs.py` sends request THEN it SHALL include `X-Automation-Key` header
3. WHEN `register_care_logs.py` reads API Key THEN it SHALL read from `AUTOMATION_API_KEY` environment variable
4. WHEN authentication fails THEN it SHALL log error and display user-friendly message
5. WHEN API Key is not set THEN it SHALL display setup instructions to user

### Requirement 9: 環境変数テンプレート更新

**User Story:** As a 新規開発者, I want to see Automation API configuration in `.env.example`, so that I can set up the feature correctly.

#### Acceptance Criteria

1. WHEN `.env.example` is viewed THEN it SHALL include `ENABLE_AUTOMATION_API` with description
2. WHEN `.env.example` is viewed THEN it SHALL include `AUTOMATION_API_KEY` with generation instructions
3. WHEN `.env.example` is viewed THEN it SHALL include security warnings for production use
4. WHEN `.env.example` is viewed THEN it SHALL include example API Key generation command

### Requirement 10: ドキュメント作成

**User Story:** As a 開発者, I want to read documentation about Automation API, so that I can understand how to use it correctly.

#### Acceptance Criteria

1. WHEN documentation is created THEN it SHALL explain the dual authentication architecture
2. WHEN documentation is created THEN it SHALL provide API Key generation instructions
3. WHEN documentation is created THEN it SHALL include curl examples for each endpoint
4. WHEN documentation is created THEN it SHALL include Python examples for Kiro Hook usage
5. WHEN documentation is created THEN it SHALL explain security considerations
6. WHEN documentation is created THEN it SHALL include troubleshooting guide

---

## Technical Notes

### API Key生成方法

```bash
# 強力なAPI Keyを生成（32文字以上）
python -c "import secrets; print('AUTOMATION_API_KEY=' + secrets.token_urlsafe(32))"
```

### 環境変数設定例

```bash
# .env
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d
```

### エンドポイント一覧

| エンドポイント | メソッド | 認証 | 説明 |
|--------------|---------|------|------|
| `/api/v1/animals` | POST | OAuth2 | 猫登録（ユーザー） |
| `/api/automation/animals` | POST | API Key | 猫登録（自動化） |
| `/api/v1/care-logs` | POST | OAuth2 | 世話記録登録（ユーザー） |
| `/api/automation/care-logs` | POST | API Key | 世話記録登録（自動化） |

### セキュリティ境界

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  /api/v1/*           │    │  /api/automation/*       │  │
│  │  ユーザー向けAPI      │    │  Hook/MCP専用API         │  │
│  ├──────────────────────┤    ├──────────────────────────┤  │
│  │ 認証: OAuth2 + JWT   │    │ 認証: API Key (固定)     │  │
│  │ Cookie: HTTPOnly     │    │ Header: X-Automation-Key │  │
│  │ 対象: 管理画面       │    │ 対象: Hook/MCP           │  │
│  │ 権限: ユーザーロール │    │ 権限: 限定操作のみ       │  │
│  │ 監査: user_id記録    │    │ 監査: automation記録     │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### 実装優先度

1. **High Priority** (POC必須):
   - API Key認証モジュール
   - 世話記録登録Automation API
   - Kiro Hook統合

2. **Medium Priority** (POC推奨):
   - 猫登録Automation API
   - 設定管理の拡張
   - 環境変数テンプレート更新

3. **Low Priority** (本番移行時):
   - Rate Limiting
   - 詳細な監査ログ
   - API使用統計

---

## Success Criteria

- すべてのAcceptance Criteriaが満たされている
- Kiro HookからAutomation APIで世話記録を登録できる
- ユーザー認証とAPI Key認証が独立して動作する
- 本番環境でのセキュリティ検証が通過する
- ドキュメントが完成し、レビュー済み
- テストカバレッジが70%以上

---

**最終更新**: 2025-11-24
**Context7参照**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
