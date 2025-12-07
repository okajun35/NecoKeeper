# Implementation Plan

This document is the implementation task list for the NecoKeeper system. Each task can be implemented iteratively, building on the deliverables of prior tasks.

## Current Status

**Project Status**: MVP Core complete! Phase 10 (Multilingual support) finished, all core features implemented.

**Completed:**
- ✅ Phase 1: Project foundation and database (11 tasks)
- ✅ Phase 2: Authentication & authorization system (7 tasks)
- ✅ Phase 3: Animal management features (6 tasks)
- ✅ Phase 4: CareLog features (5 tasks)
- ✅ Phase 4: Volunteer management (4 tasks)
- ✅ Phase 5: Medical record features (9 tasks) ✅ Completed 2024-11-18
- ✅ Phase 6: PDF generation features (5 tasks)
- ✅ Phase 6: CSV/Excel export features (4 tasks) ✅ Completed 2024-11-18
- ✅ Phase 7: Adoption management features (4 tasks) ✅ Completed 2024-11-18
- ✅ Phase 8: Admin UI (15 tasks) ✅ Completed 2024-11-18
- ✅ Phase 9: Public API + PWA (13 tasks)
- ✅ Phase 10: Multilingual support (5 tasks) ✅ Completed 2024-11-22

**Implemented Features:**
- ✅ Database (12 models)
- ✅ JWT-based authentication & authorization (RBAC, permission checks)
- ✅ Animal management (CRUD, search, status management, image gallery)
- ✅ CareLog management (CRUD, CSV export, copy previous values, filters)
- ✅ Volunteer management (CRUD, activity history)
- ✅ Medical record management (CRUD, medical actions master, billing calculation, admin UI) ✅ Completed 2024-11-18
- ✅ Adoption management (applicants, interviews, adoption records, admin UI) ✅ Completed 2024-11-18
- ✅ PDF generation (QR cards, imposed cards, paper forms, reports)
- ✅ Admin UI (dashboard, animal ledger, care logs, medical records, adoption management, volunteers, report export, settings, login, weight chart, image gallery, search) ✅ Completed 2024-11-18
- ✅ Public API (unauthenticated CareLog input, list, detail)
- ✅ PWA features (manifest.json, Service Worker, offline sync)
- ✅ Multilingual support (Japanese/English, i18next integration, 800+ translation keys) ✅ Completed 2024-11-22
- ✅ Integration tests (232 tests, coverage 84.90%)

**Next Steps**: Phase 11 (Security and logging), Phase 12 (Backups), Phase 15 (Remaining documentation)

**🎉 Production Deployment Complete!**
- **URL**: https://necokeeper.onrender.com
- **Plan**: Render Free Plan (1-week PoC)
- **Deployment date**: 2024-11-23
- **Verification**: ✅ Login screen, APIs, and multilingual support all working correctly

**Important Notes:**

1. **Use Context7 MCP**: Before any code implementation, use Context7 MCP to consult the latest library documentation.

2. **Code quality standards (code-structure-review integration):**
  - Add `from __future__ import annotations` to all files.
  - For type hints, use `collections.abc` (`list[T]`, `dict[K, V]`, `Sequence[T]`, `Iterator[T]`).
  - Use `X | None` syntax for optional types (not `Optional[X]`).
  - Use `X | Y` syntax for unions (not `Union[X, Y]`).
  - Add explicit type annotations to empty collections.
  - For SQLAlchemy models, use `server_default=func.now()` and `onupdate=func.now()`.
  - Standardize error handling (HTTPException, logging).
  - Add docstrings (Args, Returns, Raises, Example) to all functions.

3. **Mypy strict mode**: All code must pass `mypy --strict`.

4. **Tests**: Write tests in parallel with implementation to ensure quality.

### How to Use Context7 MCP
1. **Resolve library ID**: Use `mcp_context7_resolve_library_id` to look up library names.
2. **Fetch documentation**: Use `mcp_context7_get_library_docs` to retrieve up-to-date docs (recommended: tokens 5000).
3. **Implementation basis**: Use the retrieved docs as the primary reference for design and implementation.
4. **Version check**: If you suspect deprecations, confirm via Context7.

## Quick Start Guide

### Development Environment Setup (first time only)
```bash
# 1. Create virtual environment
python -m venv .venv

# 2. Activate virtual environment (Windows)
.venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Environment variables
# Create a .env file and set required environment variables
```

### Task Execution Flow
1. Check the "Context7 MCP usage guidelines" for the relevant Phase.
2. Use Context7 MCP to fetch the latest documentation.
3. Implement tasks one by one.
4. After completing implementation, mark the checkbox.
5. Move on to the next task.

## Notes for Executing Tasks

- All tasks are mandatory (including tests).
- Each task can be implemented independently, but pay attention to dependencies.
- **Required**: Use Context7 MCP to consult the latest library documentation.
- At the start of each Phase, review the relevant Context7 guidelines.
- Write tests in parallel with implementation to ensure quality.

## Implementation Priority

### Highest Priority (MVP Core)
1. ✅ Phase 1: Project foundation and database
2. ✅ Phase 2: Authentication & authorization system
3. ✅ Phase 3: Animal management (basic CRUD)
4. ✅ Phase 4: CareLog (basic input)
5. ✅ Phase 6: PDF generation (QR cards)
6. ✅ Phase 9: Public forms (basic input)

### High Priority (MVP Extended)
7. ✅ Phase 5: Medical record features
8. ✅ Phase 7: Adoption management
9. ✅ Phase 8: Admin UI (basic screens)
10. Phase 11: Security and logging

### Medium Priority (Enhancement)
11. ✅ Phase 10: Multilingual support
12. Phase 12: Backup and data management
13. Phase 15: Deployment and documentation

### Low Priority (Optional)
14. Phase 13: OCR features
15. Phase 14: Help and support
16. Phase 16: Performance optimization and tests
17. Phase 17: Final polishing and release

---

## Phase 1: Project Foundation and Database ✅ Completed

**Context7 MCP usage guidelines:**
- Before each task, always use Context7 MCP to consult the latest documentation.
- FastAPI implementation: use `mcp_context7_get_library_docs` with `/fastapi/fastapi` (tokens: 5000).
- SQLAlchemy implementation: use `mcp_context7_get_library_docs` with `/sqlalchemy/sqlalchemy` (tokens: 5000).
- Pydantic implementation: use `mcp_context7_get_library_docs` with `/pydantic/pydantic` (tokens: 5000).
- WeasyPrint implementation: use `mcp_context7_resolve_library_id` to search for "WeasyPrint", then fetch the docs.

**Code quality improvements (code-structure-review integration):**
- Add `from __future__ import annotations` to all files.
- For type hints, use `collections.abc` (`list[T]`, `dict[K, V]`, `Sequence[T]`, `Iterator[T]`).
- Use `X | None` for optionals (not `Optional[X]`).
- Use `X | Y` for unions (not `Union[X, Y]`).
- Add explicit type annotations to empty collections.
- In the database module, add PostgreSQL-compatible naming conventions.

### 1. Project structure and setup

Create the basic project structure and set up required dependencies.

- [x] 1.1 Create project directory structure
  - Directories: `app/`, `data/`, `media/`, `backups/`, `tests/`
  - Subdirectories: `app/models/`, `app/schemas/`, `app/api/`, `app/services/`, `app/auth/`, `app/templates/`, `app/static/`
  - _Requirements: Technical Constraint 1, Technical Constraint 2_

- [x] 1.2 Create `requirements.txt`
  - FastAPI, SQLAlchemy, Pydantic, WeasyPrint, bcrypt, python-multipart, jinja2, qrcode, python-dotenv, alembic
  - For tests: pytest, pytest-asyncio, httpx, faker
  - _Requirements: Technical Constraint 1_

- [x] 1.3 Implement config module (`app/config.py`)
  - Load environment variables (DATABASE_URL, SECRET_KEY, DEBUG, LOG_LEVEL)
  - Use Pydantic Settings for type-safe configuration management
  - _Requirements: Requirement 20.3_

- [x] 1.4 Create FastAPI application entry point (`app/main.py`)
  - Instantiate the FastAPI app
  - Configure CORS middleware
  - Configure static files and templates
  - _Requirements: Technical Constraint 1_

- [x] 1.5 Create development setup script
  - Script to create virtualenv, install dependencies, and initialize the database
  - Document manual setup steps in `README.md`
  - _Requirements: Requirement 31_

### 2. Database design and initialization

Implement the SQLite database and SQLAlchemy models.

- [x] 2.1 Implement database connection module (`app/database.py`)
  - **Context7**: Refer to `/sqlalchemy/sqlalchemy` docs (especially Async engine and session management).
  - Create SQLAlchemy engine (create_engine with SQLite).
  - Session management (SessionLocal, `get_db` dependency).
  - Define Base class (DeclarativeBase).
  - Use `settings.database_url` for the DB file path.
  - _Requirements: Technical Constraint 1_

