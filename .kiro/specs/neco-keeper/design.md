# Design Document

## Overview

NecoKeeper is a web application that digitizes daily operations of cat rescue organizations. It is built with FastAPI (backend) + SQLite (database) + Tailwind CSS (frontend) and is optimized for small organizations (around 10 members, 10–20 cats).

### Related Documents

- [Authentication & Authorization Specification](./authentication.md): JWT authentication, RBAC, and frontend/backend integration
- [Image Management Specification](./image-management.md): Cat profile photos and image gallery behavior

### Design Principles

1. **Keep it simple**: Avoid over-engineering; this is a PoC/MVP.
2. **Mobile first**: Volunteers must be able to enter records comfortably from smartphones.
3. **Offline friendly**: Support offline recording and automatic sync via PWA.
4. **Low-cost operations**: Must be runnable on free-tier hosting services.
5. **Gradual digitalization**: Designed to co-exist with paper forms during transition.

### Technology Stack

- **Backend**: FastAPI 0.104+ (Python 3.10+)
- **Database**: SQLite 3.35+
- **ORM**: SQLAlchemy 2.0+ (`Mapped`, `mapped_column`)
- **Authentication**: JWT + OAuth2 Password Flow (python-jose + passlib/bcrypt)
- **PDF Generation**: WeasyPrint 60+
- **Frontend UI**: Tailwind CSS 3.3+ (CDN)
- **Frontend JS**: HTMX 2.0+ + Alpine.js 3.x
- **PWA**: Service Worker + IndexedDB
- **Internationalization**: i18next (JSON translation files)
- **OCR**: Tesseract (optional, via MCP integration)
- **Type Checking**: mypy (strict mode)
- **Code Formatting/Lint**: Ruff

### Code Quality Standards

- **Type hints**: Full type hints for all functions (`from __future__ import annotations`, `X | None`, `collections.abc`).
- **Docstrings**: Docstrings for all functions and classes (Args, Returns, Raises, Example).
- **Error handling**: Unified pattern using `HTTPException` and structured logging.
- **Naming conventions**: PostgreSQL-compatible naming to ease future DB migration.
- **Tests**: Pytest with DDD-style layering (domain, application, infrastructure).

## Architecture

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                        Client Layer                          │
├──────────────────────┬──────────────────────────────────────┤
│  Admin UI (Tailwind) │  Public Form (Tailwind + PWA)        │
│  - Admin dashboard   │  - Scan QR → input CareLog           │
│  - Auth required     │  - No authentication required        |
│  - PC / mobile UI    │  - Mobile optimized                  │
│  - HTMX + Alpine.js  │  - Service Worker                    │
└──────────────────────┴──────────────────────────────────────┘
                              ↓ HTTPS
┌─────────────────────────────────────────────────────────────┐
│                     Application Layer                        │
│                      FastAPI Server                          │
├─────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐      │
│  │ Auth Module  │  │ API Endpoints│  │ PDF Generator│      │
│  │ - JWT/OAuth2 │  │ - REST API   │  │ - WeasyPrint │      │
│  │ - RBAC       │  │ - CRUD       │  │ - QR Code    │      │
│  └──────────────┘  └──────────────┘  └──────────────┘      │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                      Data Layer                              │
│                   SQLite Database                            │
├─────────────────────────────────────────────────────────────┤
│  Animals | CareLog | MedicalRecord | Users | Volunteers     │
│  Applicants | Procedures | Medications | Vaccines           │
│  AuditLog | Sessions | Settings                             │
└─────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────┐
│                    Storage Layer                             │
├─────────────────────────────────────────────────────────────┤
│  /data/app.sqlite3  │  /media/photos/  │  /backups/         │
└─────────────────────────────────────────────────────────────┘
```

### Directory Structure

```
necokeeper/
├── app/
│   ├── main.py                 # FastAPI application entry point
│   ├── config.py               # Settings management (environment variables)
│   ├── database.py             # Database connection
│   ├── models/                 # SQLAlchemy models
│   │   ├── animal.py
│   │   ├── care_log.py
│   │   ├── medical_record.py
│   │   ├── user.py
│   │   ├── volunteer.py
│   │   └── ...
│   ├── schemas/                # Pydantic schemas (validation)
│   │   ├── animal.py
│   │   ├── care_log.py
│   │   └── ...
│   ├── api/                    # API endpoints
│   │   ├── v1/
│   │   │   ├── animals.py
│   │   │   ├── care_logs.py
│   │   │   ├── medical_records.py
│   │   │   ├── auth.py
│   │   │   └── ...
│   ├── services/               # Business logic layer
│   │   ├── animal_service.py
│   │   ├── care_log_service.py
│   │   ├── pdf_service.py
│   │   ├── ocr_service.py
│   │   └── ...
│   ├── auth/                   # Authentication & authorization
│   │   ├── jwt.py             # JWT generation/verification
│   │   ├── password.py        # Password hashing
│   │   ├── dependencies.py    # Auth dependencies
│   │   └── permissions.py     # Permission checks
│   ├── templates/              # Jinja2 templates
│   │   ├── admin/              # Admin UI (Tailwind + HTMX + Alpine.js)
│   │   ├── public/             # Public form (Tailwind + PWA)
│   │   └── pdf/                # PDF templates
│   ├── static/                 # Static assets
│   │   ├── css/
│   │   ├── js/
│   │   ├── img/
│   │   └── i18n/               # Translation files (JSON)
│   └── utils/                  # Utilities
│       ├── qr_code.py
│       ├── validators.py
│       └── ...
├── data/
│   └── app.sqlite3             # SQLite database
├── media/
│   └── photos/                 # Cat photos
├── backups/                    # Backup files
├── tests/                      # Test code
├── requirements.txt            # Python dependencies
├── render.yaml                 # Render deployment config
├── railway.json                # Railway deployment config
├── fly.toml                    # Fly.io deployment config
└── README.md                   # Deployment instructions
```


## Data Models

### ER Diagram (Main Entities)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Animals   │1    n │   CareLog    │n    1 │ Volunteers  │
│─────────────│───────│──────────────│───────│─────────────│
│ id (PK)     │       │ id (PK)      │       │ id (PK)     │
│ name        │       │ animal_id(FK)│       │ name        │
│ photo       │       │ recorder_id  │       │ contact     │
│ pattern     │       │ weight       │       │ status      │
│ status      │       │ food         │       │ ...         │
│ ...         │       │ created_at   │       └─────────────┘
└─────────────┘       └──────────────┘
      │1
      │
      │n
┌──────────────┐       ┌─────────────┐
│MedicalRecord │n    1 │    Users    │
│──────────────│───────│─────────────│
│ id (PK)      │       │ id (PK)     │
│ animal_id(FK)│       │ email       │
│ vet_id (FK)  │       │ password    │
│ date         │       │ role        │
│ weight       │       │ ...         │
│ symptoms     │       └─────────────┘
│ ...          │
└──────────────┘

┌─────────────┐       ┌──────────────┐
│ Applicants  │1    n │AdoptionRecord│
│─────────────│───────│──────────────│
│ id (PK)     │       │ id (PK)      │
│ name        │       │ animal_id(FK)│
│ contact     │       │ applicant_id │
│ address     │       │ interview_dt │
│ ...         │       │ decision     │
└─────────────┘       └──────────────┘
```

