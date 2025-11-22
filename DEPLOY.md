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
| **Dockerfile Path** | ./Dockerfile | Dockerfileの場所 |
| **Instance Type** | Free | 無料プラン |

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
- **環境変数はRender Dashboard画面から設定**（Dockerに内蔵しない）

**環境変数の設定方法**:

1. **Advanced** → **Environment Variables** をクリック
2. **Add Environment Variable** で以下を1つずつ追加：

```bash
# 必須
SECRET_KEY=<32文字以上のランダム文字列>
DATABASE_URL=sqlite:////tmp/data/necokeeper.db
ENVIRONMENT=production
DEBUG=false

# 推奨
CORS_ORIGINS=https://necokeeper.onrender.com
MEDIA_DIR=/tmp/media
BACKUP_DIR=/tmp/backups
LOG_FILE=/tmp/logs/necokeeper.log
LOG_LEVEL=INFO
```

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

#### 6. 初回セットアップ（Render環境のみ）

**注意**:
- ⚠️ **Render Free Planでは再デプロイのたびにデータが消えます**
- ⚠️ 再デプロイ後は毎回この手順が必要です
- ✅ ローカル開発環境では`data/necokeeper.db`が永続化されるため不要

デプロイ完了後、以下の手順で初期化：

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

**Starter Planへの移行後**:
- ✅ Persistent Diskでデータ永続化
- ✅ 初回のみ初期化すればOK
- ✅ 再デプロイでもデータは保持される

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
DATABASE_URL=sqlite:////app/data/necokeeper.db

# メディアファイルパスを永続化ディスクに変更
MEDIA_DIR=/app/media
BACKUP_DIR=/app/backups
LOG_FILE=/app/logs/necokeeper.log
```

#### 4. 再デプロイ

**Manual Deploy** → **Deploy latest commit**

#### 5. データベース初期化（再度）

Persistent Diskは空なので、再度初期化が必要：

```bash
alembic upgrade head
```

初期管理者アカウントも再作成してください。

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

## 🔧 トラブルシューティング

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
