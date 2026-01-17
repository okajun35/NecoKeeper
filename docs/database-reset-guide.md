# データベース初期化ガイド

## 概要
NecoKeeperのデータベースをリセットして初期データを投入する手順です。
Alembicを使用してマイグレーションを実行し、シードスクリプトでテストデータを作成します。

## 前提条件
- Python仮想環境が有効化されていること（`.venv`）
- `requirements.txt`の依存パッケージがインストール済みであること

## 手順

### 1. データベースファイルの削除（オプション）

完全にリセットする場合は、既存のデータベースファイルを削除します。

```bash
cd /home/hddwm390/NecoKeeper
rm -f data/necokeeper.db
```

**注意:** この操作は元に戻せません。必要に応じてバックアップを取ってください。

### 2. Alembicマイグレーションの実行

データベーススキーマを最新バージョンに更新します。

```bash
# 仮想環境を有効化
source .venv/bin/activate

# Alembicマイグレーション実行
alembic upgrade head
```

**確認:** マイグレーションが成功すると、以下のようなメッセージが表示されます:
```
INFO  [alembic.runtime.migration] Running upgrade  -> xxxxx, 説明
```

### 3. シードデータの投入

テストデータを作成します。

```bash
# マスターデータとサンプルデータを投入
python scripts/seed_master_data.py
```

**投入されるデータ:**
- ユーザー（admin, staff, vet）
- 動物データ（10匹の猫）
- ボランティア情報
- 世話記録
- 診療記録
- 診療行為マスター

### 4. デフォルト認証情報

初期化後、以下のアカウントでログインできます:

| 役割 | メールアドレス | パスワード |
|------|---------------|-----------|
| 管理者 | admin@example.com | admin123 |
| スタッフ | staff@example.com | admin123 |
| 獣医師 | vet@example.com | admin123 |

### 5. 動作確認

アプリケーションを起動して動作確認します。

```bash
# アプリケーション起動
python -m app.main

# または uvicorn で起動
uvicorn app.main:app --reload
```

ブラウザで以下のURLにアクセス:
- 管理画面ログイン: http://localhost:8000/admin/login
- ダッシュボード: http://localhost:8000/admin

## トラブルシューティング

### Alembicマイグレーションエラー

**症状:** `Target database is not up to date` エラー

**対処法:**
```bash
# 現在のマイグレーション状態を確認
alembic current

# 強制的にリセット（データベースを削除してから）
rm -f data/necokeeper.db
alembic upgrade head
```

### シードスクリプトエラー

**症状:** `no such table: users` エラー

**対処法:**
Alembicマイグレーションが正常に完了していることを確認してください。

```bash
# マイグレーション状態確認
alembic current

# テーブルが作成されているか確認
sqlite3 data/necokeeper.db "SELECT name FROM sqlite_master WHERE type='table';"
```

### アカウントロック

誤ったパスワードで複数回ログインを試みると、アカウントがロックされます。

**対処法:**
```bash
# ロック解除SQL
sqlite3 data/necokeeper.db "UPDATE users SET failed_login_count=0, locked_until=NULL WHERE email='admin@example.com';"
```

## 注意事項

### 本番環境
本番環境では以下の点に注意してください:

1. **データベースバックアップ**
   ```bash
   cp data/necokeeper.db backups/necokeeper_$(date +%Y%m%d_%H%M%S).db
   ```

2. **パスワード変更**
   初期パスワード（`admin123`）は開発用です。本番環境では必ず変更してください。

3. **環境変数**
   `.env`ファイルで以下を設定:
   - `ENVIRONMENT=production`
   - `DEBUG=false`
   - `DEMO_FEATURES=false`

### 開発環境

開発中に頻繁にリセットする場合は、以下のエイリアスを設定すると便利です:

```bash
# ~/.bashrc または ~/.zshrc に追加
alias neco-reset='cd /home/hddwm390/NecoKeeper && source .venv/bin/activate && rm -f data/necokeeper.db && alembic upgrade head && python scripts/seed_master_data.py'
```

使用方法:
```bash
neco-reset
```

## 関連ドキュメント

- [Alembic マイグレーション](../alembic/README)
- [テストデータ仕様](./test-data-spec.md)
- [環境変数設定](../.env.example)
- [デプロイガイド](../DEPLOY.md)

## 更新履歴

- 2026-01-17: 初版作成（Issue #95対応）
