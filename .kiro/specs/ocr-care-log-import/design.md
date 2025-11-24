# Design Document

## Overview

手書きの猫世話記録表（PDF/画像）をOCR解析し、NecoKeeperのデータベースに自動登録するシステムを設計します。Kiroをオーケストレーターとして、マルチモーダルLLMによる画像解析とHookスクリプトによる自動化を組み合わせた実装を行います。

## Architecture

### System Components - 3-Phase Hook Workflow

**Design Rationale**: 段階的なワークフローにより、各フェーズで人間の確認・修正が可能。OCRの誤認識を事前に修正でき、データの整合性を保証。

```
┌─────────────────────────────────────────────────────────────┐
│  Phase 1: PDF → Image (自動Hook)                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: PDFを tmp/pdfs/ に配置                                │
│    ↓                                                        │
│  Kiro Hook: ファイル保存を検知                                │
│    ↓                                                        │
│  pdf_to_image.py: PDF → PNG変換                             │
│    ↓                                                        │
│  Output: tmp/images/ に画像を出力                            │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 2: Image → JSON (手動 + Kiroチャット)                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  User: Kiroチャットで画像を添付                               │
│    ↓                                                        │
│  User: 「ID12の猫、11/14-11/23のデータをJSONに変換」          │
│    ↓                                                        │
│  Kiro: マルチモーダルLLMでOCR解析                             │
│    ↓                                                        │
│  Kiro: JSON生成                                             │
│    ↓                                                        │
│  User: JSONを確認・修正（必要に応じて）                        │
│    ↓                                                        │
│  User: tmp/json/ に保存                                     │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
┌─────────────────────────────────────────────────────────────┐
│  Phase 3: JSON → Database (自動Hook)                         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Kiro Hook: ファイル保存を検知                                │
│    ↓                                                        │
│  register_care_logs.py: JSON読み込み                         │
│    ↓                                                        │
│  API認証 (POST /api/v1/auth/token)                          │
│    ↓                                                        │
│  データ登録 (POST /api/v1/care-logs)                         │
│    ↓                                                        │
│  Output: 結果ログ + 処理済みファイル移動                       │
│                                                             │
└─────────────────────────────────────────────────────────────┘
                         ↓
                 ┌──────────────────┐
                 │  PostgreSQL DB   │
                 │  care_logs table │
                 └──────────────────┘
```

### Benefits of 3-Phase Workflow

1. **人間の確認ポイント**
   - Phase 2でJSONを確認・修正可能
   - OCRミスを事前に修正
   - データ品質の保証

2. **段階的な処理**
   - 各Phaseが独立して動作
   - エラー時の切り分けが容易
   - 再実行が簡単

3. **柔軟性**
   - PDFスキップして直接画像から開始可能
   - JSONを手動作成して登録も可能
   - 部分的な自動化

4. **Kiroの強みを活用**
   - ファイル監視Hookで自動化
   - チャットでインタラクティブな修正
   - LLMの画像解析能力を活用

### Workflow Sequence

#### Workflow 1: Direct Image Processing (Image → JSON → Database)

**Use Case**: ユーザーが既に画像ファイルを持っている場合

```
User → File System: 画像を tmp/images/ に配置（または既に存在）
  │
  ├─→ User → Kiro Chat: 画像を添付
  │                     「ID12の猫、2024-11-14から11-23のデータをJSONに変換して
  │                      tmp/json/care_log_20241114.json に保存して」
  │
  ├─→ Kiro: ユーザープロンプトから抽出
  │     - animal_id: 12
  │     - start_date: 2024-11-14
  │     - end_date: 2024-11-23
  │     - output_path: tmp/json/care_log_20241114.json
  │
  ├─→ Kiro → LLM: マルチモーダル解析
  │     │         プロンプト: 「animal_id=12, 期間=2024-11-14～11-23で
  │     │                     この画像からJSONを生成」
  │     │
  │     └─→ LLM: OCR解析 → JSON生成
  │           [
  │             {"animal_id": 12, "log_date": "2024-11-14", "time_slot": "morning", ...},
  │             {"animal_id": 12, "log_date": "2024-11-14", "time_slot": "noon", ...},
  │             ...
  │           ]
  │
  ├─→ Kiro: JSONをファイルに保存
  │     tmp/json/care_log_20241114.json
  │
  ├─→ User: JSONを確認・修正（必要に応じて）
  │
  ├─→ Kiro Hook: ファイル保存を検知（tmp/json/*.json）
  │     │
  │     └─→ register_care_logs.py 自動実行
  │           │
  │           ├─→ API認証 (POST /api/v1/auth/token)
  │           │
  │           ├─→ データ登録 (POST /api/v1/care-logs)
  │           │
  │           └─→ 結果ログ出力 + ファイル移動
  │
  └─→ Kiro → User: 「✅ 24件の記録を登録しました」
```

