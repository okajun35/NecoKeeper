# OCR Care Log Import Guide

## 概要

このガイドでは、手書きの猫世話記録表（PDF/画像）をOCR解析し、NecoKeeperのデータベースに自動登録する方法を説明します。

## 前提条件

### システム要件
- Python 3.10以上
- NecoKeeper APIが起動していること（デフォルト: `http://localhost:8000`）
- 管理者アカウントの認証情報

### 必要な環境変数

`.env`ファイルに以下を設定してください：

```bash
# NecoKeeper API設定
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=your_secure_password

# OCR設定（オプション）
OCR_TEMP_DIR=tmp/images
OCR_LOG_FILE=logs/ocr-import.log
```

### 依存ライブラリのインストール

```bash
# 仮想環境を有効化
source .venv/bin/activate  # Linux/Mac
# または
.venv\Scripts\activate  # Windows

# 必要なライブラリをインストール
pip install pdf2image Pillow requests python-dotenv
```

---

## ワークフロー1: 画像ファイルからのインポート

### 対応フォーマット
- JPEG (`.jpg`, `.jpeg`)
- PNG (`.png`)

### 基本的な使い方

#### ステップ1: 画像ファイルを準備

手書きの世話記録表を撮影またはスキャンして画像ファイルを用意します。

**推奨事項**:
- 解像度: 300 DPI以上
- フォーマット: JPEG または PNG
- ファイルサイズ: 10MB以下
- 照明: 均一で明るい環境
- 角度: 正面から撮影（歪みを最小限に）

#### ステップ2: Kiroで画像を開く

Kiroのチャット画面で画像ファイルをドラッグ&ドロップするか、画像追加ボタンをクリックして選択します。

#### ステップ3: プロンプトを入力

以下の形式でプロンプトを入力します：

```
この画像から猫ID {animal_id} の {year}年{month}月の記録を登録して
```

**例**:
```
この画像から猫ID 5 の2025年11月の記録を登録して
```

または猫の名前を使用：

```
この画像から猫「あみ」の2025年11月の記録を登録して
```

#### ステップ4: 処理の実行

Kiroが以下の処理を自動的に実行します：

1. **画像解析**: マルチモーダルLLMが画像内のテキストと表構造を解析
2. **データ抽出**: 日付、時間帯、食欲、元気、排尿などの情報を抽出
3. **JSON生成**: 抽出したデータをCare Log形式のJSONに変換
4. **バリデーション**: データの妥当性を検証
5. **API登録**: NecoKeeper APIを通じてデータベースに登録

#### ステップ5: 結果の確認

処理が完了すると、以下のような結果が表示されます：

```
✅ 登録完了
- 成功: 10件
- 失敗: 0件
- 対象猫: あみ (ID: 3)
- 対象期間: 2025年11月
```

---

## ワークフロー2: PDFファイルからのインポート

### 対応フォーマット
- PDF (`.pdf`)

### 基本的な使い方

#### ステップ1: PDFファイルを準備

手書きの世話記録表をスキャンしてPDFファイルを作成します。

**注意事項**:
- **最初のページのみ**が処理されます
- 複数ページのPDFの場合、2ページ目以降は無視されます
- ファイルサイズ: 50MB以下推奨

#### ステップ2: Kiroでプロンプトを入力

PDFファイルのパスを含むプロンプトを入力します：

```
このPDFから猫「あみ」の2025年5月の記録を登録して
```

または：

```
record.pdfから猫ID 3の2025年5月の記録を登録して
```

#### ステップ3: 処理の実行

Kiroが以下の処理を自動的に実行します：

1. **PDF変換**: PDFの最初のページを画像に変換（`scripts/hooks/pdf_to_image.py`）
2. **画像解析**: 変換した画像をマルチモーダルLLMで解析
3. **データ抽出**: 世話記録情報を抽出
4. **JSON生成**: Care Log形式のJSONに変換
5. **バリデーション**: データの妥当性を検証
6. **API登録**: データベースに登録（`scripts/hooks/register_care_logs.py`）

