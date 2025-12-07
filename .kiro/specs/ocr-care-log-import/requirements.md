# Requirements Document

## Introduction

Implement a feature that performs OCR on handwritten cat care log sheets (PDF/images) and automatically registers the results into the NecoKeeper database. This reduces the effort of manual data entry by digitizing care logs that volunteers record on paper.

**Key design decision**: adopt a three-phase Kiro Hook workflow:
1. **Phase 1 (automatic)**: PDF → Image conversion
2. **Phase 2 (interactive)**: Image → JSON conversion (user specifies cat ID and date range via Kiro chat)
3. **Phase 3 (automatic)**: JSON → Database registration

This design prevents OCR misrecognition while ensuring data consistency by adding a human review point. Issues such as handwritten "12" being misread as "2" are avoided because the user explicitly specifies these values in Phase 2.

## Glossary

- **OCR (Optical Character Recognition)**: Technology that reads characters in an image and converts them into text data.
- **Kiro**: A local AI development assistant that orchestrates scripts and LLMs based on user instructions.
- **Multimodal LLM**: A large language model that can understand both images and text, used here to analyze images and generate JSON.
- **Hook**: A script executed by Kiro, responsible for tasks such as PDF conversion and data registration.
- **Care Log**: A daily record of cat care, including appetite, energy, urination, cleaning, and so on.
- **Time Slot**: The time of the record; one of `morning`, `noon`, or `evening`.
- **from_paper**: A flag indicating that data was imported from paper records via OCR.

## Requirements

### Requirement 1: Phase 2 - Image to JSON Conversion (Interactive)

**User Story:** As a volunteer, I want to use Kiro chat to convert a handwritten care log image to JSON with specified metadata (animal_id, date_range), so that I can digitize paper records with human verification before database registration.

**Design Rationale:** Phase 2 is interactive to allow human verification and correction of OCR results before database registration.

#### Acceptance Criteria

1. WHEN a user attaches an image file (jpg, png) in Kiro chat with animal_id and date_range in the prompt THEN Kiro SHALL extract the care log data and convert it to JSON format
2. WHEN the user specifies a JSON output path THEN Kiro SHALL save the generated JSON to the specified path
3. WHEN the image contains multiple days of records THEN Kiro SHALL extract all records within the specified date range
4. WHEN the image quality is poor or text is unreadable THEN Kiro SHALL mark unclear fields with "?" and notify the user
5. WHEN the LLM cannot interpret the image content THEN Kiro SHALL notify the user and request clarification
6. WHEN JSON is generated THEN all records SHALL have from_paper flag set to True
7. WHEN JSON is saved to tmp/json/ THEN the user SHALL have the opportunity to review and edit before automatic registration
8. WHEN the user confirms the JSON is correct THEN they SHALL save it to trigger Phase 3 Hook

### Requirement 2: Phase 1 - PDF to Image Conversion (Automatic Hook)

**User Story:** As a volunteer, I want to place a PDF file in a watched folder so that it is automatically converted to an image, enabling me to proceed with OCR analysis.

**Design Rationale:** Phase 1 is fully automated using Kiro Hook to reduce manual steps.

#### Acceptance Criteria

1. WHEN a user places a PDF file in tmp/pdfs/ THEN the Kiro Hook SHALL automatically detect the file
2. WHEN the Hook detects a PDF file THEN it SHALL convert the first page to a PNG image
3. WHEN the PDF has multiple pages THEN the Hook SHALL only process the first page
4. WHEN PDF conversion is complete THEN the Hook SHALL save the image to tmp/images/ with a descriptive filename
5. WHEN PDF conversion fails THEN the Hook SHALL log the error and notify the user
6. WHEN the image is saved THEN the Hook SHALL display the next steps to the user (use Kiro chat for Phase 2)

### Requirement 3

**User Story:** As a system administrator, I want the OCR system to map handwritten records to the existing Care Log data model, so that imported data is consistent with manually entered records.

#### Acceptance Criteria

1. WHEN extracting care log data THEN the System SHALL create one record per time slot (morning/noon/evening) per day
2. WHEN the handwritten record contains "ごはん" (meal) field THEN the System SHALL map it to the appetite field with appropriate scoring (1-5)
3. WHEN the handwritten record contains "元気" (energy) field THEN the System SHALL map it to the energy field with appropriate scoring (1-5)
4. WHEN the handwritten record contains "排尿" (urination) field THEN the System SHALL map it to the urination boolean field
5. WHEN the handwritten record contains "排便" (defecation) field THEN the System SHALL map it to a memo field as defecation is not in the current model
6. WHEN the handwritten record contains "嘔吐" (vomiting) field THEN the System SHALL map it to a memo field as vomiting is not in the current model
7. WHEN the handwritten record contains "投薬" (medication) field THEN the System SHALL map it to a memo field as medication is not in the current model
8. WHEN the handwritten record contains "備考" (notes) field THEN the System SHALL map it to the memo field
9. WHEN the handwritten record contains time indicators (朝/昼/夕) THEN the System SHALL map them to time_slot field (morning/noon/evening)

