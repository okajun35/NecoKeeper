# Implementation Plan

## Overview

世話記録一覧画面を日次ビュー形式に改修します。バックエンドで新規APIエンドポイントを作成し、フロントエンドで日次ビュー形式のテーブルを実装します。

---

## Tasks

- [x] 1. バックエンド: 日次ビューAPIエンドポイントの実装

  - 新規エンドポイント `/api/v1/care-logs/daily-view` を作成
  - クエリパラメータ: animal_id, start_date, end_date, page, page_size
  - 認証必須（JWT）
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 6.1, 6.2_

- [x] 1.1 Pydanticスキーマの作成


  - `TimeSlotRecord`: 時点ごとの記録情報（exists, log_id, appetite, energy）
  - `DailyViewRecord`: 日次ビューの1レコード（date, animal_id, animal_name, morning, noon, evening）
  - `DailyViewResponse`: レスポンス全体（items, total, page, page_size, total_pages）
  - _Requirements: 1.1, 1.2, 1.3_



- [ ] 1.2 サービス層関数の実装
  - `care_log_service.py` に `get_daily_view()` 関数を追加
  - 日付範囲のデフォルト値設定（過去7日間）
  - 日付×猫の組み合わせを生成
  - 各組み合わせに対して朝・昼・夕の記録を取得
  - 日次ビュー形式に変換


  - ページネーション適用
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 4.1, 4.2, 6.3_

- [ ] 1.3 APIエンドポイントの実装
  - `app/api/v1/care_logs.py` に新規エンドポイント追加
  - GET `/api/v1/care-logs/daily-view`

  - クエリパラメータのバリデーション
  - サービス層関数を呼び出し
  - レスポンス返却
  - _Requirements: 1.1, 6.1, 6.2_

- [ ] 1.4 エラーハンドリングの実装
  - 認証エラー（401）
  - バリデーションエラー（422）: 日付範囲不正、ページ番号不正
  - データベースエラー（500）
  - 適切なエラーメッセージを返却


  - _Requirements: 6.4_

- [ ] 2. フロントエンド: 日次ビュー画面の実装
  - 既存の世話記録一覧画面を日次ビュー形式に置き換え
  - HTML、JavaScript、CSSを実装
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3_



- [ ] 2.1 HTML構造の作成
  - `app/templates/admin/care_logs_list.html` を更新
  - フィルタセクション（猫選択、日付範囲）
  - 日次ビューテーブル（日付、猫、朝、昼、夕）
  - ページネーションコントロール
  - ローディングインジケーター
  - _Requirements: 1.1, 3.1, 3.2, 4.1, 4.2, 6.5_

- [x] 2.2 JavaScriptの実装


  - `app/static/js/admin/care_logs_daily_view.js` を作成
  - データ取得関数 `loadDailyView()`
  - テーブル描画関数 `renderDailyView()`
  - 行生成関数 `createDailyRow()`
  - 記録リンク生成関数 `createRecordLink()`
  - フィルタ適用関数
  - ページネーション制御関数
  - エラーハンドリング
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2, 2.3, 3.3, 3.4, 4.3, 4.4, 6.1, 6.2, 6.3, 6.4, 6.5_

- [ ] 2.3 CSSスタイリングの実装
  - `app/static/css/admin/care_logs_daily_view.css` を作成
  - テーブルスタイル
  - 記録リンクスタイル（○=緑、×=赤）
  - フィルタセクションスタイル
  - ページネーションスタイル
  - ローディング状態スタイル
  - _Requirements: 1.1, 1.2, 1.3, 2.1, 2.2_

- [ ] 2.4 レスポンシブデザインの実装
  - デスクトップ（>1024px）: テーブル表示
  - タブレット（768px-1024px）: テーブル表示（調整）
  - モバイル（<768px）: カード形式表示
  - タッチ操作対応
  - _Requirements: 5.1, 5.2, 5.3, 5.4_

- [ ] 3. フィルタ機能の実装
  - 猫選択ドロップダウン
  - 日付範囲入力
  - 検索ボタン
  - クリアボタン
  - _Requirements: 3.1, 3.2, 3.3, 3.4_

- [ ] 3.1 猫リストの取得と表示
  - `/api/v1/animals` から猫リストを取得
  - ドロップダウンに表示
  - 「すべての猫」オプションを追加
  - _Requirements: 3.1_

- [ ] 3.2 日付範囲フィルタの実装
  - 開始日・終了日の入力フィールド
  - デフォルト値: 過去7日間
  - 日付バリデーション（開始日 <= 終了日）
  - _Requirements: 3.2_

- [ ] 3.3 フィルタ適用処理の実装
  - 検索ボタンクリック時にAPIリクエスト
  - フィルタ条件をクエリパラメータに変換
  - テーブルを更新
  - _Requirements: 3.3_

- [ ] 3.4 フィルタクリア処理の実装
  - クリアボタンクリック時にフィルタをリセット
  - デフォルト値に戻す
  - テーブルを更新
  - _Requirements: 3.4_

- [ ] 4. ページネーション機能の実装
  - ページ情報の表示
  - 前へ・次へボタン
  - ページ遷移時のスクロール制御
  - _Requirements: 4.1, 4.2, 4.3, 4.4_

- [ ] 4.1 ページネーションコントロールの実装
  - 現在ページ、総ページ数、総件数の表示
  - 前へボタン（1ページ目で無効化）
  - 次へボタン（最終ページで無効化）
  - _Requirements: 4.1, 4.2_

- [ ] 4.2 ページ遷移処理の実装
  - ボタンクリック時にページ番号を更新
  - APIリクエストを送信
  - テーブルを更新
  - ページトップにスクロール
  - _Requirements: 4.3, 4.4_

