"""
Automation APIルーター

Kiro Hook、MCP、自動化スクリプト専用のAPIエンドポイントを提供します。
ユーザー認証（OAuth2）とは完全に分離された固定API Key認証を採用します。

Context7参照: /fastapi/fastapi - APIRouter with dependencies
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, status

from app.api.automation import animals, care_logs, pdf
from app.auth.api_key import get_automation_api_key

# Automation APIルーター
# すべてのエンドポイントに共通の設定を適用
router = APIRouter(
    prefix="/automation",
    tags=["automation"],
    dependencies=[Depends(get_automation_api_key)],  # 全エンドポイントでAPI Key認証
    responses={
        status.HTTP_401_UNAUTHORIZED: {
            "description": "Unauthorized - API Key is missing",
            "content": {
                "application/json": {
                    "example": {"detail": "X-Automation-Key header is required"}
                }
            },
            "headers": {
                "WWW-Authenticate": {
                    "description": "Authentication scheme",
                    "schema": {"type": "string", "example": "ApiKey"},
                }
            },
        },
        status.HTTP_403_FORBIDDEN: {
            "description": "Forbidden - Invalid API Key",
            "content": {
                "application/json": {
                    "example": {"detail": "Invalid Automation API Key"}
                }
            },
            "headers": {
                "WWW-Authenticate": {
                    "description": "Authentication scheme",
                    "schema": {"type": "string", "example": "ApiKey"},
                }
            },
        },
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "description": "Service Unavailable - Automation API is disabled",
            "content": {
                "application/json": {
                    "examples": {
                        "disabled": {
                            "summary": "API Disabled",
                            "value": {"detail": "Automation API is disabled"},
                        },
                        "not_configured": {
                            "summary": "Not Configured",
                            "value": {
                                "detail": ("Automation API Key is not configured")
                            },
                        },
                    }
                }
            },
            "headers": {
                "WWW-Authenticate": {
                    "description": "Authentication scheme",
                    "schema": {"type": "string", "example": "ApiKey"},
                }
            },
        },
    },
)


# サブルーターを登録
router.include_router(animals.router)
router.include_router(care_logs.router)
router.include_router(pdf.router)


# テスト用エンドポイント（開発時のみ）
# 実際のエンドポイントは別ファイル（care_logs.py, animals.py）で定義
@router.get("/test", include_in_schema=False)
async def test_endpoint() -> dict[str, str]:
    """
    テスト用エンドポイント

    ルーター設定とAPI Key認証が正しく動作することを確認するための
    テストエンドポイントです。本番環境では使用しません。

    Returns:
        dict[str, str]: テストメッセージ
    """
    return {"message": "Automation API is working"}


# ルーターのメタデータ
__all__ = ["router"]
