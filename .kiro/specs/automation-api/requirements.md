# Requirements Document: Automation API

## Introduction

Implement API endpoints dedicated to Kiro Hook, MCP, and automation scripts. Adopt fixed API Key authentication completely separated from user authentication (OAuth2) to achieve automation while maintaining security.

**Design Principles**:
- **Complete Separation**: Fully separate user authentication and API Key authentication
- **Dedicated Endpoints**: Independent API routes under `/api/automation/*`
- **Minimum Privileges**: Allow only cat registration and care log registration
- **Auditable**: Log all operations

**Context7 Reference**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader

---

## Glossary

- **Automation API**: API endpoints dedicated to Kiro Hook, MCP, and automation scripts
- **API Key**: Fixed authentication key managed via environment variables and sent in headers
- **X-Automation-Key**: HTTP header name for sending API Key
- **OAuth2**: Existing authentication method used for user-facing APIs
- **Dual Authentication**: Parallel operation of user authentication and API Key authentication
- **Principle of Least Privilege**: API Key allows only minimum necessary operations

---

## Requirements

### Requirement 1: API Key Authentication Module

**User Story:** As a system administrator, I want to implement API Key authentication separate from user authentication, so that automation tools can access the API securely without user credentials.

#### Acceptance Criteria

1. WHEN API Key authentication module is created THEN it SHALL use FastAPI's `APIKeyHeader` security scheme
2. WHEN API Key is validated THEN it SHALL check against `AUTOMATION_API_KEY` environment variable
3. WHEN API Key is missing THEN it SHALL return 401 Unauthorized with `WWW-Authenticate: ApiKey` header
4. WHEN API Key is invalid THEN it SHALL return 403 Forbidden
5. WHEN Automation API is disabled THEN it SHALL return 503 Service Unavailable
6. WHEN API Key is validated successfully THEN it SHALL return the validated key string
7. WHEN API Key validation is optional THEN it SHALL return None without raising an exception for invalid keys

### Requirement 2: Configuration Management Extension

**User Story:** As a system administrator, I want to configure Automation API settings via environment variables, so that I can enable/disable the feature and set secure API keys.

#### Acceptance Criteria

1. WHEN application starts THEN it SHALL load `ENABLE_AUTOMATION_API` environment variable (default: false)
2. WHEN application starts THEN it SHALL load `AUTOMATION_API_KEY` environment variable
3. WHEN Automation API is enabled in production THEN it SHALL validate that `AUTOMATION_API_KEY` is set
4. WHEN Automation API is enabled in production THEN it SHALL validate that `AUTOMATION_API_KEY` is at least 32 characters
5. WHEN API Key validation fails THEN it SHALL raise a ValueError with descriptive message
6. WHEN settings are accessed THEN it SHALL provide `is_automation_api_secure` property for validation

### Requirement 3: Automation API Router Creation

**User Story:** As a developer, I want to create a dedicated API router for automation endpoints, so that all automation operations are grouped and secured with API Key authentication.

#### Acceptance Criteria

1. WHEN Automation API router is created THEN it SHALL use `/api/automation` prefix
2. WHEN Automation API router is created THEN it SHALL apply API Key authentication to all endpoints via router-level dependencies
3. WHEN Automation API router is created THEN it SHALL be tagged with "automation" for OpenAPI documentation
4. WHEN Automation API router is created THEN it SHALL define custom error responses (401, 403, 503)
5. WHEN Automation API router is included in main app THEN it SHALL be separate from `/api/v1/*` routes

### Requirement 4: Cat Registration Automation API

**User Story:** As a Kiro Hook, I want to register a new cat via Automation API, so that I can automate cat registration without user authentication.

#### Acceptance Criteria

1. WHEN POST `/api/automation/animals` is called with valid API Key THEN it SHALL create a new cat record
2. WHEN cat is created via Automation API THEN it SHALL set `recorder_id` to None to indicate automation
3. WHEN cat creation fails THEN it SHALL return 500 Internal Server Error with error details
4. WHEN GET `/api/automation/animals/{animal_id}` is called THEN it SHALL return cat information
5. WHEN cat is not found THEN it SHALL return 404 Not Found
6. WHEN API Key is missing or invalid THEN it SHALL return 401 or 403 before executing business logic

### Requirement 5: Care Log Registration Automation API

**User Story:** As an OCR Import Hook, I want to register care logs via Automation API, so that I can automate care log registration from scanned documents.

#### Acceptance Criteria

1. WHEN POST `/api/automation/care-logs` is called with valid API Key THEN it SHALL create a new care log record
2. WHEN care log is created via Automation API THEN it SHALL accept `recorder_name` from request body (e.g., "OCR Auto Import")
3. WHEN care log is created via Automation API THEN it SHALL accept `from_paper` flag from request body
4. WHEN care log is created via Automation API THEN it SHALL accept `device_tag` from request body (e.g., "OCR-Import")
5. WHEN care log creation fails THEN it SHALL return 500 Internal Server Error with error details
6. WHEN API Key is missing or invalid THEN it SHALL return 401 or 403 before executing business logic

### Requirement 6: Main Application Integration

**User Story:** As a system administrator, I want to integrate Automation API into the main application, so that it runs alongside existing user APIs without conflicts.

#### Acceptance Criteria

1. WHEN application starts THEN it SHALL include Automation API router with `/api` prefix
2. WHEN application starts THEN it SHALL maintain existing `/api/v1/*` routes with OAuth2 authentication
3. WHEN application starts THEN it SHALL not apply OAuth2 authentication to `/api/automation/*` routes
4. WHEN application starts THEN it SHALL not apply API Key authentication to `/api/v1/*` routes
5. WHEN OpenAPI documentation is generated THEN it SHALL show both authentication schemes separately

