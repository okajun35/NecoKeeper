"""
診療記録API

診療記録のCRUD操作を提供するAPIエンドポイント。
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.medical_record import MedicalRecord
from app.models.user import User
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordListResponse,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)
from app.services import medical_record_service

router = APIRouter(prefix="/medical-records", tags=["診療記録"])


@router.get("", response_model=MedicalRecordListResponse)
async def list_medical_records(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    animal_id: Annotated[int | None, Query()] = None,
    vet_id: Annotated[int | None, Query()] = None,
    start_date: Annotated[date | None, Query()] = None,
    end_date: Annotated[date | None, Query()] = None,
) -> MedicalRecordListResponse:
    """
    診療記録一覧を取得

    時系列で降順に表示します。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（デフォルト: 1）
        page_size: 1ページあたりの件数（デフォルト: 20、最大: 100）
        animal_id: 猫IDフィルター（任意）
        vet_id: 獣医師IDフィルター（任意）
        start_date: 開始日フィルター（任意）
        end_date: 終了日フィルター（任意）

    Returns:
        MedicalRecordListResponse: 診療記録一覧とページネーション情報
    """
    return medical_record_service.list_medical_records(
        db=db,
        page=page,
        page_size=page_size,
        animal_id=animal_id,
        vet_id=vet_id,
        start_date=start_date,
        end_date=end_date,
    )


@router.post(
    "", response_model=MedicalRecordResponse, status_code=status.HTTP_201_CREATED
)
async def create_medical_record(
    medical_record_data: MedicalRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> MedicalRecord:
    """
    診療記録を登録

    獣医師または管理者が診療記録を登録します。

    Args:
        medical_record_data: 診療記録データ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        MedicalRecordResponse: 登録された診療記録
    """
    return medical_record_service.create_medical_record(
        db=db, medical_record_data=medical_record_data
    )


@router.get("/{medical_record_id}", response_model=MedicalRecordResponse)
async def get_medical_record(
    medical_record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> MedicalRecord:
    """
    診療記録の詳細を取得

    Args:
        medical_record_id: 診療記録ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        MedicalRecordResponse: 診療記録

    Raises:
        HTTPException: 診療記録が見つからない場合（404）
    """
    return medical_record_service.get_medical_record(
        db=db, medical_record_id=medical_record_id
    )


@router.put("/{medical_record_id}", response_model=MedicalRecordResponse)
async def update_medical_record(
    medical_record_id: int,
    medical_record_data: MedicalRecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> MedicalRecord:
    """
    診療記録を更新

    Args:
        medical_record_id: 診療記録ID
        medical_record_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        MedicalRecordResponse: 更新された診療記録

    Raises:
        HTTPException: 診療記録が見つからない場合（404）
    """
    return medical_record_service.update_medical_record(
        db=db,
        medical_record_id=medical_record_id,
        medical_record_data=medical_record_data,
        user_id=current_user.id,
    )