### Requirement 4: User-Specified Metadata in Kiro Chat Prompt

**User Story:** As a volunteer, I want to specify the cat ID, date range, and output path in my Kiro chat prompt, so that records are associated with the correct animal without OCR misrecognition errors.

**Design Rationale:** All critical metadata (animal_id, date_range, output_path) is user-specified in a natural language prompt to prevent OCR errors. For example, handwritten "12" can be misread as "2" or "2-", causing data integrity issues.

#### Acceptance Criteria

1. WHEN the user provides a prompt like "これはIDが12の猫の2024年11月14日～23日の記録です。JSON化してtmp/json/care_log.json に保存して" THEN Kiro SHALL extract animal_id=12, start_date=2024-11-14, end_date=2024-11-23, output_path=tmp/json/care_log.json
2. WHEN the user provides a prompt like "ID4、11/15-11/25、JSON化してtmp/json/に保存" THEN Kiro SHALL extract animal_id=4, start_date=2024-11-15, end_date=2024-11-25, and generate an appropriate filename
3. WHEN the user mentions "register_care_logs.pyの仕様に合わせて" THEN Kiro SHALL reference the JSON schema from that script
4. WHEN Kiro generates JSON THEN all records SHALL have the user-specified animal_id
5. WHEN OCR extracts a different animal_id from the image THEN Kiro SHALL override it with the user-specified value
6. WHEN OCR extracts dates outside the specified range THEN Kiro SHALL exclude those records from the JSON output
7. WHEN the user does not specify a year THEN Kiro SHALL use the current year as default

### Requirement 5: Kiro Hook Configuration and Management

**User Story:** As a system administrator, I want to configure Kiro Hooks for automatic PDF conversion and JSON registration, so that the workflow is automated and maintainable.

**Design Rationale:** Kiro Hooks provide file-watching capabilities to automate Phase 1 and Phase 3, reducing manual intervention.

#### Acceptance Criteria

