"""
帳票出力APIエンドポイント

CSV/Excel形式での帳票出力エンドポイントを提供します。

Requirements: Requirement 9.1-9.8, Requirement 25.2-25.3
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Response, status
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.auth.permissions import require_permission
from app.database import get_db
from app.models.user import User
from app.services import csv_service, excel_service

router = APIRouter(prefix="/reports", tags=["帳票出力"])


class ReportExportRequest(BaseModel):
    """帳票エクスポートリクエスト"""

    report_type: str = Field(
        ..., description="帳票種別（daily/weekly/monthly/individual）"
    )
    start_date: date = Field(..., description="開始日")
    end_date: date = Field(..., description="終了日")
    animal_id: int | None = Field(None, description="猫のID（個別帳票の場合のみ）")
    format: str = Field(..., description="出力形式（csv/excel）")
    locale: str = Field("ja", description="ロケール（ja/en）")


@router.post("/export")
async def export_report(
    request: ReportExportRequest,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("report:read"))],
) -> Response:
    """
    帳票をエクスポート（CSV/Excel）

    指定された期間の世話記録集計をCSVまたはExcel形式でエクスポートします。

    Args:
        request: 帳票エクスポートリクエスト
        db: データベースセッション
        current_user: 現在のユーザー（report:read権限が必要）

    Returns:
        Response: 生成されたCSVまたはExcel

    Raises:
        HTTPException: 不正な帳票種別の場合（400）、または未実装の場合（501）
    """
    try:
        if request.format == "csv":
            # CSV出力
            csv_data = csv_service.generate_report_csv(
                db=db,
                report_type=request.report_type,
                start_date=request.start_date,
                end_date=request.end_date,
                animal_id=request.animal_id,
                locale=request.locale,
            )

            return Response(
                content=csv_data.encode("utf-8-sig"),
                media_type="text/csv; charset=utf-8-sig",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{request.report_type}_{request.start_date}_{request.end_date}.csv"
                },
            )
        elif request.format == "excel":
            # Excel出力
            excel_data = excel_service.generate_report_excel(
                db=db,
                report_type=request.report_type,
                start_date=request.start_date,
                end_date=request.end_date,
                animal_id=request.animal_id,
                locale=request.locale,
            )

            return Response(
                content=excel_data,
                media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                headers={
                    "Content-Disposition": f"attachment; filename=report_{request.report_type}_{request.start_date}_{request.end_date}.xlsx"
                },
            )
        else:
            raise ValueError(f"不正な出力形式です: {request.format}")

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
        ) from e