#### ステップ4: 結果の確認

処理が完了すると、登録結果が表示されます。

---

## プロンプト形式の詳細

### 必須要素

1. **猫の識別子**: 猫IDまたは猫の名前
2. **対象期間**: 年と月

### プロンプトのパターン

#### パターン1: 猫IDを使用

```
この画像から猫ID {animal_id} の {year}年{month}月の記録を登録して
```

**例**:
- `この画像から猫ID 1 の2025年11月の記録を登録して`
- `この画像から猫ID 5 の2025年12月の記録を登録して`

#### パターン2: 猫の名前を使用

```
この画像から猫「{name}」の {year}年{month}月の記録を登録して
```

**例**:
- `この画像から猫「たま」の2025年11月の記録を登録して`
- `この画像から猫「あみ」の2025年12月の記録を登録して`

#### パターン3: PDFファイル

```
{filename}から猫「{name}」の {year}年{month}月の記録を登録して
```

**例**:
- `record.pdfから猫「あみ」の2025年5月の記録を登録して`
- `care_log_202511.pdfから猫ID 3の2025年11月の記録を登録して`

### オプション要素

プロンプトには以下のような追加情報を含めることもできます：

```
この画像から猫「たま」の2025年11月の記録を登録して。
読み取りにくい部分は確認してください。
```

---

## データマッピング規則

### 手書き記号の解釈

| 手書き記号 | 意味 | Care Logフィールド | 値 |
|-----------|------|-------------------|-----|
| ○ | 良好/あり | appetite, energy | 5 |
| △ | 普通 | appetite, energy | 3 |
| × | 不良/なし | appetite, energy | 1 |
| ○ | あり | urination | true |
| × | なし | urination | false |
| 数字 | 回数 | urination | true (回数はmemoに記載) |

### 時間帯のマッピング

| 手書き | Care Log |
|-------|----------|
| 朝 | morning |
| 昼 | noon |
| 夕 | evening |

### フィールドのマッピング

| 手書き項目 | Care Logフィールド | データ型 | 備考 |
|-----------|-------------------|---------|------|
| 日付 | log_date | date | YYYY-MM-DD形式 |
| 朝/昼/夕 | time_slot | string | morning/noon/evening |
| ごはん | appetite | int (1-5) | ○→5, △→3, ×→1 |
| 元気 | energy | int (1-5) | ○→5, △→3, ×→1 |
| 排尿 | urination | boolean | ○→true, ×→false |
| 排便 | memo | string | memoフィールドに追記 |
| 嘔吐 | memo | string | memoフィールドに追記 |
| 投薬 | memo | string | memoフィールドに追記 |
| 備考 | memo | string | memoフィールドに追記 |

### 自動設定されるフィールド

OCR経由で登録されたレコードには、以下のデフォルト値が自動的に設定されます：

| フィールド | 値 | 説明 |
|-----------|-----|------|
| recorder_name | "OCR自動取込" | 記録者名 |
| from_paper | true | 紙記録フラグ |
| device_tag | "OCR-Import" | デバイスタグ |
| cleaning | false | 清掃フラグ（手書き表にないため） |
| recorder_id | null | 記録者ID（未指定） |
| ip_address | null | IPアドレス（未指定） |
| user_agent | null | ユーザーエージェント（未指定） |

---

## エラーメッセージとトラブルシューティング

### エラーメッセージ一覧

#### 1. ファイル関連エラー

**エラー**: `PDF file not found: {path}`

**原因**: 指定されたPDFファイルが存在しない

**対処法**:
- ファイルパスが正しいか確認
- ファイルが存在するか確認
- 相対パスまたは絶対パスを正しく指定

---

**エラー**: `Failed to convert PDF to image: {error}`

**原因**: PDF変換処理が失敗

