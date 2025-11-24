# OCR Care Log Import Test Fixtures

This directory contains sample data and test images for testing the OCR care log import functionality.

## Files

### JSON Files

#### `sample_care_logs.json`
Standard care log data with typical records:
- Multiple days (11/4 - 11/5)
- All three time slots (morning, noon, evening)
- Various appetite and energy levels (○ = 5, △ = 3)
- Typical memo entries
- Animal ID: 1

**Use case**: Testing normal workflow with good quality data

#### `sample_edge_cases.json`
Edge case scenarios:
- Low appetite/energy (× = 1)
- Vomiting and medication records
- Different animals (IDs: 2, 3)
- Various date ranges

**Use case**: Testing error handling and edge cases

#### `sample_invalid_data.json`
Invalid data for validation testing:
- Out of range appetite value (10 instead of 1-5)
- Invalid date (Feb 30)
- Invalid time_slot (midnight instead of morning/noon/evening)
- Negative animal_id
- Missing required field (animal_id)

**Use case**: Testing JSON schema validation and error handling

### Image Files

#### `sample_care_log.png`
Standard quality handwritten care log image:
- Cat name: たま
- Period: 2025年11月
- 2 days of records (11/4 - 11/5)
- Clear, readable text
- Standard table format

**Use case**: Testing successful OCR extraction

#### `sample_edge_case.png`
Edge case care log image:
- Cat name: みけ
- Period: 2025年11月
- Records with poor health indicators (×)
- Notes about illness

**Use case**: Testing OCR with unusual values

#### `sample_poor_quality.png`
Poor quality image:
- Low contrast
- Blurry text
- Difficult to read

**Use case**: Testing error handling for poor quality images

### PDF Files

#### `sample_care_log.pdf`
Multi-day care log in PDF format:
- Cat name: あみ
- Period: 2025年5月
- 5 days of records (5/1 - 5/5)
- Includes all fields (meal, energy, urine, stool, vomit, medication)
- Various scenarios including illness and recovery

**Use case**: Testing PDF conversion and multi-day extraction

## Generating Test Files

### Regenerate Images

To regenerate the sample images:

```bash
python scripts/tests/fixtures/create_sample_images.py
```

This will create:
- `sample_care_log.png`
- `sample_edge_case.png`
- `sample_poor_quality.png`

### Regenerate PDF

To regenerate the sample PDF:

```bash
python scripts/tests/fixtures/create_sample_pdf.py
```

This will create:
- `sample_care_log.pdf`

## Data Format

### JSON Schema

All JSON files follow the Care Log schema defined in `scripts/utils/json_schema.py`:

```json
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
  "device_tag": "OCR-Import",
  "ip_address": null,
  "user_agent": null
}
```

### Symbol Mapping

The handwritten symbols are mapped as follows:

| Symbol | Field | Value |
|--------|-------|-------|
| ○ | appetite/energy | 5 |
| △ | appetite/energy | 3 |
| × | appetite/energy | 1 |
| ○ | urination | true |
| × | urination | false |
| ○ | stool/vomit/medication | "あり" (in memo) |
| × | stool/vomit/medication | "なし" (in memo) |

### Time Slot Mapping

| Japanese | English |
|----------|---------|
| 朝 | morning |
| 昼 | noon |
| 夕 | evening |

## Testing Scenarios

### Scenario 1: Image File Processing
```bash
# Use sample_care_log.png
# Expected: Extract 6 records (2 days × 3 time slots)
# Animal ID: 1
# Date range: 2025-11-04 to 2025-11-05
```

### Scenario 2: PDF File Processing
```bash
# Use sample_care_log.pdf
# Expected: Convert first page to image, then extract records
# Animal: あみ
# Date range: 2025-05-01 to 2025-05-05
# Expected: 15 records (5 days × 3 time slots)
```

### Scenario 3: Poor Quality Image
```bash
# Use sample_poor_quality.png
# Expected: Error notification about poor image quality
# System should request manual verification
```

### Scenario 4: Edge Cases
```bash
# Use sample_edge_case.png or sample_edge_cases.json
# Expected: Handle low values (×), illness indicators
# Memo should contain vomiting and medication information
```

## Integration with Tests

These fixtures are used by:
- Unit tests in `tests/utils/`
- Integration tests in `scripts/tests/test_integration.py`
- Manual testing via Kiro workflow

## Maintenance

When updating the care log schema or adding new test scenarios:

1. Update the JSON files to match the new schema
2. Regenerate images if visual format changes
3. Update this README with new scenarios
4. Run all tests to ensure compatibility

## Dependencies

The generator scripts require:
- `Pillow` (PIL) for image generation
- Python 3.10+

Install dependencies:
```bash
pip install Pillow
```

## Notes

- Images are generated programmatically to ensure consistency
- Japanese text may not render perfectly depending on available fonts
- PDF files are created from images for simplicity
- All test data uses fictional cat names and dates
