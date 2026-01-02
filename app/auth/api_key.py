"""
API Key認証モジュール

Automation API専用のAPI Key認証を提供します。
ユーザー認証（OAuth2）とは完全に分離された固定API Key認証を実装します。

Context7参照: /fastapi/fastapi - APIKeyHeader, Security
Requirements: 1.1, 1.2, 1.3, 1.4, 1.5, 1.6, 1.7
"""

from __future__ import annotations

from typing import Annotated

from fastapi import HTTPException, Security, status
from fastapi.security import APIKeyHeader

from app.config import get_settings

# API Keyヘッダースキーム
# name: HTTPヘッダー名
# auto_error: Falseにすると、キーがない場合にNoneを返す（オプショナル認証用）
automation_api_key_header = APIKeyHeader(
    name="X-Automation-Key",
    description="Automation API用の固定API Key",
    auto_error=False,
)


def get_automation_api_key(
    api_key: Annotated[str | None, Security(automation_api_key_header)],
) -> str:
    """
    Automation API Keyを検証して返す

    環境変数AUTOMATION_API_KEYと照合し、一致する場合のみ認証成功とします。
    認証に失敗した場合は適切なHTTPエラーを返します。

    Context7参照: /fastapi/fastapi - Security dependencies with HTTPException

    Args:
        api_key: X-Automation-Keyヘッダーから取得したAPI Key

    Returns:
        str: 検証済みのAPI Key

    Raises:
        HTTPException:
            - 401 Unauthorized: API Keyが未設定の場合
            - 403 Forbidden: API Keyが無効な場合
            - 503 Service Unavailable: Automation APIが無効な場合

    Example:
        @router.post("/api/automation/care-logs")
        async def create_care_log(
            api_key: str = Depends(get_automation_api_key)
        ):
            # API Key認証済みの処理
            pass
    """
    settings = get_settings()

    # 1. Automation APIが有効かチェック
    if not settings.enable_automation_api:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Automation API is disabled",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 2. API Keyが設定されているかチェック
    if not settings.automation_api_key:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Automation API Key is not configured",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 3. リクエストにAPI Keyが含まれているかチェック
    if api_key is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-Automation-Key header is required",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    # 4. API Keyが一致するかチェック
    if api_key != settings.automation_api_key:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Invalid Automation API Key",
            headers={"WWW-Authenticate": "ApiKey"},
        )

    return api_key


def verify_automation_api_key_optional(
    api_key: Annotated[str | None, Security(automation_api_key_header)],
) -> str | None:
    """
    Automation API Keyをオプショナルで検証

    API Keyが提供された場合のみ検証を行い、提供されていない場合はNoneを返します。
    無効なAPI Keyが提供された場合はエラーを返さず、Noneを返します。

    Context7参照: /fastapi/fastapi - Optional dependencies

    Args:
        api_key: X-Automation-Keyヘッダーから取得したAPI Key

    Returns:
        str | None: 検証済みのAPI Key、または未提供/無効の場合はNone

    Example:
        @router.get("/api/public/animals")
        async def list_animals(
            api_key: str | None = Depends(verify_automation_api_key_optional)
        ):
            # API Key認証はオプショナル
            # api_keyがNoneでない場合は認証済み
            pass
    """
    settings = get_settings()

    # Automation APIが無効な場合はNoneを返す
    if not settings.enable_automation_api:
        return None

    # API Keyが設定されていない場合はNoneを返す
    if not settings.automation_api_key:
        return None

    # リクエストにAPI Keyが含まれていない場合はNoneを返す
    if api_key is None:
        return None

    # API Keyが一致する場合のみ返す
    if api_key == settings.automation_api_key:
        return api_key

    # 無効なAPI Keyの場合はNoneを返す（エラーにしない）
    return None