### Table Definitions

#### Animals (Animal Master)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| name | VARCHAR(100) | YES | NULL | Cat name |
| photo | VARCHAR(255) | NO | - | Face photo path |
| pattern | VARCHAR(100) | NO | - | Coat pattern / color |
| tail_length | VARCHAR(50) | NO | - | Tail length description |
| collar | VARCHAR(100) | YES | NULL | Collar presence / color |
| age | VARCHAR(50) | NO | - | Age / size description |
| gender | VARCHAR(10) | NO | - | Gender (male/female/unknown) |
| ear_cut | BOOLEAN | NO | FALSE | Whether ear-tipped |
| features | TEXT | YES | NULL | Wounds, features, temperament |
| status | VARCHAR(20) | NO | 'protected' | Status |
| protected_at | DATE | NO | CURRENT_DATE | Rescue date |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Indexes**: status, protected_at, name

#### CareLog (Daily Care Log)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| animal_id | INTEGER | NO | - | Cat ID (FK) |
| recorder_id | INTEGER | YES | NULL | Recorder user ID (FK) |
| recorder_name | VARCHAR(100) | NO | - | Recorder display name |
| time_slot | VARCHAR(10) | NO | - | Time slot (morning/noon/evening) |
| appetite | INTEGER | NO | 3 | Appetite (1–5, 5 = best) |
| energy | INTEGER | NO | 3 | Energy (1–5, 5 = best) |
| urination | BOOLEAN | NO | FALSE | Urination (TRUE = yes, FALSE = no) |
| cleaning | BOOLEAN | NO | FALSE | Cage/room cleaning done |
| memo | TEXT | YES | NULL | Free-text memo |
| ip_address | VARCHAR(45) | YES | NULL | IP address |
| user_agent | VARCHAR(255) | YES | NULL | User agent |
| device_tag | VARCHAR(100) | YES | NULL | Device tag |
| from_paper | BOOLEAN | NO | FALSE | Copied from paper form |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Logged at |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Last updated at |
| last_updated_by | INTEGER | YES | NULL | Last updated by user ID (FK) |

**Indexes**: animal_id, created_at, recorder_id, time_slot

#### MedicalRecord (Vet Medical Record)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| animal_id | INTEGER | NO | - | Cat ID (FK) |
| vet_id | INTEGER | NO | - | Vet user ID (FK) |
| date | DATE | NO | - | Visit date |
| time_slot | VARCHAR(20) | YES | NULL | Time slot |
| weight | DECIMAL(5,2) | NO | - | Weight (kg) |
| temperature | DECIMAL(4,1) | YES | NULL | Temperature (°C) |
| symptoms | TEXT | NO | - | Symptoms |
| medical_action_id | INTEGER | YES | NULL | Medical action ID (FK) |
| dosage | INTEGER | YES | NULL | Dosage count |
| other | TEXT | YES | NULL | Other notes (e.g., lot number) |
| comment | TEXT | YES | NULL | Comment |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Last updated at |
| last_updated_by | INTEGER | YES | NULL | Last updated by user ID (FK) |

**Indexes**: animal_id, date, vet_id, medical_action_id

#### Users

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| email | VARCHAR(255) | NO | - | Email address (unique) |
| password_hash | VARCHAR(255) | NO | - | Password hash (bcrypt/argon2) |
| name | VARCHAR(100) | NO | - | Full name |
| role | VARCHAR(20) | NO | 'read_only' | Role |
| is_active | BOOLEAN | NO | TRUE | Active flag |
| failed_login_count | INTEGER | NO | 0 | Failed login attempts |
| locked_until | DATETIME | YES | NULL | Account lock-until timestamp |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Indexes**: email (unique), role

