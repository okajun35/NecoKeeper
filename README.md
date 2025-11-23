# NecoKeeper

保護猫管理システム - 保護猫団体向けの包括的な管理システム

## 概要

NecoKeeperは、保護猫団体が日々の業務を効率的に管理するためのWebアプリケーションです。

### 主な機能

- 🐱 **猫管理**: 保護猫の情報管理、写真管理
- 📝 **世話記録**: 日々の世話記録、健康管理
- 👥 **里親管理**: 里親希望者の管理、譲渡プロセス管理
- 📄 **PDF生成**: QRコード付き猫カードの生成
- 📊 **レポート**: 統計情報とレポート生成
- 💾 **バックアップ**: 自動バックアップ機能

## セットアップ

### 必要要件

- **Python 3.12以上** (このプロジェクトは Python 3.12 で開発されています)
- pip または uv (パッケージマネージャー)
- **Docker** (オプション、コンテナ実行用)

### インストール手順

1. リポジトリをクローン

```bash
git clone <repository-url>
cd NecoKeeper
```

2. 仮想環境を作成してアクティベート

**方法1: 標準の venv を使用**
```bash
# 仮想環境作成
python3 -m venv .venv

# アクティベート（Linux/macOS）
source .venv/bin/activate

# アクティベート（Windows PowerShell）
.venv\Scripts\Activate.ps1

# アクティベート（Windows CMD）
.venv\Scripts\activate.bat
```

**方法2: uv を使用（推奨・高速）**
```bash
# uvで仮想環境を作成して自動アクティベート
uv venv

# アクティベート（Linux/macOS）
source .venv/bin/activate

# アクティベート（Windows PowerShell）
.venv\Scripts\Activate.ps1
```

3. 日本語フォントをインストール（PDF生成用）

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install fonts-ipafont fonts-noto-cjk
```

**macOS:**
```bash
# Homebrewを使用
brew install font-noto-sans-cjk-jp
```

**Windows:**
- システムに日本語フォント（Yu Gothic、Meiryoなど）が既にインストールされています

4. 依存関係をインストール

**方法1: pip を使用**
```bash
pip install -r requirements.txt
```

**方法2: uv を使用（推奨・高速）**
```bash
# uvのインストール（初回のみ）
# Windows (PowerShell)
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# Linux/macOS
curl -LsSf https://astral.sh/uv/install.sh | sh

# uvで依存関係をインストール
uv pip install -r requirements.txt
```

5. 環境変数を設定

```bash
# .env.example を .env にコピー
cp .env.example .env

# .env ファイルを編集して、必要な設定を変更
# 特に SECRET_KEY は本番環境では必ず変更してください
```

**重要な環境変数**:

| 変数名 | 説明 | 開発環境 | 本番環境 |
|--------|------|----------|----------|
| `SECRET_KEY` | JWT署名用の秘密鍵（32文字以上） | 任意 | **必須変更** |
| `DEBUG` | デバッグモード | `true` | **`false`** |
| `ENVIRONMENT` | 実行環境 | `development` | `production` |
| `NECOKEEPER_DB_PATH` | DBファイルパス | `data/necokeeper.db` | 環境に応じて |
| `COOKIE_SECURE` | Cookie Secureフラグ | `false` | **`true`** |
| `COOKIE_SAMESITE` | Cookie SameSite属性 | `lax` | `lax` |
| `COOKIE_MAX_AGE` | Cookie有効期限（秒） | `7200` | `7200` |

**DB パス設定**:
- **ローカル開発**: `NECOKEEPER_DB_PATH=data/necokeeper.db`（デフォルト）
- **Render Free Plan**: `NECOKEEPER_DB_PATH=data/necokeeper.db`（イメージに含まれる）
- **Render Starter Plan**: `NECOKEEPER_DB_PATH=/app/data/necokeeper.db`（永続ディスク）
- 未設定の場合: `DATABASE_URL` の値を使用（後方互換性）

**セキュリティ注意事項**:
- ⚠️ 本番環境では`DEBUG=false`、`COOKIE_SECURE=true`を必ず設定
- ⚠️ `SECRET_KEY`は32文字以上のランダム文字列を使用
- 生成方法: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

6. アプリケーションを起動

```bash
# 開発サーバーを起動
python3 -m app.main