**Benefits**:
1. **人間の確認**: JSONを保存前に確認・修正可能
2. **柔軟性**: 画像から直接開始できる
3. **自動化**: JSON保存後は自動でDB登録

#### Workflow 2: Full PDF Processing (PDF → Image → JSON → Database)

**Use Case**: ユーザーがPDFファイルから開始する場合

```
User → File System: PDFを tmp/pdfs/ に配置
  │                 例: tmp/pdfs/care_log_202411.pdf
  │
  ├─→ Kiro Hook: ファイル保存を検知（tmp/pdfs/*.pdf）
  │     │
  │     └─→ pdf_to_image.py 自動実行
  │           │
  │           ├─→ PDF読み込み
  │           │
  │           ├─→ 最初のページをPNGに変換
  │           │
  │           └─→ tmp/images/care_log_202411_page1.png に保存
  │
  ├─→ Kiro → User: 「✅ PDF変換完了: tmp/images/care_log_202411_page1.png
  │                 次のステップ: Kiroチャットで画像を開いてJSONに変換してください」
  │
  ├─→ User → Kiro Chat: 画像を添付
  │                     「ID12の猫、2024-11-14から11-23のデータをJSONに変換して
  │                      tmp/json/care_log_20241114.json に保存して」
  │
  ├─→ Kiro → LLM: マルチモーダル解析
  │     │
  │     └─→ LLM: OCR解析 → JSON生成
  │
  ├─→ Kiro: JSONをファイルに保存
  │     tmp/json/care_log_20241114.json
  │
  ├─→ User: JSONを確認・修正（必要に応じて）
  │
  ├─→ Kiro Hook: ファイル保存を検知（tmp/json/*.json）
  │     │
  │     └─→ register_care_logs.py 自動実行
  │           │
  │           ├─→ API認証
  │           │
  │           ├─→ データ登録
  │           │
  │           └─→ 結果ログ出力
  │
  └─→ Kiro → User: 「✅ 24件の記録を登録しました」
```

**Benefits**:
1. **完全自動化**: PDF配置 → 画像変換は自動
2. **人間の確認**: JSON生成時に確認・修正可能
3. **段階的処理**: 各フェーズで状態確認可能

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

**Purpose**: ユーザーがKiroチャットで使用するプロンプトの例

**Example 1: 基本的な使い方**
```
これはIDが12の猫の2024年11月14日～23日の記録です。
猫のお世話記録登録用のregister_care_logs.pyの仕様に合わせてJSON化して
tmp/json/care_log_20241114.json に保存して
```

**Example 2: 年をまたぐ場合**
```
これはIDが4の猫の2024年11月15日～25日の記録です。
scripts/hooks/register_care_logs.pyの仕様に合わせてJSON化して
tmp/json/care_log_202411.json に保存して
```

**Example 3: 短縮形**
```
ID12、11/14-11/23、JSON化してtmp/json/に保存
```

### 4. Kiro's Internal Prompt Template

**Purpose**: Kiroが内部的に使用するLLMプロンプトテンプレート

**Template**:
```
あなたは手書きの猫世話記録表を解析するOCRアシスタントです。

ユーザーが指定した情報：
- 猫ID: {animal_id}
- 対象期間: {start_date} ～ {end_date}

この情報を使用して、画像から世話記録を抽出してください。

【重要】
- すべてのレコードの animal_id は {animal_id} に設定してください
- 日付は {start_date} から {end_date} の範囲内のみ抽出してください
- 範囲外の日付は無視してください

【抽出する項目】
1. 日付（M/D形式または11/14形式）
2. 時間帯（朝/昼/夕）
3. 飲水（○/×）
4. 元気（○/△/×）
5. 排尿（○/×）
6. 清掃（○/×）
7. メモ（手書きメモ）
8. 記録者（手書き名前）

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
    "cleaning": true | false,
    "memo": "排便: なし, 嘔吐: なし, 投薬: なし, 備考: ...",
    "recorder_name": "OCR自動取込",
    "from_paper": true,
    "recorder_id": null,
    "device_tag": "OCR-Import",
    "ip_address": null,
    "user_agent": null
  }}
]

【マッピングルール】
- 飲水: ○→appetite=5, ×→appetite=3, 空欄→appetite=3
- 元気: ○→energy=5, △→energy=3, ×→energy=1, 空欄→energy=3
- 排尿: ○→true, ×→false, 空欄→false
- 清掃: ○→true, ×→false, 空欄→false
- 朝→morning, 昼→noon, 夕→evening
- 日付: M/D形式を YYYY-MM-DD に変換（YYYYは{start_date}の年を使用）

【メモ欄の処理】
- 手書きメモがある場合: "排便: なし, 嘔吐: なし, 投薬: なし, 備考: {手書きメモ}"
- 手書きメモがない場合: "排便: なし, 嘔吐: なし, 投薬: なし"
- 記録者名がある場合: 備考に追記 "備考: {記録者名}"

【注意事項】
- 読み取れない文字は "?" で表記
- 不明確な記号は保守的に解釈（空欄として扱う）
- 各日付・時間帯ごとに1レコード作成
- animal_id は必ず {animal_id} を使用（画像から読み取らない）
- 日付範囲外のデータは出力しない

【実例】
画像に「11/14 朝 ○ ○ × ×」とある場合：
{{
  "animal_id": {animal_id},
  "log_date": "{start_date.year}-11-14",
  "time_slot": "morning",
  "appetite": 5,
  "energy": 5,
  "urination": false,
  "cleaning": false,
  "memo": "排便: なし, 嘔吐: なし, 投薬: なし",
  "recorder_name": "OCR自動取込",
  "from_paper": true,
  "recorder_id": null,
  "device_tag": "OCR-Import",
  "ip_address": null,
  "user_agent": null
}}

画像を解析して、上記形式のJSONを出力してください。
```

