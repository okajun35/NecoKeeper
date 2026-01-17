"""
認証リダイレクトミドルウェア

401 Unauthorizedエラーをキャッチし、管理画面のログインページにリダイレクトする
共通ミドルウェアです。

Context7参照: /fastapi/fastapi
- Middleware: HTTPリクエスト/レスポンスのインターセプト
- Request/Response処理

設計方針:
- APIリクエスト（/api/v1/で始まるパス）: JSONエラーレスポンスを返す
- ページリクエスト（/adminで始まるパス）: ログインページにリダイレクト
- その他のリクエスト: そのまま処理
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

from fastapi import Request, Response
from fastapi.responses import JSONResponse, RedirectResponse
from starlette.middleware.base import BaseHTTPMiddleware

from app.config import get_settings
from app.utils.path import is_admin_path

settings = get_settings()


class AuthRedirectMiddleware(BaseHTTPMiddleware):
    """
    401エラーを検出してログインページにリダイレクトするミドルウェア

    このミドルウェアは、認証が必要なエンドポイントで401エラーが発生した際に、
    リクエストの種類に応じて適切な処理を行います。

    処理フロー:
    1. /api/v1/で始まるAPIリクエスト -> 401 JSONレスポンス
    2. /adminで始まるページリクエスト -> /admin/loginにリダイレクト
    3. その他 -> そのまま通過

    Example:
        >>> app.add_middleware(AuthRedirectMiddleware)
    """

    async def dispatch(
        self,
        request: Request,
        call_next: Callable[[Request], Awaitable[Response]],
    ) -> Response:
        """
        リクエストを処理し、401エラーをハンドリング

        Args:
            request: FastAPIリクエストオブジェクト
            call_next: 次のミドルウェア/ハンドラー

        Returns:
            Response: レスポンスオブジェクト
                - 401エラー時は適切な処理を実行
                - それ以外はそのまま返す
        """
        # リクエストを次のハンドラーに渡す
        response = await call_next(request)

        # 401エラーの場合のみ処理
        if response.status_code == 401:
            # APIリクエストの場合はJSONレスポンスを返す
            if request.url.path.startswith("/api/v1/"):
                return JSONResponse(
                    status_code=401,
                    content={
                        "detail": "認証が必要です。ログインしてください。",
                    },
                    headers={"WWW-Authenticate": "Bearer"},
                )

            # 管理画面へのリクエストの場合はログインページにリダイレクト
            # ログインページ自体へのアクセスは除外
            admin_login_path = f"{settings.admin_base_path}/login"
            if is_admin_path(request.url.path) and not request.url.path.startswith(
                admin_login_path
            ):
                return RedirectResponse(
                    url=admin_login_path,
                    status_code=302,  # 一時的なリダイレクト
                )

        return response
