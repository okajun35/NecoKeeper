# Kiro Hooks Complete Guide

This is a comprehensive guide to the Kiro hook features available in the NecoKeeper project.

## 📋 Table of Contents

1. [Overview](#overview)
2. [Available Hooks](#available-hooks)
3. [How to Use](#how-to-use)
4. [Hook Details](#hook-details)
5. [Troubleshooting](#troubleshooting)

---

## Overview

Kiro hooks are a powerful feature for automating development and operations workflows. There are two trigger types:

### Trigger Types

#### 1. User Triggered
- **Characteristics**: Manual execution, full control
- **How to run**:
  - Use the context menu
  - Use the command palette (Ctrl+Shift+P)
  - Can be executed without depending on a specific file
- **Benefits**:
  - Full control over execution timing
  - Visual and intuitive
  - Easy to debug

#### 2. File Triggered
- **Characteristics**: Automatically executed on file operations
- **How to run**:
  - On file save
  - On file creation
  - On changes to files matching a specific pattern
- **Benefits**:
  - Fully automated
  - No manual operation required
  - Integrated into the workflow

---

## Available Hooks

| Hook Name | Trigger | Purpose | Status |
|----------|---------|---------|--------|
| [Pre-Commit Quality Gate](#1-pre-commit-quality-gate) | User | Quality checks before commit | ✅ Enabled |
| [Test Coverage Analyzer](#2-test-coverage-analyzer) | User | Coverage analysis and improvement suggestions | ✅ Enabled |
| [Register Care Logs (Manual)](#3-register-care-logs-manual) | User | Manual care log registration | ✅ Enabled |
| [Register Care Logs (Auto)](#4-register-care-logs-auto) | File | Automatic care log registration | ✅ Enabled |
| [PDF to Image Converter](#5-pdf-to-image-converter) | User | Convert PDF to images | ✅ Enabled |
| [Auto-Translate Localization](#6-auto-translate-localization) | File | Automated localization translation | ⚠️ Disabled |

---

## How to Use

### Method 1: Context Menu (Recommended)

1. Right-click a file in Kiro's file explorer
2. Select the "Run Hook" menu
3. Choose the hook you want to run

### Method 2: Command Palette

1. Press `Ctrl+Shift+P` (Windows/Linux) or `Cmd+Shift+P` (macOS)
2. Type `Kiro: Run Hook`
3. Choose the hook you want to run

### Method 3: Kiro Chat

```
Please run [hook name]
```

Example:
```
Please run Pre-Commit Quality Gate
```

---

## Hook Details

### 1. Pre-Commit Quality Gate

**Purpose**: Run all quality checks at once before committing.

**Trigger**: User triggered (manual execution)

**What it does**:
1. Verify changed files (`git status`)
2. Run quality checks (`make all`)
   - Lint (Ruff check)
   - Format (Ruff format)
   - Type checking (Mypy)
   - Tests (Pytest)
   - Prettier (JavaScript/JSON/YAML)
3. Analyze results and report
4. Verify coverage
5. Final verification checklist

**When to use**:
- Before committing (Required)
- Before creating a pull request
- After large changes for verification

**How to run**:
```bash
# From the command palette
Ctrl+Shift+P → "Kiro: Run Hook" → "Pre-Commit Quality Gate"

# Or directly using make
make all
```

**Sample output**:
```
✅ Quality checks completed

All checks have passed. You can safely commit.

Recommended commit message:
git commit -m "feat(api): add new endpoint"
```

**How to handle errors**:
- **Lint errors**: If auto-fixable, run `make format` again
- **Mypy errors**: Add or fix type hints
- **Test errors**: Fix the failing tests

---

### 2. Test Coverage Analyzer

**Purpose**: Analyze test coverage in detail and propose improvements.

**Trigger**: User triggered (manual execution)

**What it does**:
1. Measure current coverage
2. Analyze coverage by layer
3. Compare against target values
4. Prioritize and analyze
5. Identify missing test cases
6. Provide concrete improvement suggestions
7. Generate HTML report

**Coverage targets**:
- **Domain layer (`models/`)**: 90%+
- **Service layer (`services/`)**: 80%+
- **API layer (`api/`)**: 70%+
- **Authentication layer (`auth/`)**: 80%+
- **Utility layer (`utils/`)**: 70%+
- **Overall**: 70%+ (final goal: 80%+)

**When to use**:
- After implementing a new feature
- After adding tests
- During weekly review
- When focusing on coverage improvement

**How to run**:
```bash
# From the command palette
Ctrl+Shift+P → "Kiro: Run Hook" → "Test Coverage Analyzer"

# Or directly via command
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**Sample output**:
```
📊 Test coverage analysis report
=====================================

## Current coverage
- Overall: 80.99%
- Domain layer: 92%
- Service layer: 75%
- API layer: 78%

## Files needing improvement (by priority)

### Priority: High
1. app/services/animal_service.py (Current: 36%, Target: 80%)
   - Missing: 3 normal-case tests, 2 error-case tests
   - Estimated effort: 30 minutes
```

**Verifying the HTML report**:
```bash
# Linux
xdg-open htmlcov/index.html

# macOS
open htmlcov/index.html

# Windows
start htmlcov/index.html
```

---

### 3. Register Care Logs (Manual)

**Purpose**: Manually bulk-register care logs from a JSON file.

**Trigger**: User triggered (manual execution)

**What it does**:
1. Read the JSON file
2. Validate data format
3. Register via the Automation API
4. Show a summary of results
5. Move processed files

**When to use**:
- Registering JSON after OCR processing
- Batch import
- Data migration

**How to run**:

**Method 1: Context menu (Recommended)**
1. Right-click a JSON file in the `tmp/json/` directory
2. Select "Run Hook: Register Care Logs (Manual)"

**Method 2: Command line**
```bash
PYTHONPATH=. python scripts/hooks/register_care_logs.py tmp/json/your-file.json
```

**JSON format**:
```json
[
  {
    "animal_id": 1,
    "time_slot": "morning",
    "volunteer_name": "Taro Tanaka",
    "feeding": true,
    "cleaning": true,
    "notes": "In good condition today"
  }
]
```

**Sample output**:
```
✅ Care log registration completed

Success: 5/5 entries
Processed file: tmp/json/processed/care_log_20241114.json
```

**Prerequisites**:
- NecoKeeper API is running (`http://localhost:8000`)
- Environment variables are set in the `.env` file:
  - `NECOKEEPER_ADMIN_USERNAME`
  - `NECOKEEPER_ADMIN_PASSWORD`

---

### 4. Register Care Logs (Auto)

**Purpose**: Automatically register care logs when a JSON file is saved.

**Trigger**: File trigger (when `tmp/json/auto.json` is saved)

**What it does**:
1. Detect file changes
2. Automatically read data
3. Validate data
4. Register via API
5. Output result logs

**When to use**:
- Automating the OCR workflow
- Real-time data synchronization

**Configuration example**:
```json
{
  "enabled": true,
  "when": {
    "type": "fileEdited",
    "patterns": ["tmp/json/auto.json"]
  }
}
```

**Workflow example**:
```
1. OCR process generates JSON
   ↓
2. Save to tmp/json/auto.json
   ↓
3. Hook runs automatically
   ↓
4. Data is registered to the database
```

---

### 5. PDF to Image Converter

**Purpose**: Convert PDF files to images (pre-processing for OCR).

**Trigger**: User triggered (manual execution)

**What it does**:
1. Read the PDF file
2. Convert pages to images using PyMuPDF or pdf2image
3. Save images to `tmp/images/`
4. Notify the conversion result

**When to use**:
- Starting the OCR workflow
- Digitizing PDF documents

**How to run**:

**Method 1: Context menu**
1. Right-click a PDF file in `tmp/pdf/` or `tmp/pdfs/`
2. Select "Run Hook: PDF to Image Converter"

**Method 2: Kiro Chat**
```
Convert tmp/pdf/sample.pdf to images using PyMuPDF
```

**Method 3: Command line**
```bash
# Using PyMuPDF (Recommended)
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf --use-pymupdf

# Using pdf2image
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf
```

**Sample output**:
```
✅ PDF conversion completed

Input: tmp/pdf/sample.pdf
Output: tmp/images/sample_page1.png
        tmp/images/sample_page2.png
```

**Dependencies**:
```bash
# PyMuPDF (Recommended)
pip install PyMuPDF

# Or pdf2image
pip install pdf2image
```

---

### 6. Auto-Translate Localization

**Purpose**: Automatically translate localization files.

**Trigger**: File trigger (when localization files change)

**Status**: ⚠️ Currently disabled (`"enabled": false`)

**What it does**:
1. Detect changed text
2. Determine target languages
3. Generate translations for each language
4. Apply locale-specific rules
5. Update translation files

**How to enable**:
```json
{
  "enabled": true,
  "when": {
    "type": "fileEdited",
    "patterns": ["app/static/i18n/ja.json"]
  }
}
```

**Usage example**:
```
1. Edit app/static/i18n/ja.json
   ↓
2. Hook runs automatically
   ↓
3. en.json, zh.json, etc. are auto-translated
```

---

## Troubleshooting

### Common Issues

#### Hook does not run

**Possible causes and fixes**:

1. **Hook is disabled**
   ```json
   // Check the .kiro.hook file
   {
     "enabled": true  // Make sure it is not false
   }
   ```

2. **File pattern does not match**
   ```json
   // Check patterns
   {
     "patterns": ["tmp/json/*.json"]  // Verify the path is correct
   }
   ```

3. **Permission error**
   ```bash
   # Grant execute permission to scripts
   chmod +x scripts/hooks/*.py
   ```

#### API authentication error

**Error message**:
```
❌ Authentication failed
```

**Fix**:
```bash
# 1. Check .env file
cat .env | grep NECOKEEPER

# 2. Set required environment variables
echo "NECOKEEPER_ADMIN_USERNAME=admin" >> .env
echo "NECOKEEPER_ADMIN_PASSWORD=your_password" >> .env

# 3. Verify API is running
curl http://localhost:8000/docs
```

#### Module import error

**Error message**:
```
ModuleNotFoundError: No module named 'xxx'
```

**Fix**:
```bash
# 1. Activate virtual environment
source .venv/bin/activate

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set PYTHONPATH
export PYTHONPATH="$PWD:$PYTHONPATH"
```

### Hook-Specific Issues

#### Pre-Commit Quality Gate

**Issue**: Tests are failing
```bash
# Run only a specific test
pytest tests/test_specific.py -v

# Re-run only failed tests
pytest --lf
```

**Issue**: Too many Mypy errors
```bash
# Check only a specific file
mypy app/services/animal_service.py

# Fix them gradually
```

#### Test Coverage Analyzer

**Issue**: Cannot open HTML report
```bash
# Check if report was generated
ls -la htmlcov/

# Regenerate
pytest --cov=app --cov-report=html
```

#### Register Care Logs

**Issue**: JSON format error
```bash
# Validate JSON format
python -m json.tool tmp/json/your-file.json

# Check schema
cat scripts/utils/json_schema.py
```

**Issue**: File is not moved
```bash
# Create processed/ directory
mkdir -p tmp/json/processed

# Check permissions
ls -la tmp/json/
```

---

## Best Practices

### 1. Always run Pre-Commit Quality Gate before committing

```bash
# Recommended workflow
1. Make code changes
2. Run Pre-Commit Quality Gate
3. Commit only after all checks pass
4. Push
```

### 2. Run Test Coverage Analyzer regularly

```bash
# Recommended frequency
- After implementing new features: Required
- Weekly review: Recommended
- Before release: Required
```

### 3. Use automation for care log registration

```bash
# Recommended workflow
1. PDF → Image (manual)
2. Image → JSON (via Kiro Chat)
3. JSON → DB (automatic hook)
```

### 4. Customize hooks

```json
// Create a custom hook
{
  "enabled": true,
  "name": "My Custom Hook",
  "description": "Custom processing",
  "when": {
    "type": "userTriggered"
  },
  "then": {
    "type": "runCommand",
    "command": "python my_script.py"
  }
}
```

---

## References

- [Kiro Hooks Official Documentation](https://docs.kiro.ai/hooks)
- [NecoKeeper API Specification](../../app/api/automation/README.md)
- [MCP Integration Guide](../../app/mcp/README.md)
- [OCR Workflow Guide](./README.md)

---

**Last Updated**: November 30, 2024
**Version**: 1.0.0
