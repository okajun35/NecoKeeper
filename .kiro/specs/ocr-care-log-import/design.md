# Design Document

## Overview

手書きの猫世話記録表（PDF/画像）をOCR解析し、NecoKeeperのデータベースに自動登録するシステムを設計します。Kiroをオーケストレーターとして、マルチモーダルLLMによる画像解析とHookスクリプトによる自動化を組み合わせた実装を行います。

## Architecture

### System Components

```
┌─────────────────────────────────────────────────────────────┐
│                         User                                 │
│  (Provides image/PDF + prompt with cat ID/name)             │
└────────────────────────┬────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────────────┐
│                      Kiro (Orchestrator)                     │
│  - Receives user prompt and file                            │
│  - Detects file extension (.pdf, .jpg, .png)                │
│  - Invokes appropriate Hook or LLM                          │
│  - Manages workflow and error handling                      │
└────┬────────────────────────────────────┬───────────────────┘
     │                                    │
     │ (if PDF)                          │ (if image)
     ▼                                    ▼
┌─────────────────────┐         ┌──────────────────────────────┐
│  PDF Conversion     │         │  Multimodal LLM              │
│  Hook Script        │         │  (Image Analysis)            │
│  - pdf2image        │         │  - OCR text extraction       │
│  - Convert to JPG   │         │  - Structure understanding   │
│  - Return path      │         │  - JSON generation           │
└──────┬──────────────┘         └────────┬─────────────────────┘
       │                                 │
       │ image path                      │ JSON data
       └────────────┬────────────────────┘
                    ▼
         ┌──────────────────────┐
         │  Data Validation     │
         │  - Schema check      │
         │  - Range validation  │
         │  - Date validation   │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │  Data Registration   │
         │  Hook Script         │
         │  - API authentication│
         │  - Batch registration│
         │  - Error handling    │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │  NecoKeeper API      │
         │  POST /api/v1/       │
         │  care-logs           │
         └──────┬───────────────┘
                │
                ▼
         ┌──────────────────────┐
         │  PostgreSQL Database │
         │  care_logs table     │
         └──────────────────────┘
```

### Workflow Sequence

#### Workflow 1: Image File Processing

```
User → Kiro: "この画像からID5の猫の2025年11月の記録を登録して" + image.jpg
  │
  ├─→ Kiro: Detect file extension (.jpg)
  │
  ├─→ Kiro: Extract cat_id=5, year=2025, month=11 from prompt
  │
  ├─→ Kiro → LLM: Analyze image with structured prompt
  │     │
  │     └─→ LLM: Extract table data → Generate JSON
  │           │
  │           └─→ Return: [
  │                 {"log_date": "2025-11-04", "time_slot": "morning", ...},
  │                 {"log_date": "2025-11-04", "time_slot": "evening", ...},
  │                 ...
  │               ]
  │
  ├─→ Kiro: Validate JSON data
  │
  ├─→ Kiro → Hook: Call data_registration_hook.py with JSON
  │     │
  │     ├─→ Hook: Authenticate with API (POST /api/v1/auth/token)
  │     │
  │     ├─→ Hook: For each record, POST /api/v1/care-logs
  │     │
  │     └─→ Hook: Return summary (success: 10, failed: 0)
  │
  └─→ Kiro → User: "10件の記録を登録しました"
```

#### Workflow 2: PDF File Processing

```
User → Kiro: "このPDFから猫「あみ」の2025年5月の記録を登録して" + record.pdf
  │
  ├─→ Kiro: Detect file extension (.pdf)
  │
  ├─→ Kiro: Extract cat_name="あみ", year=2025, month=5 from prompt
  │
  ├─→ Kiro → Hook: Call pdf_conversion_hook.py with PDF path
  │     │
  │     ├─→ Hook: Convert first page to JPG using pdf2image
  │     │
  │     └─→ Hook: Return image path (tmp/images/record_page1.jpg)
  │
  ├─→ Kiro: Search cat by name "あみ" → animal_id=3
  │
  ├─→ Kiro → LLM: Analyze image with structured prompt
  │     │
  │     └─→ LLM: Extract table data → Generate JSON
  │
  ├─→ Kiro: Validate JSON data
  │
  ├─→ Kiro → Hook: Call data_registration_hook.py with JSON
  │
  └─→ Kiro → User: "15件の記録を登録しました"
```

## Components and Interfaces

### 1. PDF Conversion Hook Script

**File**: `scripts/hooks/pdf_to_image.py`

