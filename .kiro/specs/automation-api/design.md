# Design Document: Automation API

## Overview

Automation API is a dedicated API endpoint for Kiro Hook, MCP, and automation scripts. It adopts fixed API Key authentication completely separated from user authentication (OAuth2) to achieve automation while maintaining security.

**Context7 Reference**: `/fastapi/fastapi` - APIRouter with dependencies, APIKeyHeader, Security

---

## Architecture

### System Architecture

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

### Authentication Flow Comparison

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

### 1. API Key Authentication Module

**File**: `app/auth/api_key.py`

**Responsibilities**:
- API Key validation
- API Key loading from environment variables
- Error handling

**Dependencies**:
- `fastapi.security.APIKeyHeader`
- `app.config.Settings`

**Public Interface**:
```python
def get_automation_api_key(
    api_key: str | None = Security(automation_api_key_header)
) -> str:
    """Validate and return API Key"""

def verify_automation_api_key_optional(
    api_key: str | None = Security(automation_api_key_header)
) -> str | None:
    """Optionally validate API Key"""
```

**Error Responses**:
- 401 Unauthorized: API Key not set
- 403 Forbidden: Invalid API Key
- 503 Service Unavailable: Automation API disabled

### 2. Configuration Management Module

**File**: `app/config.py`

**Additional Settings**:
```python
class Settings(BaseSettings):
    # Automation API settings
    enable_automation_api: bool = False
    automation_api_key: str | None = None

    @property
    def is_automation_api_secure(self) -> bool:
        """Security validation"""
```

**Validation**:
- Production: API Key required, 32+ characters
- Development: API Key optional

### 3. Automation API Router

**File**: `app/api/automation/__init__.py`

**Responsibilities**:
- Router configuration
- Common authentication application
- Error response definition

**Configuration**:
```python
router = APIRouter(
    prefix="/automation",
    tags=["automation"],
    dependencies=[Depends(get_automation_api_key)],  # Auth for all endpoints
    responses={
        401: {"description": "Unauthorized"},
        403: {"description": "Forbidden"},
        503: {"description": "Service Unavailable"}
    }
)
```

### 4. Cat Registration Automation API

**File**: `app/api/automation/animals.py`

**Endpoints**:
- `POST /api/automation/animals` - Cat registration
- `GET /api/automation/animals/{animal_id}` - Get cat information

**Features**:
- `recorder_id=None` indicates automation
- Reuses existing business logic services

### 5. Care Log Registration Automation API

**File**: `app/api/automation/care_logs.py`

**Endpoints**:
- `POST /api/automation/care-logs` - Care log registration

**Features**:
- Accepts `recorder_name`, `from_paper`, `device_tag` from request
- Optimized for OCR Import

---

## Data Flow

### Care Log Registration Flow (OCR Import)

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
│ - recorder_name: "OCR Auto Import"           │
│ - from_paper: true                            │
│ - device_tag: "OCR-Import"                    │
│ - recorder_id: null (automation indicator)    │
└───────────────────────────────────────────────┘
```

---

## Security Design

### API Key Management

**Generation**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**Storage**:
- Environment variable: `AUTOMATION_API_KEY`
- `.env` file (gitignored)
- Production: Set via Render Dashboard, etc.

**Transmission**:
- HTTP Header: `X-Automation-Key: ${API_KEY}`
- HTTPS required (production)

### Security Boundaries

**Separation Points**:
1. **Endpoint Separation**: `/api/v1/*` vs `/api/automation/*`
2. **Authentication Separation**: OAuth2 vs API Key
3. **Permission Separation**: User roles vs Limited operations
4. **Audit Separation**: user_id vs recorder_id=None

**Attack Mitigation**:
- API Key Leakage: Manage via environment variables, not in code
- Brute Force: Rate Limiting (optional)
- MITM: HTTPS required (production)
- Privilege Escalation: Automation API limited operations only

### Audit Logs

**User Operations**:
```json
{
  "action": "create_care_log",
  "user_id": 1,
  "user_email": "admin@example.com",
  "timestamp": "2025-11-24T10:00:00Z"
}
```

**Automation Operations**:
```json
{
  "action": "create_care_log",
  "recorder_id": null,
  "recorder_name": "OCR Auto Import",
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
  "name": "Tama",
  "pattern": "Tabby",
  "status": "Under Protection",
  "gender": "male",
  "estimated_age": 2
}
```

**Response (201 Created)**:
```json
{
  "id": 13,
  "name": "Tama",
  "pattern": "Tabby",
  "status": "Under Protection",
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
  "memo": "Defecation: Yes, Vomiting: No, Medication: No",
  "recorder_name": "OCR Auto Import",
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
  "memo": "Defecation: Yes, Vomiting: No, Medication: No",
  "recorder_name": "OCR Auto Import",
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

### Unit Tests

**API Key Authentication**:
```python
def test_valid_api_key():
    """Authentication succeeds with valid API Key"""

def test_invalid_api_key():
    """403 error with invalid API Key"""

def test_missing_api_key():
    """401 error when API Key not set"""

def test_disabled_automation_api():
    """503 error when Automation API disabled"""
```

**Endpoints**:
```python
def test_create_animal_automation():
    """Cat registration succeeds"""

def test_create_care_log_automation():
    """Care log registration succeeds"""

def test_automation_api_without_auth():
    """401 error without authentication"""
```

### Integration Tests

```python
def test_ocr_import_workflow():
    """Complete OCR Import flow"""
    # 1. Create JSON file
    # 2. Execute Kiro Hook
    # 3. Call Automation API
    # 4. Verify database
```

### Security Tests

```python
def test_api_key_isolation():
    """Cannot access user API with API Key"""

def test_oauth2_isolation():
    """Cannot access Automation API with OAuth2"""

def test_production_api_key_validation():
    """Validate API Key length in production"""
```

---

## Deployment Considerations

### Environment Variable Configuration

**Development**:
```bash
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=dev-test-key-not-for-production
```

**Production (Render)**:
```bash
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=<random string 32+ characters>
```

### Security Checklist

- [ ] API Key is 32+ characters
- [ ] API Key managed via environment variables
- [ ] HTTPS connection (production)
- [ ] Rate Limiting configured (optional)
- [ ] Audit logs enabled
- [ ] No sensitive info in error messages

---

## Migration Path

### Phase 1: Implementation (POC)
- API Key authentication module
- Automation API router
- Care log registration endpoint
- Kiro Hook update

### Phase 2: Extension (Production Migration)
- Cat registration endpoint
- Rate Limiting
- Detailed audit logs
- API usage statistics

### Phase 3: Optimization (Operations)
- API Key rotation
- Multiple API Key support
- Scope-based permissions
- Webhook notifications

---

**Last Updated**: 2025-11-24
**Context7 Reference**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
