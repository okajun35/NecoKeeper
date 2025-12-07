# Implementation Plan

## Overview

手書きの猫世話記録表（PDF/画像）をOCR解析してNecoKeeperデータベースに自動登録する3段階ワークフローを実装します。

**3段階ワークフロー**:
- **Phase 1（自動Hook）**: PDF → 画像変換
- **Phase 2（対話的）**: 画像 → JSON変換（Kiroチャットで猫ID・日付範囲を指定）
- **Phase 3（自動Hook）**: JSON → データベース登録

**既存コードの状況**:
- `scripts/hooks/pdf_to_image.py` ✅ 完成
- `scripts/hooks/register_care_logs.py` ✅ 完成
- `scripts/utils/` 配下のユーティリティ ✅ 完成

---

## Tasks

- [x] 1. プロジェクト構造とユーティリティのセットアップ
  - ディレクトリ構造の作成（`tmp/pdfs/`, `tmp/images/`, `tmp/json/`, `tmp/json/processed/`）
  - 依存関係の追加（`pdf2image`, `PyMuPDF`, `requests`, `Pillow`）
  - 環境変数テンプレートの作成
  - ロギング設定の実装（`scripts/utils/logging_config.py`）
  - _Requirements: All_

- [x] 2. データマッピングユーティリティの実装
  - `scripts/utils/data_mapper.py` の実装
  - 記号→数値マッピング（○→5, △→3, ×→1）
  - 時間帯マッピング（朝→morning, 昼→noon, 夕→evening）
  - ブール値マッピング（○→true, ×→false）
  - メモフィールド集約（排便、嘔吐、投薬、備考）
  - OCRデフォルト値の適用
  - _Requirements: 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9, 10.2, 10.3, 10.4, 10.5_

- [ ]* 2.1 データマッピングのプロパティテストを作成
  - **Property 3: Time Slot Mapping Correctness**
  - **Validates: Requirements 3.9**

- [ ]* 2.2 メモフィールド集約のプロパティテストを作成
  - **Property 11: Memo Field Aggregation**
  - **Validates: Requirements 3.5, 3.6, 3.7, 3.8**

- [ ]* 2.3 デフォルト値適用のプロパティテストを作成
  - **Property 12: Default Value Application**
  - **Validates: Requirements 10.2, 10.3, 10.4, 10.5**

- [x] 3. JSONスキーマバリデーターの実装
  - `scripts/utils/json_schema.py` の実装
  - Care Log JSONスキーマの定義
  - スキーマバリデーション関数の実装
  - フィールドレベルバリデーション（範囲、型、フォーマット）
  - 日付バリデーション（年月範囲チェック付き）
  - 詳細なバリデーションエラーの返却
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ]* 3.1 JSON構造妥当性のプロパティテストを作成
  - **Property 1: JSON Structure Validity**
  - **Validates: Requirements 1.1, 3.1**

- [ ]* 3.2 日付範囲整合性のプロパティテストを作成
  - **Property 2: Date Range Consistency**
  - **Validates: Requirements 4.6**

- [ ]* 3.3 値範囲妥当性のプロパティテストを作成
  - **Property 4: Appetite and Energy Range Validity**
  - **Validates: Requirements 3.2, 3.3, 8.2**

- [ ]* 3.4 ブール値フィールド妥当性のプロパティテストを作成
  - **Property 5: Boolean Field Validity**
  - **Validates: Requirements 3.4, 8.3**

- [ ]* 3.5 from_paperフラグのプロパティテストを作成
  - **Property 6: From Paper Flag Consistency**
  - **Validates: Requirements 1.6, 10.1**

- [x] 4. 猫識別ユーティリティの実装
  - `scripts/utils/cat_identifier.py` の実装
  - GET /api/v1/animals で全猫を取得
  - animal_id（整数）による識別（メモリ内検索）
  - 名前（文字列）による識別（メモリ内検索）
  - 大文字小文字を区別しない名前マッチング
  - 複数マッチエラーの処理
  - マッチなしエラーの処理
  - データベース依存なし（APIのみ）
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ]* 4.1 猫識別のユニットテストを作成
  - IDによる識別のテスト
  - 名前による識別のテスト
  - 大文字小文字を区別しないマッチングのテスト
  - 複数マッチエラーのテスト
  - マッチなしエラーのテスト
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ]* 4.2 ユーザー指定animal_idバリデーションのプロパティテストを作成
  - **Property 7: User-Specified Animal ID Validation**
  - **Validates: Requirements 4.1, 4.3, 4.4**