**対処法**:
- PDFファイルが破損していないか確認
- ファイルサイズが大きすぎないか確認（50MB以下推奨）
- pdf2imageライブラリが正しくインストールされているか確認

```bash
pip install pdf2image
```

---

#### 2. 猫識別エラー

**エラー**: `Cat not found: {identifier}`

**原因**: 指定された猫IDまたは名前が見つからない

**対処法**:
- 猫IDが正しいか確認
- 猫の名前が正確か確認（大文字小文字は区別されません）
- NecoKeeper APIで猫のリストを確認

```bash
curl http://localhost:8000/api/v1/animals
```

---

**エラー**: `Multiple cats found with name: {name}`

**原因**: 同じ名前の猫が複数存在する

**対処法**:
- 猫IDを使用してプロンプトを再実行
- 猫の名前をより具体的に指定

**例**:
```
# 名前の代わりにIDを使用
この画像から猫ID 5 の2025年11月の記録を登録して
```

---

#### 3. データバリデーションエラー

**エラー**: `Invalid date: {date}`

**原因**: 日付が無効（例: 2月30日）

**対処法**:
- 手書き記録の日付を確認
- 画像の品質を改善して再試行
- 必要に応じて手動で修正

---

**エラー**: `Appetite value {value} is out of range (1-5)`

**原因**: 食欲の値が1-5の範囲外

**対処法**:
- 手書き記号（○△×）が正しく読み取られているか確認
- 画像の品質を改善
- 該当レコードはスキップされ、他のレコードは処理されます

---

**エラー**: `Required field missing: {field}`

**原因**: 必須フィールドが欠落

**対処法**:
- 手書き記録が完全に記入されているか確認
- 画像全体が写っているか確認
- 該当レコードはスキップされ、他のレコードは処理されます

---

#### 4. API認証エラー

**エラー**: `Authentication failed: Invalid credentials`

**原因**: 管理者認証情報が正しくない

**対処法**:
- `.env`ファイルの認証情報を確認
- ユーザー名とパスワードが正しいか確認

```bash
# .envファイルを確認
cat .env | grep NECOKEEPER_ADMIN
```

---

**エラー**: `API connection failed: Connection refused`

**原因**: NecoKeeper APIが起動していない

**対処法**:
- APIサーバーを起動

```bash
uvicorn app.main:app --reload
```

- APIのURLが正しいか確認（デフォルト: `http://localhost:8000`）

---

#### 5. 画像品質エラー

**エラー**: `Image quality too poor for OCR`

**原因**: 画像の品質が低く、テキストが読み取れない

**対処法**:
- より高解像度で撮影/スキャン（300 DPI以上推奨）
- 照明を改善
- 正面から撮影（歪みを最小限に）
- 手ブレを防ぐ

---

**エラー**: `Unreadable text in image`

**原因**: 一部のテキストが読み取れない

**対処法**:
- 読み取れない部分は "?" として記録されます
- 画像品質を改善して再試行
- 必要に応じて手動で修正

---

### トラブルシューティングガイド

#### 問題: 画像が正しく解析されない

**チェックリスト**:
- [ ] 画像の解像度は十分か（300 DPI以上）
- [ ] 照明は均一で明るいか
- [ ] 画像に歪みや影がないか
- [ ] 手書き文字が明瞭か
- [ ] 画像全体が写っているか

**対処法**:
1. 画像を再撮影/再スキャン
2. 画像編集ソフトで明るさ・コントラストを調整
3. 複数の画像を試す

---

#### 問題: 一部のレコードが登録されない

**原因**:
- データバリデーションエラー
- 日付が無効
- 値が範囲外

**対処法**:
1. エラーログを確認

```bash
cat logs/ocr-import.log
```

2. 失敗したレコードの詳細を確認
3. 手動で修正が必要な場合は、NecoKeeperのUIから直接入力

---

#### 問題: PDFが変換されない