#### Volunteers

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| name | VARCHAR(100) | NO | - | Name |
| contact | VARCHAR(255) | YES | NULL | Contact info |
| affiliation | VARCHAR(100) | YES | NULL | Affiliation |
| status | VARCHAR(20) | NO | 'active' | Activity status |
| started_at | DATE | NO | CURRENT_DATE | Start date |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Indexes**: status, name

#### Applicants (Adoption Applicants)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| name | VARCHAR(100) | NO | - | Name |
| contact | VARCHAR(255) | NO | - | Contact info |
| address | TEXT | YES | NULL | Address |
| family | TEXT | YES | NULL | Family members |
| environment | TEXT | YES | NULL | Living environment |
| conditions | TEXT | YES | NULL | Adoption conditions |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Indexes**: name, contact

#### AdoptionRecord

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| animal_id | INTEGER | NO | - | Cat ID (FK) |
| applicant_id | INTEGER | NO | - | Applicant ID (FK to `Applicants`) |
| interview_date | DATE | YES | NULL | Interview date |
| interview_note | TEXT | YES | NULL | Interview notes |
| decision | VARCHAR(20) | YES | NULL | Decision (approved/rejected/pending) |
| adoption_date | DATE | YES | NULL | Adoption date |
| follow_up | TEXT | YES | NULL | Post-adoption follow-up notes |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Indexes**: animal_id, applicant_id, adoption_date

**Use of `applicant_id`**:
- Link to the `Applicants` table to record who adopted which cat.
- Track interview history, decisions, and post-adoption follow-ups.
- Track cases where the same applicant adopts multiple cats.


#### MedicalActions (Medical Action Master)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| name | VARCHAR(100) | NO | - | Medical action name (drug, vaccine, test, etc.) |
| category | VARCHAR(50) | YES | NULL | Category (drug, vaccine, test, etc.) |
| valid_from | DATE | NO | - | Effective-from date |
| valid_to | DATE | YES | NULL | Effective-to date |
| cost_price | DECIMAL(10,2) | NO | 0.00 | Cost price (2 decimal places) |
| selling_price | DECIMAL(10,2) | NO | 0.00 | Billing unit price (2 decimal places) |
| procedure_fee | DECIMAL(10,2) | NO | 0.00 | Procedure fee (2 decimal places) |
| currency | VARCHAR(3) | NO | 'JPY' | Currency (JPY/USD) |
| dosage_unit | VARCHAR(10) | YES | NULL | Dosage unit (tablet, bottle, times, mL) |
| description | TEXT | YES | NULL | Description / notes |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |
| last_updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Last updated at |
| last_updated_by | INTEGER | YES | NULL | Last updated by user ID (FK) |

**Indexes**: name, valid_from, valid_to

**Dosage unit options**:
- tablet: tablets / capsules
- bottle: vials / bottles / injections
- times: number of procedures / tests
- mL: volume of liquid medicine in milliliters

**Billing formula**:
- Actual billing amount = (`selling_price` × dosage) + `procedure_fee`

#### AnimalImages (Cat Image Gallery)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| animal_id | INTEGER | NO | - | Cat ID (FK) |
| image_path | VARCHAR(255) | NO | - | Image file path |
| taken_at | DATE | YES | NULL | Photo taken date |
| description | TEXT | YES | NULL | Description |
| file_size | INTEGER | NO | 0 | File size (bytes) |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |

**Indexes**: animal_id, taken_at

#### StatusHistory (Status Change History)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| animal_id | INTEGER | NO | - | Cat ID (FK) |
| changed_by | INTEGER | NO | - | Changed by user ID (FK) |
| old_status | VARCHAR(20) | YES | NULL | Previous status |
| new_status | VARCHAR(20) | NO | - | New status |
| changed_at | DATETIME | NO | CURRENT_TIMESTAMP | Changed at |

**Indexes**: animal_id, changed_at

#### AuditLog (Audit Trail)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| user_id | INTEGER | YES | NULL | User ID (FK) |
| action | VARCHAR(50) | NO | - | Action type |
| target_type | VARCHAR(50) | NO | - | Target entity type |
| target_id | INTEGER | YES | NULL | Target entity ID |
| old_value | TEXT | YES | NULL | Old value (JSON serialized) |
| new_value | TEXT | YES | NULL | New value (JSON serialized) |
| ip_address | VARCHAR(45) | YES | NULL | IP address |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Logged at |

**Indexes**: user_id, action, created_at

#### RefreshTokens (Optional Refresh Token Store)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| id | INTEGER | NO | AUTO | Primary key |
| user_id | INTEGER | NO | - | User ID (FK) |
| token | VARCHAR(255) | NO | - | Refresh token (unique) |
| expires_at | DATETIME | NO | - | Expiration timestamp |
| created_at | DATETIME | NO | CURRENT_TIMESTAMP | Created at |
| revoked | BOOLEAN | NO | FALSE | Revoked flag |

**Indexes**: user_id, token (unique), expires_at

**Note**: Access tokens are stateless (JWT only). Refresh tokens are optional and used when long-lived sessions are required.

#### Settings (System Settings)

| Column | Type | NULL | Default | Description |
|---------|-----|------|-----------|------|
| key | VARCHAR(100) | NO | - | Setting key (primary key) |
| value | TEXT | NO | - | Setting value (JSON) |
| description | TEXT | YES | NULL | Description |
| updated_at | DATETIME | NO | CURRENT_TIMESTAMP | Updated at |