- [x] 5. LLMプロンプトテンプレートの作成
  - `scripts/utils/prompt_template.py` の実装
  - プレースホルダー付き構造化プロンプトテンプレートの定義
  - プロンプト内のマッピングルールドキュメント
  - 出力フォーマット仕様の追加
  - パラメータ付きプロンプト生成関数の実装
  - _Requirements: 1.1, 3.1, 3.2, 3.3, 3.4, 3.5, 3.6, 3.7, 3.8, 3.9_

- [x] 6. Phase 1: PDF変換Hookスクリプトの実装
  - `scripts/hooks/pdf_to_image.py` の実装 ✅
  - pdf2imageまたはPyMuPDFを使用したPDF最初のページ抽出
  - ファイルバリデーション（存在、拡張子、サイズ）
  - 変換失敗のエラーハンドリング
  - 一時ファイルのクリーンアップ
  - 標準化されたフォーマットで画像パスを返却
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5_

- [ ]* 6.1 PDF変換のユニットテストを作成
  - 変換成功のテスト
  - PDFが見つからないエラーのテスト
  - 破損PDFの処理テスト
  - 出力パス生成のテスト
  - エラー時のクリーンアップのテスト
  - _Requirements: 2.1, 2.2, 2.4_

- [ ]* 6.2 PDF最初のページ抽出のプロパティテストを作成
  - **Property 8: PDF First Page Extraction**
  - **Validates: Requirements 2.1, 2.3**

- [x] 7. Phase 3: データ登録Hookスクリプトの実装
  - `scripts/hooks/register_care_logs.py` の実装 ✅
  - API認証の実装（POST /api/v1/auth/token）
  - 認証トークンの保存と再利用
  - バッチ登録ループの実装
  - 個別レコード失敗のエラーハンドリング
  - 失敗時も処理を継続（停止しない）
  - 登録サマリーの生成（成功/失敗カウント）
  - 詳細なエラーログ
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5, 6.6, 6.7, 7.2, 7.4, 7.5_

- [ ]* 7.1 データ登録のユニットテストを作成
  - 認証成功のテスト
  - 認証失敗のテスト
  - バッチ登録成功のテスト
  - 個別レコード失敗処理のテスト
  - ネットワークエラーリトライロジックのテスト
  - サマリー生成のテスト
  - _Requirements: 6.4, 6.5, 7.4, 7.5_

- [ ]* 7.2 API認証成功のプロパティテストを作成
  - **Property 9: API Authentication Success**
  - **Validates: Requirements 6.3**

- [ ]* 7.3 バッチ登録原子性のプロパティテストを作成
  - **Property 10: Batch Registration Atomicity**
  - **Validates: Requirements 7.4, 7.5**

- [x] 8. Kiro Hook設定ファイルの作成
  - `.kiro/hooks/config.json` の作成
  - pdf_to_image_hook の設定（`tmp/pdfs/*.pdf` を監視）
  - register_care_logs_hook の設定（`tmp/json/*.json` を監視）
  - Hook実行スクリプトのパス設定
  - トリガー条件の設定
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6, 5.7_

- [ ] 9. Phase 2: Kiroチャット対話ワークフローのドキュメント作成
  - Kiroチャットでの画像添付方法のドキュメント
  - ユーザープロンプト例の作成
    - 基本形：「これはIDが12の猫の2024年11月14日～23日の記録です。JSON化してtmp/json/care_log.json に保存して」
    - 短縮形：「ID12、11/14-11/23、JSON化してtmp/json/に保存」
  - Kiroの内部プロンプトテンプレート使用方法
  - ユーザーによるJSON確認・修正手順
  - Phase 3 Hook自動トリガーの説明
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.7, 1.8, 4.1, 4.2, 4.3_

- [ ] 10. 使用ガイドドキュメントの作成
  - `docs/ocr-import-guide.md` の更新
  - 3段階ワークフローの説明
  - Workflow 1: 画像から直接開始（Image → JSON → Database）
  - Workflow 2: PDFから開始（PDF → Image → JSON → Database）
  - プロンプトフォーマット例
  - エラーメッセージとトラブルシューティング
  - コマンド例
  - FAQ セクション
  - _Requirements: All_

- [ ] 11. サンプルデータとテスト画像の作成
  - サンプル手書き世話記録画像の作成
  - サンプルPDFの作成
  - サンプルJSON出力ファイルの作成
  - `scripts/tests/fixtures/` への追加
  - エッジケースのサンプル（不明瞭な文字、部分的な記入）
  - _Requirements: All_