**Design Rationale**:
- ユーザー指定の `animal_id` をプロンプトに含めることで、OCRの誤認識を防止
- 日付範囲を明示することで、範囲外データの混入を防止
- 実例を示すことで、LLMの出力精度を向上

### 4. Kiro Hook Scripts

#### Hook 1: PDF to Image Converter (自動実行)

**File**: `.kiro/hooks/pdf_to_image_hook.py`

**Trigger**: ファイル保存時（`tmp/pdfs/*.pdf`）

**Purpose**: PDFの最初のページを画像に自動変換

**Implementation**:
```python
"""
Kiro Hook: PDF → Image 自動変換
Trigger: tmp/pdfs/*.pdf にファイルが保存されたとき
"""
import sys
from pathlib import Path
from scripts.hooks.pdf_to_image import convert_pdf_to_image

def main():
    pdf_path = sys.argv[1]  # Kiroから渡されるファイルパス

    try:
        # PDF → PNG変換
        image_path = convert_pdf_to_image(
            pdf_path=pdf_path,
            output_dir="tmp/images"
        )

        print(f"✅ PDF変換完了: {image_path}")
        print(f"")
        print(f"次のステップ:")
        print(f"1. Kiroチャットで画像を開く")
        print(f"2. 「ID<猫ID>の猫、<開始日>から<終了日>のデータをJSONに変換して")
        print(f"    tmp/json/<ファイル名>.json に保存して」と指示")

    except Exception as e:
        print(f"❌ PDF変換エラー: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
```

#### Hook 2: JSON to Database Registrar (自動実行)

**File**: `.kiro/hooks/register_care_logs_hook.py`

**Trigger**: ファイル保存時（`tmp/json/*.json`）

**Purpose**: JSONファイルを自動的にデータベースに登録

**Implementation**:
```python
"""
Kiro Hook: JSON → Database 自動登録
Trigger: tmp/json/*.json にファイルが保存されたとき
"""
import sys
import json
from pathlib import Path
from scripts.hooks.register_care_logs import register_care_logs
from scripts.utils.logging_config import setup_logger

logger = setup_logger("register_care_logs_hook")

def main():
    json_path = sys.argv[1]  # Kiroから渡されるファイルパス

    try:
        # JSONファイル読み込み
        with open(json_path) as f:
            care_logs = json.load(f)

        logger.info(f"JSONファイル読み込み: {json_path}")
        logger.info(f"レコード数: {len(care_logs)}")

        # API経由でデータ登録
        result = register_care_logs(
            care_logs=care_logs,
            api_base_url="http://localhost:8000",
            admin_username="admin",
            admin_password="password"  # TODO: 環境変数から取得
        )

        # 結果表示
        print(f"")
        print(f"✅ データ登録完了")
        print(f"  成功: {result['success_count']}件")
        print(f"  失敗: {result['failed_count']}件")

        if result['failed_count'] > 0:
            print(f"")
            print(f"❌ エラー詳細:")
            for error in result['errors']:
                print(f"  - {error}")

        # 処理済みファイルを移動
        processed_dir = Path("tmp/json/processed")
        processed_dir.mkdir(parents=True, exist_ok=True)

        processed_path = processed_dir / Path(json_path).name
        Path(json_path).rename(processed_path)

        logger.info(f"処理済みファイル移動: {processed_path}")

    except Exception as e:
        logger.error(f"データ登録エラー: {e}")
        print(f"❌ エラー: {e}")
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
- **Animal Not Found**: Return 404 "指定された猫が見つかりません"
- **Invalid Date Range**: Return 400 "日付範囲が不正です（開始日 > 終了日）"
- **Invalid File Format**: Return 415 "サポートされていないファイル形式です（JPG, PNG, PDFのみ）"
- **File Size Exceeded**: Return 413 "ファイルサイズが大きすぎます（最大50MB）"

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

## User Workflow

### Workflow Example: PDF → Database

```bash
# Step 1: PDFを配置（自動でHook実行）
$ cp ~/Downloads/care_log_202411.pdf tmp/pdfs/

