# Implementation Plan

## Overview

Implement a three-phase workflow that performs OCR on handwritten cat care log sheets (PDF/images) and automatically registers the results into the NecoKeeper database.

**Three-phase workflow**:
- **Phase 1 (automatic Hook)**: PDF → image conversion
- **Phase 2 (interactive)**: image → JSON conversion (user specifies cat ID and date range via Kiro chat)
- **Phase 3 (automatic Hook)**: JSON → database registration

**Status of existing code**:
- `scripts/hooks/pdf_to_image.py` ✅ implemented
- `scripts/hooks/register_care_logs.py` ✅ implemented
- Utilities under `scripts/utils/` ✅ implemented

---

## Tasks

- [x] 1. Set up project structure and utilities
  - Create directory structure (`tmp/pdfs/`, `tmp/images/`, `tmp/json/`, `tmp/json/processed/`)
  - Add dependencies (`pdf2image`, `PyMuPDF`, `requests`, `Pillow`)
  - Create environment variable template
  - Implement logging configuration (`scripts/utils/logging_config.py`)
  - _Requirements: All_

- [x] 2. Implement data mapping utilities
  - Implement `scripts/utils/data_mapper.py`
  - Map symbols to numeric values (○→5, △→3, ×→1)
  - Map time slots (朝→morning, 昼→noon, 夕→evening)
  - Map boolean values (○→true, ×→false)
  - Aggregate memo fields (defecation, vomiting, medication, notes)
  - Apply OCR default values
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 10.2, 10.3, 10.4, 10.5_

- [ ]* 2.1 Create property-based tests for data mapping
  - **Property 3: Time Slot Mapping Correctness**
  - **Validates: Requirements 3.9**

- [ ]* 2.2 Create property-based tests for memo field aggregation
  - **Property 11: Memo Field Aggregation**
  - **Validates: Requirements 3.5, 3.6, 3.7, 3.8**

- [ ]* 2.3 Create property-based tests for default value application
  - **Property 12: Default Value Application**
  - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**

- [x] 3. Implement JSON schema validator
  - Implement `scripts/utils/json_schema.py`
  - Define care log JSON schema
  - Implement schema validation function
  - Implement field-level validation (range, type, format)
  - Implement date validation (including year/month range checks)
  - Return detailed validation errors
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 3.1 Create property-based tests for JSON structure validity
  - **Property 1: JSON Structure Validity**
  - **Validates: Requirements 1.1, 3.1**

- [ ]* 3.2 Create property-based tests for date range consistency
  - **Property 2: Date Range Consistency**
  - **Validates: Requirements 4.6**

- [ ]* 3.3 Create property-based tests for value range validity
  - **Property 4: Appetite and Energy Range Validity**
  - **Validates: Requirements 3.2, 3.3, 8.2**

- [ ]* 3.4 Create property-based tests for boolean field validity
  - **Property 5: Boolean Field Validity**
  - **Validates: Requirements 3.4, 8.3**

- [ ]* 3.5 Create property-based tests for from_paper flag consistency
  - **Property 6: From Paper Flag Consistency**
  - **Validates: Requirements 1.6, 10.1**

- [x] 4. Implement cat identification utilities
  - Implement `scripts/utils/cat_identifier.py`
  - Fetch all cats via GET /api/v1/animals
  - Identify by animal_id (integer, in-memory search)
  - Identify by name (string, in-memory search)
  - Case-insensitive name matching
  - Handle multiple-match errors
  - Handle no-match errors
  - No direct database dependency (API only)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 4.1 Create unit tests for cat identification
  - Test identification by ID
  - Test identification by name
  - Test case-insensitive matching
  - Test multiple-match error
  - Test no-match error
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 4.2 Create property-based tests for user-specified animal_id validation
  - **Property 7: User-Specified Animal ID Validation**
  - **Validates: Requirements 4.1, 4.3, 4.4**

- [x] 5. Create LLM prompt template
  - Implement `scripts/utils/prompt_template.py`
  - Define structured prompt template with placeholders
  - Document mapping rules inside the prompt
  - Add output format specification
  - Implement parameterized prompt generation function
  - _Requirements: 1.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [x] 6. Phase 1: Implement PDF conversion Hook script
  - Implement `scripts/hooks/pdf_to_image.py` ✅
  - Extract first page of PDF using pdf2image or PyMuPDF
  - File validation (existence, extension, size)
  - Error handling for conversion failures
  - Clean up temporary files
  - Return image path in a standardized format
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 6.1 Create unit tests for PDF conversion
  - Test successful conversion
  - Test error when PDF not found
  - Test handling of corrupted PDFs
  - Test output path generation
  - Test cleanup on error
  - _Requirements: 2.1, 2.2, 2.4_

- [ ]* 6.2 Create property-based tests for extracting the first page of a PDF
  - **Property 8: PDF First Page Extraction**
  - **Validates: Requirements 2.1, 2.3**

- [x] 7. Phase 3: Implement data registration Hook script
  - Implement `scripts/hooks/register_care_logs.py` ✅
  - Implement API authentication (POST /api/v1/auth/token)
  - Store and reuse authentication token
  - Implement batch registration loop
  - Implement error handling for individual record failures
  - Continue processing even when some records fail
  - Generate registration summary (success/failure counts)
  - Log detailed errors
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.2, 7.4, 7.5_

- [ ]* 7.1 Create unit tests for data registration
  - Test successful authentication
  - Test authentication failure
  - Test successful batch registration
  - Test handling of individual record failures
  - Test network error retry logic
  - Test summary generation
  - _Requirements: 6.4, 6.5, 7.4, 7.5_

- [ ]* 7.2 Create property-based tests for API authentication success
  - **Property 9: API Authentication Success**
  - **Validates: Requirements 6.3**

