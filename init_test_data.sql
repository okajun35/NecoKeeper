-- テストデータ作成SQL

-- テスト猫を作成（既に存在する場合はスキップ）
INSERT OR IGNORE INTO animal (id, name, pattern, status, gender, age_years, age_months, created_at, updated_at)
VALUES (1, 'テスト猫', 'キジトラ', '保護中', 'オス', 2, 0, datetime('now'), datetime('now'));

-- テストボランティアを作成（既に存在する場合はスキップ）
INSERT OR IGNORE INTO volunteer (id, name, email, phone, status, created_at, updated_at)
VALUES (1, 'テストボランティア', 'test@example.com', '090-1234-5678', 'active', datetime('now'), datetime('now'));

-- 確認
SELECT 'テスト猫 ID=' || id || ', 名前=' || name FROM animal WHERE id = 1;
SELECT 'ボランティア ID=' || id || ', 名前=' || name FROM volunteer WHERE id = 1;
