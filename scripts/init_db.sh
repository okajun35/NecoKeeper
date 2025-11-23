#!/bin/bash
# データベース初期化スクリプト
# Render Free Plan用: 起動時に自動的にデータベースを初期化

set -e

echo "🔍 データベースの存在確認..."

# データベースファイルが存在しない場合のみ初期化
if [ ! -f "/tmp/data/necokeeper.db" ]; then
    echo "📦 データベースが見つかりません。初期化を開始します..."

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