- [x] 2.2 Implement `Animals` model (`app/models/animal.py`)
  - **Context7**: Confirm SQLAlchemy 2.0 model definitions (Mapped, mapped_column).
  - Define all columns (id, name, photo, pattern, tail_length, collar, age, gender, ear_cut, features, status, protected_at, created_at, updated_at).
  - Define indexes (status, protected_at, name).
  - Set default values (status='protected', protected_at=CURRENT_DATE).
  - Use type hints (Mapped[str], Mapped[str | None], etc.).
  - _Requirements: Requirement 1.4, Requirement 15.1_

- [x] 2.3 Implement `CareLog` model (`app/models/care_log.py`)
  - Define all columns (id, animal_id, recorder_id, recorder_name, time_slot, appetite, energy, urination, cleaning, memo, ip_address, user_agent, device_tag, from_paper, created_at, last_updated_at, last_updated_by).
  - Define foreign keys (animal_id, last_updated_by).
  - Define indexes (animal_id, created_at, recorder_id, time_slot).
  - _Requirements: Requirement 3.2, Requirement 3.6, Requirement 23.6_

- [x] 2.4 Implement `MedicalRecord` model (`app/models/medical_record.py`)
  - Define all columns (id, animal_id, vet_id, date, time_slot, weight, temperature, symptoms, medical_action_id, dosage (INTEGER, count), other, comment, created_at, updated_at, last_updated_at, last_updated_by).
  - Define foreign keys (animal_id, vet_id, medical_action_id, last_updated_by).
  - Define indexes (animal_id, date, vet_id, medical_action_id).
  - _Requirements: Requirement 5.2, Requirement 23.6_

- [x] 2.5 Implement `Users` model (`app/models/user.py`)
  - Define all columns (id, email, password_hash, name, role, is_active, failed_login_count, locked_until, created_at, updated_at).
  - Unique index on email.
  - _Requirements: Requirement 21.6, Requirement 22.2_

- [x] 2.6 Implement `Volunteers` model (`app/models/volunteer.py`)
  - Define all columns (id, name, contact, affiliation, status, started_at, created_at, updated_at).
  - Define indexes (status, name).
  - _Requirements: Requirement 4.1_

- [x] 2.7 Implement `Applicants`, `AdoptionRecord`, `StatusHistory`, `AuditLog`, `Sessions`, `Settings` models
  - Define all columns and foreign keys for each model.
  - Add appropriate indexes.
  - _Requirements: Requirement 14, Requirement 15.2, Requirement 23.1_

- [x] 2.8 Implement medical actions master model (`MedicalActions`)
  - Define all columns (id, name, valid_from, valid_to, cost_price, selling_price, procedure_fee, currency, created_at, updated_at, last_updated_at, last_updated_by).
  - Support period-based pricing and currency unit (JPY/USD).
  - Define indexes (name, valid_from, valid_to).
  - _Requirements: Requirement 6.1, Requirement 6.2, Requirement 6.3_

- [x] 2.9 Implement `AnimalImages` model (`app/models/animal_image.py`)
  - Define all columns (id, animal_id, image_path, taken_at, description, file_size, created_at).
  - Define foreign key (animal_id).
  - _Requirements: Requirement 27.3_

- [x] 2.10 Alembic migration setup
  - **Context7**: Confirm Alembic initialization and configuration.
  - Run `alembic init alembic`.
  - Configure `alembic.ini` (sqlalchemy.url).
  - Configure `env.py` (target_metadata = Base.metadata).
  - Create initial migration script (`alembic revision --autogenerate -m "Initial migration"`).
  - _Requirements: Technical Constraint 1_

- [x] 2.11 Create unit tests for domain models (DDD-based)
  - Test business rules of domain objects.
  - Test immutability of value objects.
  - Test entity identity.
  - _Requirements: Requirement 28_


## Phase 2: Authentication & Authorization System (JWT + OAuth2) ✅ Completed

**Context7 MCP usage guidelines:**
- Before implementing JWT: use `mcp_context7_get_library_docs` with `/fastapi/fastapi` and review OAuth2/JWT-related docs (tokens: 5000).
- Before implementing passlib: use `mcp_context7_resolve_library_id` to search for "passlib" and fetch documentation.
- Before implementing python-jose: use `mcp_context7_resolve_library_id` to search for "python-jose" and fetch documentation.

**Code quality improvements (code-structure-review integration):**
- Apply type-hint improvements to all authentication-related files.
- Standardize error-handling patterns (HTTPException, logging).
- Enrich docstrings (Args, Returns, Raises, Example).

### 3. Implement JWT-based authentication

Implement an authentication system using JWT + OAuth2 Password Flow.

- [x] 3.1 Implement password hashing utilities (`app/auth/password.py`)
  - **Context7**: confirm how to use passlib + bcrypt.
  - Provide hash and verify functions using `passlib.CryptContext`.
  - Implement password policy validation (minimum 8 characters, alphanumeric mix).
  - _Requirements: Requirement 21.7, Requirement 22.1_

- [x] 3.2 Implement JWT management module (`app/auth/jwt.py`)
  - **Context7**: confirm how to generate and verify JWTs with python-jose.
  - Implement JWT access token generation (expiry: 2 hours).
  - Implement JWT token verification function.
  - Configure `SECRET_KEY` (loaded from environment variables).
  - _Requirements: Requirement 21.3, Requirement 22.3, Requirement 22.8_

- [x] 3.3 Implement authentication dependencies (`app/auth/dependencies.py`)
  - **Context7**: confirm how to use FastAPI's `OAuth2PasswordBearer`.
  - Configure the `OAuth2PasswordBearer` scheme.
  - Implement `get_current_user` dependency (get user from token).
  - Implement `get_current_active_user` dependency (only active users).
  - _Requirements: Requirement 21.3_

- [x] 3.4 Implement login attempt limiting
  - Count failed attempts (on `Users` table).
  - Lock account for 15 minutes after 5 failed attempts.
  - _Requirements: Requirement 22.2_

- [x] 3.5 Implement permission-check dependencies (`app/auth/permissions.py`)
  - Define role-based permission matrix.
  - Implement `require_role` dependency.
  - Implement `require_permission` dependency.
  - _Requirements: Requirement 10.1-10.5_

- [x] 3.6 Implement authentication API endpoints (`app/api/v1/auth.py`)
  - **Context7**: review FastAPI docs for OAuth2 Password Flow endpoints.
  - `POST /api/v1/auth/token` (login, obtain JWT token).
  - `GET /api/v1/auth/me` (get current user info).
  - Use `OAuth2PasswordRequestForm`.
  - _Requirements: Requirement 21.1-21.4, Requirement 21.8-21.9_

- [x] 3.7 Create tests for authentication features
  - Test password hashing.
  - Test JWT generation/verification.
  - Test authentication dependencies.
  - Test login API.
  - Test permission checks.
  - _Requirements: Requirement 22_

## Phase 3: Animal Management Features ✅ Completed

**Context7 MCP usage guidelines:**
- For Pydantic: use `mcp_context7_get_library_docs` with `/pydantic/pydantic` (tokens: 5000).
- For SQLAlchemy: use `mcp_context7_get_library_docs` with `/sqlalchemy/sqlalchemy` (tokens: 5000).
- For Pillow: use `mcp_context7_get_library_docs` with `/python-pillow/Pillow` (tokens: 5000).

**Code quality improvements (code-structure-review integration):**
- Apply type-hint improvements to all schema, service, and API files.
- Standardize error-handling patterns.
- Add logging.

### 4. Animal master management

Implement CRUD functionality for individual cat records.

- [x] 4.1 Implement Pydantic schemas (`app/schemas/animal.py`)
  - `AnimalCreate`, `AnimalUpdate`, `AnimalResponse`.
  - Validation rules (required fields, format checks).
  - _Requirements: Requirement 1.2_

- [x] 4.2 Implement animal management service (`app/services/animal_service.py`)
  - `create_animal` (register cat).
  - `get_animal` (get cat details).
  - `update_animal` (update cat).
  - `delete_animal` (logical delete).
  - `list_animals` (list with pagination).
  - `search_animals` (search).
  - _Requirements: Requirement 1.1-1.3, Requirement 1.5, Requirement 24.2_

- [x] 4.3 Implement image upload utilities (`app/utils/image.py`)
  - File validation (extension, MIME type, size).
  - Image optimization (resize, compress).
  - File storage handling.
  - _Requirements: Requirement 27.9, Requirement 27.10_

- [x] 4.4 Implement animal management API endpoints (`app/api/v1/animals.py`)
  - `GET /api/v1/animals` (list).
  - `POST /api/v1/animals` (create).
  - `GET /api/v1/animals/{id}` (detail).
  - `PUT /api/v1/animals/{id}` (update).
  - `DELETE /api/v1/animals/{id}` (logical delete).
  - `GET /api/v1/animals/search` (search).
  - _Requirements: Requirement 1, Requirement 24_