- [ ] 12. Checkpoint - すべてのテストが通ることを確認
  - すべてのテストが通ることを確認し、問題があればユーザーに質問する

- [ ]* 13. 統合テストの作成
  - `scripts/tests/test_integration.py` の作成
  - エンドツーエンド画像処理ワークフローのテスト
  - エンドツーエンドPDF処理ワークフローのテスト
  - エラーリカバリーシナリオのテスト
  - サンプル手書き画像でのテスト
  - 様々なデータ品質レベルでのテスト
  - _Requirements: All_

- [ ] 14. 最終Checkpoint - すべてのテストが通ることを確認
  - すべてのテストが通ることを確認し、問題があればユーザーに質問する

---

## 実装ノート

### タスク実行順序
1. **基盤** (Tasks 1-5): 構造、ユーティリティ、バリデーションのセットアップ ✅ 完了
2. **Phase 1 & 3** (Tasks 6-7): Hookスクリプトの実装 ✅ 完了
3. **Phase 2 & 設定** (Tasks 8-9): Kiro Hook設定とチャットワークフローのドキュメント
4. **ドキュメント** (Task 10): ユーザーガイドの作成
5. **テストデータ** (Task 11): サンプルデータの作成
6. **テスト** (Tasks 12-14): 包括的なテストと検証

### タスク間の依存関係
- Task 8（Kiro Hook設定）は Tasks 6, 7 の完了が必要
- Task 9（Phase 2ドキュメント）は Task 5（プロンプトテンプレート）の完了が必要
- Task 10（使用ガイド）は Tasks 8, 9 の完了が必要
- Task 13（統合テスト）は Tasks 1-11 の完了が必要

### テスト戦略
- ユニットテストは `*` でマークされ、オプションだが推奨
- プロパティベーステストは普遍的な正しさのプロパティを検証
- 統合テストはエンドツーエンドワークフローを検証
- すべてのテストは最終デプロイ前に実行すべき

### 環境セットアップ
実装開始前に以下を確認：
- Python 3.10+ がインストール済み
- 仮想環境がアクティブ
- NecoKeeper API がローカルで実行中
- データベースがテストデータで初期化済み
- 管理者認証情報が利用可能
- 環境変数が設定済み（`NECOKEEPER_API_URL`, `NECOKEEPER_ADMIN_USERNAME`, `NECOKEEPER_ADMIN_PASSWORD`）

### Kiro Hook設定
Hookは以下のパターンでKiroから呼び出されます：
```bash
# PDF変換Hook
python scripts/hooks/pdf_to_image.py <pdf_path>

# データ登録Hook
python scripts/hooks/register_care_logs.py <json_file_path>
```

### ディレクトリ構造
```
tmp/
├── pdfs/                    # Phase 1 入力（Hook監視）
├── images/                  # Phase 1 出力 / Phase 2 入力
└── json/                    # Phase 2 出力 / Phase 3 入力（Hook監視）
    └── processed/           # Phase 3 出力（処理済み）

scripts/
├── hooks/
│   ├── pdf_to_image.py      ✅ 完成
│   └── register_care_logs.py ✅ 完成
└── utils/
    ├── logging_config.py     ✅ 完成
    ├── json_schema.py        ✅ 完成
    ├── data_mapper.py        ✅ 完成
    ├── cat_identifier.py     ✅ 完成
    └── prompt_template.py    ✅ 完成
```

### 成功基準
- すべてのコア機能タスク（1-11）が完了
- 少なくとも70%のテストカバレッジ
- すべてのプロパティベーステストが通過
- ドキュメントが完成しレビュー済み
- サンプル手書き記録のインポートに成功

### 既存コードの活用
以下のスクリプトは既に完成しており、そのまま使用可能：
- ✅ `scripts/hooks/pdf_to_image.py` - PDF変換機能完備
- ✅ `scripts/hooks/register_care_logs.py` - API認証とバッチ登録完備
- ✅ `scripts/utils/logging_config.py` - ロギング設定完備
- ✅ `scripts/utils/json_schema.py` - JSONバリデーション完備
- ✅ `scripts/utils/data_mapper.py` - データマッピング完備
- ✅ `scripts/utils/cat_identifier.py` - 猫識別完備
- ✅ `scripts/utils/prompt_template.py` - プロンプトテンプレート完備

残りのタスクは主に：
1. Kiro Hook設定ファイルの作成
2. Phase 2（Kiroチャット対話）のドキュメント作成
3. 使用ガイドの更新
4. テストの作成
