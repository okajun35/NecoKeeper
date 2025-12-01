"""
PDF生成Automation API

Kiro Hook、MCP、自動化スクリプト専用のPDF生成エンドポイントを提供します。

Context7参照: /fastapi/fastapi - APIRouter, HTTPException
Requirements: 2.2
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.database import get_db
from app.services import pdf_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/pdf/qr-card",
    summary="単一QRカードPDFを生成（Automation API）",
    description="""
    単一QRカードPDFを生成します（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    QRカードPDF生成に使用されます。API Key認証が必要です。

    1匹の猫のQRカードをA6サイズのPDFで生成します。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **Requirements**: 2.2
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "PDFが正常に生成されました",
            "content": {"application/pdf": {"example": "PDF binary data"}},
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "指定された猫が存在しません",
            "content": {
                "application/json": {"example": {"detail": "猫ID 999 が見つかりません"}}
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "サーバーエラーが発生しました",
            "content": {
                "application/json": {"example": {"detail": "PDF生成に失敗しました"}}
            },
        },
    },
)
async def generate_qr_card_automation(
    request: QRCardRequest,
    db: Session = Depends(get_db),
) -> Response:
    """
    単一QRカードPDFを生成（Automation API）

    Args:
        request: QRカード生成リクエスト
        db: データベースセッション

    Returns:
        Response: 生成されたPDF（application/pdf）

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    try:
        pdf_bytes = pdf_service.generate_qr_card_pdf(
            db=db,
            animal_id=request.animal_id,
            base_url=request.base_url,
            locale=request.locale,
        )

        logger.info(
            f"Automation API: 単一QRカードPDFを生成しました - "
            f"animal_id={request.animal_id}"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=qr_card_{request.animal_id}.pdf"
            },
        )
    except ValueError as e:
        logger.warning(
            f"Automation API: QRカード生成失敗（猫が見つからない） - "
            f"animal_id={request.animal_id}, error={e}"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(
            f"Automation API: QRカード生成失敗 - "
            f"animal_id={request.animal_id}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF生成に失敗しました",
        ) from e


class QRCardRequest(BaseModel):
    """単一QRカード生成リクエスト"""

    animal_id: int = Field(..., description="猫のID", gt=0)
    base_url: str | None = Field(None, description="ベースURL（省略時は設定から取得）")
    locale: str = Field("ja", description="ロケール（ja/en）")


class QRCardGridRequest(BaseModel):
    """面付けQRカード生成リクエスト"""

    animal_ids: list[int] = Field(
        ...,
        description="猫のIDリスト（最大10個）",
        min_length=1,
        max_length=10,
    )
    base_url: str | None = Field(None, description="ベースURL（省略時は設定から取得）")


@router.post(
    "/pdf/qr-card-grid",
    summary="面付けQRカードPDFを生成（Automation API）",
    description="""
    面付けQRカードPDFを生成します（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    QRカードPDF生成に使用されます。API Key認証が必要です。

    複数の猫のQRカードを1枚のA4用紙に2×5枚（最大10枚）配置したPDFを生成します。
    印刷してカットすることで、複数の猫のQRカードを一度に作成できます。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **Requirements**: 2.2
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "PDFが正常に生成されました",
            "content": {"application/pdf": {"example": "PDF binary data"}},
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "リクエストデータが不正です",
            "content": {
                "application/json": {
                    "example": {"detail": "一度に生成できるQRカードは最大10枚です"}
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "指定された猫が存在しません",
            "content": {
                "application/json": {"example": {"detail": "猫ID 999 が見つかりません"}}
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "サーバーエラーが発生しました",
            "content": {
                "application/json": {"example": {"detail": "PDF生成に失敗しました"}}
            },
        },
    },
)
async def generate_qr_card_grid_automation(
    request: QRCardGridRequest,
    db: Session = Depends(get_db),
) -> Response:
    """
    面付けQRカードPDFを生成（Automation API）

    Args:
        request: 面付けQRカード生成リクエスト
        db: データベースセッション

    Returns:
        Response: 生成されたPDF（application/pdf）

    Raises:
        HTTPException: 猫が見つからない場合（404）、またはIDが10個を超える場合（400）
    """
    try:
        pdf_bytes = pdf_service.generate_qr_card_grid_pdf(
            db=db,
            animal_ids=request.animal_ids,
            base_url=request.base_url,
        )

        logger.info(
            f"Automation API: QRカードPDFを生成しました - "
            f"animal_ids={request.animal_ids}"
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": "attachment; filename=qr_card_grid.pdf"},
        )
    except ValueError as e:
        if "10枚" in str(e):
            logger.warning(
                f"Automation API: QRカード生成失敗（枚数超過） - "
                f"animal_ids={request.animal_ids}"
            )
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
        logger.warning(
            f"Automation API: QRカード生成失敗（猫が見つからない） - "
            f"animal_ids={request.animal_ids}, error={e}"
        )
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e
    except Exception as e:
        logger.error(
            f"Automation API: QRカード生成失敗 - "
            f"animal_ids={request.animal_ids}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="PDF生成に失敗しました",
        ) from e
