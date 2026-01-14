# Issue #79 作業仕様まとめ

## 仕様の要点
- 年齢区分（子猫・成猫・老猫など）は削除する
- 月齢は必須ではなく、null=不明として扱う
- 推定月齢フラグを追加する（bool、デフォルト false）
- 推定月齢フラグがtrueでも月齢がnullなら年齢不明として扱う

## チェックリスト

### したこと
- [x] `Animal` モデルを `age` から `age_months`/`age_is_estimated` に変更
- [x] スキーマ（`app/schemas/animal.py`）を更新
- [x] Automation API のレスポンス例を更新
- [x] MCP `register_cat` を新フィールド対応に更新
- [x] MCP API クライアントの例を更新
- [x] Alembic マイグレーション追加（`age`削除 + `age_months`/`age_is_estimated`追加）
- [x] テストと初期化スクリプトの `age` 参照を `age_months` に更新

### これからすべきこと
- [ ] DBにマイグレーション適用: `alembic upgrade head`
- [ ] 影響範囲のテスト実行（例: `python -m pytest tests/api/test_animals.py -q`）
- [ ] フルテスト実行（`make test`）
- [x] UI/フォームで年齢区分が表示されていないか確認（必要なら修正）

## 変更ファイル
- `app/models/animal.py`
- `app/schemas/animal.py`
- `app/api/automation/animals.py`
- `app/mcp/tools/register_cat.py`
- `app/mcp/api_client.py`
- `alembic/versions/f4e98ee7ca5a_replace_animal_age_with_months.py`
- `tests/**`
- `init_db.py`
- `reproduce_issue.py`
