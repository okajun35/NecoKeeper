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
    ApplicantCreateExtended,
    ApplicantHouseholdMemberCreate,
    ApplicantHouseholdMemberResponse,
    ApplicantPetCreate,
    ApplicantPetResponse,
    ApplicantResponseExtended,
    ApplicantUpdateExtended,
)
from app.services import adoption_service

router = APIRouter(prefix="/adoptions", tags=["adoptions"])


# ========================================
# Applicant Extended（拡張版里親希望者）エンドポイント
# Issue #91: 詳細な申込情報の管理用
# ========================================


@router.get(
    "/applicants-extended",
    response_model=list[ApplicantResponseExtended],
)
def list_applicants_extended(  # type: ignore[no-untyped-def]
    skip: int = 0,
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者一覧を取得（拡張版・家族構成・ペット情報含む）

    Args:
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        list[ApplicantResponseExtended]: 里親希望者のリスト（詳細情報付き）
    """
    applicants = adoption_service.list_applicants_extended(db, skip=skip, limit=limit)
    return applicants


@router.post(
    "/applicants-extended",
    response_model=ApplicantResponseExtended,
    status_code=status.HTTP_201_CREATED,
)
def create_applicant_extended(  # type: ignore[no-untyped-def]
    applicant_data: ApplicantCreateExtended,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を登録（拡張版・詳細情報付き）

    連絡先（LINE/メール）、住居情報、家族構成、先住ペット等の
    詳細情報を含めて登録します。

    Args:
        applicant_data: 里親希望者データ（拡張版）
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponseExtended: 登録された里親希望者（詳細情報付き）
    """
    applicant = adoption_service.create_applicant_extended(
        db, applicant_data, user_id=current_user.id
    )
    return applicant


@router.get(
    "/applicants-extended/{applicant_id}",
    response_model=ApplicantResponseExtended,
)
def get_applicant_extended(  # type: ignore[no-untyped-def]
    applicant_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を取得（拡張版・家族構成・ペット情報含む）

    Args:
        applicant_id: 里親希望者ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponseExtended: 里親希望者（詳細情報付き）
    """
    applicant = adoption_service.get_applicant_extended(db, applicant_id)
    return applicant


@router.put(
    "/applicants-extended/{applicant_id}",
    response_model=ApplicantResponseExtended,
)
def update_applicant_extended(  # type: ignore[no-untyped-def]
    applicant_id: int,
    applicant_data: ApplicantUpdateExtended,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    里親希望者を更新（拡張版）

    Args:
        applicant_id: 里親希望者ID
        applicant_data: 更新データ（拡張版）
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantResponseExtended: 更新された里親希望者（詳細情報付き）
    """
    applicant = adoption_service.update_applicant_extended(
        db, applicant_id, applicant_data, user_id=current_user.id
    )
    return applicant


# ========================================
# Household Member（家族構成）エンドポイント
# ========================================


@router.post(
    "/applicants-extended/{applicant_id}/household-members",
    response_model=ApplicantHouseholdMemberResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_household_member(  # type: ignore[no-untyped-def]
    applicant_id: int,
    member_data: ApplicantHouseholdMemberCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    家族メンバーを追加

    Args:
        applicant_id: 里親希望者ID
        member_data: 家族メンバーデータ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantHouseholdMemberResponse: 追加された家族メンバー
    """
    member = adoption_service.add_household_member(
        db, applicant_id, member_data, user_id=current_user.id
    )
    return member


@router.delete(
    "/applicants-extended/{applicant_id}/household-members/{member_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_household_member(  # type: ignore[no-untyped-def]
    applicant_id: int,
    member_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    家族メンバーを削除

    Args:
        applicant_id: 里親希望者ID
        member_id: 家族メンバーID
        db: データベースセッション
        current_user: 現在のユーザー
    """
    adoption_service.delete_household_member(
        db, applicant_id, member_id, user_id=current_user.id
    )


# ========================================
# Pet（先住ペット）エンドポイント
# ========================================


@router.post(
    "/applicants-extended/{applicant_id}/pets",
    response_model=ApplicantPetResponse,
    status_code=status.HTTP_201_CREATED,
)
def add_pet(  # type: ignore[no-untyped-def]
    applicant_id: int,
    pet_data: ApplicantPetCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    先住ペットを追加

    Args:
        applicant_id: 里親希望者ID
        pet_data: ペットデータ
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        ApplicantPetResponse: 追加されたペット情報
    """
    pet = adoption_service.add_pet(db, applicant_id, pet_data, user_id=current_user.id)
    return pet


@router.delete(
    "/applicants-extended/{applicant_id}/pets/{pet_id}",
    status_code=status.HTTP_204_NO_CONTENT,
)
def delete_pet(  # type: ignore[no-untyped-def]
    applicant_id: int,
    pet_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_from_cookie_or_header),
):
    """
    先住ペットを削除

    Args:
        applicant_id: 里親希望者ID
        pet_id: ペットID
        db: データベースセッション
        current_user: 現在のユーザー
    """
    adoption_service.delete_pet(db, applicant_id, pet_id, user_id=current_user.id)


# ========================================
# AdoptionRecord（譲渡記録）エンドポイント
# ========================================


@router.get("/records", response_model=list[AdoptionRecordResponse])
def list_adoption_records(  # type: ignore[no-untyped-def]
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
def create_interview_record(  # type: ignore[no-untyped-def]
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
def create_adoption(  # type: ignore[no-untyped-def]
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
def get_adoption_record(  # type: ignore[no-untyped-def]
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
def update_adoption_record(  # type: ignore[no-untyped-def]
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
