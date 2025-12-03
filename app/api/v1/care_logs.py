"""
世話記録APIエンドポイント

世話記録のCRUD操作とCSVエクスポートを提供します。
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Response, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.care_log import CareLog
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
) -> CareLogListResponse:
    """
    世話記録一覧を取得

    ページネーション付きで世話記録の一覧を取得します。
    猫ID、日付範囲、時点でフィルタリングすることも可能です。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）
        animal_id: 猫IDフィルター
        start_date: 開始日フィルター
        end_date: 終了日フィルター
        time_slot: 時点フィルター（morning/noon/evening）

    Returns:
        CareLogListResponse: 世話記録一覧とページネーション情報
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
) -> CareLog:
    """
    世話記録を登録

    新しい世話記録を登録します。
    ボランティアがPublicフォームから入力した記録を保存します。

    Args:
        care_log_data: 世話記録データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        CareLogResponse: 登録された世話記録
    """
    return care_log_service.create_care_log(db=db, care_log_data=care_log_data)


@router.get("/daily-view", response_model=dict)
async def get_daily_view(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    animal_id: int | None = Query(None, description="猫IDフィルター"),
    start_date: date | None = Query(None, description="開始日（デフォルト: 7日前）"),
    end_date: date | None = Query(None, description="終了日（デフォルト: 今日）"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
) -> dict[str, object]:
    """
    日次ビュー形式で世話記録を取得

    1日×1匹を1行で表示する形式で世話記録を取得します。
    朝・昼・夕の記録を横に並べて表示します。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        animal_id: 猫IDフィルター（Noneの場合は全猫）
        start_date: 開始日（デフォルト: 7日前）
        end_date: 終了日（デフォルト: 今日）
        page: ページ番号
        page_size: 1ページあたりの件数

    Returns:
        dict: 日次ビュー形式のデータ
            - items: list[DailyViewRecord]
            - total: int
            - page: int
            - page_size: int
            - total_pages: int
    """
    return care_log_service.get_daily_view(
        db=db,
        animal_id=animal_id,
        start_date=start_date,
        end_date=end_date,
        page=page,
        page_size=page_size,
    )


@router.get("/latest/{animal_id}", response_model=CareLogResponse | None)
async def get_latest_care_log(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> CareLog | None:
    """
    最新の世話記録を取得

    指定された猫の最新の世話記録を取得します。
    前回入力値コピー機能で使用します。

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        CareLogResponse | None: 最新の世話記録（存在しない場合はNone）
    """
    return care_log_service.get_latest_care_log(db=db, animal_id=animal_id)


@router.get("/export", response_class=Response)
async def export_care_logs(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("csv:export"))],
    animal_id: int | None = Query(None, description="猫IDフィルター"),
    start_date: date | None = Query(None, description="開始日フィルター"),
    end_date: date | None = Query(None, description="終了日フィルター"),
) -> Response:
    """
    世話記録をCSVエクスポート

    世話記録をCSV形式でエクスポートします。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー（csv:export権限が必要）
        animal_id: 猫IDフィルター
        start_date: 開始日フィルター
        end_date: 終了日フィルター

    Returns:
        Response: CSV形式の世話記録データ
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
) -> CareLogResponse:
    """
    世話記録の詳細を取得

    指定されたIDの世話記録の詳細情報を取得します。

    Args:
        care_log_id: 世話記録ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        CareLogResponse: 世話記録の詳細情報

    Raises:
        HTTPException: 世話記録が見つからない場合（404）
    """
    return care_log_service.get_care_log(db=db, care_log_id=care_log_id)


@router.put("/{care_log_id}", response_model=CareLogResponse)
async def update_care_log(
    care_log_id: int,
    care_log_data: CareLogUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("care:write"))],
) -> CareLogResponse:
    """
    世話記録を更新

    指定されたIDの世話記録を更新します。

    Args:
        care_log_id: 世話記録ID
        care_log_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（care:write権限が必要）

    Returns:
        CareLogResponse: 更新された世話記録

    Raises:
        HTTPException: 世話記録が見つからない場合（404）
    """
    return care_log_service.update_care_log(
        db=db,
        care_log_id=care_log_id,
        care_log_data=care_log_data,
        user_id=current_user.id,
    )
