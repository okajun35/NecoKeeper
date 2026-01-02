"""
NecoKeeper - FastAPIアプリケーションのエントリーポイント

保護猫管理システムのメインアプリケーションファイル。
FastAPIアプリケーションの初期化、ミドルウェアの設定、ルーターの登録を行います。
"""

from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import (
    HTMLResponse,
    JSONResponse,
    PlainTextResponse,
    RedirectResponse,
)
from fastapi.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api import automation
from app.api.v1 import (
    admin_pages,
    adoptions,
    animals,
    auth,
    care_logs,
    dashboard,
    images,
    language,
    medical_actions,
    medical_records,
    pdf,
    public,
    public_pages,
    reports,
    users,
    volunteers,
)
from app.config import get_settings
from app.middleware.auth_redirect import AuthRedirectMiddleware

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

# 認証リダイレクトミドルウェア（401エラーを共通処理）
app.add_middleware(AuthRedirectMiddleware)


# 静的ファイルのマウント
# メディアファイル（画像など）
if Path(settings.media_dir).exists():
    app.mount(
        "/media",
        StaticFiles(directory=settings.media_dir),
        name="media",
    )

# 静的アセット（CSS、JS、画像など）
if Path("app/static").exists():
    app.mount("/static", StaticFiles(directory="app/static"), name="static")


# ルートエンドポイント - ランディングページ
@app.get("/", response_class=HTMLResponse, tags=["Root"])
def root(request: Request) -> HTMLResponse:
    """
    ルートエンドポイント - 公開ランディングページ

    ハッカソン訪問者向けのプロジェクト紹介ページ。
    認証不要で、プロジェクトの概要、機能、デモを紹介。
    """
    from pathlib import Path

    from fastapi.templating import Jinja2Templates

    templates_dir = Path(__file__).parent / "templates"
    templates = Jinja2Templates(directory=str(templates_dir))

    return templates.TemplateResponse(
        "public/landing.html",
        {
            "request": request,
            "settings": settings,
            "github_url": settings.github_repo_url,
            "demo_video_url": f"https://www.youtube.com/embed/{settings.demo_video_id}",
        },
    )


# ヘルスチェックエンドポイント
@app.get("/health", tags=["Health"])
def health_check() -> dict[str, str]:
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


# robots.txt エンドポイント（検索エンジンクローラー制御）
@app.get("/robots.txt", tags=["SEO"])
def robots_txt() -> PlainTextResponse:
    """
    robots.txt エンドポイント

    ハッカソンデモサイトのため、すべての検索エンジンクローラーを
    ブロックします。本番環境では適切に設定してください。

    Returns:
        PlainTextResponse: robots.txt の内容
    """
    content = """# NecoKeeper - Hackathon Demo Site
# Prevent all search engine crawlers from indexing this site

User-agent: *
Disallow: /
"""
    return PlainTextResponse(content=content, media_type="text/plain")