**Example keys**:
- `organization_info`: Organization name, address, contact info.
- `image_limits`: Image constraints (max count, max file size).
- `language`: Default language.
- `timezone`: Time zone.

## Components and Interfaces

### API Endpoints

#### Authentication API

```
POST   /api/v1/auth/token          # Login (issue JWT access token)
GET    /api/v1/auth/me             # Get current user info
POST   /api/v1/auth/refresh        # Refresh token (optional)
```

#### Animal Management API

```
GET    /api/v1/animals             # List animals
POST   /api/v1/animals             # Create animal
GET    /api/v1/animals/{id}        # Retrieve animal detail
PUT    /api/v1/animals/{id}        # Update animal
DELETE /api/v1/animals/{id}        # Soft-delete animal
GET    /api/v1/animals/search      # Search animals
POST   /api/v1/animals/import      # Bulk CSV import
GET    /api/v1/animals/export      # Bulk CSV export
```

#### CareLog API

```
GET    /api/v1/care-logs           # List care logs
POST   /api/v1/care-logs           # Create care log
GET    /api/v1/care-logs/{id}      # Retrieve care log detail
PUT    /api/v1/care-logs/{id}      # Update care log
GET    /api/v1/care-logs/export    # Export care logs as CSV
```

#### Medical Record API

```
GET    /api/v1/medical-records     # List medical records
POST   /api/v1/medical-records     # Create medical record
GET    /api/v1/medical-records/{id}# Retrieve medical record detail
PUT    /api/v1/medical-records/{id}# Update medical record
```

#### PDF Generation API

```
POST   /api/v1/pdf/qr-card         # Generate QR card PDF
POST   /api/v1/pdf/paper-form      # Generate paper form PDF
POST   /api/v1/pdf/medical-detail  # Generate medical statement PDF
POST   /api/v1/pdf/report          # Generate aggregate report PDF
```

#### Volunteer Management API

```
GET    /api/v1/volunteers          # List volunteers
POST   /api/v1/volunteers          # Create volunteer
GET    /api/v1/volunteers/{id}     # Retrieve volunteer detail
PUT    /api/v1/volunteers/{id}     # Update volunteer
```

#### Adoption Management API

```
GET    /api/v1/applicants          # List adoption applicants
POST   /api/v1/applicants          # Create applicant
GET    /api/v1/applicants/{id}     # Retrieve applicant detail
PUT    /api/v1/applicants/{id}     # Update applicant
POST   /api/v1/adoptions           # Create adoption record
PUT    /api/v1/adoptions/{id}      # Update adoption record
```

#### Master Data API

```
GET    /api/v1/procedures          # List procedure master
POST   /api/v1/procedures          # Create procedure master record
GET    /api/v1/medications         # List medication master
POST   /api/v1/medications         # Create medication master record
GET    /api/v1/vaccines            # List vaccine master
POST   /api/v1/vaccines            # Create vaccine master record
```

#### Dashboard API

```
GET    /api/v1/dashboard/stats     # Get dashboard stats
GET    /api/v1/dashboard/chart     # Get chart data for graphs
```

#### Image Management API

```
POST   /api/v1/animals/{id}/images # Upload image for cat
GET    /api/v1/animals/{id}/images # List images for cat
DELETE /api/v1/images/{id}         # Delete image
```

#### OCR API

```
POST   /api/v1/ocr/upload          # Upload image/PDF and trigger OCR
GET    /api/v1/ocr/status/{job_id} # Get OCR job status
```

#### Public API (No Authentication)

```
GET    /api/v1/public/animals/{animal_id}              # Get public cat info
GET    /api/v1/public/volunteers                       # List active volunteers
POST   /api/v1/public/care-logs                        # Save care log (IP/User-Agent recorded)
GET    /api/v1/public/care-logs/latest/{animal_id}    # Get latest values for copy
GET    /api/v1/public/care-logs/animal/{animal_id}    # Get last 7 days of logs for cat
GET    /api/v1/public/care-logs/animal/{animal_id}/{log_id}  # Get specific log detail
GET    /api/v1/public/care-logs/status/today          # Get today’s recording status for all cats
```


### Frontend Structure

#### Admin UI (Tailwind CSS + HTMX + Alpine.js)

**Tech stack**:
- **Tailwind CSS 3.3+**: Utility-first CSS framework (via CDN)
- **HTMX 2.0+**: HTML-based dynamic UI updates
- **Alpine.js 3.x**: Lightweight reactive components

**Layout structure**:
```
┌────────────────────────────────────────────────┐
│ Header (logo, user name, logout)                │
├────────┬───────────────────────────────────────┤
│        │ Dashboard                             │
│ Side   │ ┌─────────┬─────────┬─────────┐     │
│ bar    │ │Protected│Adoptable│Adopted  │     │
│        │ │  15     │   8     │   3     │     │
│ - Animals│└─────────┴─────────┴─────────┘     │
│ - Care   │┌───────────────────────────────┐   │
│ - Medical││ CareLog count (last 7 days)  │   │
│ - Adoption││ [Chart]                      │   │
│ - Masters│└───────────────────────────────┘   │
│ - Reports│┌───────────────────────────────┐   │
│ - Settings││ Long-term protected cats      │   │
│        │ │ [Table]                        │   │
│        │ └───────────────────────────────┘   │
└────────┴───────────────────────────────────────┘
```

