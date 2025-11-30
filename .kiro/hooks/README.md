# Kiro Hooks Configuration

このディレクトリには、NecoKeeperプロジェクトの開発・運用を自動化するKiroフック設定が含まれています。

## 📚 ドキュメント

- **[完全ガイド](./HOOKS_GUIDE.md)** - 全フックの詳細な説明と使用方法
- **[クイックリファレンス](./QUICK_REFERENCE.md)** - よく使うコマンドとワークフローのチートシート
- **[OCRワークフロー](#overview)** - OCRケアログインポートの詳細（このファイル）

---

## OCR Care Log Import Workflow

This directory contains Kiro Hook configurations for automating the OCR care log import workflow.

## Overview

The OCR care log import workflow consists of 3 phases:

1. **Phase 1**: PDF → Image conversion
2. **Phase 2**: Image → JSON conversion (via Kiro chat with user-specified metadata)
3. **Phase 3**: JSON → Database registration

### Hook Trigger Type: Manual

Both hooks use **manual triggers**, which means:
- ✅ Right-click on any file matching the pattern to run the hook
- ✅ Works on existing files (no need to create new files)
- ✅ Works regardless of how the file was created (IDE, command-line, etc.)
- ✅ Full control over when to execute
- ✅ Visual, intuitive interface

**Why Manual Triggers?**
- **Flexibility**: Works with any file, anytime
- **Reliability**: No dependency on file system events
- **User Control**: Execute only when ready
- **Better UX**: Right-click context menu is intuitive

## Practical Workflow (Recommended)

### Method 1: Manual Hook Trigger (Easiest)

**Best for**: Quick, visual workflow with right-click context menu

**Step 1: PDF to Image**
1. Navigate to `tmp/pdf/` or `tmp/pdfs/` in Kiro file explorer
2. Right-click on a PDF file (e.g., `sample-cat-log.pdf`)
3. Select **"Run Hook: PDF to Image Converter"**
4. Kiro will execute the conversion and show the output path

**Step 2: Image to JSON (Interactive)**
1. Attach the generated image in Kiro chat
2. Provide prompt with metadata:
```
これはIDが12の猫の2024年11月14日～23日の記録です。
scripts/utils/prompt_template.py のテンプレートを参照して、
JSON化してtmp/json/care_log_20241114.json に保存してください。
```

**Step 3: JSON to Database**
1. Navigate to `tmp/json/` in Kiro file explorer
2. Right-click on the JSON file (e.g., `care_log_20241114.json`)
3. Select **"Run Hook: Care Log Data Registration"**
4. Kiro will register the data and show the summary

### Method 2: Kiro Chat Commands

**Best for**: Automation, scripting, or when you prefer typing commands

**Step 1: PDF to Image**
```
tmp/pdf/sample-cat-log.pdf を PyMuPDF で画像に変換してください
```

**Step 2: Image to JSON (Interactive)**
```
[画像を添付: tmp/images/sample-cat-log_page1.png]

これはIDが12の猫の2024年11月14日～23日の記録です。
JSON化してtmp/json/care_log_20241114.json に保存してください。
```

**Step 3: JSON to Database**
```
tmp/json/care_log_20241114.json をデータベースに登録してください
```

### Method 3: Command Line

**Best for**: Automation, CI/CD, or batch processing

```bash
# Step 1: PDF to Image
python scripts/hooks/pdf_to_image.py tmp/pdf/sample-cat-log.pdf --use-pymupdf

# Step 2: Image to JSON (requires Kiro chat for OCR)

# Step 3: JSON to Database
python scripts/hooks/register_care_logs.py tmp/json/care_log_20241114.json
```

### Why Use Manual Hooks?

1. **Visual**: Right-click context menu is intuitive
2. **Reliable**: Works on any file, regardless of how it was created
3. **Flexible**: Can be triggered on existing files
4. **Integrated**: Executes within Kiro with full error handling
5. **No typing**: No need to remember command syntax

## Configured Hooks

### 1. PDF to Image Converter (`pdf_to_image.kiro.hook`)

**Purpose**: Converts PDF files to images for OCR processing.

**Configuration**:
- **Enabled**: Yes
- **Trigger**: Manual (right-click on file)
- **Patterns**: `tmp/pdfs/*.pdf`, `tmp/pdf/*.pdf`
- **Action**: Runs `python scripts/hooks/pdf_to_image.py {{file_path}} --use-pymupdf`
- **Output**: PNG image saved to `tmp/images/`

**How to Use**:
1. Right-click on any PDF file in `tmp/pdf/` or `tmp/pdfs/`
2. Select "Run Hook: PDF to Image Converter"
3. Kiro executes the conversion automatically

**Requirements Validated**:
- 5.1: Two Kiro Hooks configured
- 5.2: Supports PDF files in watched directories
- 5.4: Receives file path as argument
- 5.5: Logs result and notifies user on success
- 5.6: Logs error with details on failure

**Usage**:

**Method 1: Manual Hook Trigger (Recommended)**

1. Navigate to `tmp/pdf/` or `tmp/pdfs/` in Kiro file explorer
2. Right-click on a PDF file
3. Select **"Run Hook: PDF to Image Converter"**
4. Kiro will execute the conversion and display results

**Method 2: Via Kiro Chat**

```
tmp/pdf/sample-cat-log.pdf を PyMuPDF で画像に変換してください
```

**Method 3: Command Line**
```bash
# Using PyMuPDF (recommended - no external dependencies)
python scripts/hooks/pdf_to_image.py tmp/pdf/your-file.pdf --use-pymupdf

# Using pdf2image (requires poppler installation)
python scripts/hooks/pdf_to_image.py tmp/pdf/your-file.pdf
```

**Next Steps After Conversion**:
1. Open Kiro chat
2. Attach the generated image
3. Provide prompt: "これはIDが<猫ID>の猫の<開始日>～<終了日>の記録です。JSON化してtmp/json/<ファイル名>.json に保存して"

### 2. Care Log Data Registration (`register_care_logs.kiro.hook`)

**Purpose**: Registers care log data to the NecoKeeper database.

**Configuration**:
- **Enabled**: Yes
- **Trigger**: Manual (right-click on file)
- **Patterns**: `tmp/json/*.json`, `tmp/*.json`
- **Action**: Runs `python scripts/hooks/register_care_logs.py {{file_path}}`
- **Output**: Registers data via API, moves processed file to `tmp/json/processed/`

**How to Use**:
1. Right-click on any JSON file in `tmp/json/` or `tmp/`
2. Select "Run Hook: Care Log Data Registration"
3. Kiro executes the registration automatically

**Requirements Validated**:
- 5.1: Two Kiro Hooks configured
- 5.3: Supports JSON files in watched directories
- 5.4: Receives file path as argument
- 5.5: Logs result and notifies user on success
- 5.6: Logs error with details on failure
- 6.2: Reads and validates JSON structure
- 6.3: Authenticates with NecoKeeper API
- 6.4: Registers each record via POST /api/v1/care-logs
- 6.5: Displays summary with success/failure counts
- 6.6: Moves processed JSON to `tmp/json/processed/`
- 6.7: Logs detailed error messages and keeps file on failure

**Prerequisites**:
- NecoKeeper API must be running (default: http://localhost:8000)
- Environment variables must be set:
  - `NECOKEEPER_API_URL` (optional, defaults to http://localhost:8000)
  - `NECOKEEPER_ADMIN_USERNAME` (required)
  - `NECOKEEPER_ADMIN_PASSWORD` (required)

**Usage**:

**Method 1: Manual Hook Trigger (Recommended)**

1. Navigate to `tmp/json/` in Kiro file explorer
2. Right-click on a JSON file
3. Select **"Run Hook: Care Log Data Registration"**
4. Kiro will execute the registration and display summary

**Method 2: Via Kiro Chat**

```
tmp/json/care_log_20241114.json をデータベースに登録してください
```

**Method 3: Command Line**
```bash
python scripts/hooks/register_care_logs.py tmp/json/your-file.json
```

**Error Handling**:
- Authentication failures: All records marked as failed
- Individual record failures: Processing continues with remaining records
- Network errors: Detailed error messages logged
- Failed files remain in `tmp/json/` for retry

## Directory Structure

```
tmp/
├── pdfs/                    # Phase 1 input (Hook監視)
├── images/                  # Phase 1 output / Phase 2 input
└── json/                    # Phase 2 output / Phase 3 input (Hook監視)
    └── processed/           # Phase 3 output (処理済み)
```

## Environment Setup

### Required Environment Variables

Create a `.env` file in the project root with the following variables:

```bash
# NecoKeeper API Configuration
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=your_secure_password
```

### Required Dependencies

```bash
# PDF conversion (choose one)
pip install pdf2image  # Recommended
# OR
pip install PyMuPDF    # Alternative

# API requests
pip install requests

# Other dependencies
pip install python-dotenv
```

## Testing the Workflow

### Test PDF to Image Conversion

**Via Kiro Chat (Recommended)**:
```
tmp/pdf/file.pdf を PyMuPDF で画像に変換してください
```

**Via Command Line**:
```bash
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf --use-pymupdf
```

**Expected Output**:
- Image created: `tmp/images/file_page1.png`
- Log message: "PDF変換が完了しました"

### Test Care Log Registration

**Prerequisites**:
```bash
# 1. Ensure API is running
uvicorn app.main:app --reload

# 2. Set environment variables in .env file
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=password
```

**Via Kiro Chat (Recommended)**:
```
tmp/test_care_logs.json をデータベースに登録してください
```

**Via Command Line**:
```bash
python scripts/hooks/register_care_logs.py tmp/test_care_logs.json
```

**Expected Output**:
- Registration summary with success/failure counts
- Processed file moved to `tmp/json/processed/`

## Troubleshooting

### PDF Conversion Hook Issues

**Problem**: Hook doesn't trigger
- **Solution**: Ensure the hook is enabled in `pdf_to_image.kiro.hook`
- **Solution**: Check that the file is placed in `tmp/pdfs/` directory
- **Solution**: Verify file has `.pdf` extension

**Problem**: Conversion fails
- **Solution**: Install pdf2image or PyMuPDF: `pip install pdf2image`
- **Solution**: Check PDF file is not corrupted
- **Solution**: Verify file size is under 50MB

### Registration Hook Issues

**Problem**: Authentication fails
- **Solution**: Verify environment variables are set correctly
- **Solution**: Check API is running: `curl http://localhost:8000/docs`
- **Solution**: Verify admin credentials are correct

**Problem**: Registration fails
- **Solution**: Check JSON format matches schema (see `scripts/utils/json_schema.py`)
- **Solution**: Verify animal_id exists in database
- **Solution**: Check date format is YYYY-MM-DD
- **Solution**: Ensure appetite/energy values are 1-5

**Problem**: File not moved to processed/
- **Solution**: Check write permissions on `tmp/json/processed/` directory
- **Solution**: Verify registration completed successfully (status: success or partial_success)

## Logs

All hook executions are logged to:
- `logs/ocr-import.log` - Detailed execution logs
- Console output - Summary and user notifications

## Disabling Hooks

To temporarily disable a hook, edit the `.kiro.hook` file and set:

```json
{
  "enabled": false,
  ...
}
```

## Manual Execution

Hooks can also be executed manually for testing:

```bash
# PDF to Image
python scripts/hooks/pdf_to_image.py tmp/pdfs/test.pdf

# Care Log Registration
python scripts/hooks/register_care_logs.py tmp/json/test.json
```

## References

- Requirements: `.kiro/specs/ocr-care-log-import/requirements.md`
- Design: `.kiro/specs/ocr-care-log-import/design.md`
- User Guide: `docs/ocr-import-guide.md`
