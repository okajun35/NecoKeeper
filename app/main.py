"""
NecoKeeper - FastAPIアプリケーションのエントリーポイント

保護猫管理システムのメインアプリケーションファイル。
FastAPIアプリケーションの初期化、ミドルウェアの設定、ルーターの登録を行います。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles

from app.api.v1 import (
    admin_pages,
    animals,
    auth,
    care_logs,
    images,
    pdf,
    public,
    public_pages,
    volunteers,
)
from app.config import get_settings

# 設定を取得
settings = get_settings()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    """
    アプリケーションのライフサイクル管理

    起動時と終了時に実行される処理を定義します。
    - 起動時: データベース接続、必要なディレクトリの作成など
    - 終了時: リソースのクリーンアップ
    """
    # 起動時の処理
    print(f"🚀 {settings.app_name} v{settings.app_version} を起動しています...")
    print(f"📝 環境: {settings.environment}")
    print(f"🔧 デバッグモード: {settings.debug}")

    # 必要なディレクトリを作成
    Path(settings.media_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.backup_dir).mkdir(parents=True, exist_ok=True)
    Path(settings.log_file).parent.mkdir(parents=True, exist_ok=True)
    Path(settings.database_url.replace("sqlite:///", "")).parent.mkdir(
        parents=True, exist_ok=True
    )

    print("✅ 起動完了")

    yield

    # 終了時の処理
    print("👋 アプリケーションを終了しています...")


# FastAPIアプリケーションの初期化
app = FastAPI(
    title=settings.app_name,
    version=settings.app_version,
    description="""
    ## NecoKeeper - 保護猫管理システム

    保護猫団体向けの包括的な管理システムです。

    ### 主な機能

    * **猫管理**: 保護猫の情報管理、写真管理
    * **世話記録**: 日々の世話記録、健康管理
    * **里親管理**: 里親希望者の管理、譲渡プロセス管理
    * **PDF生成**: QRコード付き猫カードの生成
    * **レポート**: 統計情報とレポート生成
    * **バックアップ**: 自動バックアップ機能

    ### 認証

    管理画面へのアクセスにはログインが必要です。
    """,
    debug=settings.debug,
    lifespan=lifespan,
    docs_url="/docs" if settings.debug else None,
    redoc_url="/redoc" if settings.debug else None,
)


# CORSミドルウェアの設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# 静的ファイルのマウント
# メディアファイル（画像など）
if Path(settings.media_dir).exists():
    app.mount("/media", StaticFiles(directory=settings.media_dir), name="media")

# 静的アセット（CSS、JS、画像など）
if Path("app/static").exists():
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ルートエンドポイント
@app.get("/", tags=["Root"])
async def root() -> dict[str, str | None]:
    """
    ルートエンドポイント

    アプリケーションの基本情報を返します。
    """
    return {
        "app_name": settings.app_name,
        "version": settings.app_version,
        "environment": settings.environment,
        "status": "running",
        "docs_url": "/docs" if settings.debug else None,
    }


# ヘルスチェックエンドポイント
@app.get("/health", tags=["Health"])
async def health_check() -> dict[str, str]:
    """
    ヘルスチェックエンドポイント

    アプリケーションの稼働状態を確認します。
    ロードバランサーやモニタリングツールから使用されます。
    """
    return {
        "status": "healthy",
        "app_name": settings.app_name,
        "version": settings.app_version,
    }


# グローバル例外ハンドラー
@app.exception_handler(Exception)
async def global_exception_handler(request, exc: Exception) -> JSONResponse:  # type: ignore[no-untyped-def]
    """
    グローバル例外ハンドラー

    予期しないエラーをキャッチして、適切なレスポンスを返します。
    """
    import traceback

    # デバッグモードの場合は詳細なエラー情報を返す
    if settings.debug:
        return JSONResponse(
            status_code=500,
            content={
                "error": "Internal Server Error",
                "detail": str(exc),
                "traceback": traceback.format_exc(),
            },
        )

    # 本番環境では簡潔なエラーメッセージのみ
    return JSONResponse(
        status_code=500,
        content={
            "error": "Internal Server Error",
            "detail": "予期しないエラーが発生しました。管理者に連絡してください。",
        },
    )


# APIルーターの登録
app.include_router(auth.router, prefix="/api/v1")
app.include_router(animals.router, prefix="/api/v1")
app.include_router(care_logs.router, prefix="/api/v1")
app.include_router(images.router, prefix="/api/v1")
app.include_router(pdf.router, prefix="/api/v1")
app.include_router(public.router, prefix="/api/v1")  # Public API（認証不要）
app.include_router(public_pages.router)  # Public Pages（HTMLテンプレート）
app.include_router(admin_pages.router)  # Admin Pages（管理画面）
app.include_router(volunteers.router, prefix="/api/v1")

# TODO: 以下のルーターを追加予定
# from app.api.v1 import medical_records, adopters
# app.include_router(medical_records.router, prefix="/api/v1", tags=["Medical Records"])
# app.include_router(adopters.router, prefix="/api/v1", tags=["Adopters"])


if __name__ == "__main__":
    """
    開発用サーバーの起動

    本番環境では uvicorn または gunicorn を使用してください。
    """
    import uvicorn

    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