# または uvicorn を直接使用
uvicorn app.main:app --reload
```

6. サンプルデータを投入（オプション）

開発・テスト用のサンプルデータを投入できます：

```bash
python scripts/seed_sample_data.py
```

投入されるデータ：
- **ユーザー**: 3人（管理者2名、獣医師1名）
- **ボランティア**: 4人
- **猫**: 10匹（様々なステータス：保護中、譲渡可能、譲渡済み、治療中）
- **世話記録**: 約140件（過去7日分）
- **ステータス履歴**: 10件

ログイン情報：
- 開発用管理者: `admin@example.com` / `admin123`
- 管理者: `admin@necokeeper.local` / `admin123`
- 獣医師: `vet@necokeeper.local` / `vet123`

7. ブラウザでアクセス

- アプリケーション: http://localhost:8000
- 管理画面: http://localhost:8000/admin
- API ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

### Dockerを使用したセットアップ（推奨）

Dockerを使用すると、環境構築が簡単になります。

#### 前提条件
- Docker Desktop（Windows/Mac）または Docker Engine（Linux）

#### クイックスタート（単体コンテナ）

**注意**: 単体コンテナではデータが永続化されません。データ永続化にはDocker Composeを使用してください。

```bash
# 1. イメージをビルド
docker build -t necokeeper .

# 2. コンテナを起動（ローカル開発用）
docker run -d -p 8000:8000 \
  --name necokeeper \
  -e SECRET_KEY=$(python -c "import secrets; print(secrets.token_urlsafe(32))") \
  -e DATABASE_URL=sqlite:////tmp/data/necokeeper.db \
  -e ENVIRONMENT=development \
  -e DEBUG=true \
  necokeeper

# 3. ログを確認
docker logs -f necokeeper

# 4. ブラウザでアクセス
# http://localhost:8000
```

#### Docker Composeを使用（ローカル開発・データ永続化）

**推奨**: Docker Composeを使用すると、データが永続化されます。

```bash
# コンテナをビルド＆起動
docker-compose up -d

# ログを確認
docker-compose logs -f

# コンテナを停止（データは保持される）
docker-compose down

# コンテナとボリュームを削除（データも削除）
docker-compose down -v
```

**データ永続化**:
- ✅ `./data/necokeeper.db` - データベース
- ✅ `./media/` - アップロード画像
- ✅ `./backups/` - バックアップファイル
- ✅ `./logs/` - ログファイル

**初回のみ必要な手順**:
```bash
# データベース初期化（初回のみ）
docker-compose exec web alembic upgrade head

# 管理者アカウント作成（初回のみ）
docker-compose exec web python -c "
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

**2回目以降の起動**:
```bash
# データは保持されているので、そのまま起動
docker-compose up -d
```

#### Dockerコンテナの管理

```bash
# コンテナを停止
docker stop necokeeper

# コンテナを再起動
docker restart necokeeper

# コンテナを削除
docker rm -f necokeeper

# イメージを削除
docker rmi necokeeper
```

### Renderへのデプロイ

**🎉 本番環境デプロイ完了！**

- **URL**: https://necokeeper.onrender.com
- **プラン**: Render Free Plan
- **デプロイ日**: 2024-11-23
- **動作確認**: ✅ ログイン画面、API、多言語対応すべて正常動作

詳細なデプロイ手順は [DEPLOY.md](DEPLOY.md) を参照してください。

