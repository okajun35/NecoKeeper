"""
PDF生成APIエンドポイント

QRカード、紙記録フォーム、診療明細、帳票のPDF生成エンドポイントを提供します。

Requirements: Requirement 2, Requirement 7, Requirement 9
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.config import settings
from app.database import get_db
from app.models.user import User
from app.services import pdf_service

router = APIRouter(prefix="/pdf", tags=["PDF生成"])


class QRCardRequest(BaseModel):
    """QRカード生成リクエスト"""

    animal_id: int = Field(..., description="猫のID")
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
    locale: str = Field("ja", description="ロケール（ja/en）")


class PaperFormRequest(BaseModel):
    """紙記録フォーム生成リクエスト"""

    animal_id: int = Field(..., description="猫のID")
    year: int = Field(..., description="年", ge=2000, le=2100)
    month: int = Field(..., description="月", ge=1, le=12)


class MedicalDetailRequest(BaseModel):
    """診療明細生成リクエスト"""

    medical_record_id: int = Field(..., description="診療記録ID")


class ReportRequest(BaseModel):
    """帳票生成リクエスト"""

    report_type: str = Field(
        ..., description="帳票種別（daily/weekly/monthly/individual/medical_summary）"
    )
    start_date: date = Field(..., description="開始日")
    end_date: date = Field(..., description="終了日")
    animal_id: int | None = Field(None, description="猫のID（個別帳票の場合のみ）")
    locale: str = Field("ja", description="ロケール（ja/en）")


@router.post("/qr-card")
def generate_qr_card(
    request: QRCardRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:read"))],
) -> Response:
    """
    QRカードPDFを生成（A6サイズ）

    猫の顔写真、名前、ID、QRコードを含むA6サイズのPDFを生成します。
    QRコードをスキャンすると、その猫のPublic記録入力フォームにアクセスできます。

    Args:
        request: QRカード生成リクエスト
        db: データベースセッション
        current_user: 現在のユーザー（animal:read権限が必要）

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

        filename = (
            f"necro_tag_{request.animal_id}.pdf"
            if settings.kiroween_mode
            else f"qr_card_{request.animal_id}.pdf"
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/qr-card-grid")
def generate_qr_card_grid(
    request: QRCardGridRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:read"))],
) -> Response:
    """
    面付けQRカードPDFを生成（A4サイズ、2×5枚）

    複数の猫のQRカードを1枚のA4用紙に2×5枚（最大10枚）配置したPDFを生成します。
    印刷してカットすることで、複数の猫のQRカードを一度に作成できます。

    Args:
        request: 面付けQRカード生成リクエスト
        db: データベースセッション
        current_user: 現在のユーザー（animal:read権限が必要）

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
            locale=request.locale,
        )

        filename = (
            "necro_tags_grid.pdf" if settings.kiroween_mode else "qr_card_grid.pdf"
        )
        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={"Content-Disposition": f"attachment; filename={filename}"},
        )
    except ValueError as e:
        if "10枚" in str(e):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
            ) from e
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/paper-form")
def generate_paper_form(
    request: PaperFormRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:read"))],
) -> Response:
    """
    紙記録フォームPDFを生成（A4サイズ、1ヶ月分）

    指定された猫の1ヶ月分の世話記録用紙をA4サイズのPDFで生成します。
    日付欄と記録欄（時点、食欲、元気、排尿、清掃、メモ）が含まれます。

    Args:
        request: 紙記録フォーム生成リクエスト
        db: データベースセッション
        current_user: 現在のユーザー（animal:read権限が必要）

    Returns:
        Response: 生成されたPDF（application/pdf）

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    try:
        pdf_bytes = pdf_service.generate_paper_form_pdf(
            db=db,
            animal_id=request.animal_id,
            year=request.year,
            month=request.month,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=paper_form_{request.animal_id}_{request.year}{request.month:02d}.pdf"
            },
        )
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/medical-detail")
def generate_medical_detail(
    request: MedicalDetailRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:read"))],
) -> Response:
    """
    診療明細PDFを生成（A4縦サイズ）

    指定された診療記録の明細をA4縦サイズのPDFで生成します。
    猫の顔写真、診療日、体重、体温、症状、薬品名、投薬量などが含まれます。

    Args:
        request: 診療明細生成リクエスト
        db: データベースセッション
        current_user: 現在のユーザー（medical:read権限が必要）

    Returns:
        Response: 生成されたPDF（application/pdf）

    Raises:
        HTTPException: 診療記録が見つからない場合（404）、または未実装の場合（501）
    """
    try:
        pdf_bytes = pdf_service.generate_medical_detail_pdf(
            db=db,
            medical_record_id=request.medical_record_id,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=medical_detail_{request.medical_record_id}.pdf"
            },
        )
    except NotImplementedError as e:
        raise HTTPException(
            status_code=status.HTTP_501_NOT_IMPLEMENTED, detail=str(e)
        ) from e
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e)) from e


@router.post("/report")
def generate_report(
    request: ReportRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("report:read"))],
) -> Response:
    """
    帳票PDFを生成（日報・週報・月次集計）

    指定された期間の世話記録集計や医療費集計をPDFで生成します。
    帳票種別により、日報、週報、月次集計のいずれかを生成します。

    Args:
        request: 帳票生成リクエスト
        db: データベースセッション
        current_user: 現在のユーザー（report:read権限が必要）

    Returns:
        Response: 生成されたPDF（application/pdf）

    Raises:
        HTTPException: 不正な帳票種別の場合（400）、または未実装の場合（501）
    """
    try:
        pdf_bytes = pdf_service.generate_report_pdf(
            db=db,
            report_type=request.report_type,
            start_date=request.start_date,
            end_date=request.end_date,
            animal_id=request.animal_id,
            locale=request.locale,
        )

        return Response(
            content=pdf_bytes,
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename=report_{request.report_type}_{request.start_date}_{request.end_date}.pdf"
            },
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
