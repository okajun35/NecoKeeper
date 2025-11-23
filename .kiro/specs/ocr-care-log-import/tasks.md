# Implementation Plan

## Overview

This implementation plan outlines the tasks required to build the OCR-based care log import system. The plan follows an incremental approach, building core functionality first, then adding error handling and testing.

---

## Tasks

- [ ] 1. Set up project structure and dependencies
  - Create directory structure for hooks and utilities
  - Add required dependencies to requirements.txt
  - Create environment variable template
  - Set up logging configuration
  - _Requirements: All_

- [ ] 2. Implement PDF conversion Hook script
  - Create `scripts/hooks/pdf_to_image.py`
  - Implement PDF first page extraction using pdf2image or PyMuPDF
  - Add file validation (existence, extension, size)
  - Implement error handling for conversion failures
  - Add temporary file cleanup
  - Return image path in standardized format
  - _Requirements: 2.1, 2.2, 2.4, 2.5_

- [ ]* 2.1 Write unit tests for PDF conversion
  - Test successful conversion
  - Test PDF not found error
  - Test corrupted PDF handling
  - Test output path generation
  - Test cleanup on error
  - _Requirements: 2.1, 2.2, 2.4_

- [ ] 3. Implement cat identification utility
  - Create `scripts/utils/cat_identifier.py`
  - Fetch all animals via GET /api/v1/animals
  - Implement identification by animal_id (integer) in memory
  - Implement identification by name (string) with in-memory search
  - Add case-insensitive name matching
  - Handle multiple matches error
  - Handle no matches error
  - No database dependency (API only)
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 3.1 Write unit tests for cat identification
  - Test identification by ID
  - Test identification by name
  - Test case-insensitive matching
  - Test multiple matches error
  - Test no matches error
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 4. Implement JSON schema validator
  - Create `scripts/utils/json_schema.py`
  - Define Care Log JSON schema
  - Implement schema validation function
  - Add field-level validation (ranges, types, formats)
  - Add date validation with year-month range check
  - Return detailed validation errors
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 4.1 Write property test for JSON schema validation
  - **Property 1: JSON Structure Validity**
  - **Validates: Requirements 1.1, 3.1**

- [ ]* 4.2 Write property test for date range consistency
  - **Property 2: Date Range Consistency**
  - **Validates: Requirements 5.2**

- [ ]* 4.3 Write property test for value range validation
  - **Property 4: Appetite and Energy Range Validity**
  - **Validates: Requirements 3.2, 3.3, 8.2**

- [ ]* 4.4 Write property test for boolean field validity
  - **Property 5: Boolean Field Validity**
  - **Validates: Requirements 3.4, 8.3**

