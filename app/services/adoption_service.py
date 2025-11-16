"""
里親管理サービス

里親希望者と譲渡プロセスのビジネスロジックを実装します。
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.adoption_record import AdoptionRecord
from app.models.animal import Animal
from app.models.applicant import Applicant
from app.models.status_history import StatusHistory
from app.schemas.adoption import (
    AdoptionRecordCreate,
    AdoptionRecordUpdate,
    ApplicantCreate,
    ApplicantUpdate,
)

logger = logging.getLogger(__name__)


# ========================================
# Applicant（里親希望者）管理
# ========================================


def create_applicant(
    db: Session, applicant_data: ApplicantCreate, user_id: int
) -> Applicant:
    """
    里親希望者を登録

    Args:
        db: データベースセッション
        applicant_data: 里親希望者データ
        user_id: 登録者のユーザーID

    Returns:
        Applicant: 登録された里親希望者

    Raises:
        HTTPException: 登録失敗時

    Example:
        >>> applicant_data = ApplicantCreate(
        ...     name="山田太郎", contact="090-1234-5678", address="東京都渋谷区"
        ... )
        >>> applicant = create_applicant(db, applicant_data, user_id=1)
        >>> applicant.name
        '山田太郎'
    """
    try:
        applicant = Applicant(**applicant_data.model_dump())
        db.add(applicant)
        db.commit()
        db.refresh(applicant)

        logger.info(
            f"里親希望者を登録しました: ID={applicant.id}, 名前={applicant.name}, "
            f"登録者={user_id}"
        )
        return applicant

    except Exception as e:
        db.rollback()
        logger.error(f"里親希望者の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親希望者の登録に失敗しました",
        ) from e


def get_applicant(db: Session, applicant_id: int) -> Applicant:
    """
    里親希望者を取得

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID

    Returns:
        Applicant: 里親希望者

    Raises:
        HTTPException: 里親希望者が見つからない場合

    Example:
        >>> applicant = get_applicant(db, applicant_id=1)
        >>> applicant.name
        '山田太郎'
    """
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        logger.warning(f"里親希望者が見つかりません: ID={applicant_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"里親希望者（ID: {applicant_id}）が見つかりません",
        )
    return applicant


def list_applicants(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[Applicant]:
    """
    里親希望者一覧を取得

    Args:
        db: データベースセッション
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限

    Returns:
        Sequence[Applicant]: 里親希望者のリスト

    Example:
        >>> applicants = list_applicants(db, skip=0, limit=10)
        >>> len(applicants)
        5
    """
    return db.query(Applicant).offset(skip).limit(limit).all()


def update_applicant(
    db: Session, applicant_id: int, applicant_data: ApplicantUpdate, user_id: int
) -> Applicant:
    """
    里親希望者を更新

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID
        applicant_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        Applicant: 更新された里親希望者

    Raises:
        HTTPException: 里親希望者が見つからない、または更新失敗時

    Example:
        >>> update_data = ApplicantUpdate(contact="090-9876-5432")
        >>> applicant = update_applicant(
        ...     db, applicant_id=1, applicant_data=update_data, user_id=1
        ... )
        >>> applicant.contact
        '090-9876-5432'
    """
    applicant = get_applicant(db, applicant_id)

    try:
        # 更新データを適用（Noneでないフィールドのみ）
        update_dict = applicant_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(applicant, key, value)

        db.commit()
        db.refresh(applicant)

        logger.info(f"里親希望者を更新しました: ID={applicant_id}, 更新者={user_id}")
        return applicant

    except Exception as e:
        db.rollback()
        logger.error(f"里親希望者の更新に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親希望者の更新に失敗しました",
        ) from e


# ========================================
# AdoptionRecord（譲渡記録）管理
# ========================================


def create_interview_record(
    db: Session, record_data: AdoptionRecordCreate, user_id: int
) -> AdoptionRecord:
    """
    面談記録を登録

    Args:
        db: データベースセッション
        record_data: 面談記録データ
        user_id: 登録者のユーザーID

    Returns:
        AdoptionRecord: 登録された面談記録

    Raises:
        HTTPException: 猫または里親希望者が見つからない、または登録失敗時

    Example:
        >>> from datetime import date
        >>> record_data = AdoptionRecordCreate(
        ...     animal_id=1,
        ...     applicant_id=1,
        ...     interview_date=date(2025, 11, 15),
        ...     interview_note="面談実施。飼育環境良好。",
        ...     decision="pending",
        ... )
        >>> record = create_interview_record(db, record_data, user_id=1)
        >>> record.decision
        'pending'
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == record_data.animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫（ID: {record_data.animal_id}）が見つかりません",
        )

    # 里親希望者の存在確認
    get_applicant(db, record_data.applicant_id)

    try:
        record = AdoptionRecord(**record_data.model_dump())
        db.add(record)
        db.commit()
        db.refresh(record)

        logger.info(
            f"面談記録を登録しました: ID={record.id}, 猫ID={record.animal_id}, "
            f"希望者ID={record.applicant_id}, 登録者={user_id}"
        )
        return record

    except Exception as e:
        db.rollback()
        logger.error(f"面談記録の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="面談記録の登録に失敗しました",
        ) from e


