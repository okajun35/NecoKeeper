# NecoKeeper - デプロイガイド

このドキュメントでは、NecoKeeperをRenderにデプロイする手順を説明します。

## 📋 目次

- [Free Plan PoC デプロイ（1週間）](#free-plan-poc-デプロイ1週間)
- [Starter Planへの移行（ハッカソン審査時）](#starter-planへの移行ハッカソン審査時)
- [ローカル開発環境](#ローカル開発環境)
- [トラブルシューティング](#トラブルシューティング)

---

## 🆓 Free Plan PoC デプロイ（1週間）

**目的**: ハッカソン向けの1週間のデモ環境

**制約**:
- ⚠️ データは再デプロイで消える（PoC割り切り）
- ⚠️ 15分間アクセスなしでスピンダウン（初回アクセス時に遅延）
- ⚠️ 月750時間の制限

### 前提条件

- GitHubアカウント
- Renderアカウント（無料）
- GitHubリポジトリにNecoKeeperをプッシュ済み

### デプロイ手順

#### 1. Renderにログイン

https://dashboard.render.com/ にアクセスしてログイン

#### 2. 新しいWeb Serviceを作成

1. **New** → **Web Service** をクリック
2. GitHubリポジトリを接続
3. NecoKeeperリポジトリを選択

#### 3. サービス設定

| 設定項目 | 値 | 説明 |
|---------|-----|------|
| **Name** | necokeeper（または任意の名前） | サービス名（URL: necokeeper.onrender.com） |
| **Language** | Docker | Dockerfileを使用 |
| **Branch** | main | デプロイするブランチ（推奨: main） |
| **Root Directory** | （空欄） | ⚠️ 空欄のまま（入力しない） |
| **Dockerfile Path** | `./Dockerfile` | ⚠️ 正確に入力（スペース不要） |
| **Instance Type** | Free | 無料プラン |

**⚠️ よくあるエラー**:
- ❌ Dockerfile Path: `/ ./Dockerfile`（余計なスペース）
- ❌ Root Directory: `/`（不要）
- ✅ Dockerfile Path: `./Dockerfile`（正しい）
- ✅ Root Directory: （空欄）

**ブランチ戦略**:

**ハッカソン向け（推奨）**:
- `main`ブランチを直接デプロイ
- シンプルで素早いイテレーション
- プッシュするたびに自動デプロイ

**本番運用向け（将来）**:
```
main (開発) → PR → deploy (本番) → Render自動デプロイ
```
- `deploy`ブランチを作成
- `main`から`deploy`へのPRでレビュー
- `deploy`へのマージで本番デプロイ

#### 4. 環境変数を設定

**⚠️ セキュリティ重要事項**:
- 本番環境では**必ず`DEBUG=false`**に設定
- `SECRET_KEY`は**32文字以上のランダム文字列**を使用
- `CORS_ORIGINS`は**実際のドメインのみ**を指定
- **Cookie設定は本番環境で必須**（`COOKIE_SECURE=true`）
- **環境変数はRender Dashboard画面から設定**（Dockerに内蔵しない）

**環境変数の設定方法**:

1. **Advanced** → **Environment Variables** をクリック
2. **Add Environment Variable** で以下を1つずつ追加：

```bash
# 必須
SECRET_KEY=<32文字以上のランダム文字列>
ENVIRONMENT=production
DEBUG=false

# DB パス設定（Free Plan: リポジトリの DB を使用）
NECOKEEPER_DB_PATH=data/necokeeper.db

# Cookie設定（認証用）- 本番環境では必須
COOKIE_SECURE=true
COOKIE_SAMESITE=lax
COOKIE_MAX_AGE=7200

# 推奨
CORS_ORIGINS=["https://necokeeper.onrender.com"]
MEDIA_DIR=/tmp/media
BACKUP_DIR=/tmp/backups
LOG_FILE=/tmp/logs/necokeeper.log
LOG_LEVEL=INFO
```

**重要**: `CORS_ORIGINS` は JSON 配列形式で指定してください。
- 単一オリジン: `["https://necokeeper.onrender.com"]`
- 複数オリジン: `["https://necokeeper.onrender.com","https://www.example.com"]`

**DB パス設定の説明**:
- **Free Plan**: `NECOKEEPER_DB_PATH=data/necokeeper.db`（イメージに含まれる DB を使用）
- **Starter Plan**: `NECOKEEPER_DB_PATH=/mnt/data/necokeeper.db`（永続ディスクを使用）
- 未設定の場合: `DATABASE_URL` の値を使用（後方互換性）

**重要**:
- ⚠️ **本番環境では必ず`DEBUG=false`に設定してください**
- `DEBUG=true`の場合、エラー時に詳細なスタックトレースが表示され、セキュリティリスクになります
- `ENVIRONMENT=production`と`DEBUG=false`をセットで設定

**SECRET_KEYの生成方法**:
```bash
python -c "import secrets; print(secrets.token_urlsafe(32))"
```

**重要**:
- ❌ **環境変数をDockerfileに直接書かない**（Gitにコミットされる）
- ❌ **環境変数を.envファイルに書いてコミットしない**
- ✅ **Render Dashboard画面から設定する**（安全）
- ✅ **各環境（Free/Starter）で異なる値を設定可能**

**環境変数の優先順位**:
1. Render Dashboard設定（最優先）
2. Dockerfileの`ENV`指令
3. .envファイル（ローカル開発のみ）

#### 5. デプロイ実行

**Create Web Service** をクリック

デプロイには5-10分かかります。

#### 6. 初回セットアップ（Free Plan: 不要）

**Free Plan の場合**:
- ✅ **リポジトリの `data/necokeeper.db` が Docker イメージに含まれています**
- ✅ **デプロイ後すぐに使用可能**（初期化不要）
- ⚠️ **再デプロイすると、リポジトリの DB に戻ります**（変更は失われる）

**初期管理者アカウント**:
- Email: `admin@example.com`
- Password: `admin123`

**注意**:
- Free Plan では DB の変更（新規登録、データ追加）は再デプロイで消えます
- デモ・PoC 用途に最適
- 本番運用には Starter Plan への移行を推奨

**Starter Plan への移行後**:
- ✅ Persistent Disk でデータ永続化
- ✅ 再デプロイでもデータは保持される
- ⚠️ 初回のみ DB 初期化が必要（後述）

**自動初期化の設定（オプション）**:

Dockerfileに以下を追加すると、起動時に自動初期化されます：

```dockerfile
# エントリーポイントスクリプトを作成
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

ENTRYPOINT ["/docker-entrypoint.sh"]
```

`docker-entrypoint.sh`:
```bash
#!/bin/bash
set -e

# データベースマイグレーション
echo "Running database migrations..."
alembic upgrade head

# 初期管理者アカウント作成（存在しない場合のみ）
echo "Checking for admin user..."
python -c "
from app.database import SessionLocal
from app.models.user import User
from app.auth.password import hash_password

db = SessionLocal()
existing_admin = db.query(User).filter(User.email == 'admin@example.com').first()

if not existing_admin:
    admin = User(
        email='admin@example.com',
        password_hash=hash_password('admin123'),
        name='管理者',
        role='admin',
        is_active=True
    )
    db.add(admin)
    db.commit()
    print('✅ 管理者アカウント作成完了')
else:
    print('ℹ️ 管理者アカウントは既に存在します')
"

# アプリケーション起動
echo "Starting application..."
exec uvicorn app.main:app --host 0.0.0.0 --port \${PORT:-8000}
```

#### 7. アクセス確認

`https://necokeeper.onrender.com` にアクセス

**初回アクセス時の注意**:
- スピンダウンから復帰するため、30-60秒かかる場合があります
- ログイン: `admin@example.com` / `admin123`

---

## 💰 Starter Planへの移行（ハッカソン審査時）

**目的**: データ永続化と安定運用

**コスト**: $7/月

### 移行手順

#### 1. プランをアップグレード

1. Render Dashboard → NecoKeeperサービス
2. **Settings** → **Instance Type**
3. **Starter** を選択
4. **Save Changes**

#### 2. Persistent Diskを追加

1. **Disks** タブを開く
2. **Add Disk** をクリック
3. 設定:
   - **Name**: necokeeper-data
   - **Mount Path**: /app/data
   - **Size**: 1 GB
4. **Add Disk**

#### 3. 環境変数を更新

**Environment Variables** で以下を変更：

```bash
# データベースパスを永続化ディスクに変更
NECOKEEPER_DB_PATH=/app/data/necokeeper.db

# メディアファイルパスを永続化ディスクに変更
MEDIA_DIR=/app/media
BACKUP_DIR=/app/backups
LOG_FILE=/app/logs/necokeeper.log
```

**重要**: `NECOKEEPER_DB_PATH` を設定することで、永続ディスクの DB を使用します。

#### 4. 再デプロイ

**Manual Deploy** → **Deploy latest commit**

#### 5. データベース初期化（Starter Plan のみ）

Persistent Disk は空なので、初期化が必要：

1. **Shell** タブを開く（Render Dashboard）
2. データベース初期化:
   ```bash
   alembic upgrade head
   ```
3. 初期管理者アカウント作成:
   ```bash
   python -c "
   from app.database import SessionLocal
   from app.models.user import User
   from app.auth.password import hash_password

   db = SessionLocal()
   admin = User(
       email='admin@example.com',
       password_hash=hash_password('admin123'),
       name='管理者',
       role='admin',
       is_active=True
   )
   db.add(admin)
   db.commit()
   print('✅ 管理者アカウント作成完了')
   "
   ```

**または、init_db.py スクリプトを使用**:
```bash
python init_db.py
```

#### 6. データ移行（オプション）

Free Plan時のデータを移行する場合:

1. Free Plan時のデータをエクスポート（CSV等）
2. Starter Plan環境でインポート

---

## 🌿 ブランチ戦略（詳細）

### ハッカソン向け（1週間のPoC）

**推奨: `main`ブランチ直接デプロイ**

```
main → Render自動デプロイ
```

**メリット**:
- ✅ シンプル
- ✅ 素早いイテレーション
- ✅ 1人〜小規模チーム向け

**デメリット**:
- ⚠️ 本番環境に直接反映される
- ⚠️ レビュープロセスなし

**設定方法**:
1. Render Dashboard → NecoKeeperサービス
2. **Settings** → **Build & Deploy**
3. **Branch**: `main`
4. **Auto-Deploy**: `Yes`（デフォルト）

### 本番運用向け（将来）

**推奨: `deploy`ブランチ作成**

```
feature/xxx → main (開発) → PR → deploy (本番) → Render自動デプロイ
```

**メリット**:
- ✅ 本番環境の安定性
- ✅ レビュープロセス
- ✅ ロールバック容易

**設定方法**:

1. **deployブランチを作成**:
   ```bash
   git checkout -b deploy
   git push origin deploy
   ```

2. **Render設定を変更**:
   - Render Dashboard → NecoKeeperサービス
   - **Settings** → **Build & Deploy**
   - **Branch**: `deploy`に変更

3. **GitHub Branch Protection設定**（推奨）:
   - Settings → Branches → Add rule
   - Branch name pattern: `deploy`
   - ✅ Require pull request reviews before merging
   - ✅ Require status checks to pass

4. **デプロイフロー**:
   ```bash
   # 開発
   git checkout main
   git add .
   git commit -m "feat: 新機能"
   git push origin main

   # 本番デプロイ
   git checkout deploy
   git merge main
   git push origin deploy  # → Render自動デプロイ
   ```

---

## 🖥️ ローカル開発環境

### Docker Composeを使用

```bash
# イメージをビルド
docker-compose build

# コンテナを起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# コンテナを停止
docker-compose down
```

アクセス: http://localhost:8000

### 直接実行

```bash
# 仮想環境作成
python -m venv .venv

# 仮想環境アクティベート（Linux/Mac）
source .venv/bin/activate

# 仮想環境アクティベート（Windows）
.venv\Scripts\activate

# 依存関係インストール
pip install -r requirements.txt

# 環境変数設定
cp .env.example .env
# .envファイルを編集

# データベース初期化
alembic upgrade head

# 開発サーバー起動
uvicorn app.main:app --reload
```

アクセス: http://localhost:8000

---

## 🔒 Cookie設定の詳細

### Cookie設定が重要な理由

NecoKeeperは認証にJWT（JSON Web Token）を使用しており、トークンをHTTPOnly Cookieに保存します。
適切なCookie設定は、以下のセキュリティ対策に不可欠です：

| 設定 | 目的 | 開発環境 | 本番環境 |
|------|------|----------|----------|
| `httponly=True` | XSS攻撃対策（JavaScriptからアクセス不可） | ✅ 有効 | ✅ 有効 |
| `secure=True` | HTTPS必須（盗聴対策） | ❌ 無効 | ✅ **必須** |
| `samesite=lax` | CSRF攻撃対策 | ✅ 有効 | ✅ 有効 |
| `max_age=7200` | 自動削除（2時間） | ✅ 有効 | ✅ 有効 |

### 環境変数の設定

#### 本番環境（Render）

```bash
COOKIE_SECURE=true      # HTTPS必須
COOKIE_SAMESITE=lax     # CSRF対策
COOKIE_MAX_AGE=7200     # 2時間（7200秒）
```

#### 開発環境（ローカル）

```bash
COOKIE_SECURE=false     # HTTP許可（ローカル開発用）
COOKIE_SAMESITE=lax     # CSRF対策
COOKIE_MAX_AGE=7200     # 2時間（7200秒）
```

### セキュリティリスク

**❌ `COOKIE_SECURE=false`を本番環境で使用した場合**:

```
HTTP経由でトークンが送信される
    ↓
中間者攻撃（MITM）でトークンが盗まれる
    ↓
攻撃者が管理画面にアクセス可能
```

**✅ `COOKIE_SECURE=true`を本番環境で使用した場合**:

```
HTTPS経由でのみトークンが送信される
    ↓
暗号化された通信でトークンが保護される
    ↓
中間者攻撃を防止
```

### トラブルシューティング

#### ログインできない（本番環境）

**症状**: ログインボタンを押しても管理画面に遷移しない

**原因**: `COOKIE_SECURE=true`だが、HTTPでアクセスしている

**解決方法**:
1. HTTPSでアクセスしているか確認: `https://necokeeper.onrender.com`
2. Renderは自動的にHTTPSを提供するため、通常は問題なし
3. カスタムドメインを使用している場合は、SSL証明書を確認

#### ログインできない（開発環境）

**症状**: ローカル開発でログインできない

**原因**: `COOKIE_SECURE=true`だが、HTTPでアクセスしている

**解決方法**:
```bash
# .envファイルで設定
COOKIE_SECURE=false
```

#### Cookieが保存されない

**確認方法**（Chrome DevTools）:
1. F12でDevToolsを開く
2. **Application** タブ → **Cookies**
3. `access_token`が存在するか確認

**期待される値**:
- **Name**: `access_token`
- **Value**: `Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...`
- **HttpOnly**: ✅
- **Secure**: ✅（本番環境）
- **SameSite**: `Lax`
- **Expires**: 2時間後

---

## 🔧 トラブルシューティング

### Dockerfileが見つからないエラー

**エラー**:
```
Service Root Directory "/opt/render/project/src/ ./Dockerfile" is missing
error: invalid local: resolve : lstat /opt/render/project/src/ .: no such file or directory
```

**原因**: Dockerfile Pathの設定が間違っている

**解決方法**:
1. Render Dashboard → NecoKeeperサービス
2. **Settings** → **Build & Deploy**
3. **Dockerfile Path**: `./Dockerfile` に修正（余計なスペースを削除）
4. **Root Directory**: 空欄にする（何も入力しない）
5. **Save Changes**
6. **Manual Deploy** → **Deploy latest commit**

### スピンダウン対策（Free Plan）

**問題**: 15分間アクセスなしでスピンダウン

**対策**:
1. 外部監視サービスを使用（UptimeRobot等）
2. 定期的にヘルスチェックエンドポイントにアクセス
   ```bash
   curl https://necokeeper.onrender.com/health
   ```

### データ消失時の対応（Free Plan）

**問題**: 再デプロイでデータが消える

**対策**:
1. 定期的にデータをエクスポート（CSV）
2. 重要なデータは外部ストレージに保存
3. Starter Planへの早期移行を検討

### メモリ不足

**問題**: 512MBメモリ制限（Free Plan）

**対策**:
1. 大量の画像アップロードを避ける
2. PDF生成を最小限に
3. Starter Planへアップグレード（512MB → 2GB）

### 日本語フォントが表示されない

**問題**: PDF帳票で日本語が表示されない

**確認**:
```bash
# Dockerコンテナ内でフォント確認
fc-list | grep -i noto
fc-list | grep -i ipa
```

**対策**:
- Dockerfileに日本語フォントが含まれているか確認
- `fonts-noto-cjk`、`fonts-ipafont-gothic` がインストールされているか確認

### データベース接続エラー

**問題**: `sqlite3.OperationalError: unable to open database file`

**対策**:
1. DATABASE_URLのパスを確認
2. ディレクトリの権限を確認
3. Free Plan: `/tmp/data/` が存在するか確認
4. Starter Plan: Persistent Diskがマウントされているか確認

### ビルドエラー

**問題**: Dockerビルドが失敗

**確認**:
1. requirements.txtが最新か確認
2. Dockerfileの構文エラーを確認
3. Render Build Logsを確認

---

## 📚 参考リンク

- [Render公式ドキュメント](https://render.com/docs)
- [Docker公式ドキュメント](https://docs.docker.com/)
- [FastAPI公式ドキュメント](https://fastapi.tiangolo.com/)
- [SQLAlchemy公式ドキュメント](https://docs.sqlalchemy.org/)

---

## 🆘 サポート

問題が解決しない場合:
1. [GitHub Issues](https://github.com/your-repo/necokeeper/issues)
2. [Render Community](https://community.render.com/)