- [x] 4.5 Implement status management
  - Status change operations.
  - Record `StatusHistory`.
  - Status-based filtering.
  - _Requirements: Requirement 15.2, Requirement 15.3, Requirement 15.6-15.7_

- [x] 4.6 Create tests for animal management (DDD-based)
  - Unit tests for cat domain objects (status-change rules, etc.).
  - Application service tests for animal management use cases.
  - Integration tests for the animal repository (persistence).
  - _Requirements: Requirement 1, Requirement 15_

### 5. Image gallery features

**Context7 MCP usage guidelines:**
- For Pillow: use `mcp_context7_get_library_docs` with `/python-pillow/Pillow` (tokens: 5000).
- For file upload: use `mcp_context7_get_library_docs` with `/fastapi/fastapi` and review File Upload documentation.

**Code quality improvements:**
- Type hints: `from __future__ import annotations`, `X | None`, `collections.abc`.
- Error handling: HTTPException, logging.
- Docstrings: Args, Returns, Raises, Example.

Implement multi-image gallery features for cats.

- [x] 5.1 Implement image gallery service (`app/services/image_service.py`)
  - `upload_image` (upload image).
  - `list_images` (list images).
  - `delete_image` (delete image).
  - Check max number of images.
  - Check file size limits.
  - _Requirements: Requirement 27.2-27.3, Requirement 27.8-27.9_

- [x] 5.2 Implement image management API endpoints (`app/api/v1/images.py`)
  - `POST /api/v1/animals/{id}/images` (upload image).
  - `GET /api/v1/animals/{id}/images` (list images).
  - `DELETE /api/v1/images/{id}` (delete image).
  - _Requirements: Requirement 27.1-27.5_

- [x] 5.3 Implement image limit settings
  - Manage settings via the `Settings` table.
  - Default values (max 20 images, max 5MB).
  - _Requirements: Requirement 27.6-27.7, Requirement 27.10_


## Phase 4: Care Log Features ✅ Completed

**Context7 MCP usage guidelines:**
- For CSV processing: use `mcp_context7_resolve_library_id` to consider using "pandas" or the standard library `csv`.
- For FastAPI: use `mcp_context7_get_library_docs` with `/fastapi/fastapi` (tokens: 5000).

**Code quality improvements (code-structure-review integration):**
- Apply type-hint improvements to all files.
- Standardize error handling and logging.

### 6. Care log management

Implement CRUD functionality for daily care logs.

- [x] 6.1 Implement Pydantic schemas (`app/schemas/care_log.py`)
  - `CareLogCreate`, `CareLogUpdate`, `CareLogResponse`.
  - Validation rules (`time_slot`: morning/noon/evening, `appetite`/`energy`: 1-5, `urination`/`cleaning`: boolean).
  - _Requirements: Requirement 3.2_

- [x] 6.2 Implement care log service (`app/services/care_log_service.py`)
  - `create_care_log` (create record).
  - `get_care_log` (get record details).
  - `list_care_logs` (list with filtering).
  - `export_care_logs_csv` (CSV export).
  - _Requirements: Requirement 3.5, Requirement 25.2-25.3_

- [x] 6.3 Implement care log API endpoints (`app/api/v1/care_logs.py`)
  - `GET /api/v1/care-logs` (list).
  - `POST /api/v1/care-logs` (create).
  - `GET /api/v1/care-logs/{id}` (detail).
  - `PUT /api/v1/care-logs/{id}` (update).
  - `GET /api/v1/care-logs/export` (CSV export).
  - _Requirements: Requirement 3, Requirement 25_

- [x] 6.4 Implement "copy previous input" feature
  - Retrieve the latest record.
  - Provide data to the frontend.
  - _Requirements: Requirement 3.7_

- [x] 6.5 Create integration tests for care log features
  - Test CRUD operations.
  - Test CSV export.
  - _Requirements: Requirement 3, Requirement 25_

### 7. Volunteer management ✅ Completed

Implement management features for volunteer recorders.

- [x] 7.1 Implement Pydantic schemas (`app/schemas/volunteer.py`)
  - `VolunteerCreate`, `VolunteerUpdate`, `VolunteerResponse`.
  - _Requirements: Requirement 4.1_

- [x] 7.2 Implement volunteer management service (`app/services/volunteer_service.py`)
  - `create_volunteer` (create).
  - `get_volunteer` (detail).
  - `list_volunteers` (list).
  - `update_volunteer` (update).
  - `get_activity_history` (get activity history).
  - `get_active_volunteers` (list active volunteers).
  - _Requirements: Requirement 4.2, Requirement 4.4, Requirement 4.5_

- [x] 7.3 Implement volunteer management API endpoints (`app/api/v1/volunteers.py`)
  - `GET /api/v1/volunteers` (list).
  - `POST /api/v1/volunteers` (create).
  - `GET /api/v1/volunteers/{id}` (detail).
  - `PUT /api/v1/volunteers/{id}` (update).
  - `GET /api/v1/volunteers/{id}/activity` (get activity history).
  - _Requirements: Requirement 4_

- [x] 7.4 Implement active volunteer retrieval
  - Provide selection list for public form.
  - _Requirements: Requirement 4.4_

## Phase 5: Medical Record Features ✅ Completed (100%)

**Context7 MCP usage guidelines:**
- For Pydantic: use `mcp_context7_get_library_docs` with `/pydantic/pydantic` (tokens: 5000).
- For SQLAlchemy: use `mcp_context7_get_library_docs` with `/sqlalchemy/sqlalchemy` (tokens: 5000).
- For Decimal handling: review how to use Python standard library `decimal`.

**Code quality improvements:**
- Type hints: `from __future__ import annotations`, `Decimal`, `X | None`.
- Error handling: `IntegrityError`, `SQLAlchemyError`.
- Docstrings: fully documented.

**Completion date**: 2024-11-18

### 8. Medical record management ✅ Completed

Implement CRUD functionality for veterinary medical records.

- [x] 8.1 Implement Pydantic schemas (`app/schemas/medical_record.py`) ✅
  - `MedicalRecordCreate`, `MedicalRecordUpdate`, `MedicalRecordResponse`
  - Validation rules (required: consultation date, weight, symptoms)
  - _Requirements: Requirement 5.3_

- [x] 8.2 Implement medical record service (`app/services/medical_record_service.py`) ✅
  - `create_medical_record` (register record)
  - `get_medical_record` (get record details)
  - `list_medical_records` (list, chronological order)
  - `update_medical_record` (update record)
  - _Requirements: Requirement 5.1, Requirement 5.5_

- [x] 8.3 Implement medical record API endpoints (`app/api/v1/medical_records.py`) ✅
  - `GET /api/v1/medical-records` (list)
  - `POST /api/v1/medical-records` (create)
  - `GET /api/v1/medical-records/{id}` (detail)
  - `PUT /api/v1/medical-records/{id}` (update)
  - _Requirements: Requirement 5_

- [x] 8.4 Create integration tests for medical record features ✅
  - Tests for CRUD operations
  - Tests for validation rules
  - _Requirements: Requirement 5_

### 9. Medical master data management ✅ Completed

Implement master data management features for procedures, medications, and vaccines.

- [x] 9.1 Implement Pydantic schemas (`app/schemas/medical_action.py`) ✅
  - `MedicalActionCreate`, `MedicalActionUpdate`, `MedicalActionResponse`
  - Validation for period-based pricing and currency units
  - _Requirements: Requirement 6.1-6.3_

- [x] 9.2 Implement medical action master service (`app/services/medical_action_service.py`) ✅
  - `create_medical_action` (register medical action)
  - `list_medical_actions` (list)
  - `update_medical_action` (update)
  - `calculate_billing` (billing: selling_price × dosage + procedure_fee)
  - _Requirements: Requirement 6.4_

- [x] 9.3 Implement medical action master API endpoints (`app/api/v1/medical_actions.py`) ✅
  - `GET/POST /api/v1/medical-actions`
  - `GET/PUT /api/v1/medical-actions/{id}`
  - `GET /api/v1/medical-actions/{id}/calculate` (billing calculation)
  - `GET /api/v1/medical-actions/active/list` (list active medical actions)
  - _Requirements: Requirement 6_

- [x] 9.4 Implement medical action selection feature ✅
  - Provide selection list from `MedicalActions` master
  - Allow free-text input as well
  - _Requirements: Requirement 5.4_

- [x] 9.5 Add dosage unit selection to medical action master ✅
  - Database migration: add `dosage_unit` column as `VARCHAR(10)` (already done)
  - Pydantic schema update: add `dosage_unit` field (choices: tablet, piece, time, mL)
  - Admin UI update: add dosage unit dropdown to medical action master create/edit modal
  - Medical record entry screen update: display dosage unit when a medical action is selected
  - _Requirements: Requirement 6.2, Requirement 6.7_

