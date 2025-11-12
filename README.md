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

- Python 3.9以上
- pip または uv

### インストール手順

1. リポジトリをクローン

```bash
git clone <repository-url>
cd NecoKeeper
```

2. 仮想環境を作成してアクティベート

```bash
# 仮想環境作成
python3 -m venv .venv

# アクティベート（Linux/Mac）
source .venv/bin/activate

# アクティベート（Windows）
.venv\Scripts\activate
```

3. 依存関係をインストール

```bash
pip install -r requirements.txt
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

### テスト実行

```bash
pytest
```

### コードフォーマット

```bash
# Ruffでフォーマット
ruff format .

# Ruffでリント
ruff check .
```

## ライセンス

TBD

## 貢献

TBD