**Free Plan（1週間のPoC）**:
- 完全無料
- SQLiteエフェメラル（再デプロイでデータ消失）
- 15分でスピンダウン
- **現在稼働中**: https://necokeeper.onrender.com

**Starter Plan（本番運用）**:
- $7/月
- Persistent Disk（データ永続化）
- 常時稼働

## 開発

### プロジェクト構造

```
NecoKeeper/
├── app/                    # アプリケーションコード
│   ├── api/               # APIエンドポイント
│   ├── auth/              # 認証・認可
│   ├── db/                # データベース関連
│   ├── models/            # データモデル
│   ├── schemas/           # Pydanticスキーマ
│   ├── services/          # ビジネスロジック
│   ├── static/            # 静的ファイル
│   ├── templates/         # HTMLテンプレート
│   ├── config.py          # 設定管理
│   └── main.py            # エントリーポイント
├── data/                  # データベースファイル
├── media/                 # アップロードファイル
├── backups/               # バックアップファイル
├── logs/                  # ログファイル
├── tests/                 # テストコード
├── .env                   # 環境変数（gitignore）
├── .env.example           # 環境変数の例
└── requirements.txt       # Python依存関係
```

### サンプルデータ

開発・テスト環境でサンプルデータを使用する場合：

```bash
# サンプルデータを投入
python scripts/seed_sample_data.py
```

このスクリプトは以下を実行します：
1. 既存データをすべて削除
2. サンプルユーザー、ボランティア、猫、世話記録を投入
3. ログイン情報を表示

**注意**: 本番環境では実行しないでください。既存データがすべて削除されます。

### 開発ツール

#### Makeコマンド（推奨）

コミット前のチェックを簡単に実行できるMakefileを用意しています：

```bash
# ヘルプを表示
make help

# pre-commitと同じ順番で全チェック（推奨）
# lint → format → mypy → test → prettier
make all

# 基本チェック（format + lint + test）
make check

# 個別実行
make lint      # Lintチェック（Ruff）
make format    # コードフォーマット（Ruff Format）
make mypy      # 型チェック（Mypy）
make test      # テスト実行（Pytest）
make prettier  # JavaScript/JSON/YAMLフォーマット
make coverage  # カバレッジ付きテスト
make clean     # キャッシュファイル削除
```

**推奨ワークフロー（必須）**:
```bash
# コード変更後、コミット前に必ず実行
make all

# 全てパスしたらコミット
git add .
git commit -m "your message"
git push
```

**重要**: `make all`は**コミット前に必ず実行**してください。これにより以下が保証されます：
- コード品質（Lint）
- フォーマット統一（Ruff Format）
- 型安全性（Mypy）
- 全テストパス（Pytest 345テスト）
- JavaScript/JSON/YAMLフォーマット（Prettier）

**`make all` と `make check` の違い**:
- `make all`: pre-commitと同じ順番・設定で全チェック（lint → format → mypy → test → prettier）
- `make check`: 基本チェックのみ（format → lint → test）

**チェックが失敗した場合**:
- Lint/Formatエラー: 自動修正されるので再度`make all`を実行
- Mypyエラー: 型ヒントを修正
- Testエラー: テストを修正してから再実行

#### テスト実行

```bash
# すべてのテストを実行
python -m pytest

# 詳細出力
python -m pytest -v

# カバレッジ付き
python -m pytest --cov=app --cov-report=html --cov-report=term-missing
```

#### コード品質チェック

```bash
# Ruffでフォーマット
ruff format .

# Ruffでリント
ruff check . --fix

# Mypyで型チェック
mypy .
```

#### Pre-commit

コミット前に自動的にコード品質チェックが実行されます：

```bash
# Pre-commitフックをインストール
pre-commit install

# 手動で全ファイルをチェック
pre-commit run --all-files
```

Pre-commitは以下を自動実行します：
- Ruff lint & format
- Mypy型チェック
- Pytest
- 標準フック（trailing-whitespace、end-of-file-fixer等）