**Purpose**: Convert PDF first page to image

**Interface**:
```python
def convert_pdf_to_image(pdf_path: str, output_dir: str = "tmp/images") -> str:
    """
    Convert the first page of a PDF to a JPEG image.

    Args:
        pdf_path: Path to the PDF file
        output_dir: Directory to save the output image

    Returns:
        str: Path to the generated image file

    Raises:
        FileNotFoundError: If PDF file does not exist
        PDFConversionError: If conversion fails
    """
```

**Dependencies**:
- `pdf2image` or `PyMuPDF (fitz)`
- `Pillow` for image processing

**Implementation Notes**:
- Convert only the first page
- Output format: PNG
- Filename pattern: `{original_name}_page1.png`
- DPI: 300 for good OCR quality
- Clean up temporary files on error

### 2. Data Registration Hook Script

**File**: `scripts/hooks/register_care_logs.py`

**Purpose**: Register care log data via NecoKeeper API

**Interface**:
```python
def register_care_logs(
    care_logs: list[dict],
    api_base_url: str,
    admin_username: str,
    admin_password: str
) -> dict:
    """
    Register care log records via NecoKeeper API.

    Args:
        care_logs: List of care log data dictionaries
        api_base_url: Base URL of NecoKeeper API
        admin_username: Administrator username
        admin_password: Administrator password

    Returns:
        dict: Summary with success_count, failed_count, errors

    Example:
        {
            "success_count": 10,
            "failed_count": 0,
            "errors": []
        }
    """
```

**Dependencies**:
- `requests` for HTTP requests
- Environment variables for credentials

**Implementation Notes**:
- Authenticate once, reuse token
- Batch registration with error handling
- Continue on individual record failure
- Log all errors with details
- Return detailed summary

### 3. Multimodal LLM Prompt Template

**Purpose**: Structure the prompt for consistent JSON output

**Template**:
```
あなたは手書きの猫世話記録表を解析するOCRアシスタントです。

画像から以下の情報を抽出し、JSON形式で出力してください：

【対象猫】
- animal_id: {animal_id}

【対象期間】
- year: {year}
- month: {month}

【抽出する項目】
1. 日付（M/D形式）
2. 時間帯（朝/昼/夕）
3. ごはん（○/△/×）
4. 元気（○/△/×）
5. 排尿（○/×/数字）
6. 排便（○/×）
7. 嘔吐（○/×）
8. 投薬（○/×）
9. 備考（手書きメモ）

【出力形式】
以下のJSON配列形式で出力してください：

[
  {{
    "animal_id": {animal_id},
    "log_date": "YYYY-MM-DD",
    "time_slot": "morning" | "noon" | "evening",
    "appetite": 1-5,
    "energy": 1-5,
    "urination": true | false,
    "cleaning": false,
    "memo": "排便: あり, 嘔吐: なし, 投薬: なし, 備考: ...",
    "recorder_name": "OCR自動取込",
    "from_paper": true
  }}
]

【マッピングルール】
- ごはん: ○→5, △→3, ×→1
- 元気: ○→5, △→3, ×→1
- 排尿: ○→true, ×→false, 数字→true（回数はmemoに記載）
- 排便/嘔吐/投薬: ○→"あり", ×→"なし"（memoに追記）
- 空欄: デフォルト値を使用
- 朝→morning, 昼→noon, 夕→evening

【注意事項】
- 読み取れない文字は "?" で表記
- 不明確な記号は保守的に解釈
- 日付は {year}-{month:02d}-DD 形式に変換
- 各日付・時間帯ごとに1レコード作成

画像を解析して、上記形式のJSONを出力してください。
```

### 4. Cat Identification Service

**Purpose**: Resolve cat name/ID from user prompt via API

**Interface**:
```python
def identify_cat(
    identifier: str | int,
    api_base_url: str,
    auth_token: str
) -> int:
    """
    Identify cat by ID or name using NecoKeeper API.

    Args:
        identifier: Cat ID (int) or name (str)
        api_base_url: Base URL of NecoKeeper API
        auth_token: Authentication token

    Returns:
        int: animal_id

    Raises:
        CatNotFoundError: If no cat matches
        MultipleCatsFoundError: If multiple cats match

    Implementation:
        1. GET /api/v1/animals (fetch all animals)
        2. Search in memory by ID or name (case-insensitive)
        3. Return matching animal_id
    """
```

**Implementation Notes**:
- Fetch all animals via `GET /api/v1/animals`
- Search in memory (no database dependency)
- Case-insensitive name matching
- Only requires `requests` library
- No SQLAlchemy or database connection needed

