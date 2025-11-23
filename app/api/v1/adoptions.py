"""
里親管理APIエンドポイント

里親希望者と譲渡記録のCRUD操作を提供します。
"""

from __future__ import annotations

from datetime import date

from fastapi import APIRouter, Depends, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_user_from_cookie_or_header
from app.database import get_db
from app.models.user import User
from app.schemas.adoption import (
    AdoptionRecordCreate,
    AdoptionRecordResponse,
    AdoptionRecordUpdate,
    ApplicantCreate,
    ApplicantResponse,
    ApplicantUpdate,
)
from app.services import adoption_service

router = APIRouter(prefix="/adoptions", tags=["adoptions"])


# ========================================
# Applicant（里親希望者）エンドポイント
# ========================================


@router.get("/applicants", response_model=list[ApplicantResponse])
async def list_applicants(  # type: ignore[no-untyped-def]
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者一覧を取得

    Args:
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        list[ApplicantResponse]: 里親希望者のリスト
    """
    applicants = adoption_service.list_applicants(db, skip=skip, limit=limit)
    return applicants


@router.post(
    "/applicants",
    response_model=ApplicantResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_applicant(  # type: ignore[no-untyped-def]
    applicant_data: ApplicantCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を登録

    Args:
        applicant_data: 里親希望者データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponse: 登録された里親希望者
    """
    applicant = adoption_service.create_applicant(
        db, applicant_data, user_id=current_user.id
    )
    return applicant


@router.get("/applicants/{applicant_id}", response_model=ApplicantResponse)
async def get_applicant(  # type: ignore[no-untyped-def]
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を取得

    Args:
        applicant_id: 里親希望者ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponse: 里親希望者
    """
    applicant = adoption_service.get_applicant(db, applicant_id)
    return applicant


@router.put("/applicants/{applicant_id}", response_model=ApplicantResponse)
async def update_applicant(  # type: ignore[no-untyped-def]
    applicant_id: int,
    applicant_data: ApplicantUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を更新

    Args:
        applicant_id: 里親希望者ID
        applicant_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponse: 更新された里親希望者
    """
    applicant = adoption_service.update_applicant(
        db, applicant_id, applicant_data, user_id=current_user.id
    )
    return applicant


# ========================================
# AdoptionRecord（譲渡記録）エンドポイント
# ========================================


@router.get("/records", response_model=list[AdoptionRecordResponse])
async def list_adoption_records(  # type: ignore[no-untyped-def]
    animal_id: int | None = None,
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    譲渡記録一覧を取得

    Args:
        animal_id: 猫ID（指定時は特定の猫の記録のみ取得）
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        list[AdoptionRecordResponse]: 譲渡記録のリスト
    """
    records = adoption_service.list_adoption_records(
        db, animal_id=animal_id, skip=skip, limit=limit
    )
    return records


@router.post(
    "/records",
    response_model=AdoptionRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_interview_record(  # type: ignore[no-untyped-def]
    record_data: AdoptionRecordCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    面談記録を登録

    Args:
        record_data: 面談記録データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AdoptionRecordResponse: 登録された面談記録
    """
    record = adoption_service.create_interview_record(
        db, record_data, user_id=current_user.id
    )
    return record


@router.post(
    "/records/adopt",
    response_model=AdoptionRecordResponse,
    status_code=status.HTTP_201_CREATED,
)
async def create_adoption(  # type: ignore[no-untyped-def]
    animal_id: int,
    applicant_id: int,
    adoption_date: date,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    譲渡記録を登録し、猫のステータスを「譲渡済み」に更新

    Args:
        animal_id: 猫ID
        applicant_id: 里親希望者ID
        adoption_date: 譲渡日
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AdoptionRecordResponse: 登録された譲渡記録
    """
    record = adoption_service.create_adoption_record(
        db, animal_id, applicant_id, adoption_date, user_id=current_user.id
    )
    return record


@router.get("/records/{record_id}", response_model=AdoptionRecordResponse)
async def get_adoption_record(  # type: ignore[no-untyped-def]
    record_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    譲渡記録を取得

    Args:
        record_id: 譲渡記録ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AdoptionRecordResponse: 譲渡記録
    """
    record = adoption_service.get_adoption_record(db, record_id)
    return record


@router.put("/records/{record_id}", response_model=AdoptionRecordResponse)
async def update_adoption_record(  # type: ignore[no-untyped-def]
    record_id: int,
    record_data: AdoptionRecordUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    譲渡記録を更新

    Args:
        record_id: 譲渡記録ID
        record_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AdoptionRecordResponse: 更新された譲渡記録
    """
    record = adoption_service.update_adoption_record(
        db, record_id, record_data, user_id=current_user.id
    )
    return record
