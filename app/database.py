"""
データベース接続モジュール

SQLAlchemyエンジンとセッション管理を提供します。
このモジュールは、アプリケーション全体でデータベース接続を一元管理します。
"""

from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings

# 設定を取得
settings = get_settings()


# SQLAlchemyエンジンの作成
# SQLiteの場合、check_same_threadをFalseに設定してマルチスレッド対応
engine = create_engine(
    settings.database_url,
    echo=settings.database_echo,
    connect_args={"check_same_thread": False}
    if "sqlite" in settings.database_url
    else {},
)


# セッションファクトリーの作成
# expire_on_commit=False: コミット後もオブジェクトの属性にアクセス可能
SessionLocal = sessionmaker(
    bind=engine,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


# Declarative Baseクラスの定義
# すべてのORMモデルはこのクラスを継承します
class Base(DeclarativeBase):
    """
    SQLAlchemy Declarative Base

    すべてのORMモデルクラスの基底クラスです。
    """

    pass


def get_db() -> Generator[Session, None, None]:
    """
    データベースセッションの依存性注入用ジェネレーター

    FastAPIのDependency Injectionで使用されます。
    セッションを自動的に作成し、リクエスト終了時にクローズします。

    Yields:
        Session: SQLAlchemyセッションオブジェクト

    Example:
        ```python
        @app.get("/users")
        def get_users(db: Session = Depends(get_db)):
            users = db.query(User).all()
            return users
        ```
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db() -> None:
    """
    データベースの初期化

    すべてのテーブルを作成します。
    本番環境ではAlembicマイグレーションを使用することを推奨します。

    Note:
        この関数は開発環境やテスト環境でのみ使用してください。
        本番環境ではAlembicを使用してマイグレーションを管理します。
    """
    # すべてのモデルをインポートして、Base.metadataに登録

    # テーブルを作成
    Base.metadata.create_all(bind=engine)
    print("✅ データベーステーブルを作成しました")


def drop_db() -> None:
    """
    データベースの削除

    すべてのテーブルを削除します。

    Warning:
        この関数は開発環境やテスト環境でのみ使用してください。
        本番環境では絶対に使用しないでください。
    """
    Base.metadata.drop_all(bind=engine)
    print("⚠️  データベーステーブルを削除しました")