### Requirement 7: Security Measures

**User Story:** As a security officer, I want to ensure Automation API is secure, so that unauthorized access is prevented and all operations are auditable.

#### Acceptance Criteria

1. WHEN API Key is generated THEN it SHALL be at least 32 characters using `secrets.token_urlsafe(32)`
2. WHEN API Key is stored THEN it SHALL be stored in environment variables, not in code
3. WHEN API Key is transmitted THEN it SHALL be sent via HTTPS in production
4. WHEN Automation API operation is performed THEN it SHALL be logged with "automation" indicator
5. WHEN Automation API is enabled in production THEN it SHALL enforce minimum key length validation
6. WHEN Automation API is disabled THEN it SHALL return 503 for all automation endpoints
7. WHEN rate limiting is implemented (optional) THEN it SHALL limit requests per minute per IP address

### Requirement 8: Kiro Hook Integration

**User Story:** As a Kiro Hook, I want to use Automation API for care log registration, so that I can register OCR-extracted data without OAuth2 authentication flow.

#### Acceptance Criteria

1. WHEN `register_care_logs.py` is updated THEN it SHALL use `/api/automation/care-logs` endpoint
2. WHEN `register_care_logs.py` sends request THEN it SHALL include `X-Automation-Key` header
3. WHEN `register_care_logs.py` reads API Key THEN it SHALL read from `AUTOMATION_API_KEY` environment variable
4. WHEN authentication fails THEN it SHALL log error and display user-friendly message
5. WHEN API Key is not set THEN it SHALL display setup instructions to user

### Requirement 9: Environment Variable Template Update

**User Story:** As a new developer, I want to see Automation API configuration in `.env.example`, so that I can set up the feature correctly.

#### Acceptance Criteria

1. WHEN `.env.example` is viewed THEN it SHALL include `ENABLE_AUTOMATION_API` with description
2. WHEN `.env.example` is viewed THEN it SHALL include `AUTOMATION_API_KEY` with generation instructions
3. WHEN `.env.example` is viewed THEN it SHALL include security warnings for production use
4. WHEN `.env.example` is viewed THEN it SHALL include example API Key generation command

### Requirement 10: Documentation Creation

**User Story:** As a developer, I want to read documentation about Automation API, so that I can understand how to use it correctly.

#### Acceptance Criteria

1. WHEN documentation is created THEN it SHALL explain the dual authentication architecture
2. WHEN documentation is created THEN it SHALL provide API Key generation instructions
3. WHEN documentation is created THEN it SHALL include curl examples for each endpoint
4. WHEN documentation is created THEN it SHALL include Python examples for Kiro Hook usage
5. WHEN documentation is created THEN it SHALL explain security considerations
6. WHEN documentation is created THEN it SHALL include troubleshooting guide

---

## Technical Notes

### API Key Generation Method

```bash
# Generate strong API Key (32+ characters)
python -c "import secrets; print('AUTOMATION_API_KEY=' + secrets.token_urlsafe(32))"
```

### Environment Variable Configuration Example

```bash
# .env
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=xK7mP9nQ2wR5tY8uI1oP4aS6dF3gH0jK9lZ2xC5vB7nM4qW1eR3tY6uI8oP0aS2d
```

### Endpoint List

| Endpoint | Method | Auth | Description |
|----------|--------|------|-------------|
| `/api/v1/animals` | POST | OAuth2 | Cat registration (user) |
| `/api/automation/animals` | POST | API Key | Cat registration (automation) |
| `/api/v1/care-logs` | POST | OAuth2 | Care log registration (user) |
| `/api/automation/care-logs` | POST | API Key | Care log registration (automation) |

### Security Boundaries

```
┌─────────────────────────────────────────────────────────────┐
│                    FastAPI Application                       │
├─────────────────────────────────────────────────────────────┤
│                                                               │
│  ┌──────────────────────┐    ┌──────────────────────────┐  │
│  │  /api/v1/*           │    │  /api/automation/*       │  │
│  │  User-facing API     │    │  Hook/MCP-only API       │  │
│  ├──────────────────────┤    ├──────────────────────────┤  │
│  │ Auth: OAuth2 + JWT   │    │ Auth: API Key (fixed)    │  │
│  │ Cookie: HTTPOnly     │    │ Header: X-Automation-Key │  │
│  │ Target: Admin UI     │    │ Target: Hook/MCP         │  │
│  │ Permissions: Roles   │    │ Permissions: Limited ops │  │
│  │ Audit: user_id       │    │ Audit: automation flag   │  │
│  └──────────────────────┘    └──────────────────────────┘  │
│                                                               │
└─────────────────────────────────────────────────────────────┘
```

### Implementation Priority

1. **High Priority** (POC Required):
   - API Key authentication module
   - Care log registration Automation API
   - Kiro Hook integration

2. **Medium Priority** (POC Recommended):
   - Cat registration Automation API
   - Configuration management extension
   - Environment variable template update

3. **Low Priority** (Production Migration):
   - Rate Limiting
   - Detailed audit logs
   - API usage statistics

---

## Success Criteria

- All Acceptance Criteria are met
- Care logs can be registered from Kiro Hook via Automation API
- User authentication and API Key authentication operate independently
- Production security validation passes
- Documentation is complete and reviewed
- Test coverage is 70% or higher

---

**Last Updated**: 2025-11-24
**Context7 Reference**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