**チェックリスト**:
- [ ] pdf2imageがインストールされているか
- [ ] PDFファイルが破損していないか
- [ ] ファイルサイズが適切か（50MB以下）
- [ ] PDFが画像ベースか（テキストベースのPDFは非対応）

**対処法**:
1. pdf2imageを再インストール

```bash
pip install --upgrade pdf2image
```

2. PDFを画像として保存し、画像ファイルとして処理

---

#### 問題: 処理が遅い

**原因**:
- 画像サイズが大きい
- LLM処理に時間がかかる
- ネットワーク遅延

**対処法**:
1. 画像サイズを最適化（1-2MB程度）
2. 画像の解像度を調整（300-600 DPI）
3. 複数の画像を分割して処理

---

## コマンドライン使用例

### 直接スクリプトを実行する場合

#### PDF変換

```bash
# PDFを画像に変換
python scripts/hooks/pdf_to_image.py path/to/record.pdf

# 出力: tmp/images/record_page1.png
```

#### データ登録

```bash
# JSONファイルからデータを登録
python scripts/hooks/register_care_logs.py path/to/care_logs.json

# 環境変数を指定して実行
NECOKEEPER_API_URL=http://localhost:8000 \
NECOKEEPER_ADMIN_USERNAME=admin \
NECOKEEPER_ADMIN_PASSWORD=password \
python scripts/hooks/register_care_logs.py care_logs.json
```

#### 猫の識別

```python
# Pythonスクリプト内で使用
from scripts.utils.cat_identifier import identify_cat

# 猫IDで識別
animal_id = identify_cat(5, api_base_url, auth_token)

# 猫名で識別
animal_id = identify_cat("あみ", api_base_url, auth_token)
```

---

## FAQ（よくある質問）

### Q1: 複数ページのPDFを処理できますか？

**A**: 現在のバージョンでは、PDFの**最初のページのみ**が処理されます。複数ページを処理したい場合は、各ページを個別のPDFまたは画像として保存し、それぞれ処理してください。

---

### Q2: 手書き文字の認識精度はどのくらいですか？

**A**: 認識精度は以下の要因に依存します：
- 画像の解像度（300 DPI以上推奨）
- 照明条件（均一で明るい環境）
- 手書き文字の明瞭さ
- 使用するLLMモデルの性能

一般的に、明瞭な手書き文字と高品質な画像であれば、90%以上の精度が期待できます。

---

### Q3: 読み取りエラーが発生した場合、どうすればよいですか？

**A**: 以下の手順で対処してください：

1. **エラーログを確認**:
```bash
cat logs/ocr-import.log
```

2. **画像品質を改善**:
   - より高解像度で撮影/スキャン
   - 照明を改善
   - 正面から撮影

3. **手動修正**:
   - 失敗したレコードはNecoKeeperのUIから手動で入力

---

### Q4: 同じ名前の猫が複数いる場合はどうすればよいですか？

**A**: 猫の名前の代わりに**猫ID**を使用してください：

```
この画像から猫ID 5 の2025年11月の記録を登録して
```

猫IDは以下のコマンドで確認できます：

```bash
curl http://localhost:8000/api/v1/animals
```

---

### Q5: 一部のレコードが登録されない場合はどうすればよいですか？

**A**: システムは**部分的な成功**をサポートしています。一部のレコードが失敗しても、他のレコードは正常に登録されます。

失敗したレコードの詳細は以下で確認できます：

```bash
cat logs/ocr-import.log
```

失敗したレコードは、NecoKeeperのUIから手動で入力してください。

---

### Q6: OCR経由で登録されたレコードを識別できますか？

**A**: はい、OCR経由で登録されたレコードには以下のフラグが設定されます：

- `from_paper`: `true`
- `recorder_name`: `"OCR自動取込"`
- `device_tag`: `"OCR-Import"`

これらのフィールドでフィルタリングすることで、OCR経由のレコードを識別できます。

