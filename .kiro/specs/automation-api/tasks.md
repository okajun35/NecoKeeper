# Implementation Tasks: Automation API

## Overview

Automation API機能の実装タスクリストです。優先度順に実装を進めます。

**実装方針**:
- テストファーストで開発（TDD）
- 既存コードへの影響を最小化
- セキュリティを最優先

---

## Tasks

### Phase 1: 基盤実装（必須）

- [ ] 1. API Key認証モジュールの実装
  - `app/auth/api_key.py` の作成
  - `APIKeyHeader` スキームの定義
  - `get_automation_api_key()` 依存関数の実装
  - `verify_automation_api_key_optional()` 依存関数の実装
  - エラーハンドリング（401, 403, 503）
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7_
  - _Context7: /fastapi/fastapi - APIKeyHeader, Security_

- [ ] 1.1 API Key認証のユニットテストを作成
  - `tests/auth/test_api_key.py` の作成
  - 有効なAPI Keyのテスト
  - 無効なAPI Keyのテスト（403）
  - API Key未設定のテスト（401）
  - Automation API無効のテスト（503）
  - オプショナル検証のテスト
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5_

- [ ] 2. 設定管理の拡張
  - `app/config.py` の更新
  - `enable_automation_api` 設定の追加
  - `automation_api_key` 設定の追加
  - `is_automation_api_secure` プロパティの実装
  - 本番環境でのバリデーション（32文字以上）
  - _Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 2.6_

- [ ] 2.1 設定管理のユニットテストを作成
  - `tests/test_config.py` の更新
  - 本番環境でのAPI Key検証テスト
  - API Key長さ検証テスト
  - セキュリティプロパティのテスト
  - _Requirements: 2.3, 2.4, 2.5_

- [ ] 3. Automation APIルーターの作成
  - `app/api/automation/__init__.py` の作成
  - ルーター設定（prefix, tags, dependencies）
  - 共通エラーレスポンスの定義
  - _Requirements: 3.1, 3.2, 3.3, 3.4, 3.5_
  - _Context7: /fastapi/fastapi - APIRouter with dependencies_

- [ ] 4. 世話記録登録Automation APIの実装
  - `app/api/automation/care_logs.py` の作成
  - `POST /api/automation/care-logs` エンドポイント
  - リクエストスキーマの定義
  - レスポンススキーマの定義
  - エラーハンドリング
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 4.1 世話記録登録APIのユニットテストを作成
  - `tests/api/automation/test_care_logs.py` の作成
  - 正常系: 世話記録登録成功
  - 異常系: API Key未設定（401）
  - 異常系: API Key無効（403）
  - 異常系: データ不正（400）
  - 異常系: 猫が存在しない（404）
  - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6_

- [ ] 5. メインアプリケーションへの統合
  - `app/main.py` の更新
  - Automation APIルーターの登録
  - 既存ルーターとの共存確認
  - OpenAPIドキュメントの確認
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 5.1 統合テストを作成
  - `tests/test_integration_automation_api.py` の作成
  - ユーザーAPIとAutomation APIの分離確認
  - 認証方式の独立性確認
  - OpenAPIドキュメント生成確認
  - _Requirements: 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 6. Kiro Hook統合
  - `scripts/hooks/register_care_logs.py` の更新
  - `/api/automation/care-logs` エンドポイントに変更
  - `X-Automation-Key` ヘッダーの追加
  - `AUTOMATION_API_KEY` 環境変数の読み込み
  - エラーハンドリングの改善
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 6.1 Kiro Hook統合テストを作成
  - `tests/hooks/test_register_care_logs_automation.py` の作成
  - Automation API経由での登録テスト
  - API Key認証のテスト
  - エラーハンドリングのテスト
  - _Requirements: 8.1, 8.2, 8.3, 8.4, 8.5_

- [ ] 7. 環境変数テンプレート更新
  - `.env.example` の更新
  - `ENABLE_AUTOMATION_API` の追加
  - `AUTOMATION_API_KEY` の追加
  - API Key生成コマンドの記載
  - セキュリティ警告の追加
  - _Requirements: 9.1, 9.2, 9.3, 9.4_

- [ ] 8. Checkpoint - すべてのテストが通ることを確認
  - すべてのユニットテストがPass
  - すべての統合テストがPass
  - カバレッジ70%以上
  - 問題があればユーザーに質問

### Phase 2: 拡張実装（推奨）

- [ ] 9. 猫登録Automation APIの実装
  - `app/api/automation/animals.py` の作成
  - `POST /api/automation/animals` エンドポイント
  - `GET /api/automation/animals/{animal_id}` エンドポイント
  - エラーハンドリング
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6_

- [ ] 9.1 猫登録APIのユニットテストを作成
  - `tests/api/automation/test_animals.py` の作成
  - 正常系: 猫登録成功
  - 正常系: 猫情報取得成功
  - 異常系: API Key未設定（401）
  - 異常系: 猫が存在しない（404）
  - _Requirements: 4.1, 4.2, 4.3, 4.4, 4.5_

- [ ] 10. ドキュメント作成
  - `docs/automation-api-guide.md` の作成
  - デュアル認証アーキテクチャの説明
  - API Key生成方法
  - curlコマンド例
  - Pythonコード例
  - セキュリティ考慮事項
  - トラブルシューティング
  - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5, 10.6_

- [ ] 11. OCR Import Guide更新
  - `docs/ocr-import-guide.md` の更新
  - Automation API使用方法の追加
  - 環境変数設定手順の更新
  - トラブルシューティングの更新
  - _Requirements: 8.4, 8.5_