1. WHEN the system is set up THEN there SHALL be two Kiro Hooks configured: pdf_to_image_hook and register_care_logs_hook
2. WHEN pdf_to_image_hook is configured THEN it SHALL watch tmp/pdfs/*.pdf for new files
3. WHEN register_care_logs_hook is configured THEN it SHALL watch tmp/json/*.json for new files
4. WHEN a Hook is triggered THEN it SHALL receive the file path as an argument
5. WHEN a Hook completes successfully THEN it SHALL log the result and notify the user
6. WHEN a Hook fails THEN it SHALL log the error with details and exit with non-zero status
7. WHEN Hooks are configured THEN they SHALL be documented in .kiro/hooks/config.json

### Requirement 6: Phase 3 - JSON to Database Registration (Automatic Hook)

**User Story:** As a volunteer, I want JSON files to be automatically registered to the database when saved to a watched folder, so that I don't need to manually trigger the registration process.

**Design Rationale:** Phase 3 is fully automated using Kiro Hook to complete the workflow after human verification in Phase 2.

#### Acceptance Criteria

1. WHEN a user saves a JSON file to tmp/json/ THEN the Kiro Hook SHALL automatically detect the file
2. WHEN the Hook detects a JSON file THEN it SHALL read and validate the JSON structure
3. WHEN JSON validation passes THEN the Hook SHALL authenticate with the NecoKeeper API
4. WHEN authentication succeeds THEN the Hook SHALL register each record via POST /api/v1/care-logs
5. WHEN registration is complete THEN the Hook SHALL display a summary (success count, failure count)
6. WHEN registration succeeds THEN the Hook SHALL move the processed JSON to tmp/json/processed/
7. WHEN registration fails THEN the Hook SHALL log detailed error messages and keep the JSON file for retry

### Requirement 7

**User Story:** As a volunteer, I want the system to provide clear feedback during the import process, so that I can understand what is happening and troubleshoot issues.

#### Acceptance Criteria

1. WHEN the import process starts THEN the System SHALL display a progress indicator
2. WHEN each page or record is processed THEN the System SHALL log the processing status
3. WHEN an error occurs THEN the System SHALL display a clear error message with the cause
4. WHEN the import is complete THEN the System SHALL display a summary including total records, successful imports, and failures
5. WHEN records are skipped due to errors THEN the System SHALL list the skipped records with reasons

### Requirement 8

**User Story:** As a system administrator, I want the system to validate extracted data before registration, so that invalid data does not corrupt the database.

#### Acceptance Criteria

1. WHEN JSON data is generated THEN the System SHALL validate all required fields are present
2. WHEN appetite or energy values are extracted THEN the System SHALL ensure they are within the valid range (1-5)
3. WHEN boolean fields are extracted THEN the System SHALL ensure they are valid boolean values
4. WHEN date fields are extracted THEN the System SHALL ensure they are valid dates
5. WHEN validation fails THEN the System SHALL log the validation error and skip that record

### Requirement 9

**User Story:** As a system administrator, I want the system to handle special symbols and notations in handwritten records, so that data is interpreted correctly.

#### Acceptance Criteria

1. WHEN the handwritten record contains "○" symbol THEN the System SHALL interpret it as True or present
2. WHEN the handwritten record contains "×" symbol THEN the System SHALL interpret it as False or absent
3. WHEN the handwritten record contains numeric values THEN the System SHALL extract them as integers
4. WHEN the handwritten record contains empty cells THEN the System SHALL interpret them as null or default values
5. WHEN the handwritten record contains ambiguous symbols THEN the System SHALL use conservative interpretation and log a warning

### Requirement 10

**User Story:** As a system administrator, I want the system to store metadata about the import process, so that I can track the source and quality of imported data.

#### Acceptance Criteria

1. WHEN records are imported via OCR THEN the System SHALL set the from_paper flag to True
2. WHEN records are imported THEN the System SHALL set the recorder_name to a default value indicating OCR import
3. WHEN records are imported THEN the System SHALL store the import timestamp in created_at
4. WHEN records are imported THEN the System SHALL set device_tag to indicate the import source (e.g., "OCR-Import")
5. WHEN records are imported THEN the System SHALL leave recorder_id as null unless specified by the user

## Data Mapping Reference

### Handwritten Record Fields → Care Log Model

| Handwritten Field | Care Log Field | Data Type | Mapping Rule |
|-------------------|----------------|----------|--------------|
| Date | log_date | date | Combine with user-specified year and month |
| Morning/Noon/Evening (朝/昼/夕) | time_slot | string | 朝 → morning, 昼 → noon, 夕 → evening |
| Meal (ごはん) | appetite | int (1-5) | ○ → 5, △ → 3, × → 1 |
| Energy (元気) | energy | int (1-5) | ○ → 5, △ → 3, × → 1 |
| Urination (排尿) | urination | boolean | ○ → True, × → False, numeric value → True (count goes into memo) |
| Defecation (排便) | memo | string | ○ → "Defecation: yes", × → "Defecation: no" (append to memo) |
| Vomiting (嘔吐) | memo | string | ○ → "Vomiting: yes", × → "Vomiting: no" (append to memo) |
| Medication (投薬) | memo | string | ○ → "Medication: yes", × → "Medication: no" (append to memo) |
| Notes (備考) | memo | string | Append handwritten notes |
| Name (名前) | animal_id | int | User specifies in prompt, search by name or ID |

### Default Values for OCR Import

- `recorder_name`: "OCR auto import"
- `recorder_id`: null
- `from_paper`: True
- `device_tag`: "OCR-Import"
- `cleaning`: False (not in handwritten form)
- `ip_address`: null
- `user_agent`: null

## Technical Notes

### Phase 1: PDF Conversion (Automatic Hook)
- Use `pdf2image` or `PyMuPDF` library
- Convert only the first page to PNG format
- Store images in `tmp/images/` with descriptive filenames
- Hook script: `.kiro/hooks/pdf_to_image_hook.py`
- Watch pattern: `tmp/pdfs/*.pdf`

### Phase 2: Image Analysis (Interactive Kiro Chat)
- Use Kiro's multimodal LLM capability
- User attaches image in chat
- User provides prompt: "ID<猫ID>の猫、<開始日>から<終了日>のデータをJSONに変換して tmp/json/<ファイル名>.json に保存して"
- Kiro generates JSON with user-specified metadata
- User reviews and edits JSON if needed
- User saves JSON to tmp/json/ to trigger Phase 3

### Phase 3: Database Registration (Automatic Hook)
- Hook script: `.kiro/hooks/register_care_logs_hook.py`
- Watch pattern: `tmp/json/*.json`
- Authenticate with NecoKeeper API (POST /api/v1/auth/token)
- Register records via POST /api/v1/care-logs
- Move processed files to `tmp/json/processed/`
- Store API credentials in environment variables

### Directory Structure
```
tmp/
├── pdfs/                    # Phase 1 input (Hook監視)
├── images/                  # Phase 1 output / Phase 2 input
└── json/                    # Phase 2 output / Phase 3 input (Hook監視)
    └── processed/           # Phase 3 output (処理済み)
```

### Error Handling
- Log all errors to `logs/ocr-import.log`
- Phase 1/3 Hooks: Display error and exit with non-zero status
- Phase 2: Notify user in chat and request clarification
- Continue processing on non-fatal errors
- Support manual retry by re-saving files
