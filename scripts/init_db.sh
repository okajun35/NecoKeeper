#!/bin/bash
# データベース初期化スクリプト
# Render Free Plan用: 起動時にイメージ内のDBを/tmp/data/にコピー

set -e

echo "🔍 データベースの準備..."

# /tmp/data ディレクトリを作成（存在しない場合）
mkdir -p /tmp/data

# イメージ内のDBを/tmp/data/にコピー（Free Plan用）
if [ -f "/app/data/necokeeper.db" ] && [ ! -f "/tmp/data/necokeeper.db" ]; then
    echo "📦 イメージ内のDBを/tmp/data/にコピー中..."
    cp /app/data/necokeeper.db /tmp/data/necokeeper.db
    echo "✅ DBコピー完了"
elif [ ! -f "/tmp/data/necokeeper.db" ]; then
    echo "📦 DBが見つかりません。マイグレーションで初期化します..."

    # マイグレーション実行
    echo "🔄 マイグレーション実行中..."
    alembic upgrade head

    # 初期管理者アカウント作成
    echo "👤 初期管理者アカウント作成中..."
    python -c "
from app.database import SessionLocal
from app.models.user import User
from app.auth.password import hash_password

db = SessionLocal()
try:
    # 既存の管理者をチェック
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
        print('ℹ️  管理者アカウントは既に存在します')
except Exception as e:
    print(f'❌ エラー: {e}')
    db.rollback()
finally:
    db.close()
"

    echo "✅ データベース初期化完了"
else
    echo "✅ データベースは既に存在します"
fi

echo "🚀 アプリケーションを起動します..."
exec uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