- [ ] 5. Implement data registration Hook script
  - Create `scripts/hooks/register_care_logs.py`
  - Implement API authentication (POST /api/v1/auth/token)
  - Store and reuse authentication token
  - Implement batch registration loop
  - Add error handling for individual record failures
  - Continue processing on failure (don't halt)
  - Generate registration summary (success/failed counts)
  - Log all errors with details
  - _Requirements: 6.3, 6.4, 6.5, 7.2, 7.4, 7.5_

- [ ]* 5.1 Write unit tests for data registration
  - Test successful authentication
  - Test authentication failure
  - Test successful batch registration
  - Test individual record failure handling
  - Test network error retry logic
  - Test summary generation
  - _Requirements: 6.4, 6.5, 7.4, 7.5_

- [ ]* 5.2 Write property test for API authentication
  - **Property 9: API Authentication Success**
  - **Validates: Requirements 6.5**

- [ ]* 5.3 Write property test for batch registration atomicity
  - **Property 10: Batch Registration Atomicity**
  - **Validates: Requirements 7.4, 7.5**

- [ ] 6. Create LLM prompt template
  - Create `scripts/utils/prompt_template.py`
  - Define structured prompt template with placeholders
  - Add mapping rules documentation in prompt
  - Add output format specification
  - Implement prompt generation function with parameters
  - _Requirements: 1.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [ ] 7. Implement data mapping utilities
  - Create `scripts/utils/data_mapper.py`
  - Implement symbol to value mapping (○→5, △→3, ×→1)
  - Implement time slot mapping (朝→morning, 昼→noon, 夕→evening)
  - Implement boolean mapping (○→true, ×→false)
  - Implement memo field aggregation (defecation, vomiting, medication, notes)
  - Add default value application for OCR imports
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 10.2, 10.3, 10.4, 10.5_

- [ ]* 7.1 Write property test for time slot mapping
  - **Property 3: Time Slot Mapping Correctness**
  - **Validates: Requirements 3.9**

- [ ]* 7.2 Write property test for memo field aggregation
  - **Property 11: Memo Field Aggregation**
  - **Validates: Requirements 3.5, 3.6, 3.7, 3.8**

- [ ]* 7.3 Write property test for default value application
  - **Property 12: Default Value Application**
  - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**

- [ ]* 7.4 Write property test for from_paper flag
  - **Property 6: From Paper Flag Consistency**
  - **Validates: Requirements 1.6, 10.1**

- [ ] 8. Implement Kiro workflow orchestration
  - Create main orchestration logic (can be documented as Kiro usage guide)
  - Document file extension detection logic
  - Document prompt parsing for cat ID/name and year-month
  - Document LLM invocation with image and structured prompt
  - Document Hook invocation sequence
  - Document error handling and user notification
  - Document progress reporting
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 2.1, 2.5, 7.1, 7.2, 7.3, 7.4_

- [ ] 9. Create usage documentation
  - Create `docs/ocr-import-guide.md`
  - Document workflow for image files
  - Document workflow for PDF files
  - Document prompt format examples
  - Document error messages and troubleshooting
  - Add example commands
  - Add FAQ section
  - _Requirements: All_

- [ ] 10. Checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

- [ ]* 11. Integration testing
  - Create `scripts/tests/test_integration.py`
  - Test end-to-end image processing workflow
  - Test end-to-end PDF processing workflow
  - Test error recovery scenarios
  - Test with sample handwritten images
  - Test with various data quality levels
  - _Requirements: All_

- [ ] 12. Create sample data and test images
  - Create sample handwritten care log images
  - Create sample PDF with care log
  - Create sample JSON output files
  - Add to `scripts/tests/fixtures/`
  - _Requirements: All_

- [ ] 13. Final checkpoint - Ensure all tests pass
  - Ensure all tests pass, ask the user if questions arise.

---

## Implementation Notes

### Task Execution Order
1. **Foundation** (Tasks 1-4): Set up structure, utilities, and validation
2. **Core Functionality** (Tasks 5-7): Implement Hook scripts and data mapping
3. **Integration** (Task 8): Orchestrate workflow with Kiro
4. **Documentation** (Task 9): Create user guide
5. **Testing** (Tasks 10-13): Comprehensive testing and validation

### Dependencies Between Tasks
- Task 3 (cat identification) can be done in parallel with Task 2 (PDF conversion)
- Task 3 requires Task 5 (data registration) for API authentication logic, or can reuse the same auth mechanism
- Task 4 (JSON validator) must be completed before Task 5 (data registration)
- Task 7 (data mapping) should be completed before Task 8 (orchestration)
- Task 8 (orchestration) requires Tasks 2, 3, 5, 6, 7 to be completed
- Task 11 (integration testing) requires all core tasks (1-8) to be completed

### Testing Strategy
- Unit tests are marked with `*` as optional but recommended
- Property-based tests validate universal correctness properties
- Integration tests validate end-to-end workflows
- All tests should be run before final deployment

### Environment Setup
Before starting implementation, ensure:
- Python 3.10+ is installed
- Virtual environment is activated
- NecoKeeper API is running locally
- Database is initialized with test data
- Admin credentials are available

### Kiro Hook Configuration
Hooks will be invoked by Kiro using the following pattern:
```bash
# PDF Conversion Hook
python scripts/hooks/pdf_to_image.py <pdf_path>

# Data Registration Hook
python scripts/hooks/register_care_logs.py <json_file_path>
```

### Success Criteria
- All core functionality tasks (1-8) completed
- At least 70% test coverage
- All property-based tests passing
- Documentation complete and reviewed
- Successfully import sample handwritten records