### Phase 3: 最適化（オプション）

- [ ] 12. Rate Limitingの実装
  - `slowapi` ライブラリの追加
  - Automation APIへのRate Limiting適用
  - 1分間に100リクエストまで
  - _Requirements: 7.7_

- [ ] 13. 監査ログの強化
  - Automation API操作の詳細ログ
  - API Key使用統計
  - 異常アクセスの検知
  - _Requirements: 7.4_

- [ ] 14. セキュリティテストの追加
  - `tests/security/test_automation_api_security.py` の作成
  - API Key漏洩シミュレーション
  - Brute Forceテスト
  - 権限昇格テスト
  - _Requirements: 7.1, 7.2, 7.3, 7.4, 7.5, 7.6, 7.7_

- [ ] 15. 最終Checkpoint - すべてのテストが通ることを確認
  - すべてのテストがPass
  - カバレッジ80%以上
  - セキュリティテストPass
  - ドキュメント完成

---

## Implementation Notes

### タスク実行順序

**Phase 1（POC必須）**:
1. API Key認証モジュール（Task 1, 1.1）
2. 設定管理の拡張（Task 2, 2.1）
3. Automation APIルーター（Task 3）
4. 世話記録登録API（Task 4, 4.1）
5. メインアプリ統合（Task 5, 5.1）
6. Kiro Hook統合（Task 6, 6.1）
7. 環境変数テンプレート（Task 7）
8. Checkpoint（Task 8）

**Phase 2（本番推奨）**:
9. 猫登録API（Task 9, 9.1）
10. ドキュメント作成（Task 10, 11）

**Phase 3（運用最適化）**:
11. Rate Limiting（Task 12）
12. 監査ログ強化（Task 13）
13. セキュリティテスト（Task 14）
14. 最終Checkpoint（Task 15）

### タスク間の依存関係

```
Task 1 (API Key認証)
  ├─> Task 1.1 (テスト)
  └─> Task 3 (ルーター)
        └─> Task 4 (世話記録API)
              ├─> Task 4.1 (テスト)
              └─> Task 5 (統合)
                    ├─> Task 5.1 (テスト)
                    └─> Task 6 (Hook統合)
                          └─> Task 6.1 (テスト)

Task 2 (設定管理)
  └─> Task 2.1 (テスト)

Task 7 (環境変数) - 独立

Task 8 (Checkpoint) - Phase 1完了後

Task 9 (猫登録API) - Task 5完了後
  └─> Task 9.1 (テスト)

Task 10, 11 (ドキュメント) - Task 6完了後

Task 12, 13, 14 (最適化) - Phase 2完了後

Task 15 (最終Checkpoint) - 全タスク完了後
```

### テスト戦略

**ユニットテスト**:
- 各モジュールの単体テスト
- モックを使用して依存関係を分離
- カバレッジ80%以上を目標

**統合テスト**:
- エンドツーエンドのフローテスト
- 実際のデータベースを使用
- 認証方式の分離を確認

**セキュリティテスト**:
- API Key検証のテスト
- 権限分離のテスト
- エラーハンドリングのテスト

### 環境セットアップ

**開発環境**:
```bash
# .env
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=dev-test-key-for-local-development-only
```

**テスト環境**:
```bash
# pytest実行時に自動設定
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=test-key-32-characters-long-xxx
```

**本番環境**:
```bash
# Render Dashboard等で設定
ENABLE_AUTOMATION_API=true
AUTOMATION_API_KEY=<secrets.token_urlsafe(32)で生成>
```

### コミット戦略

**コミット単位**:
- 1タスク = 1コミット
- テストとコードは同じコミット
- コミットメッセージは明確に

**コミットメッセージ例**:
```bash
feat(auth): API Key認証モジュールを追加

- APIKeyHeaderスキームを定義
- get_automation_api_key()依存関数を実装
- エラーハンドリング（401, 403, 503）を追加
- ユニットテストを追加（カバレッジ95%）

Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
Context7: /fastapi/fastapi - APIKeyHeader, Security
```

### 成功基準

**Phase 1完了**:
- [ ] すべてのPhase 1タスクが完了
- [ ] すべてのテストがPass
- [ ] カバレッジ70%以上
- [ ] Kiro HookからAutomation APIで世話記録登録成功
- [ ] ユーザーAPIとAutomation APIが独立動作

**Phase 2完了**:
- [ ] すべてのPhase 2タスクが完了
- [ ] ドキュメント完成
- [ ] カバレッジ75%以上

**Phase 3完了**:
- [ ] すべてのPhase 3タスクが完了
- [ ] セキュリティテストPass
- [ ] カバレッジ80%以上
- [ ] 本番環境デプロイ準備完了

---

## Risk Management

### リスクと対策

**リスク1: 既存APIへの影響**
- 対策: 完全分離アーキテクチャ
- 検証: 統合テストで既存APIの動作確認

**リスク2: API Key漏洩**
- 対策: 環境変数で管理、コードに含めない
- 検証: セキュリティテストで検証

**リスク3: 本番環境での設定ミス**
- 対策: バリデーション機能を実装
- 検証: 起動時にセキュリティチェック

**リスク4: パフォーマンス低下**
- 対策: 既存サービスを再利用、新規ロジック最小化
- 検証: パフォーマンステスト

---

**最終更新**: 2025-11-24
**Context7参照**: `/fastapi/fastapi` - APIRouter, Security, APIKeyHeader
