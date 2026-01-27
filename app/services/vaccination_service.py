"""
ワクチン接種記録サービス（Issue #83）

ワクチン接種記録のCRUDビジネスロジックを実装します。
"""

from __future__ import annotations

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.vaccination_record import VaccinationRecord
from app.schemas.vaccination_record import (
    VaccinationRecordCreate,
    VaccinationRecordUpdate,
)


def create_vaccination_record(
    db: Session, vaccination_data: VaccinationRecordCreate
) -> VaccinationRecord:
    """
    ワクチン接種記録を登録

    Args:
        db: データベースセッション
        vaccination_data: ワクチン接種記録データ

    Returns:
        VaccinationRecord: 登録されたワクチン接種記録

    Raises:
        HTTPException: 登録に失敗した場合（500）

    Example:
        >>> data = VaccinationRecordCreate(
        ...     animal_id=1,
        ...     vaccine_category=VaccineCategoryEnum.VACCINE_3CORE,
        ...     administered_on=date(2025, 1, 15),
        ... )
        >>> record = create_vaccination_record(db, data)
    """
    try:
        record = VaccinationRecord(**vaccination_data.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ワクチン接種記録の登録に失敗しました: {e!s}",
        ) from e


def get_vaccination_record(db: Session, record_id: int) -> VaccinationRecord:
    """
    ワクチン接種記録を取得

    Args:
        db: データベースセッション
        record_id: ワクチン接種記録ID

    Returns:
        VaccinationRecord: ワクチン接種記録

    Raises:
        HTTPException: 記録が見つからない場合（404）

    Example:
        >>> record = get_vaccination_record(db, record_id=1)
    """
    record = (
        db.query(VaccinationRecord).filter(VaccinationRecord.id == record_id).first()
    )

    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ワクチン接種記録ID {record_id} が見つかりません",
        )

    return record


def update_vaccination_record(
    db: Session, record_id: int, update_data: VaccinationRecordUpdate
) -> VaccinationRecord:
    """
    ワクチン接種記録を更新

    Args:
        db: データベースセッション
        record_id: ワクチン接種記録ID
        update_data: 更新データ

    Returns:
        VaccinationRecord: 更新されたワクチン接種記録

    Raises:
        HTTPException: 記録が見つからない場合（404）、更新に失敗した場合（500）

    Example:
        >>> update_data = VaccinationRecordUpdate(memo="経過良好")
        >>> record = update_vaccination_record(db, record_id=1, update_data=update_data)
    """
    record = get_vaccination_record(db, record_id)

    try:
        update_dict = update_data.model_dump(exclude_unset=True)
        for field, value in update_dict.items():
            setattr(record, field, value)
        db.commit()
        db.refresh(record)
        return record
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ワクチン接種記録の更新に失敗しました: {e!s}",
        ) from e


def delete_vaccination_record(db: Session, record_id: int) -> None:
    """
    ワクチン接種記録を削除

    Args:
        db: データベースセッション
        record_id: ワクチン接種記録ID

    Raises:
        HTTPException: 記録が見つからない場合（404）、削除に失敗した場合（500）

    Example:
        >>> delete_vaccination_record(db, record_id=1)
    """
    record = get_vaccination_record(db, record_id)

    try:
        db.delete(record)
        db.commit()
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"ワクチン接種記録の削除に失敗しました: {e!s}",
        ) from e


def list_vaccination_records_by_animal(
    db: Session, animal_id: int
) -> list[VaccinationRecord]:
    """
    動物のワクチン接種記録一覧を取得（接種日の降順）

    Args:
        db: データベースセッション
        animal_id: 動物ID

    Returns:
        list[VaccinationRecord]: ワクチン接種記録のリスト

    Example:
        >>> records = list_vaccination_records_by_animal(db, animal_id=1)
    """
    return (
        db.query(VaccinationRecord)
        .filter(VaccinationRecord.animal_id == animal_id)
        .order_by(VaccinationRecord.administered_on.desc())
        .all()
    )