## Phase 6: PDF Generation Features ✅ Completed

**Context7 MCP usage guidelines:**
- Before implementing WeasyPrint: use `mcp_context7_resolve_library_id` to search for "WeasyPrint" and then `mcp_context7_get_library_docs` to fetch docs (tokens: 5000).
- Before implementing QR codes: use `mcp_context7_resolve_library_id` to search for "python-qrcode" and fetch docs.
- Before implementing Jinja2 templates: use `mcp_context7_get_library_docs` with `/pallets/jinja` (tokens: 5000).
- Confirm PDF-generation best practices via Context7.

### 10. QR codes and PDF generation ✅ Completed

Implement PDF generation for QR cards and paper care-log forms.

- [x] 10.1 QRコード生成ユーティリティを実装（app/utils/qr_code.py）
  - QR code image generation
  - Convert to byte array
  - Generate cat-specific URLs
  - _Requirements: Requirement 2.3_

- [x] 10.2 Implement PDF generation service (`app/services/pdf_service.py`)
  - `generate_qr_card` (generate QR card PDF)
  - `generate_qr_card_grid` (generate imposed QR card PDF, up to 10 cards)
  - `generate_paper_form` (generate paper care-log form PDF)
  - `generate_medical_detail` (generate medical detail PDF – currently marked as not implemented)
  - `generate_report` (generate report PDF – currently marked as not implemented)
  - _Requirements: Requirement 2.1-2.2, Requirement 2.5-2.8, Requirement 7.2-7.3, Requirement 9_

- [x] 10.3 Create PDF templates (`app/templates/pdf/`)
  - `qr_card.html` (A6 size)
  - `qr_card_grid.html` (A4, 2×5 cards)
  - `paper_form.html` (A4, 1 month per page)
  - _Requirements: Requirement 2, Requirement 7, Requirement 9_

- [x] 10.4 Implement PDF generation API endpoints (`app/api/v1/pdf.py`)
  - POST /api/v1/pdf/qr-card
  - POST /api/v1/pdf/qr-card-grid
  - POST /api/v1/pdf/paper-form
  - POST /api/v1/pdf/medical-detail (not yet implemented)
  - POST /api/v1/pdf/report (not yet implemented)
  - With authentication and permission checks
  - _Requirements: Requirement 2, Requirement 7, Requirement 9_

- [x] 10.5 Create tests for PDF generation features
  - QR card generation tests (9 tests)
  - Imposed card generation tests (4 tests)
  - Paper form generation tests (4 tests)
  - Error-handling tests
  - Coverage 94.81%
  - _Requirements: Requirement 28.3_


### 11. CSV/Excel export features ✅ Completed

Implement data export features in CSV and Excel formats.

- [x] 11.1 Implement CSV export service (`app/services/csv_service.py`) ✅
  - Care-log CSV export (with UTF-8 BOM)
  - Report CSV export (daily, weekly, monthly aggregates)
  - Character encoding handling (UTF-8 BOM)
  - _Requirements: Requirement 8.1, Requirement 25.3_

- [x] 11.2 Implement Excel export service (`app/services/excel_service.py`) ✅
  - Generate Excel files using `openpyxl`
  - Care-log Excel export
  - Report Excel export (daily, weekly, monthly aggregates)
  - Style configuration (headers, borders, fonts)
  - _Requirements: Requirement 7.5, Requirement 9.4_

- [x] 11.3 Implement care-log CSV/Excel export features ✅
  - GET /api/v1/care-logs/export (CSV export)
  - Date range and cat ID filters
  - Permission checks (`csv:export`)
  - _Requirements: Requirement 8.2-8.4, Requirement 25.2-25.3_

- [x] 11.4 Implement report CSV/Excel export features ✅
  - POST /api/v1/reports/export (selectable CSV/Excel formats)
  - Daily, weekly, and monthly aggregate CSV/Excel export
  - Format selection (csv/excel)
  - Permission checks (`report:read`)
  - _Requirements: Requirement 7.4-7.5, Requirement 9.3-9.4_

## Phase 7: Adoption Management Features ✅ Completed (100%)

**Completion date**: 2024-11-18

### 12. Adoption applicants and adoption management ✅ Completed

Implement features for managing the adoption process and applicants.

- [x] 12.1 Implement Pydantic schemas (`app/schemas/adoption.py`) ✅
  - ApplicantCreate, ApplicantUpdate, ApplicantResponse
  - AdoptionRecordCreate, AdoptionRecordUpdate, AdoptionRecordResponse
  - _Requirements: Requirement 14.1-14.2_

- [x] 12.2 Implement adoption management service (`app/services/adoption_service.py`) ✅
  - `create_applicant` (register applicant)
  - `list_applicants` (list applicants)
  - `create_interview_record` (register interview record)
  - `create_adoption_record` (register adoption record)
  - `update_animal_status` (update cat status)
  - `create_follow_up` (register post-adoption follow-up)
  - _Requirements: Requirement 14.3-14.5_

- [x] 12.3 Implement adoption management API endpoints (`app/api/v1/adoptions.py`) ✅
  - GET/POST /api/v1/applicants
  - GET/PUT /api/v1/applicants/{id}
  - POST /api/v1/adoptions
  - PUT /api/v1/adoptions/{id}
  - _Requirements: Requirement 14_

- [x] 12.4 Create integration tests for adoption management features ✅
  - Tests for applicant registration
  - Tests for the adoption process
  - Tests for status updates
  - _Requirements: Requirement 14_

## Phase 8: Admin UI ✅ Completed (100%)

**Context7 MCP usage guidelines:**
- Before implementing Tailwind CSS: use `mcp_context7_get_library_docs` with `/tailwindlabs/tailwindcss` (tokens: 5000).
- Before implementing HTMX: use `mcp_context7_resolve_library_id` to search for "htmx" and fetch documentation.
- Before implementing Alpine.js: use `mcp_context7_resolve_library_id` to search for "alpinejs" and fetch documentation.
- Before implementing Chart.js: use `mcp_context7_get_library_docs` with `/chartjs/Chart.js` (tokens: 5000).
- Before implementing Jinja2 templates: use `mcp_context7_get_library_docs` with `/pallets/jinja`.

**Completion date**: 2024-11-18

**Implemented technology stack:**
- Tailwind CSS 3.3+ (CDN).
- HTMX 2.0+ (dynamic UI updates).
- Alpine.js 3.x (reactive components).

### 13. Implement admin UI ✅ Completed

Implement the admin UI.

- [x] 13.1 Create base template (`app/templates/admin/base.html`) ✅
  - Layout using Tailwind CSS + HTMX + Alpine.js.
  - Responsive sidebar menu (mobile friendly).
  - Header (user name, logout, notifications).
  - Mobile menu (hamburger + overlay).
  - _Requirements: Requirement 12.1-12.2_

