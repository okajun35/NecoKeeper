.PHONY: help check format lint test coverage clean install pre-commit

# デフォルトターゲット
.DEFAULT_GOAL := help

# ヘルプメッセージ
help:
	@echo "NecoKeeper - 開発用Makeコマンド"
	@echo ""
	@echo "使用方法:"
	@echo "  make <target>"
	@echo ""
	@echo "ターゲット:"
	@echo "  help        - このヘルプメッセージを表示"
	@echo "  check       - コミット前の全チェック（format + lint + test）"
	@echo "  format      - コードフォーマット（Ruff）"
	@echo "  lint        - Lintチェック（Ruff）"
	@echo "  test        - テスト実行（Pytest）"
	@echo "  coverage    - カバレッジ付きテスト実行"
	@echo "  clean       - キャッシュファイルを削除"
	@echo "  install     - 依存パッケージをインストール"
	@echo "  pre-commit  - pre-commitフックをインストール"

# コミット前の全チェック
check: format lint test
	@echo ""
	@echo "✅ 全てのチェックが完了しました！"
	@echo "コミット可能です: git add . && git commit -m 'your message'"

# コードフォーマット
format:
	@echo "🎨 コードフォーマット中..."
	@ruff format .
	@echo "✅ フォーマット完了"

# Lintチェック
lint:
	@echo "🔍 Lintチェック中..."
	@ruff check . --fix
	@echo "✅ Lintチェック完了"

# テスト実行
test:
	@echo "🧪 テスト実行中..."
	@python -m pytest
	@echo "✅ テスト完了"

# カバレッジ付きテスト
coverage:
	@echo "📊 カバレッジ付きテスト実行中..."
	@python -m pytest --cov=app --cov-report=html --cov-report=term-missing
	@echo "✅ カバレッジレポート生成完了"
	@echo "HTMLレポート: htmlcov/index.html"

# キャッシュファイル削除
clean:
	@echo "🧹 キャッシュファイル削除中..."
	@find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".ruff_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name ".mypy_cache" -exec rm -rf {} + 2>/dev/null || true
	@find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name ".coverage" -delete 2>/dev/null || true
	@find . -type f -name "*.pyc" -delete 2>/dev/null || true
	@echo "✅ キャッシュファイル削除完了"

# 依存パッケージインストール
install:
	@echo "📦 依存パッケージインストール中..."
	@pip install -r requirements.txt
	@echo "✅ インストール完了"

# pre-commitフックインストール
pre-commit:
	@echo "🔧 pre-commitフックインストール中..."
	@pre-commit install
	@echo "✅ pre-commitフック設定完了"
