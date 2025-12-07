# Design Document

## Overview

This document designs a system that performs OCR analysis on handwritten cat care log sheets (PDF/images) and automatically registers the results into the NecoKeeper database. Kiro acts as the orchestrator, combining multimodal LLM-based image analysis with automation using Hook scripts.

## Architecture

### System Components - 3-Phase Hook Workflow

**Design Rationale**: A phased workflow allows human review and correction at each phase. This makes it possible to fix OCR misrecognitions in advance and guarantees data consistency.

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PDF → Image (automatic Hook)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: Place PDF in tmp/pdfs/                               │
│    ↓                                                        │
│  Kiro Hook: Detect file save                                │
│    ↓                                                        │
│  pdf_to_image.py: PDF → PNG conversion                      │
│    ↓                                                        │
│  Output: Write images to tmp/images/                        │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Image → JSON (manual + Kiro chat)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: Attach image in Kiro chat                            │
│    ↓                                                        │
│  User: "For cat ID 12, convert 11/14–11/23 data to JSON"    │
│    ↓                                                        │
│  Kiro: Run OCR analysis with multimodal LLM                 │
│    ↓                                                        │
│  Kiro: Generate JSON                                        │
│    ↓                                                        │
│  User: Review and (if needed) edit the JSON                 │
│    ↓                                                        │
│  User: Save to tmp/json/                                    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                 ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: JSON → Database (automatic Hook)                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kiro Hook: Detect file save                                │
│    ↓                                                        │
│  register_care_logs.py: Read JSON                           │
│    ↓                                                        │
│  API authentication (POST /api/v1/auth/token)               │
│    ↓                                                        │
│  Data registration (POST /api/v1/care-logs)                 │
│    ↓                                                        │
│  Output: Result log + move processed file                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                 ↓
            ┌──────────────────┐
            │  PostgreSQL DB   │
            │  care_logs table │
            └──────────────────┘