# PWA Manifest エンドポイント（動的生成）
@app.get("/manifest.json", tags=["PWA"])
def get_manifest() -> dict[str, Any]:
    """
    PWA Manifest を動的に生成

    Kiroween Mode の場合は Halloween アイコンを使用し、
    標準モードの場合は通常のアイコンを使用します。

    Returns:
        dict: PWA Manifest JSON
    """
    # アイコンのベースパスを決定
    if settings.kiroween_mode:
        # Kiroween Mode: Halloween アイコンを使用
        icon_base = "/static/icons/halloween_icon.webp"
        app_name = "Necro-Terminal"
        short_name = "Necro-Terminal"
        description = "Ghost in the Machine - 保護猫管理システム"
        theme_color = "#000000"
        background_color = "#000000"
    else:
        # 標準モード: 通常のアイコンを使用
        icon_base = "/static/icons/icon"
        app_name = "NecoKeeper - 保護猫管理システム"
        short_name = "NecoKeeper"
        description = "保護猫の世話記録を簡単に入力できるアプリ"
        theme_color = "#4f46e5"
        background_color = "#ffffff"

    # アイコン配列を生成
    if settings.kiroween_mode:
        # Halloween アイコンは単一ファイル（WebP）
        icons = [
            {
                "src": icon_base,
                "sizes": "512x512",
                "type": "image/webp",
                "purpose": "any maskable",
            }
        ]
    else:
        # 標準アイコンは複数サイズ（PNG）
        icons = [
            {
                "src": f"{icon_base}-72x72.png",
                "sizes": "72x72",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-96x96.png",
                "sizes": "96x96",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-128x128.png",
                "sizes": "128x128",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-144x144.png",
                "sizes": "144x144",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-152x152.png",
                "sizes": "152x152",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-192x192.png",
                "sizes": "192x192",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-384x384.png",
                "sizes": "384x384",
                "type": "image/png",
                "purpose": "any maskable",
            },
            {
                "src": f"{icon_base}-512x512.png",
                "sizes": "512x512",
                "type": "image/png",
                "purpose": "any maskable",
            },
        ]

    return {
        "name": app_name,
        "short_name": short_name,
        "description": description,
        "start_url": "/public/care-form",
        "display": "standalone",
        "background_color": background_color,
        "theme_color": theme_color,
        "orientation": "portrait",
        "icons": icons,
        "categories": ["productivity", "utilities"],
        "lang": "ja",
        "dir": "ltr",
    }


# HTTPException用のカスタムハンドラー
@app.exception_handler(StarletteHTTPException)
def http_exception_handler(
    request: Request, exc: StarletteHTTPException
) -> JSONResponse | RedirectResponse:
    """
    HTTPException用のカスタムハンドラー

    管理画面の401エラーはログインページにリダイレクト。
    APIエンドポイントはJSONエラーを返す。

    Context7参照: /fastapi/fastapi - Custom Exception Handlers

    Args:
        request: FastAPIリクエストオブジェクト
        exc: HTTPException

    Returns:
        RedirectResponse | JSONResponse: リダイレクトまたはJSONエラー
    """
    # 管理画面の401エラーはログインページにリダイレクト
    # ログインページ自体への401はリダイレクトしない（無限ループ防止）
    if (
        exc.status_code == 401
        and request.url.path.startswith("/admin")
        and not request.url.path.startswith("/admin/login")
    ):
        return RedirectResponse(url="/admin/login", status_code=302)

    # APIエンドポイントはJSONエラーを返す
    return JSONResponse(
        status_code=exc.status_code,
        content={"detail": exc.detail},
        headers=exc.headers if hasattr(exc, "headers") else None,
    )


# グローバル例外ハンドラー
@app.exception_handler(Exception)
def global_exception_handler(request, exc: Exception) -> JSONResponse:  # type: ignore[no-untyped-def]
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
# Automation API（API Key認証）
app.include_router(automation.router, prefix="/api")

# User-Facing API（OAuth2認証）
app.include_router(auth.router, prefix="/api/v1")
app.include_router(animals.router, prefix="/api/v1")
app.include_router(care_logs.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")  # ダッシュボードAPI
app.include_router(images.router, prefix="/api/v1")
app.include_router(language.router, prefix="/api/v1")  # 言語切り替えAPI
app.include_router(medical_actions.router, prefix="/api/v1")
app.include_router(medical_records.router, prefix="/api/v1")
app.include_router(pdf.router, prefix="/api/v1")
app.include_router(reports.router, prefix="/api/v1")  # 帳票出力API
app.include_router(public.router, prefix="/api/v1")  # Public API（認証不要）
app.include_router(public_pages.router)  # Public Pages（HTMLテンプレート）
app.include_router(admin_pages.router)  # Admin Pages（管理画面）
app.include_router(users.router, prefix="/api/v1")
app.include_router(volunteers.router, prefix="/api/v1")
app.include_router(adoptions.router, prefix="/api/v1")  # 里親管理API


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