**Main screens**:
1. Dashboard: KPIs, charts, and alerts.
2. Animal master list: searchable, sortable, paginated listing.
3. Animal detail: tabs (basic info, CareLogs, MedicalRecords, image gallery, weight graph).
4. CareLog list: filters and CSV export.
5. Medical record list: filters and PDF/CSV/Excel export.
6. Adoption management: applicants, interview records, adoption records.
7. Master data: medical actions, volunteers.
8. Reports: daily/weekly/monthly and per-animal reports.
9. Settings: organization info, image limits, language, user management.

**Medical Action master maintenance screen**:
```
┌────────────────────────────────────────────────┐
│ Medical Action Master                          │
├────────────────────────────────────────────────┤
│ [New]  [CSV Import]  [CSV Export]             │
├────────────────────────────────────────────────┤
│ Medical action list (DataTables)              │
│ ┌──────────────────────────────────────────┐ │
│ │ Name │ Category │ Unit │ Price    │ Ops │ │
│ ├──────────────────────────────────────────┤ │
│ │ Antibiotic A │ Drug   │ tablet │ 500 JPY  │ [Edit][Delete]│ │
│ │ Vaccine B    │ Vaccine│ bottle │ 3000 JPY │ [Edit][Delete]│ │
│ │ Blood test   │ Test   │ times  │ 5000 JPY │ [Edit][Delete]│ │
│ └──────────────────────────────────────────┘ │
└────────────────────────────────────────────────┘

Medical action create/edit modal:
┌────────────────────────────────────────────────┐
│ Register Medical Action                        │
├────────────────────────────────────────────────┤
│ Name: [________________] *required             │
│ Category: [select ▼] (drug/vaccine/test/other)│
│ Dosage unit: [select ▼] (tablet/bottle/times/mL)│
│ Cost price: [________] JPY                     │
│ Billing unit price: [________] JPY *required   │
│ Procedure fee: [________] JPY                  │
│ Currency: [JPY ▼]                              │
│ Valid from: [2025-11-15] *required             │
│ Valid to: [________] (empty = still valid)     │
│ Description: [____________________________]    │
│             [____________________________]     │
├────────────────────────────────────────────────┤
│ [Cancel]  [Save]                               │
└────────────────────────────────────────────────┘
```

**Dosage unit options**:
- **tablet**: tablets / capsules
- **bottle**: injections / drips / bottles
- **times**: number of procedures or tests
- **mL (milliliter)**: volume of liquid medicine

#### Public Form (Tailwind CSS + PWA)

**1. CareLog input form**:
```
┌────────────────────────────────────────┐
│ [Cat face photo]                       │
│ Tama (ID: 001)                         │
├────────────────────────────────────────┤
│ Recorder: [select ▼]                  │
│                                        │
│ Weight: [____] kg                      │
│ Food: [____]                           │
│ Water: [____]                          │
│ Excretion: [____]                      │
│ Medication: [____]                     │
│ Memo: [________________]               │
│                                        │
│ [Copy last values]                     │
├────────────────────────────────────────┤
│ [View records] [Save]                  │
└────────────────────────────────────────┘
```

**2. Per-cat CareLog list page**:
```
┌────────────────────────────────────────┐
│ [Cat face photo]                       │
│ Records for Tama (ID: 001)            │
├────────────────────────────────────────┤
│ Today’s recording status:             │
│ Morning: ○  Noon: ×  Evening: ○      │
├────────────────────────────────────────┤
│ Last 7 days:                          │
│ ┌──────────────────────────────────┐ │
│ │ 2025-11-15 Morning ○ Yamada      │ │
│ │ 2025-11-15 Noon    × -           │ │
│ │ 2025-11-15 Evening ○ Sato        │ │
│ │ 2025-11-14 Morning ○ Yamada      │ │
│ │ ...                              │ │
│ └──────────────────────────────────┘ │
├────────────────────────────────────────┤
│ [Enter new record]                     │
└────────────────────────────────────────┘
```

**3. All-cats daily status page**:
```
┌────────────────────────────────────────┐
│ All cats recording status (2025-11-15) │
├────────────────────────────────────────┤
│ ┌──────────────────────────────────┐ │
│ │ [Photo] Tama                     │ │
│ │ Morning: ○  Noon: ×  Evening: ○ │ │
│ │ [Record]                         │ │
│ ├──────────────────────────────────┤ │
│ │ [Photo] Mike                     │ │
│ │ Morning: ○  Noon: ○  Evening: × │ │
│ │ [Record]                         │ │
│ ├──────────────────────────────────┤ │
│ │ [Photo] Kuro                     │ │
│ │ Morning: ×  Noon: ×  Evening: × │ │
│ │ [Record]                         │ │
│ └──────────────────────────────────┘ │
└────────────────────────────────────────┘
```

**PWA features**:
- Service Worker: offline support and cache management.
- `manifest.json`: install to home screen and icons.
- IndexedDB: temporary storage while offline.
- Background Sync: automatic sync when back online.

### Authentication & Authorization Flow

#### JWT Authentication Management

