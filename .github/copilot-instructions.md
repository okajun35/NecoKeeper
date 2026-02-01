# NecoKeeper Instructions

## 概要
NecoKeeperは、保護猫の管理と譲渡を行うためのアプリケーションです。


## 利用規約
- 回答は必ず日本語でしてください。
- 基本的にNecoKeeper配下にいるのでcdコマンドは不要
- AGENTS.mdに記載されたガイドラインに従ってください。

## セットアップ手順
1. リポジトリをクローンします。
   ```bash
   git clone https://github.com/okajun35/NecoKeeper.git
   cd NecoKeeper
   ```
2. Python仮想環境を作成し、アクティブにします。
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. 依存関係をインストールします。
   ```bash
   pip install -r requirements.txt
   ```
4. データベースを初期化します。
   ```bash
   python -m app.init_db
   ```
5. アプリケーションを起動します。
   ```bash
   uvicorn app.main:app --reload
   ```

## テストの実行
テストを実行するには、以下のコマンドを使用します。
```bash
pytest
```

## コードスタイル
- Python: 4スペースインデント、行の長さ88、ダブルクオートを使用
- JavaScript: Prettierを使用してフォーマット

## コントリビュート
1. 新しいブランチを作成します。
   ```bash
   git checkout -b feature/your-feature
   ```
2. 変更を加え、コミットします。
   ```bash
   git commit -m "Add your message"
   ```
3. プルリクエストを作成します。

## ライセンス
このプロジェクトはMITライセンスの下でライセンスされています。
