# Requirements Document

## Introduction

手書きの猫世話記録表（PDF/画像）をOCR解析し、NecoKeeperのデータベースに自動登録する機能を実装します。ボランティアが紙に記録した世話記録を効率的にデジタル化し、データ入力の手間を削減します。

## Glossary

- **OCR (Optical Character Recognition)**: 光学文字認識。画像内の文字を読み取りテキストデータに変換する技術
- **Kiro**: ローカル環境で動作するAI開発アシスタント。ユーザーの指示を受けてスクリプトやLLMを呼び出す司令塔
- **マルチモーダルLLM**: 画像とテキストを理解できる大規模言語モデル。画像内容を解析してJSON化する
- **Hook**: Kiroが実行するスクリプト。PDF変換やデータ登録などの処理を担当
- **Care Log**: 猫の世話記録。食欲、元気、排尿、清掃などの日々の記録
- **Time Slot**: 記録の時点。morning（朝）、noon（昼）、evening（夕）の3つ
- **from_paper**: 紙記録からの転記フラグ。OCR経由で登録されたデータを識別するためのフラグ

## Requirements

### Requirement 1

**User Story:** As a ボランティア, I want to upload a handwritten care log image, so that I can digitize paper records without manual data entry.

#### Acceptance Criteria

1. WHEN a user provides an image file (jpg, png) with a handwritten care log THEN the System SHALL extract the care log data and convert it to JSON format
2. WHEN the extracted JSON data is valid THEN the System SHALL register the care log records to the database via API
3. WHEN the image contains multiple days of records THEN the System SHALL extract all records and register them individually
4. WHEN the image quality is poor or text is unreadable THEN the System SHALL notify the user and request manual verification or clarification
5. WHEN the LLM cannot interpret the image content THEN the System SHALL notify the user and request manual verification or clarification
6. WHEN the registration is complete THEN the System SHALL set the from_paper flag to True for all imported records

### Requirement 2

**User Story:** As a ボランティア, I want to upload a PDF file with a care log, so that I can import records from scanned documents.

#### Acceptance Criteria

1. WHEN a user provides a PDF file THEN the System SHALL convert the first page to an image file
2. WHEN PDF conversion is complete THEN the System SHALL return the image file path
3. WHEN the PDF has multiple pages THEN the System SHALL only process the first page
4. WHEN PDF conversion fails THEN the System SHALL notify the user and halt the process
5. WHEN the image is extracted THEN the System SHALL proceed with OCR analysis

### Requirement 3

**User Story:** As a システム管理者, I want the OCR system to map handwritten records to the existing Care Log data model, so that imported data is consistent with manually entered records.

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

### Requirement 4

**User Story:** As a ボランティア, I want to specify the cat in my prompt, so that records are associated with the correct animal.

#### Acceptance Criteria

1. WHEN the user provides a cat identifier (ID or name) in the prompt THEN the System SHALL use the specified animal_id for all records
2. WHEN the user provides a cat name THEN the System SHALL search the database for a matching animal by name
3. WHEN multiple cats match the provided name THEN the System SHALL request user clarification
4. WHEN no cat matches the provided identifier THEN the System SHALL notify the user and halt the import process
5. WHEN the cat is successfully identified THEN the System SHALL use the animal_id for all extracted records

### Requirement 5

**User Story:** As a システム管理者, I want the system to handle date information correctly, so that records are associated with the correct dates.

#### Acceptance Criteria

1. WHEN the user specifies a year and month in the prompt THEN the System SHALL use the specified year-month for date parsing
2. WHEN the handwritten record contains dates in M/D format THEN the System SHALL combine them with the specified year-month
3. WHEN the date format is ambiguous THEN the System SHALL request user clarification
4. WHEN a date is invalid (e.g., 2/30) THEN the System SHALL log an error and skip that record
5. WHEN no year-month is specified THEN the System SHALL use the current year and month as default

### Requirement 6

**User Story:** As a システム管理者, I want the system to use Kiro Hooks for PDF conversion and data registration, so that the workflow is automated and maintainable.

#### Acceptance Criteria

1. WHEN a PDF file is provided THEN the System SHALL invoke the PDF conversion Hook script
2. WHEN the PDF conversion Hook is invoked THEN the Hook SHALL accept a PDF file path and return the first page as an image path
3. WHEN image data is extracted and converted to JSON THEN the System SHALL invoke the data registration Hook script
4. WHEN the data registration Hook is invoked THEN the Hook SHALL accept JSON data and register it via the NecoKeeper API with administrator privileges
5. WHEN the data registration Hook is invoked THEN the Hook SHALL authenticate with the API by calling the authentication endpoint