# Kiro Hook自動実行
✅ PDF変換完了: tmp/images/care_log_202411_page1.png

次のステップ:
Kiroチャットで画像を添付して、以下のように指示してください：
「これはIDが<猫ID>の猫の<開始日>～<終了日>の記録です。
 猫のお世話記録登録用のregister_care_logs.pyの仕様に合わせてJSON化して
 tmp/json/<ファイル名>.json に保存して」

# Step 2: Kiroチャットで対話的にJSON生成
User: [画像を添付]
      「これはIDが12の猫の2024年11月14日～23日の記録です。
       猫のお世話記録登録用のregister_care_logs.pyの仕様に合わせてJSON化して
       tmp/json/care_log_20241114.json に保存して」

Kiro: [画像を解析中...]
      [ユーザープロンプトから抽出]
      - animal_id: 12
      - start_date: 2024-11-14
      - end_date: 2024-11-23
      - output_path: tmp/json/care_log_20241114.json

      [JSON生成中...]

Kiro: ✅ JSONファイルを保存しました: tmp/json/care_log_20241114.json
      24件のレコードを生成しました。

# (オプション) JSONを確認・修正
$ cat tmp/json/care_log_20241114.json
$ vim tmp/json/care_log_20241114.json  # 必要に応じて修正

# Step 3: JSONを保存（自動でHook実行）
# ファイルを保存すると自動的にKiro Hookが実行される

# Kiro Hook自動実行
JSONファイル読み込み: tmp/json/care_log_20241114.json
レコード数: 24

✅ データ登録完了
  成功: 24件
  失敗: 0件

処理済みファイル移動: tmp/json/processed/care_log_20241114.json
```

### Prompt Variations

```bash
# パターン1: 詳細指定
「これはIDが4の猫の2024年11月15日～25日の記録です。
 scripts/hooks/register_care_logs.pyの仕様に合わせてJSON化して
 tmp/json/care_log_202411.json に保存して」

# パターン2: 簡潔指定
「ID12、11/14-11/23、JSON化してtmp/json/に保存」

# パターン3: 年をまたぐ場合
「これはIDが7の猫の2024年12月25日～2025年1月5日の記録です。
 JSON化してtmp/json/care_log_202412.json に保存して」
```

### Directory Structure

```
tmp/
├── pdfs/                    # PDF配置フォルダ（Hook監視）
│   └── care_log_202411.pdf
│
├── images/                  # 変換後の画像（Hook出力）
│   └── care_log_202411_page1.png
│
└── json/                    # JSON配置フォルダ（Hook監視）
    ├── care_log_20241114.json
    └── processed/           # 処理済みファイル
        └── care_log_20241114.json
```

### User Experience Principles

1. **段階的な処理**
   - 各フェーズで状態確認可能
   - エラー時の切り分けが容易
   - 再実行が簡単

2. **人間の確認ポイント**
   - Phase 2でJSONを確認・修正可能
   - OCRミスを事前に修正
   - データ品質の保証

3. **自動化と柔軟性のバランス**
   - PDF変換は自動（Phase 1）
   - JSON生成は対話的（Phase 2）
   - DB登録は自動（Phase 3）

4. **明確なフィードバック**
   - 各Hookの実行結果を表示
   - 次のステップを明示
   - エラー時の対処方法を提示

## Future Enhancements

### Phase 2 Features
- Multi-page PDF processing（複数ページの一括処理）
- Batch processing of multiple files（複数ファイルの一括アップロード）
- OCR confidence scoring（信頼度スコア表示）
- Manual correction interface（取り込み前のプレビュー・修正機能）
- Historical data comparison（過去データとの比較・重複チェック）
- Export error logs（エラーログのCSVエクスポート）

### Phase 3 Features
- Real-time preview of extracted data（リアルタイムプレビュー）
- Interactive field correction（フィールド単位の修正UI）
- Template-based extraction for different form layouts（複数フォーマット対応）
- Mobile app integration（モバイルアプリからの直接アップロード）
- Cloud-based OCR service option（クラウドOCRサービス連携）
- AI-powered handwriting recognition improvement（手書き認識精度の継続的改善）
