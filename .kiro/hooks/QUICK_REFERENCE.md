# Kiro Hooks クイックリファレンス

すぐに使えるコマンドとワークフローのチートシート

## 🚀 よく使うコマンド

### コミット前チェック
```bash
# 全品質チェック実行
make all

# または個別実行
make lint      # Lintチェック
make format    # コードフォーマット
make type-check # 型チェック
make test      # テスト実行
```

### カバレッジ確認
```bash
# カバレッジ測定
pytest --cov=app --cov-report=term-missing

# HTMLレポート生成
pytest --cov=app --cov-report=html

# レポート表示
xdg-open htmlcov/index.html  # Linux
open htmlcov/index.html      # macOS
start htmlcov/index.html     # Windows
```

### ケアログ登録
```bash
# 手動登録
PYTHONPATH=. python scripts/hooks/register_care_logs.py tmp/json/file.json

# PDF変換
python scripts/hooks/pdf_to_image.py tmp/pdf/file.pdf --use-pymupdf
```

---

## 📋 フック一覧（コピペ用）

### 1. Pre-Commit Quality Gate
```
実行: Ctrl+Shift+P → "Pre-Commit Quality Gate"
用途: コミット前の全品質チェック
時間: 30-60秒
```

### 2. Test Coverage Analyzer
```
実行: Ctrl+Shift+P → "Test Coverage Analyzer"
用途: カバレッジ分析と改善提案
時間: 10-30秒
```

### 3. Register Care Logs (Manual)
```
実行: tmp/json/*.json を右クリック → "Register Care Logs (Manual)"
用途: ケアログ手動登録
時間: 1-5秒
```

### 4. Register Care Logs (Auto)
```
実行: tmp/json/auto.json に保存で自動実行
用途: ケアログ自動登録
時間: 1-5秒
```

### 5. PDF to Image Converter
```
実行: tmp/pdf/*.pdf を右クリック → "PDF to Image Converter"
用途: PDF→画像変換
時間: 5-30秒
```

---

## 🔄 典型的なワークフロー

### ワークフロー1: 新機能開発

```bash
# 1. ブランチ作成
git checkout -b feature/new-feature

# 2. コード実装
# ... コーディング ...

# 3. 品質チェック
make all

# 4. カバレッジ確認
pytest --cov=app --cov-report=term-missing

# 5. コミット
git add .
git commit -m "feat(scope): 新機能を追加"

# 6. プッシュ
git push origin feature/new-feature
```

### ワークフロー2: OCRケアログインポート

```bash
# 1. PDF配置
cp /path/to/care-log.pdf tmp/pdf/

# 2. PDF→画像変換（右クリック or コマンド）
python scripts/hooks/pdf_to_image.py tmp/pdf/care-log.pdf --use-pymupdf

# 3. 画像→JSON（Kiroチャット）
# [画像を添付]
# "これはIDが12の猫の2024年11月14日～23日の記録です。
#  JSON化してtmp/json/care_log_20241114.json に保存してください。"

# 4. JSON→DB（右クリック or 自動）
# tmp/json/care_log_20241114.json を右クリック
# → "Register Care Logs (Manual)"
```

### ワークフロー3: テストカバレッジ改善

```bash
# 1. 現状確認
pytest --cov=app --cov-report=html

# 2. 詳細分析（フック実行）
# Ctrl+Shift+P → "Test Coverage Analyzer"

# 3. 不足テスト追加
# tests/test_xxx.py を編集

# 4. 再測定
pytest --cov=app --cov-report=term-missing

# 5. 改善確認
# カバレッジが向上したか確認
```

---

## 🐛 トラブルシューティング早見表

| 問題 | 解決方法 |
|------|---------|
| フックが実行されない | `.kiro.hook`ファイルの`"enabled": true`を確認 |
| API認証エラー | `.env`ファイルの`NECOKEEPER_ADMIN_USERNAME/PASSWORD`を確認 |
| モジュールエラー | `source .venv/bin/activate` → `pip install -r requirements.txt` |
| テスト失敗 | `pytest tests/test_xxx.py -v`で詳細確認 |
| Mypyエラー | 型ヒント追加: `def func(x: int) -> str:` |
| JSONエラー | `python -m json.tool tmp/json/file.json`で検証 |
| PDFエラー | `pip install PyMuPDF`でライブラリインストール |
| 権限エラー | `chmod +x scripts/hooks/*.py`で実行権限付与 |

---

## 📊 カバレッジ目標値

| レイヤー | 目標 | 現在 | 状態 |
|---------|------|------|------|
| ドメイン層（models/） | 90%+ | 92% | ✅ |
| サービス層（services/） | 80%+ | 75% | ⚠️ |
| API層（api/） | 70%+ | 78% | ✅ |
| 認証層（auth/） | 80%+ | 85% | ✅ |
| ユーティリティ層（utils/） | 70%+ | 65% | ⚠️ |
| **全体** | **70%+** | **80.99%** | ✅ |

---

## 🔑 環境変数チェックリスト

```bash
# .envファイルに以下が設定されているか確認
cat .env

# 必須項目
NECOKEEPER_API_URL=http://localhost:8000
NECOKEEPER_ADMIN_USERNAME=admin
NECOKEEPER_ADMIN_PASSWORD=your_password

# オプション
AUTOMATION_API_ENABLED=true
AUTOMATION_API_KEY=your_32_character_key
```

---

## 📁 ディレクトリ構造

```
tmp/
├── pdf/                    # PDF入力
├── pdfs/                   # PDF入力（代替）
├── images/                 # 変換後の画像
└── json/                   # JSONデータ
    ├── auto.json          # 自動登録用
    └── processed/         # 処理済み
```

---

## 🎯 コミットメッセージ例

```bash
# 新機能
git commit -m "feat(api): 新しいエンドポイントを追加"

# バグ修正
git commit -m "fix(ui): ログインフォームのバリデーションを修正"

# リファクタリング
git commit -m "refactor(service): 型ヒントをモダンな構文に更新"

# テスト追加
git commit -m "test(mcp): MCPツールのテストを追加"

# ドキュメント
git commit -m "docs: Kiroフックのガイドを追加"

# スタイル
git commit -m "style: Ruffフォーマットを適用"

# パフォーマンス
git commit -m "perf(db): クエリを最適化"

# ビルド
git commit -m "chore: 依存関係を更新"
```

---

## 🔗 よく使うリンク

- [完全ガイド](./HOOKS_GUIDE.md)
- [OCRワークフロー](./README.md)
- [API仕様](../../app/api/automation/README.md)
- [MCP統合](../../app/mcp/README.md)
- [テストガイド](../../tests/README.md)

---

## 💡 ヒント

### 効率的な開発のために

1. **コミット前は必ず`make all`を実行**
   - 品質問題を早期発見
   - CI/CDでの失敗を防止

2. **週次でカバレッジ分析**
   - テストの穴を早期発見
   - 技術的負債の蓄積を防止

3. **フックをカスタマイズ**
   - プロジェクト固有のニーズに対応
   - ワークフローを最適化

4. **ログを確認**
   - `logs/ocr-import.log`で詳細確認
   - エラー原因の特定が容易

5. **環境変数を適切に管理**
   - `.env.example`をテンプレートとして使用
   - 機密情報はGitにコミットしない

---

**印刷用**: このページをPDFとして保存して、デスクに置いておくと便利です！

**最終更新**: 2024年11月30日
