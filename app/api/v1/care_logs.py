"""
世話記録APIエンドポイント

世話記録のCRUD操作とCSVエクスポートを提供します。
"""

from datetime import date
from typing import Annotated, Optional

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.user import User
from app.schemas.care_log import (
    CareLogCreate,
    CareLogListResponse,
    CareLogResponse,
    CareLogUpdate,
)
from app.services import care_log_service

router = APIRouter(prefix="/care-logs", tags=["世話記録"])


@router.get("", response_model=CareLogListResponse)
async def list_care_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    animal_id: int | None = Query(None, description="猫IDフィルター"),
    start_date: date | None = Query(None, description="開始日フィルター"),
    end_date: date | None = Query(None, description="終了日フィルター"),
    time_slot: str | None = Query(None, description="時点フィルター"),
):
    """
    世話記録一覧を取得

    ページネーション付きで世話記録の一覧を取得します。
    猫ID、日付範囲、時点でフィルタリングすることも可能です。
    """
    return care_log_service.list_care_logs(
        db=db,
        page=page,
        page_size=page_size,
        animal_id=animal_id,
        start_date=start_date,
        end_date=end_date,
        time_slot=time_slot,
    )


@router.post("", response_model=CareLogResponse, status_code=status.HTTP_201_CREATED)
async def create_care_log(
    care_log_data: CareLogCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    世話記録を登録

    新しい世話記録を登録します。
    """
    return care_log_service.create_care_log(db=db, care_log_data=care_log_data)


@router.get("/latest/{animal_id}", response_model=Optional[CareLogResponse])
async def get_latest_care_log(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    最新の世話記録を取得

    指定された猫の最新の世話記録を取得します。
    前回入力値コピー機能で使用します。
    """
    return care_log_service.get_latest_care_log(db=db, animal_id=animal_id)


@router.get("/export", response_class=Response)
async def export_care_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("csv:export"))],
    animal_id: int | None = Query(None, description="猫IDフィルター"),
    start_date: date | None = Query(None, description="開始日フィルター"),
    end_date: date | None = Query(None, description="終了日フィルター"),
):
    """
    世話記録をCSVエクスポート

    世話記録をCSV形式でエクスポートします。
    """
    csv_content = care_log_service.export_care_logs_csv(
        db=db, animal_id=animal_id, start_date=start_date, end_date=end_date
    )

    return Response(
        content=csv_content,
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=care_logs.csv"},
    )


@router.get("/{care_log_id}", response_model=CareLogResponse)
async def get_care_log(
    care_log_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    世話記録の詳細を取得

    指定されたIDの世話記録の詳細情報を取得します。
    """
    return care_log_service.get_care_log(db=db, care_log_id=care_log_id)


@router.put("/{care_log_id}", response_model=CareLogResponse)
async def update_care_log(
    care_log_id: int,
    care_log_data: CareLogUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("care:write"))],
):
    """
    世話記録を更新

    指定されたIDの世話記録を更新します。
    """
    return care_log_service.update_care_log(
        db=db,
        care_log_id=care_log_id,
        care_log_data=care_log_data,
        user_id=current_user.id,
    )
