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

3. 依存関係をインストール

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

4. 環境変数を設定

```bash
# .env.example を .env にコピー
cp .env.example .env

# .env ファイルを編集して、必要な設定を変更
# 特に SECRET_KEY は本番環境では必ず変更してください
```

5. アプリケーションを起動

```bash
# 開発サーバーを起動
python3 -m app.main

# または uvicorn を直接使用
uvicorn app.main:app --reload
```

6. ブラウザでアクセス

- アプリケーション: http://localhost:8000
- API ドキュメント: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

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

### 開発ツール

#### テスト実行

```bash
# すべてのテストを実行
python -m pytest

# 詳細出力
python -m pytest -v

# カバレッジ付き
python -m pytest --cov=app
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