## Data Models

### Care Log JSON Schema

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "array",
  "items": {
    "type": "object",
    "required": [
      "animal_id",
      "log_date",
      "time_slot",
      "appetite",
      "energy",
      "urination",
      "cleaning",
      "recorder_name",
      "from_paper"
    ],
    "properties": {
      "animal_id": {
        "type": "integer",
        "minimum": 1
      },
      "log_date": {
        "type": "string",
        "format": "date",
        "pattern": "^\\d{4}-\\d{2}-\\d{2}$"
      },
      "time_slot": {
        "type": "string",
        "enum": ["morning", "noon", "evening"]
      },
      "appetite": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5
      },
      "energy": {
        "type": "integer",
        "minimum": 1,
        "maximum": 5
      },
      "urination": {
        "type": "boolean"
      },
      "cleaning": {
        "type": "boolean"
      },
      "memo": {
        "type": ["string", "null"],
        "maxLength": 1000
      },
      "recorder_name": {
        "type": "string",
        "maxLength": 100
      },
      "from_paper": {
        "type": "boolean",
        "const": true
      },
      "recorder_id": {
        "type": ["integer", "null"]
      },
      "ip_address": {
        "type": ["string", "null"]
      },
      "user_agent": {
        "type": ["string", "null"]
      },
      "device_tag": {
        "type": ["string", "null"]
      }
    }
  }
}
```

### Database Mapping

Existing `care_logs` table structure (from `app/models/care_log.py`):

```python
class CareLog(Base):
    __tablename__ = "care_logs"

    id: Mapped[int]  # Auto-increment
    animal_id: Mapped[int]  # Foreign key to animals
    recorder_id: Mapped[int | None]  # Foreign key to volunteers (nullable)
    recorder_name: Mapped[str]  # Required
    log_date: Mapped[date]  # Required
    time_slot: Mapped[str]  # morning/noon/evening
    appetite: Mapped[int]  # 1-5, default 3
    energy: Mapped[int]  # 1-5, default 3
    urination: Mapped[bool]  # default False
    cleaning: Mapped[bool]  # default False
    memo: Mapped[str | None]  # Optional
    ip_address: Mapped[str | None]  # Optional
    user_agent: Mapped[str | None]  # Optional
    device_tag: Mapped[str | None]  # Optional
    from_paper: Mapped[bool]  # default False
    created_at: Mapped[datetime]  # Auto
    last_updated_at: Mapped[datetime]  # Auto
    last_updated_by: Mapped[int | None]  # Foreign key to users (nullable)