```python
from jose import jwt, JWTError
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

# OAuth2 scheme configuration
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/token")

# JWT settings
SECRET_KEY = "your-secret-key-here"  # to be loaded from env
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 2

# Create JWT access token
def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)

    to_encode.update({"exp": expire, "sub": str(data["user_id"])})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

# Verify token
def verify_token(token: str):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: int = int(payload.get("sub"))
        if user_id is None:
            raise credentials_exception
        return user_id
    except JWTError:
        raise credentials_exception

# Auth dependency
async def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    user_id = verify_token(token)
    user = db.query(User).filter(User.id == user_id).first()
    if user is None or not user.is_active:
        raise HTTPException(status_code=401, detail="User not found or inactive")
    return user

# Login endpoint
@app.post("/api/v1/auth/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = authenticate_user(db, form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token = create_access_token(
        data={"user_id": user.id, "role": user.role},
        expires_delta=timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    )
    return {"access_token": access_token, "token_type": "bearer"}

# Protected endpoint
@app.get("/api/v1/users/me")
async def read_users_me(current_user: User = Depends(get_current_user)):
    return current_user
```

#### Permission Check

```python
# Decorator-style permission check
@require_role(["admin", "vet"])
async def create_medical_record(request: Request):
  # Medical record creation logic
  pass

# Role-based permission matrix
PERMISSIONS = {
  "admin": ["*"],  # Full permissions
  "vet": ["medical:*", "report:read"],
  "staff": ["animal:read", "care:read", "medical:read", "report:*"],
  "read_only": ["*:read"],
  "volunteer": []  # Public form only
}
```

  ### PDF Generation Flow

  #### QR Card Generation

```python
# 1. Generate QR code
qr_url = f"https://necokeeper.example.com/public/care/{animal.id}"
qr_img = qrcode.make(qr_url)

# 2. Render HTML template
html = render_template("pdf/qr_card.html", animal=animal, qr_img=qr_img)

# 3. Generate PDF with WeasyPrint
pdf = HTML(string=html).write_pdf()

# 4. Return response
return Response(pdf, media_type="application/pdf")
```

#### Multi-up Card Generation

```python
# Arrange 2×5 cards on an A4 page
animals_list = [animals[i:i+10] for i in range(0, len(animals), 10)]
for page_animals in animals_list:
    html += render_template("pdf/qr_card_grid.html", animals=page_animals)
```

### Internationalization

#### Translation File Structure

```json
// static/i18n/ja.json
{
  "common": {
    "save": "保存",
    "cancel": "キャンセル",
    "delete": "削除"
  },
  "animal": {
    "name": "名前",
    "pattern": "柄・色",
    "status": "ステータス"
  },
  "care_log": {
    "weight": "体重",
    "food": "食事量"
  }
}

// static/i18n/en.json
{
  "common": {
    "save": "Save",
    "cancel": "Cancel",
    "delete": "Delete"
  },
  "animal": {
    "name": "Name",
    "pattern": "Pattern/Color",
    "status": "Status"
  }
}
```

#### Language Switching

```javascript
// Frontend (i18next)
i18next.init({
  lng: localStorage.getItem('language') || navigator.language.split('-')[0],
  fallbackLng: 'ja',
  resources: {
    ja: { translation: jaTranslation },
    en: { translation: enTranslation }
  }
});

// Backend (Jinja2)
{% set lang = request.cookies.get('language', 'ja') %}
{{ t[lang]['common']['save'] }}
```

## Error Handling

### Error Categories

1. **Validation Error** (400 Bad Request)
  - Missing required fields.
  - Invalid format (email, date, etc.).
  - Out-of-range values.

2. **Authentication Error** (401 Unauthorized)
  - Login failure.
  - Session/token expired.

3. **Authorization Error** (403 Forbidden)
  - Insufficient permissions.

4. **Resource Not Found** (404 Not Found)
  - Non-existent cat ID.
  - Non-existent record.

5. **Server Error** (500 Internal Server Error)
  - Database connection error.
  - PDF generation error.
  - OCR processing error.

### Error Response Format

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "There is an error in the submitted data.",
    "details": [
      {
        "field": "weight",
        "message": "Weight must be within the range 0.1–50.0 kg."
      }
    ]
  }
}
```

### Error Logging

```python
import logging

logger = logging.getLogger(__name__)

# Log levels
# INFO: normal operations
# WARNING: warnings (e.g., login failures)
# ERROR: errors (e.g., DB errors)
# CRITICAL: fatal errors (system down)

logger.error(
    f"Database error: {str(e)}",
    extra={
        "user_id": user.id,
        "endpoint": request.url.path,
        "method": request.method
    }
)
```

## Testing Strategy

### Test Policy

1. **Unit tests**: Each service and utility function.
2. **Integration tests**: API endpoints.
3. **E2E tests**: Main user flows (optional, but desirable).

### Test Tooling

**Backend tests:**
- **pytest**: test framework.
- **pytest-asyncio**: async test support.
- **httpx**: API client for tests.
- **faker**: test data generation.

**Frontend tests:**
- **Jest**: JavaScript test framework.
- **Playwright**: E2E tests (optional).
- **jsdom**: DOM simulation for unit tests.

### Target Coverage

- Service layer: 80% or higher.
- API layer: 70% or higher.
- Overall: 60% or higher.

### Test Design Policy (DDD style inspired by t-wada)

**Test structure:**
- **Domain logic tests**: Validate business rules (unit tests).
- **Application service tests**: Validate use cases (integration tests).
- **Infrastructure tests**: Validate external dependencies (integration tests).

**Test examples**

```python
# tests/domain/test_animal_domain.py
import pytest
from app.domain.animal import Animal, AnimalStatus

