# Kiro Hooks 完全ガイド

NecoKeeperプロジェクトで利用可能なKiroフック機能の包括的なガイドです。

## 📋 目次

1. [概要](#概要)
2. [利用可能なフック一覧](#利用可能なフック一覧)
3. [使用方法](#使用方法)
4. [各フックの詳細](#各フックの詳細)
5. [トラブルシューティング](#トラブルシューティング)

---

## 概要

Kiroフックは、開発・運用プロセスを自動化するための強力な機能です。以下の2つのトリガータイプがあります：

### トリガータイプ

#### 1. ユーザートリガー（User Triggered）
- **特徴**: 手動実行、完全なコントロール
- **実行方法**:
  - 右クリックメニューから選択
  - コマンドパレット（Ctrl+Shift+P）から実行
  - ファイルに依存しない実行も可能
- **メリット**:
  - 実行タイミングを完全制御
  - 視覚的で直感的
  - デバッグが容易

#### 2. ファイルトリガー（File Triggered）
- **特徴**: ファイル操作時に自動実行
- **実行方法**:
  - ファイル保存時
  - ファイル作成時
  - 特定パターンのファイル変更時
- **メリット**:
  - 完全自動化
  - 手動操作不要
  - ワークフロー統合

---

## 利用可能なフック一覧

| フック名 | トリガー | 用途 | 状態 |
|---------|---------|------|------|
| [Pre-Commit Quality Gate](#1-pre-commit-quality-gate) | ユーザー | コミット前品質チェック | ✅ 有効 |
| [Test Coverage Analyzer](#2-test-coverage-analyzer) | ユーザー | カバレッジ分析と改善提案 | ✅ 有効 |
| [Register Care Logs (Manual)](#3-register-care-logs-manual) | ユーザー | ケアログ手動登録 | ✅ 有効 |
| [Register Care Logs (Auto)](#4-register-care-logs-auto) | ファイル | ケアログ自動登録 | ✅ 有効 |
| [PDF to Image Converter](#5-pdf-to-image-converter) | ユーザー | PDF→画像変換 | ✅ 有効 |
| [Auto-Translate Localization](#6-auto-translate-localization) | ファイル | 多言語翻訳自動化 | ⚠️ 無効 |

---

## 使用方法

### 方法1: 右クリックメニュー（推奨）

1. Kiroのファイルエクスプローラーでファイルを右クリック
2. 「Run Hook」メニューを選択
3. 実行したいフックを選択

### 方法2: コマンドパレット

1. `Ctrl+Shift+P`（Windows/Linux）または `Cmd+Shift+P`（macOS）
2. 「Kiro: Run Hook」と入力
3. 実行したいフックを選択

### 方法3: Kiroチャット

```
[フック名]を実行してください
```

例:
```
Pre-Commit Quality Gateを実行してください
```

---

## 各フックの詳細

### 1. Pre-Commit Quality Gate

**目的**: コミット前に全ての品質チェックを一括実行

**トリガー**: ユーザートリガー（手動実行）

**実行内容**:
1. 変更ファイルの確認（`git status`）
2. 品質チェック実行（`make all`）
   - Lint（Ruff check）
   - Format（Ruff format）
   - 型チェック（Mypy）
   - テスト実行（Pytest）
   - Prettier（JavaScript/JSON/YAML）
3. 結果の分析とレポート
4. カバレッジ確認
5. 最終確認チェックリスト

**使用タイミング**:
- コミット前（必須）
- プルリクエスト作成前
- 大きな変更後の確認

**実行方法**:
```bash
# コマンドパレットから
Ctrl+Shift+P → "Kiro: Run Hook" → "Pre-Commit Quality Gate"

# または直接makeコマンド
make all
```

**出力例**:
```
✅ 品質チェック完了

全てのチェックがパスしました。コミット可能です。

推奨コミットメッセージ:
git commit -m "feat(api): 新しいエンドポイントを追加"
```

**エラー時の対応**:
- **Lintエラー**: 自動修正可能な場合は`make format`を再実行
- **Mypyエラー**: 型ヒントを追加・修正
- **Testエラー**: 失敗したテストを修正

---

### 2. Test Coverage Analyzer

**目的**: テストカバレッジを詳細分析して改善提案

**トリガー**: ユーザートリガー（手動実行）

**実行内容**:
1. 現在のカバレッジ測定
2. レイヤー別カバレッジ分析
3. 目標値との比較
4. 優先度付けと分析
5. 不足しているテストケースの特定
6. 具体的な改善提案
7. HTMLレポート生成

**カバレッジ目標**:
- **ドメイン層（models/）**: 90%以上
- **サービス層（services/）**: 80%以上
- **API層（api/）**: 70%以上
- **認証層（auth/）**: 80%以上
- **ユーティリティ層（utils/）**: 70%以上
- **全体**: 70%以上（最終目標80%）

**使用タイミング**:
- 新機能実装後
- テスト追加後
- 週次レビュー時
- カバレッジ改善時

**実行方法**:
```bash
# コマンドパレットから
Ctrl+Shift+P → "Kiro: Run Hook" → "Test Coverage Analyzer"

# または直接コマンド
pytest --cov=app --cov-report=html --cov-report=term-missing
```

**出力例**:
```
📊 テストカバレッジ分析レポート
=====================================

## 現在のカバレッジ
- 全体: 80.99%
- ドメイン層: 92%
- サービス層: 75%
- API層: 78%

## 改善が必要なファイル（優先度順）

### 優先度：高
1. app/services/animal_service.py (現在: 36%, 目標: 80%)
   - 不足: 正常系テスト3件、異常系テスト2件
   - 推定工数: 30分
```

**HTMLレポート確認**:
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

**目的**: JSONファイルから手動でケアログを一括登録

**トリガー**: ユーザートリガー（手動実行）

**実行内容**:
1. JSONファイルの読み込み
2. データ形式の検証
3. Automation API経由で登録
4. 結果サマリーの表示
5. 処理済みファイルの移動

**使用タイミング**:
- OCR処理後のJSON登録
- バッチインポート
- データ移行

**実行方法**:

**方法1: 右クリック（推奨）**
1. `tmp/json/`ディレクトリのJSONファイルを右クリック
2. 「Run Hook: Register Care Logs (Manual)」を選択

**方法2: コマンドライン**
```bash
PYTHONPATH=. python scripts/hooks/register_care_logs.py tmp/json/your-file.json
```

**JSONフォーマット**:
```json
[
  {
    "animal_id": 1,
    "time_slot": "morning",
    "volunteer_name": "田中太郎",
    "feeding": true,
    "cleaning": true,
    "notes": "元気に過ごしています"
  }
]
```

**出力例**:
```
✅ ケアログ登録完了

成功: 5/5件
処理済みファイル: tmp/json/processed/care_log_20241114.json
```

**前提条件**:
- NecoKeeper APIが起動中（`http://localhost:8000`）
- 環境変数が設定済み（`.env`ファイル）
  - `NECOKEEPER_ADMIN_USERNAME`
  - `NECOKEEPER_ADMIN_PASSWORD`

---

### 4. Register Care Logs (Auto)

**目的**: JSONファイル保存時に自動でケアログを登録

**トリガー**: ファイルトリガー（`tmp/json/auto.json`保存時）

**実行内容**:
1. ファイル変更検知
2. 自動的にデータ読み込み
3. バリデーション
4. API経由で登録
5. 結果ログ出力

**使用タイミング**:
- OCRワークフローの自動化
- リアルタイムデータ同期

**設定方法**:
```json
{
  "enabled": true,
  "when": {
    "type": "fileEdited",
    "patterns": ["tmp/json/auto.json"]
  }
}
```

**ワークフロー例**:
```
1. OCR処理でJSONを生成
   ↓
2. tmp/json/auto.json に保存
   ↓
3. フックが自動実行
   ↓
4. データベースに登録完了
```

---

### 5. PDF to Image Converter

**目的**: PDFファイルを画像に変換（OCR前処理）

**トリガー**: ユーザートリガー（手動実行）

**実行内容**:
1. PDFファイルの読み込み
2. PyMuPDFまたはpdf2imageで画像変換
3. `tmp/images/`に保存
4. 変換結果の通知

**使用タイミング**:
- OCRワークフローの開始
- PDF資料のデジタル化

**実行方法**:

**方法1: 右クリック**
1. `tmp/pdf/`または`tmp/pdfs/`のPDFファイルを右クリック
2. 「Run Hook: PDF to Image Converter」を選択

**方法2: Kiroチャット**
```
tmp/pdf/sample.pdf を PyMuPDF で画像に変換してください
```

**方法3: コマンドライン**
```bash
# PyMuPDF使用（推奨）
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf --use-pymupdf

# pdf2image使用
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf
```

**出力例**:
```
✅ PDF変換完了

入力: tmp/pdf/sample.pdf
出力: tmp/images/sample_page1.png
      tmp/images/sample_page2.png
```

**依存関係**:
```bash
# PyMuPDF（推奨）
pip install PyMuPDF

# または pdf2image
pip install pdf2image
```

---

### 6. Auto-Translate Localization

**目的**: 多言語ファイルの自動翻訳

**トリガー**: ファイルトリガー（ローカライゼーションファイル変更時）

**状態**: ⚠️ 現在無効（`"enabled": false`）

**実行内容**:
1. 変更されたテキストの検出
2. ターゲット言語の特定
3. 各言語への翻訳生成
4. ロケール固有の規則適用
5. 翻訳ファイルの更新

**有効化方法**:
```json
{
  "enabled": true,
  "when": {
    "type": "fileEdited",
    "patterns": ["app/static/i18n/ja.json"]
  }
}
```

**使用例**:
```
1. app/static/i18n/ja.json を編集
   ↓
2. フックが自動実行
   ↓
3. en.json, zh.json などに自動翻訳
```

---

## トラブルシューティング

### 共通の問題

#### フックが実行されない

**原因と解決方法**:

1. **フックが無効化されている**
   ```json
   // .kiro.hookファイルを確認
   {
     "enabled": true  // falseになっていないか確認
   }
   ```

2. **ファイルパターンが一致しない**
   ```json
   // patternsを確認
   {
     "patterns": ["tmp/json/*.json"]  // パスが正しいか確認
   }
   ```

3. **権限エラー**
   ```bash
   # スクリプトに実行権限を付与
   chmod +x scripts/hooks/*.py
   ```

#### API認証エラー

**エラーメッセージ**:
```
❌ Authentication failed
```

**解決方法**:
```bash
# 1. .envファイルを確認
cat .env | grep NECOKEEPER

# 2. 必要な環境変数を設定
echo "NECOKEEPER_ADMIN_USERNAME=admin" >> .env
echo "NECOKEEPER_ADMIN_PASSWORD=your_password" >> .env

# 3. APIが起動しているか確認
curl http://localhost:8000/docs
```

#### モジュールインポートエラー

**エラーメッセージ**:
```
ModuleNotFoundError: No module named 'xxx'
```

**解決方法**:
```bash
# 1. 仮想環境を有効化
source .venv/bin/activate

# 2. 依存関係をインストール
pip install -r requirements.txt

# 3. PYTHONPATHを設定
export PYTHONPATH="$PWD:$PYTHONPATH"
```

### フック別の問題

#### Pre-Commit Quality Gate

**問題**: テストが失敗する
```bash
# 特定のテストのみ実行
pytest tests/test_specific.py -v

# 失敗したテストのみ再実行
pytest --lf
```

**問題**: Mypyエラーが多すぎる
```bash
# 特定のファイルのみチェック
mypy app/services/animal_service.py

# 段階的に修正
```

#### Test Coverage Analyzer

**問題**: HTMLレポートが開けない
```bash
# レポートが生成されているか確認
ls -la htmlcov/

# 再生成
pytest --cov=app --cov-report=html
```

#### Register Care Logs

**問題**: JSONフォーマットエラー
```bash
# JSON形式を検証
python -m json.tool tmp/json/your-file.json

# スキーマ確認
cat scripts/utils/json_schema.py
```

**問題**: ファイルが移動されない
```bash
# processed/ディレクトリを作成
mkdir -p tmp/json/processed

# 権限確認
ls -la tmp/json/
```

---

## ベストプラクティス

### 1. コミット前は必ずPre-Commit Quality Gateを実行

```bash
# 推奨ワークフロー
1. コード変更
2. Pre-Commit Quality Gate実行
3. 全てパスしたらコミット
4. プッシュ
```

### 2. 定期的にTest Coverage Analyzerを実行

```bash
# 推奨頻度
- 新機能実装後: 必須
- 週次レビュー: 推奨
- リリース前: 必須
```

### 3. ケアログ登録は自動化を活用

```bash
# 推奨ワークフロー
1. PDF → Image（手動）
2. Image → JSON（Kiroチャット）
3. JSON → DB（自動フック）
```

### 4. フックのカスタマイズ

```json
// 独自のフックを作成
{
  "enabled": true,
  "name": "My Custom Hook",
  "description": "カスタム処理",
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

## 参考リンク

- [Kiro Hooks 公式ドキュメント](https://docs.kiro.ai/hooks)
- [NecoKeeper API仕様](../../app/api/automation/README.md)
- [MCP統合ガイド](../../app/mcp/README.md)
- [OCRワークフローガイド](./README.md)

---

**最終更新**: 2024年11月30日
**バージョン**: 1.0.0