- [ ] 5. 記録リンク機能の実装
  - ○リンク: 詳細/編集画面へ遷移
  - ×リンク: 新規登録画面へ遷移（パラメータ付き）
  - _Requirements: 2.1, 2.2, 2.3_

- [ ] 5.1 ○リンクの実装
  - 記録が存在する場合に表示
  - クリック時に `/admin/care-logs/{log_id}` へ遷移
  - 緑色で表示
  - _Requirements: 2.1_

- [ ] 5.2 ×リンクの実装
  - 記録が存在しない場合に表示
  - クリック時に `/admin/care-logs/new?animal_id={id}&date={date}&time_slot={slot}` へ遷移
  - 赤色で表示
  - _Requirements: 2.2, 2.3_

- [ ] 6. CSVエクスポート機能の実装
  - CSVエクスポートボタン
  - フィルタ条件を含めた全データをエクスポート
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 6.1 CSVエクスポートボタンの実装
  - ボタンクリック時にAPIリクエスト
  - `/api/v1/care-logs/daily-view/export` エンドポイントを呼び出し
  - フィルタ条件を含める
  - _Requirements: 7.1_

- [ ] 6.2 CSVエクスポートAPIの実装
  - GET `/api/v1/care-logs/daily-view/export`
  - フィルタ条件を受け取る
  - 全データを取得（ページネーションなし）
  - CSV形式に変換
  - UTF-8 with BOM
  - ファイル名: `care_logs_YYYYMMDD.csv`
  - _Requirements: 7.1, 7.2, 7.3, 7.4_

- [ ] 7. テストの実装
  - バックエンドのユニットテスト
  - APIテスト
  - フロントエンドの手動テスト
  - _Requirements: All_

- [ ] 7.1 バックエンドユニットテストの作成
  - `tests/services/test_care_log_service.py` に追加
  - `test_get_daily_view_default_date_range()`: デフォルト日付範囲
  - `test_get_daily_view_with_animal_filter()`: 猫フィルタ
  - `test_get_daily_view_with_date_range()`: 日付範囲フィルタ
  - `test_get_daily_view_pagination()`: ページネーション
  - `test_get_daily_view_empty_result()`: 結果なし
  - `test_get_daily_view_data_transformation()`: データ変換ロジック
  - _Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 3.1, 3.2, 4.1, 4.2_

- [ ] 7.2 APIテストの作成
  - `tests/api/test_care_logs.py` に追加
  - `test_daily_view_endpoint_success()`: 正常系
  - `test_daily_view_endpoint_with_filters()`: フィルタ適用
  - `test_daily_view_endpoint_pagination()`: ページネーション
  - `test_daily_view_endpoint_unauthorized()`: 認証エラー
  - `test_daily_view_endpoint_invalid_date_range()`: バリデーションエラー
  - `test_daily_view_export_csv()`: CSVエクスポート
  - _Requirements: 1.1, 3.3, 4.3, 6.1, 6.4, 7.1_

- [ ] 7.3 フロントエンド手動テストの実施
  - ブラウザ互換性テスト（Chrome, Firefox, Safari）
  - レスポンシブデザインテスト（デスクトップ、タブレット、モバイル）
  - フィルタ機能テスト
  - ページネーション機能テスト
  - リンククリック動作テスト
  - CSVエクスポート機能テスト
  - エラーハンドリングテスト
  - _Requirements: 2.1, 2.2, 2.3, 3.3, 3.4, 4.3, 5.1, 5.2, 5.3, 5.4, 6.4, 7.1_

- [ ] 8. 既存コードのクリーンアップ
  - 旧バージョンのコードを削除または非推奨化
  - コメントとドキュメントの更新
  - _Requirements: All_

- [ ] 8.1 旧世話記録一覧画面の削除
  - 旧JavaScript（`care_logs_list.js`）を削除または置き換え
  - 旧CSS（該当部分）を削除
  - 未使用のコードを削除
  - _Requirements: All_

- [ ] 8.2 ドキュメントの更新
  - README.mdに新機能の説明を追加
  - APIドキュメントを更新
  - コード内コメントを追加
  - _Requirements: All_

---

## Implementation Notes

### 実装順序

1. **Phase 1: バックエンド実装**（タスク1）
   - スキーマ定義 → サービス層 → APIエンドポイント → エラーハンドリング

2. **Phase 2: フロントエンド基本実装**（タスク2）
   - HTML構造 → JavaScript基本機能 → CSS基本スタイル

3. **Phase 3: 機能追加**（タスク3-6）
   - フィルタ機能 → ページネーション → 記録リンク → CSVエクスポート

4. **Phase 4: レスポンシブ対応**（タスク2.4）
   - モバイル・タブレット対応

5. **Phase 5: テストと品質保証**（タスク7）
   - ユニットテスト → APIテスト → 手動テスト

6. **Phase 6: クリーンアップ**（タスク8）
   - 旧コード削除 → ドキュメント更新

### 重要な注意点

1. **データ変換ロジック**
   - バックエンドで日次ビュー形式に変換
   - フロントエンドはシンプルに保つ

2. **パフォーマンス**
   - インデックスを活用したクエリ最適化
   - ページネーションで大量データに対応

3. **ユーザビリティ**
   - ローディング状態を明確に表示
   - エラーメッセージは分かりやすく

4. **後方互換性**
   - 既存のAPIエンドポイントは維持
   - 段階的な移行を可能にする

### テスト戦略

- **ユニットテスト**: サービス層のロジックを検証
- **APIテスト**: エンドポイントの動作を検証
- **手動テスト**: UI/UXを検証

### デプロイ計画

1. バックエンドAPIをデプロイ
2. フロントエンドを段階的にロールアウト
3. ユーザーフィードバックを収集
4. 必要に応じて調整
