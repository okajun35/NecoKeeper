.PHONY: help all check format lint mypy test coverage prettier clean install pre-commit

# デフォルトターゲット
.DEFAULT_GOAL := help

# mypyで解析するパス（pre-commitと同一設定）
MYPY_TARGETS = app/

# ヘルプメッセージ
help:
	@echo "NecoKeeper - 開発用Makeコマンド"
	@echo ""
	@echo "使用方法:"
	@echo "  make <target>"
	@echo ""
	@echo "ターゲット:"
	@echo "  help        - このヘルプメッセージを表示"
	@echo "  all         - pre-commitと同じ順番で全チェック（推奨）"
	@echo "  check       - 基本チェック（format + lint + test）"
	@echo "  format      - コードフォーマット（Ruff）"
	@echo "  lint        - Lintチェック（Ruff）"
	@echo "  mypy        - 型チェック（Mypy）"
	@echo "  test        - テスト実行（Pytest）"
	@echo "  coverage    - カバレッジ付きテスト実行"
	@echo "  prettier    - JavaScript/JSON/YAMLフォーマット"
	@echo "  clean       - キャッシュファイルを削除"
	@echo "  install     - 依存パッケージをインストール"
	@echo "  pre-commit  - pre-commitフックをインストール"

# pre-commitと同じ順番で全チェック
all: lint format mypy test prettier
	@echo ""
	@echo "✅ 全てのチェックが完了しました！"
	@echo "コミット可能です: git add . && git commit -m 'your message'"

# コミット前の基本チェック
check: format lint test
	@echo ""
	@echo "✅ 基本チェックが完了しました！"
	@echo "コミット可能です: git add . && git commit -m 'your message'"

# Lintチェック（Ruff - 最初に実行）
lint:
	@echo "🔍 [1/5] Lintチェック中（Ruff）..."
	@ruff check . --fix
	@echo "✅ Lintチェック完了"

# コードフォーマット（Ruff Format）
format:
	@echo "🎨 [2/5] コードフォーマット中（Ruff Format）..."
	@ruff format .
	@echo "✅ フォーマット完了"

# 型チェック（Mypy）
# pre-commitと同じ設定: app/配下のPythonファイルのみチェック
mypy:
	@echo "🔎 [3/5] 型チェック中（Mypy）..."
	@mypy --config-file=mypy.ini $(MYPY_TARGETS) || (echo "⚠️  Mypy型チェックでエラーが見つかりました" && exit 1)
	@echo "✅ 型チェック完了"

# 国際化翻訳ファイルをコンパイル
i18n-compile:
	@echo "🌐 i18n翻訳ファイルをコンパイル中..."
	@pybabel compile -d app/locales
	@echo "✅ i18n翻訳ファイルのコンパイル完了"

# テスト実行（Pytest）
test:
	@echo "🧪 [4/5] テスト実行中（Pytest）..."
	@echo "🌐 i18n翻訳ファイルをコンパイル中..."
	@pybabel compile -d app/locales
	@python -m pytest -v --tb=short
	@echo "✅ テスト完了"

# Prettier（JavaScript/JSON/YAML）
prettier:
	@echo "💅 [5/5] JavaScript/JSON/YAMLフォーマット中（Prettier）..."
	@if command -v npx >/dev/null 2>&1; then \
		npx -y prettier --write 'app/static/js/**/*.js' '*.json' '*.yaml' '.pre-commit-config.yaml' 2>&1 | grep -v "No files matching" || true; \
	elif command -v prettier >/dev/null 2>&1; then \
		prettier --write 'app/static/js/**/*.js' '*.json' '*.yaml' '.pre-commit-config.yaml' 2>&1 | grep -v "No files matching" || true; \
	else \
		echo "ℹ️  Prettierがインストールされていません。スキップします（pre-commitで自動実行されます）"; \
	fi
	@echo "✅ Prettierチェック完了"

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