def create_adoption_record(
    db: Session,
    animal_id: int,
    applicant_id: int,
    adoption_date: date,
    user_id: int,
) -> AdoptionRecord:
    """
    譲渡記録を登録し、猫のステータスを「譲渡済み」に更新

    Args:
        db: データベースセッション
        animal_id: 猫ID
        applicant_id: 里親希望者ID
        adoption_date: 譲渡日
        user_id: 登録者のユーザーID

    Returns:
        AdoptionRecord: 登録された譲渡記録

    Raises:
        HTTPException: 猫または里親希望者が見つからない、または登録失敗時

    Example:
        >>> from datetime import date
        >>> record = create_adoption_record(
        ...     db,
        ...     animal_id=1,
        ...     applicant_id=1,
        ...     adoption_date=date(2025, 11, 20),
        ...     user_id=1,
        ... )
        >>> record.adoption_date
        datetime.date(2025, 11, 20)
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫（ID: {animal_id}）が見つかりません",
        )

    # 里親希望者の存在確認
    get_applicant(db, applicant_id)

    try:
        # 譲渡記録を作成
        record = AdoptionRecord(
            animal_id=animal_id,
            applicant_id=applicant_id,
            adoption_date=adoption_date,
            decision="approved",
        )
        db.add(record)
        db.flush()  # IDを取得

        # 猫のステータスを「譲渡済み」に更新
        old_status = animal.status
        animal.status = "譲渡済み"

        # ステータス変更履歴を記録
        status_history = StatusHistory(
            animal_id=animal_id,
            changed_by=user_id,
            old_status=old_status,
            new_status="譲渡済み",
        )
        db.add(status_history)

        db.commit()
        db.refresh(record)

        logger.info(
            f"譲渡記録を登録しました: ID={record.id}, 猫ID={animal_id}, "
            f"希望者ID={applicant_id}, 譲渡日={adoption_date}, 登録者={user_id}"
        )
        logger.info(
            f"猫のステータスを更新しました: 猫ID={animal_id}, {old_status} → 譲渡済み"
        )
        return record

    except Exception as e:
        db.rollback()
        logger.error(f"譲渡記録の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="譲渡記録の登録に失敗しました",
        ) from e


def update_adoption_record(
    db: Session, record_id: int, record_data: AdoptionRecordUpdate, user_id: int
) -> AdoptionRecord:
    """
    譲渡記録を更新

    Args:
        db: データベースセッション
        record_id: 譲渡記録ID
        record_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        AdoptionRecord: 更新された譲渡記録

    Raises:
        HTTPException: 譲渡記録が見つからない、または更新失敗時

    Example:
        >>> update_data = AdoptionRecordUpdate(follow_up="譲渡後1週間経過。問題なし。")
        >>> record = update_adoption_record(
        ...     db, record_id=1, record_data=update_data, user_id=1
        ... )
        >>> record.follow_up
        '譲渡後1週間経過。問題なし。'
    """
    record = db.query(AdoptionRecord).filter(AdoptionRecord.id == record_id).first()
    if not record:
        logger.warning(f"譲渡記録が見つかりません: ID={record_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"譲渡記録（ID: {record_id}）が見つかりません",
        )

    try:
        # 更新データを適用（Noneでないフィールドのみ）
        update_dict = record_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(record, key, value)

        db.commit()
        db.refresh(record)

        logger.info(f"譲渡記録を更新しました: ID={record_id}, 更新者={user_id}")
        return record

    except Exception as e:
        db.rollback()
        logger.error(f"譲渡記録の更新に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="譲渡記録の更新に失敗しました",
        ) from e


def get_adoption_record(db: Session, record_id: int) -> AdoptionRecord:
    """
    譲渡記録を取得

    Args:
        db: データベースセッション
        record_id: 譲渡記録ID

    Returns:
        AdoptionRecord: 譲渡記録

    Raises:
        HTTPException: 譲渡記録が見つからない場合

    Example:
        >>> record = get_adoption_record(db, record_id=1)
        >>> record.decision
        'approved'
    """
    record = db.query(AdoptionRecord).filter(AdoptionRecord.id == record_id).first()
    if not record:
        logger.warning(f"譲渡記録が見つかりません: ID={record_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"譲渡記録（ID: {record_id}）が見つかりません",
        )
    return record


def list_adoption_records(
    db: Session, animal_id: int | None = None, skip: int = 0, limit: int = 100
) -> Sequence[AdoptionRecord]:
    """
    譲渡記録一覧を取得

    Args:
        db: データベースセッション
        animal_id: 猫ID（指定時は特定の猫の記録のみ取得）
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限

    Returns:
        Sequence[AdoptionRecord]: 譲渡記録のリスト

    Example:
        >>> records = list_adoption_records(db, animal_id=1)
        >>> len(records)
        2
    """
    query = db.query(AdoptionRecord)
    if animal_id is not None:
        query = query.filter(AdoptionRecord.animal_id == animal_id)
    return query.offset(skip).limit(limit).all()