### Requirement 7

**User Story:** As a ボランティア, I want the system to provide clear feedback during the import process, so that I can understand what is happening and troubleshoot issues.

#### Acceptance Criteria

1. WHEN the import process starts THEN the System SHALL display a progress indicator
2. WHEN each page or record is processed THEN the System SHALL log the processing status
3. WHEN an error occurs THEN the System SHALL display a clear error message with the cause
4. WHEN the import is complete THEN the System SHALL display a summary including total records, successful imports, and failures
5. WHEN records are skipped due to errors THEN the System SHALL list the skipped records with reasons

### Requirement 8

**User Story:** As a システム管理者, I want the system to validate extracted data before registration, so that invalid data does not corrupt the database.

#### Acceptance Criteria

1. WHEN JSON data is generated THEN the System SHALL validate all required fields are present
2. WHEN appetite or energy values are extracted THEN the System SHALL ensure they are within the valid range (1-5)
3. WHEN boolean fields are extracted THEN the System SHALL ensure they are valid boolean values
4. WHEN date fields are extracted THEN the System SHALL ensure they are valid dates
5. WHEN validation fails THEN the System SHALL log the validation error and skip that record

### Requirement 9

**User Story:** As a システム管理者, I want the system to handle special symbols and notations in handwritten records, so that data is interpreted correctly.

#### Acceptance Criteria

1. WHEN the handwritten record contains "○" symbol THEN the System SHALL interpret it as True or present
2. WHEN the handwritten record contains "×" symbol THEN the System SHALL interpret it as False or absent
3. WHEN the handwritten record contains numeric values THEN the System SHALL extract them as integers
4. WHEN the handwritten record contains empty cells THEN the System SHALL interpret them as null or default values
5. WHEN the handwritten record contains ambiguous symbols THEN the System SHALL use conservative interpretation and log a warning

### Requirement 10

**User Story:** As a システム管理者, I want the system to store metadata about the import process, so that I can track the source and quality of imported data.

#### Acceptance Criteria

1. WHEN records are imported via OCR THEN the System SHALL set the from_paper flag to True
2. WHEN records are imported THEN the System SHALL set the recorder_name to a default value indicating OCR import
3. WHEN records are imported THEN the System SHALL store the import timestamp in created_at
4. WHEN records are imported THEN the System SHALL set device_tag to indicate the import source (e.g., "OCR-Import")
5. WHEN records are imported THEN the System SHALL leave recorder_id as null unless specified by the user

## Data Mapping Reference

### Handwritten Record Fields → Care Log Model

| 手書き項目 | Care Log Field | Data Type | Mapping Rule |
|-----------|----------------|-----------|--------------|
| 日付 | log_date | date | Combine with user-specified year-month |
| 朝/昼/夕 | time_slot | string | 朝→morning, 昼→noon, 夕→evening |
| ごはん | appetite | int (1-5) | ○→5, △→3, ×→1 |
| 元気 | energy | int (1-5) | ○→5, △→3, ×→1 |
| 排尿 | urination | boolean | ○→True, ×→False, 数字→True (count in memo) |
| 排便 | memo | string | ○→"排便あり", ×→"排便なし" (append to memo) |
| 嘔吐 | memo | string | ○→"嘔吐あり", ×→"嘔吐なし" (append to memo) |
| 投薬 | memo | string | ○→"投薬あり", ×→"投薬なし" (append to memo) |
| 備考 | memo | string | Append handwritten notes |
| 名前 | animal_id | int | User specifies in prompt, search by name or ID |

### Default Values for OCR Import

- `recorder_name`: "OCR自動取込"
- `recorder_id`: null
- `from_paper`: True
- `device_tag`: "OCR-Import"
- `cleaning`: False (not in handwritten form)
- `ip_address`: null
- `user_agent`: null

## Technical Notes

### PDF Conversion
- Use `pdf2image` or `PyMuPDF` library
- Convert only the first page to JPEG format
- Store temporary images in `tmp/images/`
- Clean up temporary files after processing

### Image Analysis
- Use Kiro's multimodal LLM capability
- Pass image via chat "Add image" feature
- Provide structured prompt with expected JSON format
- Handle OCR errors gracefully

### API Authentication
- Store API credentials in environment variables or config file
- Use existing NecoKeeper authentication endpoints
- Handle token refresh if needed

### Error Handling
- Log all errors to `logs/ocr-import.log`
- Continue processing on non-fatal errors
- Provide detailed error messages to user
- Support retry mechanism for failed records
