"""
言語切り替えAPIエンドポイント

言語設定の取得・変更を提供します。
"""

from __future__ import annotations

from fastapi import APIRouter, Response
from pydantic import BaseModel, Field

router = APIRouter(prefix="/language", tags=["language"])


class LanguageRequest(BaseModel):
    """言語設定リクエスト"""

    language: str = Field(..., description="言語コード", pattern="^(ja|en)$")


class LanguageResponse(BaseModel):
    """言語設定レスポンス"""

    language: str = Field(..., description="現在の言語コード")
    message: str = Field(..., description="メッセージ")


@router.post("/set", response_model=LanguageResponse)
def set_language(
    request: LanguageRequest,
    response: Response,
) -> LanguageResponse:
    """
    言語を設定

    Cookieに言語設定を保存します。

    Args:
        request: 言語設定リクエスト
        response: FastAPIレスポンスオブジェクト

    Returns:
        LanguageResponse: 設定結果

    Example:
        >>> # POST /api/v1/language/set
        >>> # Body: {"language": "en"}
        >>> # Response: {"language": "en", "message": "Language set to English"}
    """
    language = request.language

    # Cookieに言語設定を保存（有効期限: 1年）
    response.set_cookie(
        key="language",
        value=language,
        max_age=365 * 24 * 60 * 60,  # 1年
        httponly=False,  # JavaScriptからアクセス可能
        samesite="lax",
    )

    message = (
        "言語を日本語に設定しました" if language == "ja" else "Language set to English"
    )

    return LanguageResponse(language=language, message=message)


@router.get("/current", response_model=LanguageResponse)
def get_current_language(
    response: Response,
) -> LanguageResponse:
    """
    現在の言語設定を取得

    Cookieから言語設定を取得します。

    Args:
        response: FastAPIレスポンスオブジェクト

    Returns:
        LanguageResponse: 現在の言語設定

    Example:
        >>> # GET /api/v1/language/current
        >>> # Response: {"language": "ja", "message": "Current language is Japanese"}
    """
    # Cookieから言語を取得（デフォルト: ja）
    cookie_header = response.headers.get("Set-Cookie", "")
    language = "en" if "language=en" in cookie_header else "ja"

    message = (
        "現在の言語は日本語です" if language == "ja" else "Current language is English"
    )

    return LanguageResponse(language=language, message=message)