- [x] 13.2 Implement dashboard screen (`app/templates/admin/dashboard.html`) ✅
  - Statistic cards (cats under protection, adoptable, today's logs, volunteers).
  - List of recent care logs.
  - List of cats that need records.
  - Responsive layout for mobile and desktop.
  - _Requirements: Requirement 12.3, Requirement 16.1-16.4_

- [x] 13.3 Implement cat ledger list screen (`app/templates/admin/animals/list.html`) ✅
  - Search and filter (by status, page size).
  - Responsive card layout.
  - Action buttons (detail, edit, QR).
  - Responsive for mobile and desktop.
  - _Requirements: Requirement 12.4, Requirement 15.3, Requirement 15.6-15.7_

- [x] 13.4 Implement cat detail screen (`app/templates/admin/animals/detail.html`) ✅
  - Tab layout (basic info, care logs, medical records, image gallery, weight chart).
  - Basic info edit form.
  - Status change feature.
  - QR card export button (A6 portrait PDF, photo 30mm, QR code 60mm).
  - Paper care-log form export button (year/month modal, A4 size).
  - Support for embedding base64-encoded photos.
  - Weight trend chart (Chart.js line chart, average weight baseline, data table).
  - _Requirements: Requirement 1.3, Requirement 15.2, Requirement 2.1-2.7_

- [x] 13.5 Implement care-log list screen (`app/templates/admin/care_logs/list.html`) ✅
  - Static HTML template implemented.
  - Mobile: card-based layout.
  - Desktop: table layout.
  - CSV export button.
  - Pagination UI.
  - _Requirements: Requirement 25.1_

- [x] 13.5.1 Implement dynamic behavior for care-log list (JavaScript) ✅
  - Fetch data from API (`/api/v1/care-logs`)
  - Implement filters (cat, date range, time slot)
  - Implement pagination
  - Wire up CSV export button
  - Dynamic rendering for mobile/desktop layouts
  - Loading state and error handling
  - _Requirements: Requirement 25.1_

- [x] 13.6 Implement medical-record list screen (`app/templates/admin/medical_records/list.html`) ✅
  - HTML template implementation (mobile & desktop).
  - JavaScript implementation (`app/static/js/admin/medical_records_list.js`).
  - Filters (cat, vet, date range).
  - Pagination.
  - Time-series display (descending).
  - Display medical actions and medication info.
  - Routing implementation (`/admin/medical-records`).
  - _Requirements: Requirement 5.5, Requirement 7.1_

- [x] 13.7 Implement adoption management screens (`app/templates/admin/adoptions/`) ✅
  - Applicant list screen (search, filter, pagination).
  - Applicant create/edit screen.
  - Adoption record list screen (filters by cat, applicant, status).
  - Interview record create/edit functions.
  - Responsive layout for mobile and desktop.
  - _Requirements: Requirement 14_

- [x] 13.8 Implement volunteer master management screens (`app/templates/admin/volunteers/`) ✅
  - Volunteer list screen (search, filter).
  - Mobile: card view.
  - Desktop: table view.
  - Action buttons (detail, edit).
  - _Requirements: Requirement 4_

- [x] 13.9 Implement report output screens (`app/templates/admin/reports/`) ✅
  - Daily report output (per-day care-log aggregation).
  - Weekly report output (per-week care-log aggregation).
  - Monthly aggregation output (monthly medical costs and record counts).
  - Per-cat report output (summary per cat).
  - Period selection form.
  - Format selection (PDF/CSV/Excel).
  - Responsive layout for mobile and desktop.
  - _Requirements: Requirement 9.1-9.8_

- [x] 13.10 Implement settings screens (`app/templates/admin/settings/`) ✅
  - Organization information settings.
  - Image settings (max number of images, max file size).
  - Language settings.
  - Security settings (session timeout, login attempt limit).
  - Backup settings (automatic backups, retention period).
  - Responsive layout for mobile and desktop.
  - _Requirements: Requirement 27.6-27.7, Requirement 31.3-31.4_
  - Organization information settings.
  - Image restriction settings.
  - Language settings.
  - User management.
  - _Requirements: Requirement 27.6-27.7, Requirement 31.3-31.4_

- [x] 13.11 Implement login screen (`app/templates/admin/login.html`) ✅
  - Email and password input form.
  - Error message display.
  - _Requirements: Requirement 21.1-21.2_

- [x] 13.12 Implement weight trend chart ✅
  - Display graph using Chart.js (line chart).
  - Show average weight baseline.
  - Show data table alongside the chart.
  - JavaScript implementation (`app/static/js/admin/animal_detail.js`).
  - _Requirements: Requirement 26.1-26.4_

- [x] 13.13 Implement image gallery tab ✅
  - Thumbnail display.
  - Image upload dialog.
  - Zoom/enlarge feature.
  - Sorting (by taken date, by created date).
  - JavaScript implementation (`app/static/js/admin/animal_detail.js`).
  - Auto-add `/media/` prefix to image paths.
  - Image delete functionality.
  - _Requirements: Requirement 27.1-27.5_

- [x] 13.14 Implement search features ✅
  - Real-time search (JavaScript).
  - Advanced search form (gender, age range, status, protected date range).
  - Implemented in the animal ledger list screen.
  - _Requirements: Requirement 24.1-24.5_


## Phase 9: Public Forms (PWA) ✅ Completed

**Context7 MCP usage guidelines:**
- Before implementing Tailwind CSS: use `mcp_context7_get_library_docs` with `/tailwindlabs/tailwindcss` (tokens: 5000).
- Before implementing PWA/Service Worker: use `mcp_context7_resolve_library_id` to search for "Workbox" and fetch documentation.
- Before implementing IndexedDB: use `mcp_context7_resolve_library_id` to search for "IndexedDB" or "Dexie.js" (wrapper library recommended).

### 14. Implement public forms ✅

Implement an unauthenticated care-log input form.

- [x] 14.1 Create public form template (`app/templates/public/care_form.html`) ✅
  - Mobile-optimized with Tailwind CSS.
  - Single-screen layout.
  - Display cat name and face thumbnail.
  - Input fields (time slot, appetite 1–5, energy 1–5, urination yes/no, cleaning done/not done, memo).
  - Volunteer selection list.
  - Fixed-position save button at bottom of screen.
  - _Requirements: Requirement 3.1-3.4, Requirement 13.1-13.5_

- [x] 14.2 Implement API endpoints for public form (`app/api/v1/public.py`) ✅
  - GET /api/v1/public/animals/{animal_id} (fetch cat information)
  - GET /api/v1/public/volunteers (list of active volunteers)
  - `POST /api/v1/public/care-logs` (save record, automatically record IP address and User-Agent).
  - `GET /api/v1/public/care-logs/latest/{animal_id}` (get previous input values).
  - 11 tests implemented (coverage 97.62%).
  - _Requirements: Requirement 3.5-3.7_

- [x] 14.3 Implement "copy previous input" feature (JavaScript) ✅
  - Retrieve latest record.
  - Auto-fill the form.
  - _Requirements: Requirement 3.7_

- [x] 14.4 Implement PWA settings ✅
  - Create `manifest.json` (icons, name, theme color).
  - Implement Service Worker (`app/static/js/sw.js`).
  - Offline caching strategy.
  - _Requirements: Requirement 18.1-18.2_

- [x] 14.5 Implement offline features ✅
  - Temporary storage in IndexedDB.
  - Automatic sync when coming back online.
  - Sync status display (synced, pending, syncing).
  - _Requirements: Requirement 18.3-18.5_

- [x] 14.6 Implement add-to-home-screen prompt ✅
  - Show prompt on first access.
  - _Requirements: Requirement 18.2_

- [x] 14.7 Create behavior tests for public form ✅
  - Tests for form input and save behavior.
  - Tests for offline features.
  - _Requirements: Requirement 3, Requirement 18_

### 14.8 Implement record list features ✅ Completed

Implement features that allow volunteers to check record status.

- [x] 14.8.1 Implement per-cat record list API endpoints (`app/api/v1/public.py`) ✅
  - `GET /api/v1/public/care-logs/animal/{animal_id}` (list of records for the last 7 days).
  - `GET /api/v1/public/care-logs/animal/{animal_id}/{log_id}` (details for a specific record).
  - Return date, time slot, recorder name, and record status (✓/✗).
  - Implement Pydantic schemas (`AnimalCareLogListResponse`, `CareLogSummary`).
  - Implement tests (3 test cases).
  - _Requirements: Requirement 3.11-3.13_

- [x] 14.8.2 Implement all-cats record status API endpoints (`app/api/v1/public.py`) ✅
  - `GET /api/v1/public/care-logs/status/today` (today's record status for all cats).
  - Return each cat's name, face photo, and today's morning/noon/evening record status (✓/✗).
  - Implement Pydantic schemas (`AllAnimalsStatusResponse`, `AnimalStatusSummary`).
  - Implement tests (3 test cases).
  - _Requirements: Requirement 3.14-3.16_

- [x] 14.8.3 Implement per-cat record list page (`app/templates/public/care_log_list.html`) ✅
  - Mobile-optimized with Tailwind CSS.
  - Visually display today's record status (morning/noon/evening).
  - List of records for the last 7 days (date, time slot, recorder name, status).
  - Record detail modal (appetite, energy, urination, cleaning, memo).
  - Link to the record input form.
  - JavaScript implementation (`app/static/js/care_log_list.js`).
  - Image fallback handling.
  - _Requirements: Requirement 3.11-3.13_

- [x] 14.8.4 Implement all-cats record status page (`app/templates/public/all_animals_status.html`) ✅
  - Mobile-optimized with Tailwind CSS.
  - Show list of all cats (face thumbnail, name).
  - Show today's record status per cat (morning ✓/✗, noon ✓/✗, evening ✓/✗).
  - Links to each cat's record input and record list forms.
  - JavaScript implementation (`app/static/js/all_animals_status.js`).
  - Image fallback handling.
  - _Requirements: Requirement 3.14-3.17_

- [x] 14.8.5 Add link from record input form to record list ✅
  - Add a "View record list" button (`app/templates/public/care_form.html`).
  - Navigate to the individual cat's record list page (set dynamically via JavaScript).
  - _Requirements: Requirement 3.10_

- [x] 14.8.6 Create tests for record list features ✅
  - Tests for per-cat record list API (3 test cases)
  - Tests for specific-record detail API (3 test cases)
  - Tests for all-cats record status API (3 test cases)
  - Tests for record-status decision logic
  - _Requirements: Requirement 3_

## Phase 10: Multilingual Support ✅ Completed (100%)

**Context7 MCP usage guidelines:**
- Before implementing i18next: use `mcp_context7_get_library_docs` with `/i18next/i18next` (tokens: 5000).
- For backend localization: confirm Jinja2-based implementation approaches via Context7.

**Completion date**: 2024-11-22

### 15. Implement i18n ✅ Completed

Implement Japanese/English multilingual support.

- [x] 15.1 Create translation files (`app/static/i18n/`) ✅
  - `ja.json` (Japanese) - completed
  - `en.json` (English) - completed
  - Define phrases by category (common UI, cat ledger, care logs, medical records, adoption management, reports, error messages)
  - 17 categories, 800+ translation keys implemented
  - `README.md` (usage and naming-convention documentation)
  - _Requirements: Requirement 19.2, Requirement 19.6_

- [x] 15.2 Implement frontend multilingual support (JavaScript) ✅
  - Integrate i18next library
  - Implement language switcher
  - Save language preference to localStorage
  - Auto-select based on browser language settings
  - _Requirements: Requirement 19.3-19.5_

- [x] 15.3 Implement backend multilingual support (Jinja2) ✅
  - Load translation files in templates
  - Implement language-switching endpoint
  - _Requirements: Requirement 19.3_

- [x] 15.4 Implement multilingual support for PDF reports ✅
  - Switch languages in PDF templates
  - _Requirements: Requirement 19.7_

- [x] 15.5 Create tests for multilingual support ✅
  - Tests for language switching
  - Consistency checks for translation files
  - _Requirements: Requirement 19_

## Phase 11: Security and Logging

### 16. Security hardening

Implement security measures.

- [ ] 16.1 Implement security-header middleware (`app/middleware/security.py`)
  - X-Content-Type-Options: nosniff
  - X-Frame-Options: DENY
  - X-XSS-Protection: 1; mode=block
  - Strict-Transport-Security（HTTPS時）
  - _Requirements: Requirement 22.5_

- [ ] 16.2 Strengthen input validation
  - Strict validation using Pydantic schemas
  - File-upload validation (extension, MIME type, size)
  - _Requirements: Requirement 22.6_

- [ ] 16.3 Implement audit-log features (`app/services/audit_service.py`)
  - Record important operations (cat status changes, adoption decisions, user creation/deletion, master-data changes)
  - Save to `AuditLog` table
  - _Requirements: Requirement 23.1-23.2_

- [ ] 16.4 Implement audit-log screens (`app/templates/admin/audit_logs/`)
  - Chronological list view
  - Filter features (date range, operator, operation type)
  - CSV export
  - _Requirements: Requirement 23.3-23.5_

- [ ] 16.5 Create tests for security features
  - Tests for security headers
  - Tests for audit-log recording
  - _Requirements: Requirement 22, Requirement 23_

### 17. Logging and error handling

Implement logging and error-handling features.

- [ ] 17.1 Implement logging configuration (`app/logging_config.py`)
  - `RotatingFileHandler` (10 MB, 5 files)
  - Log-level configuration (INFO, WARNING, ERROR, CRITICAL)
  - Log format configuration
  - _Requirements: Requirement 29.6_

- [ ] 17.2 エラーハンドリングミドルウェアを実装（app/middleware/error_handler.py）
  - Catch exceptions.
  - Generate error responses (JSON format).
  - Record error logs.
  - _Requirements: Requirement 29.1-29.3_

- [ ] 17.3 Implement error pages (`app/templates/errors/`)
  - Error pages for 400, 401, 403, 404, 500.
  - User-friendly messages.
  - _Requirements: Requirement 29.1_

- [ ] 17.4 Implement database-connection error handling
  - Retry logic.
  - Admin notification.
  - _Requirements: Requirement 29.2_

- [ ] 17.5 Implement network error handling (PWA)
  - Switch to offline mode.
  - Automatic sync after recovery.
  - _Requirements: Requirement 29.4_


## Phase 12: Backup and Data Management

**Context7 MCP usage guidelines:**
- Before implementing APScheduler: use `mcp_context7_get_library_docs` with `/agronholm/apscheduler` (tokens: 5000).
- Confirm FastAPI integration patterns via Context7 documentation.

### 18. Backup features

Implement automatic backup features.

- [ ] 18.1 Implement backup tasks (`app/tasks/backup.py`)
  - Backup SQLite database
  - Backup `/media` directory
  - Timestamped backup filenames
  - Automatically delete backups older than 90 days
  - _Requirements: Requirement 11.1-11.3, Requirement 30.1-30.2_

- [ ] 18.2 Implement scheduler configuration
  - Schedule regular execution with APScheduler (every night at 2:00)
  - Record error logs when backups fail
  - _Requirements: Requirement 11.1, Requirement 11.4_

- [ ] 18.3 Implement data retention management
  - Retain adopted-cat data indefinitely
  - Retain personal data of adoption applicants for 3 years
  - Implement personal-data deletion feature
  - _Requirements: Requirement 30.3-30.5_

- [ ] 18.4 Create tests for backup features
  - Tests for backup execution
  - Tests for deletion of old backups
  - _Requirements: Requirement 11, Requirement 30_

### 19. Initial setup

Implement the first-time setup wizard.

- [ ] 19.1 Implement setup wizard screens (`app/templates/setup/wizard.html`)
  - Step 1: Create initial admin account
  - Step 2: Register organization information
  - Step 3: Basic settings (language, timezone, image limits)
  - _Requirements: Requirement 31.1-31.4_

- [ ] 19.2 Implement setup API endpoints (`app/api/v1/setup.py`)
  - POST /api/v1/setup/admin (create admin)
  - POST /api/v1/setup/organization (register organization information)
  - POST /api/v1/setup/settings (basic settings)
  - POST /api/v1/setup/complete (mark setup as complete)
  - _Requirements: Requirement 31.2-31.5_

- [ ] 19.3 Implement sample-data seeding (`app/db/init_data.py`)
  - One sample cat
  - One sample volunteer
  - _Requirements: Requirement 31.6_

- [ ] 19.4 Implement first-run detection logic
  - If `Users` table is empty, redirect to setup wizard
  - _Requirements: Requirement 31.1_

## Phase 13: OCR Features (Optional)

### 20. OCR processing

Implement features to assist with data migration from paper records.

- [ ] 20.1 Implement OCR service (`app/services/ocr_service.py`)
  - Image/PDF upload handling
  - Run Tesseract OCR
  - Extract text
  - Provide data to editable forms
  - _Requirements: Requirement 17.5-17.7_

- [ ] 20.2 Implement MCP integration
  - Integrate Google Cloud Vision API
  - Integrate AWS Textract
  - Implement OCR-service selection
  - _Requirements: Requirement 17.9_

- [ ] 20.3 Implement Kiro Hook integration
  - Watch specified folders
  - Automatically run OCR when files are added
  - _Requirements: Requirement 17.8_

- [ ] 20.4 Implement OCR API endpoints (`app/api/v1/ocr.py`)
  - POST /api/v1/ocr/upload (upload → OCR processing)
  - GET /api/v1/ocr/status/{job_id} (get processing status)
  - _Requirements: Requirement 17.5, Requirement 17.10_

- [ ] 20.5 Implement OCR result review screens (`app/templates/admin/ocr/`)
  - Display recognized text
  - Edit form
  - Save button
  - _Requirements: Requirement 17.6-17.7_

- [ ] 20.6 Implement progress-notification features
  - Show progress via WebSocket or polling
  - _Requirements: Requirement 17.10_

- [ ] 20.7 Create tests for OCR features
  - Tests for OCR processing
  - Tests for MCP integration
  - _Requirements: Requirement 17_

## Phase 14: Help and Support

### 21. Help features

Implement user-facing help features.

- [ ] 21.1 Create online help pages (`app/templates/help/`)
  - Usage guides for each feature (with images)
  - Frequently Asked Questions (FAQ)
  - _Requirements: Requirement 32.2-32.4_

- [ ] 21.2 Place help buttons
  - Add help buttons to each admin screen
  - Contextual help (show help relevant to the current page)
  - _Requirements: Requirement 32.1-32.2_

- [ ] 21.3 Implement contact form (`app/templates/help/contact.html`)
  - Inquiry input form
  - Email sending feature
  - _Requirements: Requirement 32.5-32.6_

- [ ] 21.4 Create privacy-policy page
  - Clearly state purposes of data collection and usage
  - _Requirements: Requirement 30.6_

## Phase 15: Deployment and Documentation

**Context7 MCP usage guidelines:**
- Before implementing Docker: refer to Render's latest docs (https://render.com/docs/docker).
- Before implementing `render.yaml`: refer to the Blueprint spec (https://render.com/docs/blueprint-spec).
- Before using Persistent Disks: refer to https://render.com/docs/disks.

**Deployment strategy (hackathon PoC):**
- Use **Docker-based deployment** to reliably install OS-dependent packages (WeasyPrint, Pillow, etc.).
- **Two-stage deployment strategy**:
  - **Phase 1 (Free Plan - 1-week PoC):**
    - SQLite (ephemeral, `/tmp/`).
    - Data is assumed to be lost on redeploy (PoC trade-off).
    - No PostgreSQL (simple architecture).
  - **Phase 2 (Starter Plan - for hackathon judging):**
    - SQLite + Persistent Disk (1GB) for production.
    - Data persistence.
- No `render.yaml` required (deploy directly from Render Dashboard UI).
- Use **multi-stage builds** to optimize image size.

**Free Plan constraints (acceptable for PoC):**
- ⚠️ No Persistent Disk → ephemeral filesystem (PoC trade-off).
- ⚠️ Spins down after 15 minutes of inactivity (cold start latency).
- ⚠️ Monthly limit of 750 hours (sufficient for a 1-week demo).
- ✅ No PostgreSQL required (simple architecture).

### 22. Docker containerization (for Free Plan PoC) ✅ Completed

**Completion date**: 2024-11-23
**Deployment target**: Render Free Plan (https://necokeeper.onrender.com)
**Deployment status**: ✅ Running normally (login screen verified).

Implement Docker containerization.

- [x] 22.1 Create Dockerfile (multi-stage build) ✅
  - **Stage 1: Builder** - install dependencies.
    - Python 3.12 base image.
    - WeasyPrint dependencies (`libpango`, `libcairo`, `libgdk-pixbuf`).
    - **Japanese fonts** (`fonts-noto-cjk`, `fonts-ipafont-gothic`).
    - Install Python packages from `requirements.txt`.
  - **Stage 2: Runtime** - lightweight image for production.
    - Copy only required runtime packages.
    - Copy **Japanese fonts** (required for Japanese PDF output).
    - Run as non-root user (security).
    - Configure health check (`HEALTHCHECK`).
  - **Database settings**:
    - SQLite only (ephemeral, `/tmp/necokeeper.db`).
    - Data loss on redeploy (PoC trade-off).
  - **Media file settings**:
    - Ephemeral filesystem (`/tmp/media/`).
  - **Important**: PDFs will not display Japanese correctly without fonts.
  - _Requirements: Requirement 20.1-20.2, Requirement 2.1-2.8（PDF生成）_

- [x] 22.2 Create `.dockerignore` ✅
  - Exclude unnecessary files from build context.
  - `.git`, `.venv`, `__pycache__`, `*.pyc`, `tests/`, `docs/`, `data/`, `media/`, `backups/`.
  - Optimize build time and image size.
  - _Requirements: Requirement 20.1_

- [x] 22.3 Create `docker-compose.yml` (for local development) ✅
  - Define web service.
  - Volume mounts (`data/`, `media/`, `backups/`).
  - Environment variable configuration.
  - Port mapping (`8000:8000`).
  - _Requirements: Requirement 31_

- [x] 22.4 Run Docker build and execution tests ✅
  - Build Docker image locally.
  - Verify container startup (SQLite, ephemeral).
  - Verify health check behavior.
  - **Render Free Plan deployment completed**: https://necokeeper.onrender.com
  - **Verification**: login screen loads correctly; multilingual (Japanese/English) works.
  - _Requirements: Requirement 20.1_

### 23. Render deployment configuration (for Free Plan PoC)

Create deployment configuration for Render.

- [ ] 23.1 Create environment-variable template (`.env.example`)
  - List and describe required environment variables.
  - `DATABASE_URL`: `sqlite:////tmp/necokeeper.db` (ephemeral).
  - `SECRET_KEY`: (recommend auto-generation).
  - `ENVIRONMENT`: `production`.
  - `CORS_ORIGINS`: production domain.
  - `MEDIA_DIR`: `/tmp/media` (ephemeral).
  - _Requirements: Requirement 20.3_

- [ ] 23.2 Create deployment guide (DEPLOY.md)
  - **Free Plan PoC deployment steps (1 week):**
    1. Connect GitHub repository.
    2. In Render Dashboard: New → Web Service.
    3. Language: Docker.
    4. Dockerfile Path: `./Dockerfile`.
    5. Configure environment variables:
       - `DATABASE_URL`: `sqlite:////tmp/necokeeper.db`.
       - `SECRET_KEY`: (auto-generate).
       - `ENVIRONMENT`: `production`.
    6. Plan: Free.
    7. Deploy.
    8. ⚠️ Note: data is lost on redeploy (PoC trade-off).
  - **Migration to Starter Plan (for hackathon judging):**
    1. Upgrade Web Service to Starter Plan ($7/month).
    2. Add Persistent Disk (1GB, `/app/data`).
    3. Update environment variables:
       - `DATABASE_URL`: `sqlite:////app/data/necokeeper.db`.
       - `MEDIA_DIR`: `/app/media`.
    4. Redeploy.
    5. Initialize database (`alembic upgrade head`).
    6. Create initial admin account.
  - **Troubleshooting:**
    - Handling spin-down (Free Plan, 15 minutes).
    - Handling data loss (re-initialize).
    - Memory issues.
  - _Requirements: Requirement 20.5-20.6_

- [ ] 23.3 Update `README.md`
  - Project overview.
  - Main features.
  - Tech stack.
  - Local development setup.
  - Deployment to Render (link to DEPLOY.md).
  - ⚠️ Note Free Plan constraints (data loss).
  - License information.
  - _Requirements: Requirement 20.5_

### 24. Documentation

Prepare development and operations documentation.

- [ ] 24.1 Review and update API specifications
  - Review FastAPI auto-generated OpenAPI (Swagger) specs
  - Accessible at the `/docs` endpoint
  - Enrich descriptions for each endpoint
  - _Requirements: Technical constraint 1_

- [ ] 24.2 開発環境セットアップガイドを作成（DEVELOPMENT.md）
  - **Local development environment:**
    - Install Python 3.12.
    - Create virtual environment (`python -m venv .venv`).
    - Install dependencies (`pip install -r requirements.txt`).
    - Configure environment variables (`.env` file).
    - Initialize database (`alembic upgrade head`).
    - Start development server (`uvicorn app.main:app --reload`).
  - **Docker development environment:**
    - `docker-compose up -d`.
    - Configure hot reloading.
  - **Running tests:**
    - How to run `pytest`.
    - How to measure coverage.
  - **Code quality checks:**
    - `ruff`, `mypy`, `pre-commit`.
  - _Requirements: Requirement 31_

- [ ] 24.3 Create operations manual (`OPERATIONS.md`)
  - **Backup & restore procedures:**
    - Verify automatic backup settings.
    - Run manual backups.
    - Restore procedures.
  - **User management procedures:**
    - Create admin accounts.
    - Reset passwords.
    - Change permissions.
  - **Monitoring:**
    - How to check logs.
    - Error monitoring.
    - Performance monitoring.
  - **Troubleshooting:**
    - Common issues and resolutions.
    - Database connection errors.
    - Out-of-memory issues.
    - Disk space issues.
  - _Requirements: Requirement 11, Requirement 21_

- [ ] 24.4 Create architecture documentation (`ARCHITECTURE.md`)
  - System architecture diagram
  - Database schema
  - API design
  - Authentication/authorization flows
  - File structure
  - Technology stack
  - _Requirements: Technical constraint 1_

- [ ] 24.5 Create contribution guide (`CONTRIBUTING.md`)
  - Development flow (Git workflow).
  - Coding conventions.
  - Pull request guidelines.
  - Testing requirements.
  - _Requirements: 技術的制約1_

## Phase 16: Performance optimization and testing

**Context7 MCP usage guidelines:**
- Before implementing pytest: use `mcp_context7_get_library_docs` with `/pytest-dev/pytest` (tokens: 5000).
- Before implementing pytest-asyncio: use `mcp_context7_resolve_library_id` to search for "pytest-asyncio".
- Before implementing Pillow: use `mcp_context7_get_library_docs` with `/python-pillow/Pillow` (tokens: 5000).

### 25. Performance optimization

Optimize system performance.

- [ ] 25.1 Optimize database indexes
  - Review indexes on frequently searched columns
  - Add composite indexes where appropriate
  - _Requirements: Requirement 28.1-28.2_

- [ ] 25.2 Optimize queries
  - Eliminate N+1 problems (eager loading)
  - Exclude unnecessary columns
  - _Requirements: Requirement 28.1_

- [ ] 25.3 Implement image optimization
  - Automatic resizing on upload
  - Compression processing
  - _Requirements: Requirement 27.9_

- [ ] 25.4 Implement caching strategy
  - Cache the list of active volunteers
  - Cache configuration values
  - _Requirements: Requirement 28.1_

- [ ] 25.5 Run performance tests
  - Measure response times (screen transitions 3s, record save 2s, PDF generation 10s)
  - Concurrent-connection tests (20 users)
  - Large-data tests (100 cats)
  - _Requirements: Requirement 28.1-28.5_

### 26. Integration and E2E tests

Run tests for the entire system.

- [ ] 26.1 Create integration tests (DDD-based)
  - Collaboration tests between domain services
  - Integration tests for application services
  - Integration tests for infrastructure layer
  - Contract tests for API endpoints
  - _Requirements: Requirement 28_

- [ ] 26.2 Create frontend tests
  - Test JavaScript functions with Jest + jsdom
  - Test PWA features (offline sync, caching)
  - _Requirements: Requirement 18_

- [ ] 26.3 Create E2E tests
  - Test user flows (cat registration → record input → report output)
  - Use Playwright
  - _Requirements: Requirement 28_

- [ ] 26.4 Run browser compatibility tests
  - Chrome, Firefox, Safari, Edge (latest + previous)
  - iOS 14+, Android 10+
  - _Requirements: Requirement 28.7-28.8_

- [ ] 26.5 Run security tests
  - SQL injection tests
  - XSS tests
  - CSRF countermeasure tests
  - _Requirements: Requirement 22_

## Phase 17: Final adjustments and release

### 27. Final adjustments

Perform final adjustments before release.

- [ ] 27.1 Verify multilingual support for error messages
  - Ensure all error messages are included in translation files
  - _Requirements: Requirement 19.6_

- [ ] 27.2 Final UI/UX adjustments
  - Verify mobile display
  - Verify button sizes (minimum 44×44 px)
  - _Requirements: Requirement 13.2_

- [ ] 27.3 Verify default configuration values
  - Image limits (max 20 images, max 5 MB)
  - Session timeout (2 hours)
  - Login attempt limit (5 attempts)
  - _Requirements: Requirement 22, Requirement 27.10_

- [ ] 27.4 Verify log output
  - Log-level configuration in production
  - Masking of sensitive information
  - _Requirements: Requirement 29.6_

- [ ] 27.5 Verify HTTPS configuration
  - Enforce HTTPS in production
  - Verify security headers
  - _Requirements: Requirement 22.5_

- [ ] 27.6 Run load tests
  - Verify behavior with 20 concurrent users
  - Verify system availability of 95%
  - _Requirements: Requirement 28.4, Requirement 28.6_

### 28. Release preparation

Perform final preparations for release.

- [ ] 28.1 Deploy to production environment
  - Deploy to Render/Railway/Fly.io
  - Configure environment variables
  - Configure database persistence
  - _Requirements: Requirement 20.1-20.5_

- [ ] 28.2 Seed initial data
  - Run setup wizard
  - Create initial admin account
  - Insert sample data
  - _Requirements: Requirement 31_

- [ ] 28.3 Verify backup configuration
  - Verify automatic backup behavior
  - Verify backup file locations
  - _Requirements: Requirement 11_

- [ ] 28.4 Configure monitoring
  - Monitor error logs
  - Monitor system uptime
  - _Requirements: Requirement 29.2_

- [ ] 28.5 Publish user-facing documentation
  - Publish online help
  - Publish FAQ
  - Publish privacy policy
  - _Requirements: Requirement 32_

- [ ] 28.6 Create release notes
  - List implemented features
  - Known limitations
  - Future roadmap
  - _Requirements: Schedule constraint 1_

---

## Completion

Once all tasks are complete, the MVP of the NecoKeeper system is finished.

Next steps:
1. Collect user feedback.
2. Fix bugs and implement improvements.
3. Plan Phase 2 features (notifications, SNS integration, AI features, etc.).

---

## Progress Summary

### Completion status by Phase
- [x] Phase 1: Project foundation and database (11/11 completed) ✅
- [x] Phase 2: Authentication & authorization system (7/7 completed) ✅
- [x] Phase 3: Animal management features (6/6 completed) ✅
- [x] Phase 4: Care Log features (5/5 completed) ✅
- [x] Phase 4: Volunteer management (4/4 completed) ✅
- [x] Phase 5: Medical record features (4/4 completed) ✅ 2024-11-18
- [x] Phase 5: Medical master data management (5/5 completed) ✅
- [x] Phase 6: PDF generation features (5/5 completed) ✅
- [x] Phase 6: CSV/Excel export features (4/4 completed) ✅ 2024-11-18
- [x] Phase 7: Adoption management features (4/4 completed) ✅ 2024-11-18
- [x] Phase 8: Admin UI (15/15 completed) ✅ 2024-11-18
- [x] Phase 9: Public forms (PWA) (7/7 completed) ✅
- [x] Phase 9: Record list features (6/6 completed) ✅
- [x] Phase 10: Multilingual support (5/5 completed) ✅ 2024-11-22
- [ ] Phase 11: Security and logging (0/10 completed)
- [ ] Phase 12: Backup and data management (0/7 completed)
- [ ] Phase 13: OCR features (optional) (0/7 completed)
- [ ] Phase 14: Help and support (0/4 completed)
- [x] Phase 15: Deployment and documentation (4/11 completed) - Docker containerization completed ✅
- [ ] Phase 16: Performance optimization and tests (0/10 completed)
- [ ] Phase 17: Final polishing and release (0/12 completed)

### Overall progress
**Completed tasks**: 85 / 142 tasks (59.9%)
**MVP Core completed**: Phases 1–10 (backend + admin UI + PWA + record lists + CSV/Excel export + multilingual support) fully completed ✅
**Docker containerization completed**: Phase 15 Task 22 (Render Free Plan deployment completed) ✅
**Production environment**: https://necokeeper.onrender.com (running)
**Estimated remaining time**: ~57–85 hours (1–1.5 hours per task)

### Implemented features
- ✅ Database (all 12 models).
- ✅ JWT-based authentication & authorization (RBAC, permission checks).
- ✅ Animal management (CRUD, search, status management, image gallery).
- ✅ Care Log features (CRUD, CSV export, copy previous values, filters).
- ✅ Volunteer management (CRUD, activity history).
- ✅ Medical record features (CRUD, medical actions master, billing calculation, admin UI) ✅ Completed 2024-11-18.
- ✅ Adoption management (applicants, interviews, adoption records, admin UI) ✅ Completed 2024-11-18.
- ✅ Image upload, optimization, and gallery management.
- ✅ PDF generation (QR cards, imposed cards, paper forms).
- ✅ Public API (unauthenticated care-log input, list, detail).
- ✅ PWA features (`manifest.json`, Service Worker, offline sync).
- ✅ Record list features (per-cat and all-cats status, record detail modals).
- ✅ Admin UI (dashboard, animal ledger, care logs, medical records, adoption management, volunteers, report export, settings, login, weight chart, image gallery, search) ✅ Completed 2024-11-18.
- ✅ Multilingual support (Japanese/English, i18next integration, 800+ translation keys) ✅ Completed 2024-11-22.
- ✅ Docker containerization (multi-stage build, Japanese font support) ✅ Completed 2024-11-23.
- ✅ Render Free Plan deployment (https://necokeeper.onrender.com) ✅ Completed 2024-11-23.
- ✅ Integration tests (232 tests, coverage 84.90%).

### Implemented APIs (30+ endpoints total)
- **Auth**: 2 endpoints.
- **Animal management**: 6 endpoints.
- **Care logs**: 6 endpoints.
- **Volunteer management**: 5 endpoints.
- **Medical records**: 4 endpoints.
- **Medical actions master**: 5 endpoints.
- **PDF generation**: 5 endpoints.
- **Public API**: 7 endpoints (record input, record list, record detail, all-cats status).

### Next tasks to implement (priority)

**Important**: Before implementation, always apply code-structure-review improvements:
- Add `from __future__ import annotations` to all files.
- Use `collections.abc` and `X | None` in type hints.
- Standardize error handling and logging.
- Write complete docstrings.

**Recommended order:**

1. **Phase 15**: Deployment and documentation (priority: highest)
  - Task 22.1–22.4: Docker containerization (simple configuration).
  - Task 23.1–23.3: Render deployment settings (Free Plan PoC).
  - Task 24.1–24.5: Documentation.
  - Estimated time: 11–16 hours.
  - **Reason**: establish hackathon PoC environment early (1-week demo).
  - **Deployment strategy**: two steps, Free Plan (SQLite ephemeral) → Starter Plan (Persistent Disk).

2. **Phase 11**: Security and logging (priority: high)
  - Task 16.1–16.5: security hardening.
  - Task 17.1–17.5: logging and error handling.
  - Estimated time: 10–15 hours.

3. **Phase 12**: Backup and data management (priority: high)
  - Task 18.1–18.4: backup features.
  - Task 19.1–19.4: initial setup.
  - Estimated time: 11–16 hours.

4. **Phase 16**: Performance optimization and tests (priority: medium)
  - Task 25.1–25.5: performance optimization.
  - Task 26.1–26.5: integration and E2E tests.
  - Estimated time: 15–22 hours.