def test_animal_can_be_adopted_when_ready():
    """Cats in READY_FOR_ADOPTION status can be adopted (domain rule)."""
    animal = Animal(name="たま", status=AnimalStatus.READY_FOR_ADOPTION)
    assert animal.can_be_adopted() is True

def test_animal_cannot_be_adopted_when_under_treatment():
    """Cats UNDER_TREATMENT cannot be adopted (business rule)."""
    animal = Animal(name="たま", status=AnimalStatus.UNDER_TREATMENT)
    assert animal.can_be_adopted() is False

# tests/application/test_animal_service.py
@pytest.mark.asyncio
async def test_register_new_animal_use_case(db_session):
    """Use case: register a new cat."""
    service = AnimalService(db_session)
    command = RegisterAnimalCommand(
        name="たま",
        pattern="三毛",
        gender="female"
    )
    animal = await service.register_animal(command)
    assert animal.name == "たま"
    assert animal.status == AnimalStatus.PROTECTED

# tests/infrastructure/test_animal_repository.py
@pytest.mark.asyncio
async def test_animal_repository_persistence(db_session):
    """Persistence test for AnimalRepository."""
    repo = AnimalRepository(db_session)
    animal = Animal(name="たま", pattern="三毛")
    saved_animal = await repo.save(animal)
    found_animal = await repo.find_by_id(saved_animal.id)
    assert found_animal.name == "たま"
```


## Deployment

### Hosting Service Comparison

| Service | Persistent storage | Free tier | SQLite support | Recommendation |
|---------|--------------------|----------|----------------|----------------|
| Render  | Yes (Disk)         | 750h/month | Yes          | ★★★ |
| Railway | Yes (Volume)       | $5 credit/month | Yes      | ★★★ |
| Fly.io  | Yes (Volume)       | 3GB/month | Yes          | ★★☆ |

### Render Deployment Config

```yaml
# render.yaml
services:
  - type: web
    name: necokeeper
    env: python
    buildCommand: pip install -r requirements.txt
    startCommand: uvicorn app.main:app --host 0.0.0.0 --port $PORT
    envVars:
      - key: DATABASE_URL
        value: /data/app.sqlite3
      - key: SECRET_KEY
        generateValue: true
      - key: PYTHON_VERSION
        value: 3.11.0
    disk:
      name: necokeeper-data
      mountPath: /data
      sizeGB: 1
```

### Railway Deployment Config

```json
{
  "$schema": "https://railway.app/railway.schema.json",
  "build": {
    "builder": "NIXPACKS"
  },
  "deploy": {
    "startCommand": "uvicorn app.main:app --host 0.0.0.0 --port $PORT",
    "restartPolicyType": "ON_FAILURE",
    "restartPolicyMaxRetries": 10
  }
}
```

### Fly.io Deployment Config

```toml
# fly.toml
app = "necokeeper"
primary_region = "nrt"

[build]
  builder = "paketobuildpacks/builder:base"

[env]
  PORT = "8080"

[http_service]
  internal_port = 8080
  force_https = true
  auto_stop_machines = true
  auto_start_machines = true
  min_machines_running = 0

[[mounts]]
  source = "necokeeper_data"
  destination = "/data"
```

### Environment Variables

```bash
# .env.example
DATABASE_URL=sqlite:///data/app.sqlite3
SECRET_KEY=your-secret-key-here
ALLOWED_HOSTS=localhost,127.0.0.1
DEBUG=False
LOG_LEVEL=INFO

# Optional (OCR features)
OCR_ENABLED=False
TESSERACT_PATH=/usr/bin/tesseract
GOOGLE_CLOUD_VISION_API_KEY=
AWS_TEXTRACT_ACCESS_KEY=
```

### Backup Strategy

#### Automatic Backup

```python
# app/tasks/backup.py
import shutil
from datetime import datetime
from pathlib import Path

async def backup_database():
    """Back up database and media files."""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = Path("/backups")
    backup_dir.mkdir(exist_ok=True)

    # SQLite backup
    db_path = Path("/data/app.sqlite3")
    backup_db = backup_dir / f"app_{timestamp}.sqlite3"
    shutil.copy2(db_path, backup_db)

    # Media files backup
    media_path = Path("/media")
    backup_media = backup_dir / f"media_{timestamp}.tar.gz"
    shutil.make_archive(backup_media.with_suffix(""), "gztar", media_path)

    # Delete backups older than 90 days
    cutoff = datetime.now() - timedelta(days=90)
    for backup_file in backup_dir.glob("*"):
        if backup_file.stat().st_mtime < cutoff.timestamp():
            backup_file.unlink()
```

#### Scheduling

```python
# app/main.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()
  scheduler.add_job(backup_database, "cron", hour=2, minute=0)  # Every day at 2:00
scheduler.start()
```

## Security Considerations

### Security Measures

1. **Authentication & Authorization**
  - Password hashing with bcrypt/passlib.
  - JWT + OAuth2 Password Flow.
  - Login attempt limit (lock for 15 minutes after 5 failures).
  - Access token expiry (2 hours).
  - Bearer token authentication (`Authorization: Bearer {token}`).

2. **Input Validation**
  - Validation with Pydantic.
  - SQL injection protection via SQLAlchemy ORM.
  - File upload validation (extension, MIME type, size).

3. **Transport Security**
  - HTTPS required in production.
  - HSTS (HTTP Strict Transport Security).
  - Secure flag for cookies.

4. **Data Protection**
  - Optional encryption for personally identifiable information.
  - Regular backups.
  - Audit logging.

5. **Vulnerability Mitigation**
  - Regular dependency updates.
  - Security headers.
  - Rate limiting for APIs.

### Security Headers

```python
# app/middleware/security.py
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        response = await call_next(request)
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains"
        return response