- [ ]* 7.3 Create property-based tests for batch registration atomicity
  - **Property 10: Batch Registration Atomicity**
  - **Validates: Requirements 7.4, 7.5**

- [x] 8. Create Kiro Hook configuration file
  - Create `.kiro/hooks/config.json`
  - Configure pdf_to_image_hook (watch `tmp/pdfs/*.pdf`)
  - Configure register_care_logs_hook (watch `tmp/json/*.json`)
  - Set script paths for Hooks
  - Configure trigger conditions
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 9. Phase 2: Create documentation for Kiro chat interactive workflow
  - Document how to attach images in Kiro chat
  - Create user prompt examples
    - Basic: "This is the record for cat ID 12 from November 14 to 23, 2024. Convert it to JSON and save it as tmp/json/care_log.json."
    - Short: "ID12, 11/14-11/23, convert to JSON and save to tmp/json/"
  - Document how to use Kiro's internal prompt template
  - Document how users review and edit JSON
  - Explain automatic triggering of Phase 3 Hook
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 4.1, 4.2, 4.3_

- [ ] 10. Create user guide documentation
  - Update `docs/ocr-import-guide.md`
  - Explain the three-phase workflow
  - Workflow 1: Start directly from images (Image → JSON → Database)
  - Workflow 2: Start from PDF (PDF → Image → JSON → Database)
  - Provide prompt format examples
  - Document error messages and troubleshooting
  - Provide command examples
  - Add FAQ section
  - _Requirements: All_

- [ ] 11. Create sample data and test images
  - Create sample handwritten care log images
  - Create sample PDFs
  - Create sample JSON output files
  - Add them to `scripts/tests/fixtures/`
  - Create edge case samples (unclear characters, partially filled records)
  - _Requirements: All_

- [ ] 12. Checkpoint - verify all tests pass
  - Confirm all tests pass; if there are issues, ask the user

- [ ]* 13. Create integration tests
  - Create `scripts/tests/test_integration.py`
  - Test end-to-end image processing workflow
  - Test end-to-end PDF processing workflow
  - Test error recovery scenarios
  - Test with sample handwritten images
  - Test with various levels of data quality
  - _Requirements: All_

- [ ] 14. Final checkpoint - verify all tests pass
  - Confirm all tests pass; if there are issues, ask the user

---

## Implementation Notes

### Task execution order
1. **Foundation** (Tasks 1–5): Set up structure, utilities, and validation ✅ done
2. **Phase 1 & 3** (Tasks 6–7): Implement Hook scripts ✅ done
3. **Phase 2 & configuration** (Tasks 8–9): Kiro Hook configuration and chat workflow documentation
4. **Documentation** (Task 10): Create user guide
5. **Test data** (Task 11): Create sample data
6. **Testing** (Tasks 12–14): Comprehensive testing and verification

### Task dependencies
- Task 8 (Kiro Hook configuration) depends on completion of Tasks 6 and 7
- Task 9 (Phase 2 documentation) depends on completion of Task 5 (prompt template)
- Task 10 (user guide) depends on completion of Tasks 8 and 9
- Task 13 (integration tests) depends on completion of Tasks 1–11

### Testing strategy
- Unit tests are marked with `*`; they are optional but recommended
- Property-based tests validate general correctness properties
- Integration tests validate end-to-end workflows
- All tests should be run before final deployment

### Environment setup
Before starting implementation, confirm the following:
- Python 3.10+ is installed
- Virtual environment is active
- NecoKeeper API is running locally
- Database is initialized with test data
- Administrator credentials are available
- Environment variables are set (`NECOKEEPER_API_URL`, `NECOKEEPER_ADMIN_USERNAME`, `NECOKEEPER_ADMIN_PASSWORD`)

### Kiro Hook configuration
Hooks are invoked from Kiro with the following patterns:
```bash
# PDF conversion Hook
python scripts/hooks/pdf_to_image.py <pdf_path>

# Data registration Hook
python scripts/hooks/register_care_logs.py <json_file_path>
```

### Directory structure
```
tmp/
├── pdfs/                    # Phase 1 input (Hook watched)
├── images/                  # Phase 1 output / Phase 2 input
└── json/                    # Phase 2 output / Phase 3 input (Hook watched)
  └── processed/           # Phase 3 output (processed)

scripts/
├── hooks/
│   ├── pdf_to_image.py      ✅ implemented
│   └── register_care_logs.py ✅ implemented
└── utils/
  ├── logging_config.py     ✅ implemented
  ├── json_schema.py        ✅ implemented
  ├── data_mapper.py        ✅ implemented
  ├── cat_identifier.py     ✅ implemented
  └── prompt_template.py    ✅ implemented
```

### Success criteria
- All core functional tasks (1–11) are complete
- At least 70% test coverage
- All property-based tests pass
- Documentation is complete and reviewed
- Import of sample handwritten records succeeds

### Use of existing code
The following scripts are already complete and can be used as-is:
- ✅ `scripts/hooks/pdf_to_image.py` - fully implemented PDF conversion
- ✅ `scripts/hooks/register_care_logs.py` - fully implemented API authentication and batch registration
- ✅ `scripts/utils/logging_config.py` - logging configuration
- ✅ `scripts/utils/json_schema.py` - JSON validation
- ✅ `scripts/utils/data_mapper.py` - data mapping
- ✅ `scripts/utils/cat_identifier.py` - cat identification
- ✅ `scripts/utils/prompt_template.py` - prompt template

The remaining work mainly consists of:
1. Creating the Kiro Hook configuration file
2. Writing Phase 2 (Kiro chat interaction) documentation
3. Updating the user guide
4. Creating tests