```

### Benefits of 3-Phase Workflow

1. **Human review points**
  - JSON can be reviewed and corrected in Phase 2
  - OCR errors can be fixed beforehand
  - Ensures data quality

2. **Phased processing**
  - Each phase runs independently
  - Easy to isolate errors
  - Easy to rerun

3. **Flexibility**
  - Can skip PDF and start directly from images
  - JSON can also be created manually and registered
  - Supports partial automation

4. **Leveraging Kiro’s strengths**
  - Automation via file-watching Hooks
  - Interactive corrections via chat
  - Utilizes LLM’s image analysis capabilities

### Workflow Sequence

#### Workflow 1: Direct Image Processing (Image → JSON → Database)

**Use Case**: When the user already has image files

```
User → File System: Place images in tmp/images/ (or they already exist)
  │
  ├─→ User → Kiro Chat: Attach image
  │                     "For cat ID 12, convert data from 2024-11-14 to 11-23
  │                      to JSON and save as tmp/json/care_log_20241114.json"
  │
  ├─→ Kiro: Extract from user prompt
  │     - animal_id: 12
  │     - start_date: 2024-11-14
  │     - end_date: 2024-11-23
  │     - output_path: tmp/json/care_log_20241114.json
  │
  ├─→ Kiro → LLM: Multimodal analysis
  │     │         Prompt: "animal_id=12, period=2024-11-14 to 11-23.
  │     │                  Generate JSON from this image."
  │     │
  │     └─→ LLM: OCR analysis → JSON generation
  │           [
  │             {"animal_id": 12, "log_date": "2024-11-14", "time_slot": "morning", ...},
  │             {"animal_id": 12, "log_date": "2024-11-14", "time_slot": "noon", ...},
  │             ...
  │           ]
  │
  ├─→ Kiro: Save JSON to file
  │     tmp/json/care_log_20241114.json
  │
  ├─→ User: Review and, if necessary, edit the JSON
  │
  ├─→ Kiro Hook: Detect file save (tmp/json/*.json)
  │     │
  │     └─→ Automatically run register_care_logs.py
  │           │
  │           ├─→ API authentication (POST /api/v1/auth/token)
  │           │
  │           ├─→ Data registration (POST /api/v1/care-logs)
  │           │
  │           └─→ Output result log + move file
  │
  └─→ Kiro → User: "✅ Registered 24 records."
```

**Benefits**:
1. **Human review**: JSON can be checked and corrected before saving
2. **Flexibility**: Can start directly from images
3. **Automation**: After JSON is saved, DB registration runs automatically

#### Workflow 2: Full PDF Processing (PDF → Image → JSON → Database)

**Use Case**: When the user starts from a PDF file

```
User → File System: Place PDF in tmp/pdfs/
  │                 Example: tmp/pdfs/care_log_202411.pdf
  │
  ├─→ Kiro Hook: Detect file save (tmp/pdfs/*.pdf)
  │     │
  │     └─→ Automatically run pdf_to_image.py
  │           │
  │           ├─→ Read PDF
  │           │
  │           ├─→ Convert first page to PNG
  │           │
  │           └─→ Save as tmp/images/care_log_202411_page1.png
  │
  ├─→ Kiro → User: "✅ PDF conversion complete: tmp/images/care_log_202411_page1.png
  │                 Next: open the image in Kiro Chat and convert to JSON."
  │
  ├─→ User → Kiro Chat: Attach image
  │                     "For cat ID 12, convert data from 2024-11-14 to 11-23
  │                      to JSON and save as tmp/json/care_log_20241114.json"
  │
  ├─→ Kiro → LLM: Multimodal analysis
  │     │
  │     └─→ LLM: OCR analysis → JSON generation
  │
  ├─→ Kiro: Save JSON to file
  │     tmp/json/care_log_20241114.json
  │
  ├─→ User: Review and, if necessary, edit the JSON
  │
  ├─→ Kiro Hook: Detect file save (tmp/json/*.json)
  │     │
  │     └─→ Automatically run register_care_logs.py
  │           │
  │           ├─→ API authentication
  │           │
  │           ├─→ Data registration
  │           │
  │           └─→ Output result log
  │
  └─→ Kiro → User: "✅ Registered 24 records."
```

**Benefits**:
1. **Full automation**: PDF placement → image conversion is automatic
2. **Human review**: JSON can be reviewed and corrected during generation
3. **Phased processing**: Status can be checked at each phase

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

### 3. User Prompt Examples

**Purpose**: Example prompts that users can use in Kiro chat

**Example 1: Basic usage**
```
This is the record for cat ID 12 from November 14 to 23, 2024.
Convert it to JSON according to the spec of register_care_logs.py
for cat care log registration and save it as tmp/json/care_log_20241114.json.
```

**Example 2: Spanning across years**
```
This is the record for cat ID 4 from November 15 to 25, 2024.
Convert it to JSON according to the spec of scripts/hooks/register_care_logs.py
and save it as tmp/json/care_log_202411.json.
```

**Example 3: Short form**
```
ID12, 11/14-11/23, convert to JSON and save to tmp/json/.
```

### 4. Kiro's Internal Prompt Template

**Purpose**: LLM prompt template that Kiro uses internally

**Template**:
```
You are an OCR assistant that analyzes handwritten cat care log sheets.

Information specified by the user:
- Cat ID: {animal_id}
- Target period: {start_date} to {end_date}

Use this information to extract care records from the image.

[Important]
- Set animal_id to {animal_id} for all records
- Extract dates only within the range from {start_date} to {end_date}
- Ignore dates outside the range

[Items to extract]
1. Date (M/D format or 11/14 format)
2. Time slot (morning/noon/evening in Japanese: 朝/昼/夕)
3. Water intake (○/×)
4. Energy (○/△/×)
5. Urination (○/×)
6. Cleaning (○/×)
7. Memo (handwritten notes)
8. Recorder (handwritten name)

[Output format]
Output a JSON array in the following format:

[
  {{
    "animal_id": {animal_id},
    "log_date": "YYYY-MM-DD",
    "time_slot": "morning" | "noon" | "evening",
    "appetite": 1-5,
    "energy": 1-5,
    "urination": true | false,
    "cleaning": true | false,
    "memo": "Stool: none, Vomit: none, Meds: none, Notes: ...",
    "recorder_name": "OCR Auto Import",
    "from_paper": true,
    "recorder_id": null,
    "device_tag": "OCR-Import",
    "ip_address": null,
    "user_agent": null
  }}
]

[Mapping rules]
- Water intake: ○ → appetite=5, × → appetite=3, blank → appetite=3
- Energy: ○ → energy=5, △ → energy=3, × → energy=1, blank → energy=3
- Urination: ○ → true, × → false, blank → false
- Cleaning: ○ → true, × → false, blank → false
- 朝 → morning, 昼 → noon, 夕 → evening
- Date: convert M/D format to YYYY-MM-DD (use the year of {start_date} for YYYY)

[Memo field handling]
- If there is a handwritten memo: "Stool: none, Vomit: none, Meds: none, Notes: {handwritten memo}"
- If there is no handwritten memo: "Stool: none, Vomit: none, Meds: none"
- If there is a recorder name: append to notes "Notes: {recorder name}"

[Notes]
- Use "?" for unreadable characters
- Interpret ambiguous symbols conservatively (treat as blank)
- Create one record per date and time slot
- Always use {animal_id} for animal_id (do not read it from the image)
- Do not output data outside the specified date range

[Example]
If the image has "11/14 朝 ○ ○ × ×":
{{
  "animal_id": {animal_id},
  "log_date": "{start_date.year}-11-14",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": false,
  "cleaning": false,
  "memo": "Stool: none, Vomit: none, Meds: none",
  "recorder_name": "OCR Auto Import",
  "from_paper": true,
  "recorder_id": null,
  "device_tag": "OCR-Import",
  "ip_address": null,
  "user_agent": null
}}

Analyze the image and output JSON in the above format.
```

**Design Rationale**:
- Including the user-specified `animal_id` in the prompt prevents OCR misrecognition
- Explicitly specifying the date range prevents data outside the range from being included
- Providing concrete examples improves LLM output quality

### 4. Kiro Hook Scripts

#### Hook 1: PDF to Image Converter (automatic execution)

**File**: `.kiro/hooks/pdf_to_image_hook.py`

**Trigger**: On file save (`tmp/pdfs/*.pdf`)

**Purpose**: Automatically convert the first page of a PDF to an image

**Implementation**:
```python
"""
Kiro Hook: PDF → Image automatic conversion
Trigger: when a file is saved to tmp/pdfs/*.pdf
"""
import sys
from pathlib import Path
from scripts.hooks.pdf_to_image import convert_pdf_to_image

def main():
    pdf_path = sys.argv[1]  # File path passed from Kiro

    try:
        # PDF → PNG conversion
        image_path = convert_pdf_to_image(
            pdf_path=pdf_path,
            output_dir="tmp/images"
        )

        print(f"✅ PDF conversion complete: {image_path}")
        print(f"")
        print(f"Next steps:")
        print(f"1. Open the image in Kiro chat")
        print(f"2. Instruct: 'For cat ID <CatID>, convert data from <StartDate> to <EndDate> to JSON")
        print(f"   and save it as tmp/json/<filename>.json'")

    except Exception as e:
        print(f"❌ PDF conversion error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Hook 2: JSON to Database Registrar (automatic execution)

**File**: `.kiro/hooks/register_care_logs_hook.py`

**Trigger**: On file save (`tmp/json/*.json`)

**Purpose**: Automatically register JSON files into the database

**Implementation**:
```python
"""
Kiro Hook: JSON → Database automatic registration
Trigger: when a file is saved to tmp/json/*.json
"""
import sys
import json
from pathlib import Path
from scripts.hooks.register_care_logs import register_care_logs
from scripts.utils.logging_config import setup_logger

logger = setup_logger("register_care_logs_hook")

def main():
    json_path = sys.argv[1]  # File path passed from Kiro

    try:
        # Read JSON file
        with open(json_path) as f:
            care_logs = json.load(f)

        logger.info(f"Loaded JSON file: {json_path}")
        logger.info(f"Record count: {len(care_logs)}")

        # Register data via API
        result = register_care_logs(
          care_logs=care_logs,
          api_base_url="http://localhost:8000",
          admin_username="admin",
          admin_password="password"  # TODO: load from environment variables
        )

        # Show results
        print(f"")
        print(f"✅ Data registration complete")
        print(f"  Success: {result['success_count']}")
        print(f"  Failed: {result['failed_count']}")

        if result['failed_count'] > 0:
            print(f"")
          print(f"❌ Error details:")
            for error in result['errors']:
                print(f"  - {error}")

        # Move processed file
        processed_dir = Path("tmp/json/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)

        processed_path = processed_dir / Path(json_path).name
        Path(json_path).rename(processed_path)

        logger.info(f"Moved processed file: {processed_path}")

    except Exception as e:
        logger.error(f"Data registration error: {e}")
        print(f"❌ Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

**Hook Configuration**:
```json
// .kiro/hooks/config.json
{
  "hooks": [
    {
      "name": "pdf_to_image",
      "trigger": "file_save",
      "watch": "tmp/pdfs/*.pdf",
      "script": ".kiro/hooks/pdf_to_image_hook.py"
    },
    {
      "name": "register_care_logs",
      "trigger": "file_save",
      "watch": "tmp/json/*.json",
      "script": ".kiro/hooks/register_care_logs_hook.py"
    }
  ]
}
```

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
- `recorder_name`: "OCR Auto Import"
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

### Property 7: User-Specified Animal ID Validation
*For any* user-specified animal_id, the system must verify the animal exists in the database before processing OCR data.
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

#### 4. User Input Validation Errors
- **Animal Not Found**: Return 404 "Specified cat not found"
- **Invalid Date Range**: Return 400 "Invalid date range (start date > end date)"
- **Invalid File Format**: Return 415 "Unsupported file format (JPG, PNG, PDF only)"
- **File Size Exceeded**: Return 413 "File size is too large (maximum 50MB)"

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

#### User Input Validation Tests
- Test valid animal_id acceptance
- Test invalid animal_id rejection (404)
- Test valid date range acceptance
- Test invalid date range rejection (start > end)
- Test file format validation (JPG, PNG, PDF)
- Test file size limit enforcement (50MB)

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

#### Property 7: User-Specified Animal ID Validation Test
```python
@given(animal_id=st.integers(min_value=1, max_value=1000))
def test_user_specified_animal_id_validation(animal_id, db_session):
    """
    Property: System must verify animal_id exists before processing
    **Validates: Requirements 4.1, 4.3, 4.4**
    """
    # Create test animal
    if animal_id % 2 == 0:  # Even IDs exist
        animal = Animal(id=animal_id, name=f"Cat{animal_id}")
        db_session.add(animal)
        db_session.commit()

    # Test validation
    if animal_id % 2 == 0:
        assert validate_animal_id(db_session, animal_id) is True
    else:
        with pytest.raises(HTTPException) as exc:
            validate_animal_id(db_session, animal_id)
        assert exc.value.status_code == 404
```

#### Property 13: Date Range Validation Test
```python
@given(
    start_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31)),
    end_date=st.dates(min_value=date(2020, 1, 1), max_value=date(2030, 12, 31))
)
def test_date_range_validation(start_date, end_date):
    """
    Property: System must reject invalid date ranges (start > end)
    **Validates: User-specified metadata validation**
    """
    if start_date <= end_date:
        assert validate_date_range(start_date, end_date) is True
    else:
        with pytest.raises(HTTPException) as exc:
            validate_date_range(start_date, end_date)
        assert exc.value.status_code == 400
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
    "memo": "Stool: present, Vomit: none, Meds: none",
    "recorder_name": "OCR Auto Import",
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
    "memo": "Stool: none, Vomit: none, Meds: none, Notes: Ate dinner well",
    "recorder_name": "OCR Auto Import",
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

## User Workflow

### Workflow Example: PDF → Database

```bash
# Step 1: Place PDF (Hook runs automatically)
$ cp ~/Downloads/care_log_202411.pdf tmp/pdfs/

# Kiro Hook auto-execution
✅ PDF conversion complete: tmp/images/care_log_202411_page1.png

Next steps:
Attach the image in Kiro chat and instruct, for example:
"This is the record for cat ID <CatID> from <StartDate> to <EndDate>.
 Convert it to JSON according to the spec of register_care_logs.py for cat care log registration
 and save it as tmp/json/<filename>.json."

# Step 2: Interactive JSON generation in Kiro chat
User: [Attach image]
  "This is the record for cat ID 12 from November 14 to 23, 2024.
   Convert it to JSON according to the spec of register_care_logs.py for cat care log registration
   and save it as tmp/json/care_log_20241114.json."

Kiro: [Analyzing image...]
  [Extracting from user prompt]
  - animal_id: 12
  - start_date: 2024-11-14
  - end_date: 2024-11-23
  - output_path: tmp/json/care_log_20241114.json

  [Generating JSON...]

Kiro: ✅ Saved JSON file: tmp/json/care_log_20241114.json
  Generated 24 records.

# (Optional) Review and edit JSON
$ cat tmp/json/care_log_20241114.json
$ vim tmp/json/care_log_20241114.json  # Edit if necessary

# Step 3: Save JSON (Hook runs automatically)
# Saving the file automatically triggers the Kiro Hook

# Kiro Hook auto-execution
Reading JSON file: tmp/json/care_log_20241114.json
Record count: 24

✅ Data registration complete
  Success: 24
  Failed: 0

Moved processed file: tmp/json/processed/care_log_20241114.json
```

### Prompt Variations

```bash
# Pattern 1: Detailed instruction
"This is the record for cat ID 4 from November 15 to 25, 2024.
 Convert it to JSON according to the spec of scripts/hooks/register_care_logs.py
 and save it as tmp/json/care_log_202411.json."

# Pattern 2: Concise instruction
"ID12, 11/14-11/23, convert to JSON and save to tmp/json/."

# Pattern 3: Spanning across years
"This is the record for cat ID 7 from December 25, 2024 to January 5, 2025.
 Convert it to JSON and save it as tmp/json/care_log_202412.json."
```

### Directory Structure

```
tmp/
├── pdfs/                    # PDF placement folder (Hook watched)
│   └── care_log_202411.pdf
│
├── images/                  # Converted images (Hook output)
│   └── care_log_202411_page1.png
│
└── json/                    # JSON placement folder (Hook watched)
  ├── care_log_20241114.json
  └── processed/           # Processed files
    └── care_log_20241114.json
```

### User Experience Principles

1. **Phased processing**
  - Status can be checked at each phase
  - Easy to isolate errors
  - Easy to rerun

2. **Human review points**
  - JSON can be checked and corrected in Phase 2
  - OCR errors can be fixed beforehand
  - Ensures data quality

3. **Balance between automation and flexibility**
  - PDF conversion is automatic (Phase 1)
  - JSON generation is interactive (Phase 2)
  - DB registration is automatic (Phase 3)

4. **Clear feedback**
  - Show execution results of each Hook
  - Clearly describe the next steps
  - Provide guidance on how to handle errors

## Future Enhancements

### Phase 2 Features
- Multi-page PDF processing (batch processing of multiple pages)
- Batch processing of multiple files (bulk upload)
- OCR confidence scoring (display of confidence scores)
- Manual correction interface (preview and corrections before import)
- Historical data comparison (comparison with past data and duplicate checks)
- Export error logs (export error logs as CSV)

### Phase 3 Features
- Real-time preview of extracted data
- Interactive field correction (field-level editing UI)
- Template-based extraction for different form layouts (support multiple formats)
- Mobile app integration (direct upload from mobile app)
- Cloud-based OCR service option
- AI-powered handwriting recognition improvement (continuous improvement of handwriting recognition accuracy)