```

**OCR Import Default Values**:
- `recorder_name`: "OCR自動取込"
- `recorder_id`: null
- `from_paper`: True
- `device_tag`: "OCR-Import"
- `cleaning`: False (not in handwritten form)
- `ip_address`: null
- `user_agent`: null
- `last_updated_by`: null

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: JSON Structure Validity
*For any* extracted care log data, the generated JSON must conform to the defined schema with all required fields present and correctly typed.
**Validates: Requirements 1.1, 3.1**

### Property 2: Date Range Consistency
*For any* extracted record with a date, the date must fall within the user-specified year and month range.
**Validates: Requirements 5.2**

### Property 3: Time Slot Mapping Correctness
*For any* handwritten time indicator (朝/昼/夕), the mapped time_slot value must be exactly one of "morning", "noon", or "evening".
**Validates: Requirements 3.9**

### Property 4: Appetite and Energy Range Validity
*For any* extracted appetite or energy value, the value must be an integer between 1 and 5 inclusive.
**Validates: Requirements 3.2, 3.3, 8.2**

### Property 5: Boolean Field Validity
*For any* extracted boolean field (urination, cleaning, from_paper), the value must be a valid boolean (true or false).
**Validates: Requirements 3.4, 8.3**

### Property 6: From Paper Flag Consistency
*For any* record imported via OCR, the from_paper flag must be set to True.
**Validates: Requirements 1.6, 10.1**

### Property 7: Cat Identification Uniqueness
*For any* cat identifier provided by the user, the system must resolve to exactly one animal_id or raise an error.
**Validates: Requirements 4.1, 4.3, 4.4**

### Property 8: PDF First Page Extraction
*For any* PDF file provided, the conversion process must extract exactly the first page as an image.
**Validates: Requirements 2.1, 2.3**

### Property 9: API Authentication Success
*For any* data registration attempt, the Hook must successfully authenticate with the API before attempting to register records.
**Validates: Requirements 6.5**

### Property 10: Batch Registration Atomicity
*For any* batch of care log records, if one record fails validation or registration, the system must continue processing remaining records and report all failures.
**Validates: Requirements 7.4, 7.5**

### Property 11: Memo Field Aggregation
*For any* record with multiple memo-worthy items (defecation, vomiting, medication, notes), all items must be concatenated into the memo field with clear delimiters.
**Validates: Requirements 3.5, 3.6, 3.7, 3.8**

### Property 12: Default Value Application
*For any* record with missing optional fields, the system must apply the defined default values for OCR imports.
**Validates: Requirements 10.2, 10.3, 10.4, 10.5**

## Error Handling

### Error Categories

#### 1. File Processing Errors
- **PDF Not Found**: Notify user, halt process
- **PDF Conversion Failed**: Notify user with error details, halt process
- **Image Not Readable**: Notify user, request manual verification

#### 2. LLM Analysis Errors
- **Image Quality Too Poor**: Notify user, suggest better scan/photo
- **Unreadable Text**: Mark fields as "?" in JSON, notify user
- **Ambiguous Symbols**: Use conservative interpretation, log warning

#### 3. Data Validation Errors
- **Invalid Date**: Skip record, log error, continue processing
- **Out of Range Values**: Skip record, log error, continue processing
- **Missing Required Fields**: Skip record, log error, continue processing

#### 4. Cat Identification Errors
- **Cat Not Found**: Notify user, halt process
- **Multiple Cats Found**: Request user clarification, halt process
- **Invalid Identifier**: Notify user, halt process

#### 5. API Registration Errors
- **Authentication Failed**: Notify user, halt process
- **Network Error**: Retry 3 times, then notify user
- **Individual Record Failed**: Log error, continue with next record
- **Validation Error from API**: Log error with details, continue

### Error Response Format

```json
{
  "status": "partial_success" | "failed",
  "summary": {
    "total_records": 15,
    "successful": 12,
    "failed": 3
  },
  "errors": [
    {
      "record_index": 5,
      "log_date": "2025-11-10",
      "time_slot": "morning",
      "error_type": "validation_error",
      "error_message": "Appetite value 7 is out of range (1-5)",
      "action": "skipped"
    }
  ]
}
```

## Testing Strategy

### Unit Tests

#### PDF Conversion Hook Tests
- Test successful PDF to image conversion
- Test PDF not found error
- Test corrupted PDF handling
- Test output file path generation
- Test cleanup on error

#### Data Registration Hook Tests
- Test successful API authentication
- Test successful batch registration
- Test authentication failure handling
- Test network error retry logic
- Test individual record failure handling
- Test summary generation

#### Cat Identification Tests
- Test identification by ID
- Test identification by name
- Test multiple matches error
- Test no matches error
- Test case-insensitive name matching

#### Data Validation Tests
- Test JSON schema validation
- Test date range validation
- Test appetite/energy range validation
- Test boolean field validation
- Test required field presence

### Integration Tests

#### End-to-End Image Processing
- Test complete workflow from image to database
- Test with various handwriting styles
- Test with poor quality images
- Test with multiple days of records

#### End-to-End PDF Processing
- Test complete workflow from PDF to database
- Test with single-page PDF
- Test with multi-page PDF (only first page processed)

#### Error Recovery Tests
- Test graceful handling of LLM failures
- Test partial batch registration
- Test user notification on errors

### Property-Based Tests

#### Property 1: JSON Structure Validity Test
```python
@given(care_log_data=st.lists(st.builds(CareLogData)))
def test_json_structure_validity(care_log_data):
    """
    Property: Generated JSON must conform to schema
    **Validates: Requirements 1.1, 3.1**
    """
    json_output = generate_json(care_log_data)
    assert validate_json_schema(json_output, CARE_LOG_SCHEMA)
```

#### Property 2: Date Range Consistency Test
```python
@given(
    year=st.integers(min_value=2020, max_value=2030),
    month=st.integers(min_value=1, max_value=12),
    day=st.integers(min_value=1, max_value=28)
)
def test_date_range_consistency(year, month, day):
    """
    Property: Extracted dates must fall within specified range
    **Validates: Requirements 5.2**
    """
    date_str = f"{year}-{month:02d}-{day:02d}"
    record = {"log_date": date_str}
    assert is_date_in_range(record, year, month)