---

### Q7: 日付の形式はどのように指定しますか？

**A**: 手書き記録では**M/D形式**（例: 11/4）で記入してください。年と月はプロンプトで指定します：

```
この画像から猫ID 5 の2025年11月の記録を登録して
```

システムが自動的に`2025-11-04`形式に変換します。

---

### Q8: 空欄のフィールドはどのように処理されますか？

**A**: 空欄のフィールドには以下のデフォルト値が適用されます：

- `appetite`: 3（普通）
- `energy`: 3（普通）
- `urination`: false
- `cleaning`: false
- `memo`: null（空文字列）

---

### Q9: 処理にかかる時間はどのくらいですか？

**A**: 処理時間は以下の要因に依存します：

- 画像サイズ: 1-2MB程度で最適
- レコード数: 1日3回×7日 = 21レコードで約30-60秒
- LLM処理: 画像解析に20-40秒
- API登録: レコードあたり1-2秒

一般的に、1週間分の記録（21レコード）で**1-2分程度**です。

---

### Q10: セキュリティ上の注意点はありますか？

**A**: 以下の点に注意してください：

1. **認証情報の管理**:
   - `.env`ファイルをGitにコミットしない
   - 管理者パスワードを定期的に変更

2. **ファイルの取り扱い**:
   - 一時ファイルは自動的に削除されます
   - 機密情報を含む画像は処理後に削除

3. **API接続**:
   - HTTPS接続を推奨（本番環境）
   - APIトークンは安全に保管

---

## サポート

### ログファイルの確認

問題が発生した場合は、まずログファイルを確認してください：

```bash
# OCRインポートログ
cat logs/ocr-import.log

# アプリケーションログ
cat server.log
```

### デバッグモードの有効化

詳細なログを出力するには、環境変数を設定します：

```bash
export LOG_LEVEL=DEBUG
```

### 問題の報告

問題を報告する際は、以下の情報を含めてください：

1. エラーメッセージ
2. ログファイルの関連部分
3. 使用した画像の例（可能であれば）
4. 実行したコマンドまたはプロンプト
5. 環境情報（OS、Pythonバージョン等）

---

## 付録

### A. サンプルJSON出力

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
    "device_tag": "OCR-Import",
    "ip_address": null,
    "user_agent": null
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
    "device_tag": "OCR-Import",
    "ip_address": null,
    "user_agent": null
  }
]
```

### B. 手書き記録表のサンプル

```
猫の世話記録表 - 2025年11月

猫名: あみ

日付 | 時間 | ごはん | 元気 | 排尿 | 排便 | 嘔吐 | 投薬 | 備考
-----|------|--------|------|------|------|------|------|------
11/4 | 朝   | ○     | ○   | ○   | ○   | ×   | ×   |
11/4 | 夕   | ○     | ○   | ×   | ×   | ×   | ×   | 夕ご飯もよく食べられました
11/5 | 朝   | △     | ○   | ○   | ○   | ×   | ×   |
11/5 | 昼   | ○     | ○   | ○   | ×   | ×   | ×   |
11/5 | 夕   | ○     | ○   | ×   | ○   | ×   | ×   |
```

### C. 環境変数の完全リスト

```bash
# 必須
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=your_secure_password

# オプション
OCR_TEMP_DIR=tmp/images
OCR_LOG_FILE=logs/ocr-import.log
LOG_LEVEL=INFO

# データベース（NecoKeeper本体）
DATABASE_URL=postgresql://user:password@localhost/necokeeper

# セキュリティ（NecoKeeper本体）
SECRET_KEY=your_secret_key_here
```

### D. 関連ドキュメント

- [NecoKeeper README](../README.md)
- [デプロイガイド](../DEPLOY.md)
- [API仕様書](./api-documentation.md)（作成予定）

---

**最終更新**: 2025-11-23
**バージョン**: 1.0.0