```

## Performance Optimization

### Database Optimization

1. **Index design**
  - Add indexes to frequently queried columns.
  - Use composite indexes where appropriate.

2. **Query optimization**
  - Avoid N+1 problems with eager loading.
  - Implement pagination.
  - Select only necessary columns.

3. **Connection pooling**
  - Configure SQLAlchemy connection pool.
  - Max connections: around 20.

### Caching Strategy

```python
# app/cache.py
from functools import lru_cache

@lru_cache(maxsize=128)
def get_active_volunteers():
    """Cache the list of active volunteers."""
    return db.query(Volunteer).filter(Volunteer.status == "active").all()
```

### Image Optimization

```python
# app/utils/image.py
from PIL import Image

def optimize_image(image_path: Path, max_size: tuple = (1920, 1080)):
    """Optimize image (resize and compress)."""
    img = Image.open(image_path)
    img.thumbnail(max_size, Image.Resampling.LANCZOS)
    img.save(image_path, optimize=True, quality=85)
```

## Monitoring and Logging

### Logging Configuration

```python
# app/logging_config.py
import logging
from logging.handlers import RotatingFileHandler

def setup_logging():
    logger = logging.getLogger("necokeeper")
    logger.setLevel(logging.INFO)

    # Rotating file handler
    file_handler = RotatingFileHandler(
        "logs/app.log",
        maxBytes=10485760,  # 10MB
        backupCount=5
    )
    file_handler.setFormatter(
        logging.Formatter(
            "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        )
    )
    logger.addHandler(file_handler)

    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(
        logging.Formatter("%(levelname)s: %(message)s")
    )
    logger.addHandler(console_handler)
```

### Metrics Collection

```python
# app/middleware/metrics.py
from prometheus_client import Counter, Histogram
import time

request_count = Counter("http_requests_total", "Total HTTP requests", ["method", "endpoint", "status"])
request_duration = Histogram("http_request_duration_seconds", "HTTP request duration")

class MetricsMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.time()
        response = await call_next(request)
        duration = time.time() - start_time

        request_count.labels(
            method=request.method,
            endpoint=request.url.path,
            status=response.status_code
        ).inc()
        request_duration.observe(duration)

        return response
```

## Migration Strategy

### Initial Data Seeding

```python
# app/db/init_data.py
async def init_database():
    """Insert initial data into the database."""
    # Initial admin account
    admin_user = User(
        email="admin@example.com",
        password_hash=hash_password("changeme"),
        name="管理者",
        role="admin"
    )
    db.add(admin_user)

    # Sample cat data
    sample_animal = Animal(
        name="サンプル猫",
        pattern="キジトラ",
        gender="female",
        age="成猫",
        status="保護中"
    )
    db.add(sample_animal)

    # Sample volunteer data
    sample_volunteer = Volunteer(
        name="サンプルボランティア",
        status="active"
    )
    db.add(sample_volunteer)

    await db.commit()
```

### Database Migration

```python
# alembic/versions/001_initial.py
from alembic import op
import sqlalchemy as sa

def upgrade():
    op.create_table(
        "animals",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(100), nullable=True),
        sa.Column("pattern", sa.String(100), nullable=False),
        # ... other columns
        sa.PrimaryKeyConstraint("id")
    )
    op.create_index("ix_animals_status", "animals", ["status"])

def downgrade():
    op.drop_index("ix_animals_status", table_name="animals")
    op.drop_table("animals")
```

## Future Enhancements

### Phase 2 Feature Candidates

1. **Notification features**
  - Email notifications (adoption decisions, visit reminders).
  - Push notifications (PWA).

2. **Reporting improvements**
  - Custom report builder.
  - Additional chart types (pie, bar, etc.).

3. **SNS integration**
  - Auto-post adoptable cats (X/Twitter, Instagram).
  - Automatic image resize/optimization for SNS.

4. **Mobile app**
  - React Native / Flutter.
  - Native camera integration.

5. **AI features**
  - Cat face recognition.
  - Anomaly detection for health status.

6. **Multi-tenant support**
  - Manage multiple organizations.
  - Optional data sharing across organizations.

## Appendix

### Development Environment Setup

```bash
# Create Python virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Initialize database
alembic upgrade head
python -m app.db.init_data

# Start development server
uvicorn app.main:app --reload --port 8000
```

### Main Library Versions

```
fastapi==0.104.1
uvicorn[standard]==0.24.0
sqlalchemy==2.0.23
pydantic==2.5.0
python-multipart==0.0.6
jinja2==3.1.2
weasyprint==60.1
qrcode[pil]==7.4.2
bcrypt==4.1.1
itsdangerous==2.1.2
python-dotenv==1.0.0
alembic==1.12.1
pytest==7.4.3
pytest-asyncio==0.21.1
httpx==0.25.1
```

### References

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [WeasyPrint Documentation](https://doc.courtbouillon.org/weasyprint/)
- [Tailwind CSS Documentation](https://tailwindcss.com/docs)
- [HTMX Documentation](https://htmx.org/docs/)
- [Alpine.js Documentation](https://alpinejs.dev/)
- [PWA Documentation](https://web.dev/progressive-web-apps/)
