# NecoKeeper - Dockerfile
# マルチステージビルドで最適化されたDockerイメージ
# Free Plan PoC向け（SQLiteエフェメラル）

# ============================================
# Stage 1: Builder
# 依存関係のインストールとビルド
# ============================================
FROM python:3.12-slim as builder

# 作業ディレクトリ
WORKDIR /app

# システムパッケージの更新とビルド依存関係のインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint依存パッケージ
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    libffi-dev \
    shared-mime-info \
    fontconfig \
    # 日本語フォント（PDF帳票の日本語表示に必須）
    fonts-noto-cjk \
    fonts-ipafont-gothic \
    fonts-ipafont-mincho \
    # ビルドツール
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Pythonパッケージのインストール
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# ============================================
# Stage 2: Runtime
# 本番環境用の軽量イメージ
# ============================================
FROM python:3.12-slim

# 作業ディレクトリ
WORKDIR /app

# 実行時に必要なシステムパッケージのみインストール
RUN apt-get update && apt-get install -y --no-install-recommends \
    # WeasyPrint実行時依存パッケージ
    libpango-1.0-0 \
    libpangoft2-1.0-0 \
    libcairo2 \
    libgdk-pixbuf-2.0-0 \
    shared-mime-info \
    fontconfig \
    && rm -rf /var/lib/apt/lists/*

# 日本語フォントをBuilderからコピー（PDF生成に必須）
COPY --from=builder /usr/share/fonts /usr/share/fonts
COPY --from=builder /etc/fonts /etc/fonts

# フォントキャッシュを更新
RUN fc-cache -fv

# Pythonパッケージをbuilderからコピー
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# アプリケーションコードをコピー
COPY app/ ./app/
COPY alembic/ ./alembic/
COPY alembic.ini .

# リポジトリの DB をイメージに含める（Free Plan 用）
COPY data ./data

# 初期化スクリプトをコピー（パーミッション設定前）
COPY scripts/init_db.sh /app/scripts/init_db.sh

# エフェメラルディレクトリの作成（Free Plan用）
# 注意: これらのディレクトリは再デプロイで消える
RUN mkdir -p /tmp/data /tmp/media /tmp/backups /tmp/logs && \
    chmod 777 /tmp/data /tmp/media /tmp/backups /tmp/logs && \
    chmod +x /app/scripts/init_db.sh

# 非rootユーザーの作成（セキュリティ）
RUN useradd -m -u 1000 necokeeper && \
    chown -R necokeeper:necokeeper /app /tmp/data /tmp/media /tmp/backups /tmp/logs

# 非rootユーザーに切り替え
USER necokeeper

# 環境変数の設定（デフォルト値）
# 注意: Render Dashboard設定が優先されます
# SECRET_KEY, ENVIRONMENT, DEBUG等は必ずRender Dashboardから設定してください
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    # Free Plan用のエフェメラルパス（Render Dashboard設定で上書き可能）
    DATABASE_URL=sqlite:////tmp/data/necokeeper.db \
    MEDIA_DIR=/tmp/media \
    BACKUP_DIR=/tmp/backups \
    LOG_FILE=/tmp/logs/necokeeper.log

# ポート公開
EXPOSE 8000

# ヘルスチェック設定
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health').read()"

# 起動コマンド（自動初期化付き）
# Renderの$PORT環境変数を使用（デフォルト8000）
CMD ["/app/scripts/init_db.sh"]