```

#### Property 3: Time Slot Mapping Test
```python
@given(time_indicator=st.sampled_from(["朝", "昼", "夕"]))
def test_time_slot_mapping(time_indicator):
    """
    Property: Time indicators must map to valid time_slot values
    **Validates: Requirements 3.9**
    """
    time_slot = map_time_slot(time_indicator)
    assert time_slot in ["morning", "noon", "evening"]
```

#### Property 4: Value Range Validation Test
```python
@given(
    appetite=st.integers(min_value=1, max_value=5),
    energy=st.integers(min_value=1, max_value=5)
)
def test_value_range_validity(appetite, energy):
    """
    Property: Appetite and energy must be in valid range
    **Validates: Requirements 3.2, 3.3, 8.2**
    """
    record = {"appetite": appetite, "energy": energy}
    assert validate_ranges(record) is True
```

#### Property 5: From Paper Flag Test
```python
@given(care_log=st.builds(CareLogData))
def test_from_paper_flag_consistency(care_log):
    """
    Property: OCR imports must have from_paper=True
    **Validates: Requirements 1.6, 10.1**
    """
    json_record = generate_json_record(care_log, source="ocr")
    assert json_record["from_paper"] is True
```

### Test Data

#### Sample Handwritten Record Images
- Clear handwriting, complete data
- Poor quality scan
- Partially filled records
- Multiple days on one page
- Various handwriting styles

#### Sample JSON Data
```json
[
  {
    "animal_id": 1,
    "log_date": "2025-11-04",
    "time_slot": "morning",
    "appetite": 5,
    "energy": 5,
    "urination": true,
    "cleaning": false,
    "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
    "recorder_name": "OCR自動取込",
    "from_paper": true,
    "recorder_id": null,
    "device_tag": "OCR-Import"
  },
  {
    "animal_id": 1,
    "log_date": "2025-11-04",
    "time_slot": "evening",
    "appetite": 5,
    "energy": 5,
    "urination": false,
    "cleaning": false,
    "memo": "排便: なし, 嘔吐: なし, 投薬: なし, 備考: 夕ご飯もよく食べられました",
    "recorder_name": "OCR自動取込",
    "from_paper": true,
    "recorder_id": null,
    "device_tag": "OCR-Import"
  }
]
```

## Security Considerations

### API Credentials
- Store admin credentials in environment variables
- Never log credentials
- Use secure token storage
- Implement token refresh mechanism

### File Handling
- Validate file extensions
- Limit file size (max 10MB for images, 50MB for PDFs)
- Sanitize file names
- Clean up temporary files
- Restrict file access permissions

### Input Validation
- Validate all user inputs
- Sanitize file paths
- Prevent path traversal attacks
- Validate JSON structure before processing

## Performance Considerations

### PDF Conversion
- Use appropriate DPI (300) for balance between quality and size
- Implement timeout for conversion (30 seconds)
- Clean up temporary files immediately after use

### LLM Analysis
- Implement timeout for LLM requests (60 seconds)
- Cache common patterns if applicable
- Limit image size before sending to LLM

### API Registration
- Batch register records in groups of 10
- Implement connection pooling
- Use async requests if possible
- Implement exponential backoff for retries

## Deployment Considerations

### Dependencies
```
pdf2image==1.16.3  # or PyMuPDF==1.23.8 (choose one)
Pillow==10.1.0
requests==2.31.0
pydantic==2.5.0
python-dotenv==1.0.0
```

**Note**: Scripts are standalone and only require `requests` library. No SQLAlchemy or database dependencies needed.

### Environment Variables
```
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=<secure_password>
OCR_TEMP_DIR=tmp/images
OCR_LOG_FILE=logs/ocr-import.log
```

### Directory Structure
```
scripts/
├── hooks/
│   ├── pdf_to_image.py
│   └── register_care_logs.py
├── utils/
│   ├── cat_identifier.py
│   ├── data_validator.py
│   └── json_schema.py
└── tests/
    ├── test_pdf_conversion.py
    ├── test_data_registration.py
    └── test_integration.py

tmp/
└── images/  # Temporary image storage

logs/
└── ocr-import.log  # Import logs
```

## Future Enhancements

### Phase 2 Features
- Multi-page PDF processing
- Batch processing of multiple files
- OCR confidence scoring
- Manual correction interface
- Historical data comparison
- Automatic cat name recognition from image

### Phase 3 Features
- Real-time preview of extracted data
- Interactive field correction
- Template-based extraction for different form layouts
- Mobile app integration
- Cloud-based OCR service option
