# マイグレーション安全性チェック

## 既存データの変換について

### ✅ 既存データは自動的に修正されます

案1のマイグレーションでは、**すべての既存データのタイムスタンプを+9時間**して、UTC→JSTに変換します。

## 変換の具体例

### Before（現在のUTCデータ）
```sql
SELECT id, log_date, created_at, last_updated_at
FROM care_logs
WHERE id = 703;

-- 結果:
-- id: 703
-- log_date: 2025-12-02
-- created_at: 2025-12-01 17:25:28  (UTC)
-- last_updated_at: 2025-12-01 17:25:28  (UTC)
```

### After（マイグレーション後のJSTデータ）
```sql
SELECT id, log_date, created_at, last_updated_at
FROM care_logs
WHERE id = 703;

-- 結果:
-- id: 703
-- log_date: 2025-12-02
-- created_at: 2025-12-02 02:25:28  (JST) ← +9時間
-- last_updated_at: 2025-12-02 02:25:28  (JST) ← +9時間
```

→ **log_dateとcreated_atの日付が一致！**

## マイグレーションSQL

```python
def upgrade():
    """既存データをUTC→JSTに変換"""

    # 1. care_logs テーブル
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 2. animals テーブル
    op.execute("""
        UPDATE animals
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours'),
            protected_at = CASE
                WHEN protected_at IS NOT NULL
                THEN date(protected_at, '+9 hours')
                ELSE NULL
            END
    """)

    # 3. medical_records テーブル
    op.execute("""
        UPDATE medical_records
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours'),
            treatment_date = CASE
                WHEN treatment_date IS NOT NULL
                THEN date(treatment_date, '+9 hours')
                ELSE NULL
            END
    """)

    # 4. users テーブル
    op.execute("""
        UPDATE users
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 5. volunteers テーブル
    op.execute("""
        UPDATE volunteers
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 6. status_history テーブル
    op.execute("""
        UPDATE status_history
        SET changed_at = datetime(changed_at, '+9 hours')
    """)

    # 7. adoption_records テーブル
    op.execute("""
        UPDATE adoption_records
        SET adoption_date = CASE
                WHEN adoption_date IS NOT NULL
                THEN date(adoption_date, '+9 hours')
                ELSE NULL
            END,
            created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

def downgrade():
    """ロールバック: JST→UTCに戻す"""

    # 逆の操作（-9時間）
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)

    # ... 他のテーブルも同様
```

## 安全性の確保

### 1. バックアップ（必須）
```bash
# マイグレーション実行前に必ずバックアップ
cp data/necokeeper.db data/necokeeper_backup_$(date +%Y%m%d_%H%M%S).db
```

### 2. ドライラン（推奨）
```bash
# SQLを確認（実行はしない）
alembic upgrade head --sql > migration.sql
cat migration.sql  # 内容を確認
```

### 3. ロールバック可能
```bash
# 問題があれば元に戻せる
alembic downgrade -1
```

### 4. テスト環境で事前確認
```bash
# テストDBで先に実行
cp data/necokeeper.db data/necokeeper_test.db
NECOKEEPER_DB_PATH=data/necokeeper_test.db alembic upgrade head

# 問題なければ本番実行
alembic upgrade head
```

## 影響範囲の確認

### 変換対象のレコード数を確認
```sql
-- care_logs
SELECT COUNT(*) FROM care_logs;

-- animals
SELECT COUNT(*) FROM animals;

-- medical_records
SELECT COUNT(*) FROM medical_records;

-- users
SELECT COUNT(*) FROM users;

-- volunteers
SELECT COUNT(*) FROM volunteers;
```

### 変換前後の比較（サンプル）
```sql
-- 変換前のデータをメモ
SELECT id, log_date, created_at
FROM care_logs
ORDER BY id DESC
LIMIT 5;

-- マイグレーション実行

-- 変換後のデータを確認
SELECT id, log_date, created_at
FROM care_logs
ORDER BY id DESC
LIMIT 5;

-- 差分を確認（+9時間になっているはず）
```

## 実行時間の見積もり

| レコード数 | 実行時間（目安） |
|-----------|----------------|
| 100件 | < 1秒 |
| 1,000件 | < 5秒 |
| 10,000件 | < 30秒 |
| 100,000件 | < 5分 |

SQLiteの`UPDATE`は高速なので、通常のデータ量であれば数秒で完了します。

## チェックリスト

マイグレーション実行前に確認：

- [ ] データベースのバックアップを取得
- [ ] テスト環境で動作確認済み
- [ ] 影響範囲（レコード数）を確認
- [ ] ロールバック手順を理解
- [ ] ダウンタイムの計画（必要に応じて）

## まとめ

**案1では既存データもすべて自動的にJSTに変換されます。**

- ✅ マイグレーション実行で全データ+9時間
- ✅ log_dateとcreated_atの日付が一致
- ✅ ロールバック可能（-9時間で元に戻る）
- ✅ バックアップを取れば安全

**データがずれたままになることはありません！**
