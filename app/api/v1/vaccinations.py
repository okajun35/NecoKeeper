"""
ワクチン接種記録API（Issue #83）

ワクチン接種記録のCRUD操作を提供するAPIエンドポイント。
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.user import User
from app.models.vaccination_record import VaccinationRecord
from app.schemas.vaccination_record import (
    VaccinationRecordCreate,
    VaccinationRecordResponse,
    VaccinationRecordUpdate,
)
from app.services import vaccination_service

router = APIRouter(prefix="/vaccinations", tags=["ワクチン接種記録"])


@router.get("/animal/{animal_id}", response_model=list[VaccinationRecordResponse])
def list_vaccination_records_by_animal(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> list[VaccinationRecord]:
    """
    動物のワクチン接種記録一覧を取得

    指定した動物のワクチン接種記録を接種日の降順で取得します。

    Args:
        animal_id: 動物ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        list[VaccinationRecordResponse]: ワクチン接種記録一覧
    """
    return vaccination_service.list_vaccination_records_by_animal(
        db=db, animal_id=animal_id
    )


@router.post(
    "", response_model=VaccinationRecordResponse, status_code=status.HTTP_201_CREATED
)
def create_vaccination_record(
    vaccination_data: VaccinationRecordCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> VaccinationRecord:
    """
    ワクチン接種記録を登録

    Args:
        vaccination_data: ワクチン接種記録データ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        VaccinationRecordResponse: 登録されたワクチン接種記録
    """
    return vaccination_service.create_vaccination_record(
        db=db, vaccination_data=vaccination_data
    )


@router.get("/{record_id}", response_model=VaccinationRecordResponse)
def get_vaccination_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> VaccinationRecord:
    """
    ワクチン接種記録を取得

    Args:
        record_id: ワクチン接種記録ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        VaccinationRecordResponse: ワクチン接種記録
    """
    return vaccination_service.get_vaccination_record(db=db, record_id=record_id)


@router.put("/{record_id}", response_model=VaccinationRecordResponse)
def update_vaccination_record(
    record_id: int,
    update_data: VaccinationRecordUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> VaccinationRecord:
    """
    ワクチン接種記録を更新

    Args:
        record_id: ワクチン接種記録ID
        update_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        VaccinationRecordResponse: 更新されたワクチン接種記録
    """
    return vaccination_service.update_vaccination_record(
        db=db, record_id=record_id, update_data=update_data
    )


@router.delete("/{record_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_vaccination_record(
    record_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> None:
    """
    ワクチン接種記録を削除

    Args:
        record_id: ワクチン接種記録ID
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）
    """
    vaccination_service.delete_vaccination_record(db=db, record_id=record_id)
