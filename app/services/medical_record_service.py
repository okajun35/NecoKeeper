"""
診療記録サービス

診療記録のCRUD操作を提供します。
"""

from __future__ import annotations

import logging
from datetime import date

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.medical_action import MedicalAction
from app.models.medical_record import MedicalRecord
from app.models.user import User
from app.schemas.medical_record import (
    MedicalRecordCreate,
    MedicalRecordListResponse,
    MedicalRecordResponse,
    MedicalRecordUpdate,
)

logger = logging.getLogger(__name__)


def create_medical_record(
    db: Session, medical_record_data: MedicalRecordCreate
) -> MedicalRecord:
    """
    診療記録を登録

    Args:
        db: データベースセッション
        medical_record_data: 診療記録データ

    Returns:
        MedicalRecord: 登録された診療記録

    Raises:
        HTTPException: データベースエラーが発生した場合

    Example:
        >>> record_data = MedicalRecordCreate(
        ...     animal_id=1,
        ...     vet_id=2,
        ...     date=date(2025, 11, 15),
        ...     weight=Decimal("4.5"),
        ...     symptoms="食欲不振",
        ... )
        >>> record = create_medical_record(db, record_data)
    """
    try:
        medical_record = MedicalRecord(**medical_record_data.model_dump())
        db.add(medical_record)
        db.commit()
        db.refresh(medical_record)

        logger.info(
            f"診療記録を登録しました: ID={medical_record.id}, "
            f"猫ID={medical_record.animal_id}, 日付={medical_record.date}"
        )
        return medical_record

    except Exception as e:
        db.rollback()
        logger.error(f"診療記録の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="診療記録の登録に失敗しました",
        ) from e


def get_medical_record(db: Session, medical_record_id: int) -> MedicalRecord:
    """
    診療記録の詳細を取得

    Args:
        db: データベースセッション
        medical_record_id: 診療記録ID

    Returns:
        MedicalRecord: 診療記録

    Raises:
        HTTPException: 診療記録が見つからない場合

    Example:
        >>> record = get_medical_record(db, 1)
    """
    try:
        medical_record = (
            db.query(MedicalRecord)
            .filter(MedicalRecord.id == medical_record_id)
            .first()
        )

        if not medical_record:
            logger.warning(f"診療記録が見つかりません: ID={medical_record_id}")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {medical_record_id} の診療記録が見つかりません",
            )

        return medical_record

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"診療記録の取得に失敗しました: ID={medical_record_id}, エラー={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="診療記録の取得に失敗しました",
        ) from e


def list_medical_records(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    animal_id: int | None = None,
    vet_id: int | None = None,
    start_date: date | None = None,
    end_date: date | None = None,
) -> MedicalRecordListResponse:
    """
    診療記録一覧を取得（ページネーション付き、時系列表示）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        animal_id: 猫IDフィルター
        vet_id: 獣医師IDフィルター
        start_date: 開始日フィルター
        end_date: 終了日フィルター

    Returns:
        MedicalRecordListResponse: 診療記録一覧とページネーション情報

    Example:
        >>> records = list_medical_records(db, page=1, animal_id=1)
    """
    # クエリを構築
    query = db.query(MedicalRecord)

    # フィルター
    if animal_id:
        query = query.filter(MedicalRecord.animal_id == animal_id)

    if vet_id:
        query = query.filter(MedicalRecord.vet_id == vet_id)

    if start_date:
        query = query.filter(MedicalRecord.date >= start_date)

    if end_date:
        query = query.filter(MedicalRecord.date <= end_date)

    # 総件数を取得
    total = query.count()

    # ページネーション（時系列で降順）
    offset = (page - 1) * page_size
    medical_records = (
        query.order_by(MedicalRecord.date.desc(), MedicalRecord.id.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # リレーション情報を含むレスポンスを作成
    items: list[MedicalRecordResponse] = []
    for record in medical_records:
        # 猫名を取得
        animal = db.query(Animal).filter(Animal.id == record.animal_id).first()
        animal_name = animal.name if animal else None

        # 獣医師名を取得
        vet = db.query(User).filter(User.id == record.vet_id).first()
        vet_name = vet.name if vet else None

        # 診療行為名と投薬単位を取得
        medical_action_name = None
        dosage_unit = None
        if record.medical_action_id:
            medical_action = (
                db.query(MedicalAction)
                .filter(MedicalAction.id == record.medical_action_id)
                .first()
            )
            if medical_action:
                medical_action_name = medical_action.name
                dosage_unit = medical_action.unit

        # レスポンスオブジェクトを作成
        response = MedicalRecordResponse(
            id=record.id,
            animal_id=record.animal_id,
            vet_id=record.vet_id,
            date=record.date,
            time_slot=record.time_slot,
            weight=record.weight,
            temperature=record.temperature,
            symptoms=record.symptoms,
            medical_action_id=record.medical_action_id,
            dosage=record.dosage,
            other=record.other,
            comment=record.comment,
            created_at=record.created_at,
            updated_at=record.updated_at,
            last_updated_at=record.last_updated_at,
            last_updated_by=record.last_updated_by,
            animal_name=animal_name,
            vet_name=vet_name,
            medical_action_name=medical_action_name,
            dosage_unit=dosage_unit,
        )
        items.append(response)

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return MedicalRecordListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def update_medical_record(
    db: Session,
    medical_record_id: int,
    medical_record_data: MedicalRecordUpdate,
    user_id: int,
) -> MedicalRecord:
    """
    診療記録を更新

    Args:
        db: データベースセッション
        medical_record_id: 診療記録ID
        medical_record_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        MedicalRecord: 更新された診療記録

    Raises:
        HTTPException: 診療記録が見つからない場合、またはデータベースエラーが発生した場合

    Example:
        >>> update_data = MedicalRecordUpdate(weight=Decimal("4.6"))
        >>> record = update_medical_record(db, 1, update_data, user_id=2)
    """
    try:
        medical_record = get_medical_record(db, medical_record_id)

        # 診療記録を更新
        update_dict = medical_record_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(medical_record, key, value)

        # 更新者を記録
        medical_record.last_updated_by = user_id

        db.commit()
        db.refresh(medical_record)

        logger.info(f"診療記録を更新しました: ID={medical_record_id}")
        return medical_record

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(
            f"診療記録の更新に失敗しました: ID={medical_record_id}, エラー={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="診療記録の更新に失敗しました",
        ) from e
