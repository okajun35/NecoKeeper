"""
里親管理サービス

Issue #91: 譲渡記録の充実化
里親希望者と譲渡プロセスのビジネスロジックを実装します。
"""

from __future__ import annotations

import logging
import re
from collections.abc import Sequence
from datetime import date, datetime
from typing import Any

from fastapi import HTTPException, status
from sqlalchemy import func, or_
from sqlalchemy.orm import Session

from app.models.adoption_consultation import AdoptionConsultation
from app.models.adoption_record import AdoptionRecord
from app.models.animal import Animal
from app.models.applicant import Applicant, ApplicantHouseholdMember, ApplicantPet
from app.schemas.adoption import (
    AdoptionConsultationCreate,
    AdoptionConsultationUpdate,
    AdoptionRecordCreate,
    AdoptionRecordUpdate,
    ApplicantCreateExtended,
    ApplicantHouseholdMemberCreate,
    ApplicantPetCreate,
    ApplicantUpdateExtended,
)
from app.services.status_history_helper import record_status_change

logger = logging.getLogger(__name__)


# ========================================
# Applicant（里親希望者）管理
# ========================================


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
        animal.status = "ADOPTED"

        # ステータス変更履歴を記録（新フォーマットで統一）
        record_status_change(
            db=db,
            animal_id=animal_id,
            old_status=old_status,
            new_status="ADOPTED",
            user_id=user_id,
            reason="譲渡記録の作成",
        )

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


# ========================================
# 拡張Applicant（里親申込）管理 - Issue #91
# ========================================


def _validate_applicant_extended(applicant_data: ApplicantCreateExtended) -> None:
    """
    拡張里親申込の条件付き必須バリデーション

    Pydanticのmodel_validatorで基本的なバリデーションは行われているが、
    サービス層でも再度チェックを行う。

    Args:
        applicant_data: 申込データ

    Raises:
        ValueError: バリデーションエラー時
    """
    # 連絡手段の整合性チェック
    if applicant_data.contact_type == "line" and not applicant_data.contact_line_id:
        raise ValueError("LINE連絡を選択した場合、LINE IDの入力が必須です")
    if applicant_data.contact_type == "email" and not applicant_data.contact_email:
        raise ValueError("メール連絡を選択した場合、メールアドレスの入力が必須です")

    # 転居予定の整合性チェック
    if applicant_data.relocation_plan == "planned" and (
        not applicant_data.relocation_time_note
        or not applicant_data.relocation_cat_plan
    ):
        raise ValueError("転居予定がある場合、時期と猫の処遇の入力が必須です")

    # お留守番の整合性チェック
    if applicant_data.alone_time_status in ("sometimes", "regular") and (
        applicant_data.alone_time_weekly_days is None
        or applicant_data.alone_time_hours is None
    ):
        raise ValueError("お留守番がある場合、週何回と1回あたりの時間の入力が必須です")

    # 家族構成の「その他」チェック
    for member in applicant_data.household_members:
        if member.relation == "other" and not member.relation_other:
            raise ValueError("続柄が「その他」の場合、詳細の入力が必須です")


def _validate_contact_info(data: dict[str, Any]) -> None:
    """
    連絡手段の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    contact_type = data.get("contact_type")
    if contact_type == "line" and not data.get("contact_line_id"):
        raise ValueError("LINE連絡を選択した場合、LINE IDの入力が必須です")
    if contact_type == "email" and not data.get("contact_email"):
        raise ValueError("メール連絡を選択した場合、メールアドレスの入力が必須です")


def _validate_consultation_contact_info(data: dict[str, Any]) -> None:
    """
    相談の連絡手段整合性チェック

    Args:
        data: 相談データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    contact_type = data.get("contact_type")
    if contact_type == "line" and not data.get("contact_line_id"):
        raise ValueError("LINE連絡を選択した場合、LINE IDの入力が必須です")
    if contact_type == "email" and not data.get("contact_email"):
        raise ValueError("メール連絡を選択した場合、メールアドレスの入力が必須です")


def _validate_relocation_plan(data: dict[str, Any]) -> None:
    """
    転居予定の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    if data.get("relocation_plan") == "planned" and (
        not data.get("relocation_time_note") or not data.get("relocation_cat_plan")
    ):
        raise ValueError("転居予定がある場合、時期と猫の処遇の入力が必須です")


def _validate_alone_time(data: dict[str, Any]) -> None:
    """
    お留守番の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    alone_time_status = data.get("alone_time_status")
    if alone_time_status in ("sometimes", "regular") and (
        data.get("alone_time_weekly_days") is None
        or data.get("alone_time_hours") is None
    ):
        raise ValueError("お留守番がある場合、週何回と1回あたりの時間の入力が必須です")


def _validate_occupation(data: dict[str, Any]) -> None:
    """
    職業の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    if data.get("occupation") == "other" and not data.get("occupation_other"):
        raise ValueError("職業が「その他」の場合、詳細の入力が必須です")


def _validate_emergency_relation(data: dict[str, Any]) -> None:
    """
    緊急連絡先続柄の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    if data.get("emergency_relation") == "other" and not data.get(
        "emergency_relation_other"
    ):
        raise ValueError("緊急連絡先の続柄が「その他」の場合、詳細の入力が必須です")


def _validate_pet_limit(data: dict[str, Any]) -> None:
    """
    ペット飼育上限の整合性チェック（更新時用）

    Args:
        data: マージ済みの申込データ（既存値+更新値）

    Raises:
        ValueError: バリデーションエラー時
    """
    if (
        data.get("pet_permission") == "allowed"
        and data.get("pet_limit_type") == "limited"
        and data.get("pet_limit_count") is None
    ):
        raise ValueError("ペット上限ありの場合、上限数の入力が必須です")


def create_applicant_extended(
    db: Session, applicant_data: ApplicantCreateExtended, user_id: int
) -> Applicant:
    """
    拡張里親申込を登録

    Issue #91の仕様に基づく全項目入力フォームからの登録処理。
    家族構成・先住ペット情報も同時に登録する。

    Args:
        db: データベースセッション
        applicant_data: 里親申込データ
        user_id: 登録者のユーザーID

    Returns:
        Applicant: 登録された里親申込

    Raises:
        ValueError: バリデーションエラー時
        HTTPException: 登録失敗時

    Example:
        >>> applicant_data = ApplicantCreateExtended(
        ...     name_kana="ヤマダタロウ",
        ...     name="山田太郎",
        ...     age=35,
        ...     phone="090-1234-5678",
        ...     contact_type="line",
        ...     contact_line_id="yamada_taro",
        ...     ...
        ... )
        >>> applicant = create_applicant_extended(db, applicant_data, user_id=1)
        >>> applicant.name
        '山田太郎'
    """
    # バリデーション
    _validate_applicant_extended(applicant_data)

    try:
        consultation: AdoptionConsultation | None = None
        if applicant_data.source_consultation_id is not None:
            consultation = get_consultation(db, applicant_data.source_consultation_id)
            if consultation.status == "closed":
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="対応終了の相談は申込に変換できません",
                )
            if (
                consultation.status == "converted"
                and consultation.applicant_id is not None
            ):
                raise HTTPException(
                    status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
                    detail="この相談はすでに申込化されています",
                )

        # メインデータを準備（household_membersとpetsを除外）
        main_data = applicant_data.model_dump(
            exclude={"household_members", "pets", "source_consultation_id"}
        )

        # 後方互換用フィールドを設定
        main_data["contact"] = (
            applicant_data.contact_line_id or applicant_data.contact_email or ""
        )
        if consultation and not main_data.get("conditions"):
            # 相談内容は既存の後方互換フィールド conditions に保存する
            main_data["conditions"] = consultation.consultation_note

        # Applicantを作成
        applicant = Applicant(**main_data)
        db.add(applicant)
        db.flush()  # IDを取得

        # 家族構成を登録
        for member_data in applicant_data.household_members:
            member = ApplicantHouseholdMember(
                applicant_id=applicant.id,
                **member_data.model_dump(),
            )
            db.add(member)

        # 先住ペットを登録
        for pet_data in applicant_data.pets:
            pet = ApplicantPet(
                applicant_id=applicant.id,
                **pet_data.model_dump(),
            )
            db.add(pet)

        if consultation:
            consultation.status = "converted"
            consultation.applicant_id = applicant.id

        db.commit()
        db.refresh(applicant)

        logger.info(
            f"拡張里親申込を登録しました: ID={applicant.id}, 名前={applicant.name}, "
            f"家族構成={len(applicant_data.household_members)}人, "
            f"先住ペット={len(applicant_data.pets)}件, "
            f"登録者={user_id}"
        )
        return applicant

    except ValueError:
        # バリデーションエラーはそのまま再送出
        raise
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"拡張里親申込の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親申込の登録に失敗しました",
        ) from e


def get_consultation(db: Session, consultation_id: int) -> AdoptionConsultation:
    """
    里親相談を取得

    Args:
        db: データベースセッション
        consultation_id: 相談ID

    Returns:
        AdoptionConsultation: 里親相談

    Raises:
        HTTPException: 相談が見つからない場合
    """
    consultation = (
        db.query(AdoptionConsultation)
        .filter(AdoptionConsultation.id == consultation_id)
        .first()
    )
    if not consultation:
        logger.warning(f"里親相談が見つかりません: ID={consultation_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"里親相談（ID: {consultation_id}）が見つかりません",
        )
    return consultation


def list_consultations(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    status_filter: str | None = None,
) -> Sequence[AdoptionConsultation]:
    """
    里親相談一覧を取得

    Args:
        db: データベースセッション
        skip: スキップ件数
        limit: 取得件数上限
        status_filter: ステータスフィルター（open/converted/closed）

    Returns:
        Sequence[AdoptionConsultation]: 里親相談一覧
    """
    query = db.query(AdoptionConsultation)
    if status_filter:
        query = query.filter(AdoptionConsultation.status == status_filter)

    return (
        query.order_by(AdoptionConsultation.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def list_intake_entries(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    request_type: str = "all",
) -> list[dict[str, Any]]:
    """
    受付一覧（相談/譲渡申込）を取得

    Args:
        db: データベースセッション
        skip: スキップ件数
        limit: 取得件数上限
        request_type: 取得種別（all/application/consultation）

    Returns:
        list[dict[str, Any]]: 受付一覧データ
    """
    if request_type == "application":
        applicants = (
            db.query(Applicant)
            .order_by(Applicant.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_build_intake_entry_from_applicant(a) for a in applicants]

    if request_type == "consultation":
        consultations = (
            db.query(AdoptionConsultation)
            .order_by(AdoptionConsultation.created_at.desc())
            .offset(skip)
            .limit(limit)
            .all()
        )
        return [_build_intake_entry_from_consultation(c) for c in consultations]

    applicants = db.query(Applicant).order_by(Applicant.created_at.desc()).all()
    consultations = (
        db.query(AdoptionConsultation)
        .order_by(AdoptionConsultation.created_at.desc())
        .all()
    )

    merged = _merge_intake_entries_for_all(
        [
            *[_build_intake_entry_from_applicant(a) for a in applicants],
            *[_build_intake_entry_from_consultation(c) for c in consultations],
        ]
    )
    end = skip + limit
    return merged[skip:end]


def _build_intake_entry_from_applicant(applicant: Applicant) -> dict[str, Any]:
    return {
        "id": applicant.id,
        "request_type": "application",
        "application_id": applicant.id,
        "consultation_id": None,
        "name_kana": applicant.name_kana,
        "name": applicant.name,
        "phone": applicant.phone,
        "contact_type": applicant.contact_type,
        "contact_line_id": applicant.contact_line_id,
        "contact_email": applicant.contact_email,
        "consultation_note": None,
        "status": None,
        "created_at": applicant.created_at,
    }


def _build_intake_entry_from_consultation(
    consultation: AdoptionConsultation,
) -> dict[str, Any]:
    return {
        "id": consultation.id,
        "request_type": "consultation",
        "application_id": consultation.applicant_id,
        "consultation_id": consultation.id,
        "name_kana": consultation.name_kana,
        "name": consultation.name,
        "phone": consultation.phone,
        "contact_type": consultation.contact_type,
        "contact_line_id": consultation.contact_line_id,
        "contact_email": consultation.contact_email,
        "consultation_note": consultation.consultation_note,
        "status": consultation.status,
        "created_at": consultation.created_at,
    }


def _merge_intake_entries_for_all(
    entries: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    sorted_entries = sorted(
        entries,
        key=lambda entry: _cast_datetime(entry.get("created_at")),
        reverse=True,
    )
    merged_entries: list[dict[str, Any]] = []
    index_by_key: dict[str, int] = {}

    for entry in sorted_entries:
        dedupe_key = _build_intake_dedupe_key(entry)
        if not dedupe_key:
            merged_entries.append(dict(entry))
            continue

        existing_index = index_by_key.get(dedupe_key)
        if existing_index is None:
            merged_entries.append(dict(entry))
            index_by_key[dedupe_key] = len(merged_entries) - 1
            continue

        existing = merged_entries[existing_index]
        if (
            existing.get("request_type") == entry.get("request_type")
            or existing.get("request_type") == "both"
        ):
            merged_entries.append(dict(entry))
            continue

        merged_entries[existing_index] = _merge_two_intake_entries(existing, entry)

    return merged_entries


def _merge_two_intake_entries(
    primary: dict[str, Any], secondary: dict[str, Any]
) -> dict[str, Any]:
    merged = dict(primary)
    merged["request_type"] = "both"
    merged["application_id"] = _get_application_id(primary) or _get_application_id(
        secondary
    )
    merged["consultation_id"] = _get_consultation_id(primary) or _get_consultation_id(
        secondary
    )

    if not merged.get("consultation_note"):
        merged["consultation_note"] = primary.get("consultation_note") or secondary.get(
            "consultation_note"
        )

    consultation_status = (
        (
            primary.get("status")
            if primary.get("request_type") == "consultation"
            else None
        )
        or (
            secondary.get("status")
            if secondary.get("request_type") == "consultation"
            else None
        )
        or None
    )
    merged["status"] = consultation_status

    if not merged.get("phone"):
        merged["phone"] = secondary.get("phone")
    if not merged.get("contact_type"):
        merged["contact_type"] = secondary.get("contact_type")
    if not merged.get("contact_line_id"):
        merged["contact_line_id"] = secondary.get("contact_line_id")
    if not merged.get("contact_email"):
        merged["contact_email"] = secondary.get("contact_email")
    if not merged.get("name_kana"):
        merged["name_kana"] = secondary.get("name_kana")

    return merged


def _build_intake_dedupe_key(entry: dict[str, Any]) -> str | None:
    normalized_name = _normalize_name(entry.get("name"))
    normalized_phone = _normalize_phone(entry.get("phone"))
    normalized_contact_type = _normalize_contact_type(entry.get("contact_type"))

    if not normalized_name or not normalized_phone or not normalized_contact_type:
        return None

    return f"{normalized_name}|{normalized_phone}|{normalized_contact_type}"


def _normalize_name(name: Any) -> str:
    return re.sub(r"\s+", "", str(name or "")).strip().lower()


def _normalize_phone(phone: Any) -> str:
    return re.sub(r"\D", "", str(phone or ""))


def _normalize_contact_type(contact_type: Any) -> str:
    return str(contact_type or "").strip().lower()


def _get_application_id(entry: dict[str, Any]) -> int | None:
    application_id = entry.get("application_id")
    if application_id:
        return int(application_id)
    if entry.get("request_type") == "application":
        entry_id = entry.get("id")
        return int(entry_id) if entry_id else None
    return None


def _get_consultation_id(entry: dict[str, Any]) -> int | None:
    consultation_id = entry.get("consultation_id")
    if consultation_id:
        return int(consultation_id)
    if entry.get("request_type") == "consultation":
        entry_id = entry.get("id")
        return int(entry_id) if entry_id else None
    return None


def _cast_datetime(value: Any) -> datetime:
    if isinstance(value, datetime):
        return value
    return datetime.min


def create_consultation(
    db: Session,
    consultation_data: AdoptionConsultationCreate,
    user_id: int,
) -> AdoptionConsultation:
    """
    里親相談を登録

    Args:
        db: データベースセッション
        consultation_data: 相談データ
        user_id: 登録者ID

    Returns:
        AdoptionConsultation: 登録された相談
    """
    try:
        consultation = AdoptionConsultation(**consultation_data.model_dump())
        db.add(consultation)
        db.commit()
        db.refresh(consultation)

        logger.info(
            f"里親相談を登録しました: ID={consultation.id}, 名前={consultation.name}, 登録者={user_id}"
        )
        return consultation
    except Exception as e:
        db.rollback()
        logger.error(f"里親相談の登録に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親相談の登録に失敗しました",
        ) from e


def update_consultation(
    db: Session,
    consultation_id: int,
    consultation_data: AdoptionConsultationUpdate,
    user_id: int,
) -> AdoptionConsultation:
    """
    里親相談を更新

    Args:
        db: データベースセッション
        consultation_id: 相談ID
        consultation_data: 更新データ
        user_id: 更新者ID

    Returns:
        AdoptionConsultation: 更新された相談
    """
    consultation = get_consultation(db, consultation_id)

    try:
        update_dict = consultation_data.model_dump(exclude_unset=True)

        merged_data: dict[str, Any] = {}
        for column in consultation.__table__.columns:
            key = column.name
            if key in update_dict:
                merged_data[key] = update_dict[key]
            else:
                merged_data[key] = getattr(consultation, key, None)

        _validate_consultation_contact_info(merged_data)

        for key, value in update_dict.items():
            setattr(consultation, key, value)

        db.commit()
        db.refresh(consultation)

        logger.info(f"里親相談を更新しました: ID={consultation_id}, 更新者={user_id}")
        return consultation
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_CONTENT,
            detail=str(e),
        ) from e
    except Exception as e:
        db.rollback()
        logger.error(f"里親相談の更新に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親相談の更新に失敗しました",
        ) from e


def get_applicant_extended(db: Session, applicant_id: int) -> Applicant:
    """
    拡張里親申込を取得（関連データ含む）

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID

    Returns:
        Applicant: 里親希望者（household_members, petsを含む）

    Raises:
        HTTPException: 里親希望者が見つからない場合

    Example:
        >>> applicant = get_applicant_extended(db, applicant_id=1)
        >>> len(applicant.household_members)
        2
    """
    applicant = db.query(Applicant).filter(Applicant.id == applicant_id).first()
    if not applicant:
        logger.warning(f"里親希望者が見つかりません: ID={applicant_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"里親希望者（ID: {applicant_id}）が見つかりません",
        )
    return applicant


def list_applicants_extended(
    db: Session, skip: int = 0, limit: int = 100
) -> Sequence[Applicant]:
    """
    拡張里親申込一覧を取得

    Args:
        db: データベースセッション
        skip: スキップ件数（ページネーション）
        limit: 取得件数上限

    Returns:
        Sequence[Applicant]: 里親希望者のリスト（関連データ含む）

    Example:
        >>> applicants = list_applicants_extended(db, skip=0, limit=10)
        >>> len(applicants)
        5
    """
    return (
        db.query(Applicant)
        .order_by(Applicant.created_at.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def search_applicants_extended(
    db: Session, q: str, skip: int = 0, limit: int = 20
) -> Sequence[Applicant]:
    """
    拡張里親申込を検索（部分一致）

    検索対象:
    - 氏名
    - ふりがな
    - 電話番号
    - 連絡先（メール/LINE ID）

    並び順:
    - updated_at DESC
    - id DESC
    """
    keyword = (q or "").strip()
    if len(keyword) < 2:
        return []

    like_keyword = f"%{keyword}%"

    conditions = [
        Applicant.name.ilike(like_keyword),
        Applicant.name_kana.ilike(like_keyword),
        Applicant.contact_email.ilike(like_keyword),
        Applicant.contact_line_id.ilike(like_keyword),
    ]

    normalized_phone_keyword = re.sub(r"\D", "", keyword)
    if len(normalized_phone_keyword) >= 2:
        normalized_phone = func.replace(
            func.replace(func.coalesce(Applicant.phone, ""), "-", ""),
            " ",
            "",
        )
        conditions.append(normalized_phone.ilike(f"%{normalized_phone_keyword}%"))

    return (
        db.query(Applicant)
        .filter(or_(*conditions))
        .order_by(Applicant.updated_at.desc(), Applicant.id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


def update_applicant_extended(
    db: Session,
    applicant_id: int,
    applicant_data: ApplicantUpdateExtended,
    user_id: int,
) -> Applicant:
    """
    拡張里親申込を更新

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
        >>> update_data = ApplicantUpdateExtended(monthly_budget_yen=15000)
        >>> applicant = update_applicant_extended(
        ...     db, applicant_id=1, applicant_data=update_data, user_id=1
        ... )
        >>> applicant.monthly_budget_yen
        15000
    """
    applicant = get_applicant_extended(db, applicant_id)

    try:
        # 更新データを適用（Noneでないフィールドのみ）
        update_dict = applicant_data.model_dump(exclude_unset=True)

        # 既存データと更新データをマージしてバリデーション
        merged_data: dict[str, Any] = {}
        for column in applicant.__table__.columns:
            key = column.name
            if key in update_dict:
                merged_data[key] = update_dict[key]
            else:
                merged_data[key] = getattr(applicant, key, None)

        # 条件付きバリデーション（更新後のデータ全体で検証）
        _validate_contact_info(merged_data)
        _validate_relocation_plan(merged_data)
        _validate_alone_time(merged_data)
        _validate_occupation(merged_data)
        _validate_emergency_relation(merged_data)
        _validate_pet_limit(merged_data)

        # contactカラムの更新（後方互換性のため）
        # contact_type, contact_line_id, contact_email のいずれかが更新されたら再計算
        contact_fields_updated = any(
            key in update_dict
            for key in ["contact_type", "contact_line_id", "contact_email"]
        )
        if contact_fields_updated:
            contact_type = merged_data.get("contact_type")
            if contact_type == "line":
                update_dict["contact"] = merged_data.get("contact_line_id")
            elif contact_type == "email":
                update_dict["contact"] = merged_data.get("contact_email")
            else:
                update_dict["contact"] = None

        # 更新を適用
        for key, value in update_dict.items():
            setattr(applicant, key, value)

        db.commit()
        db.refresh(applicant)

        logger.info(f"拡張里親申込を更新しました: ID={applicant_id}, 更新者={user_id}")
        return applicant

    except Exception as e:
        db.rollback()
        logger.error(f"拡張里親申込の更新に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="里親申込の更新に失敗しました",
        ) from e


def add_household_member(
    db: Session,
    applicant_id: int,
    member_data: ApplicantHouseholdMemberCreate,
    user_id: int | None = None,
) -> ApplicantHouseholdMember:
    """
    家族構成メンバーを追加

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID
        member_data: 家族メンバーデータ（スキーマ）
        user_id: 操作ユーザーID

    Returns:
        ApplicantHouseholdMember: 追加された家族構成メンバー

    Raises:
        HTTPException: 里親希望者が見つからない、または登録失敗時
    """

    # 里親希望者の存在確認
    get_applicant(db, applicant_id)

    try:
        member = ApplicantHouseholdMember(
            applicant_id=applicant_id,
            relation=member_data.relation,
            relation_other=member_data.relation_other,
            age=member_data.age,
        )
        db.add(member)
        db.commit()
        db.refresh(member)

        logger.info(
            f"家族構成メンバーを追加しました: 申込者ID={applicant_id}, "
            f"続柄={member_data.relation}, 年齢={member_data.age}, "
            f"user_id={user_id}"
        )
        return member

    except Exception as e:
        db.rollback()
        logger.error(f"家族構成メンバーの追加に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="家族構成メンバーの追加に失敗しました",
        ) from e


def add_pet(
    db: Session,
    applicant_id: int,
    pet_data: ApplicantPetCreate,
    user_id: int | None = None,
) -> ApplicantPet:
    """
    先住ペットを追加

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID
        pet_data: ペットデータ（スキーマ）
        user_id: 操作ユーザーID

    Returns:
        ApplicantPet: 追加された先住ペット

    Raises:
        HTTPException: 里親希望者が見つからない、または登録失敗時
    """

    # 里親希望者の存在確認
    get_applicant(db, applicant_id)

    try:
        pet = ApplicantPet(
            applicant_id=applicant_id,
            pet_category=pet_data.pet_category,
            count=pet_data.count,
            breed_or_type=pet_data.breed_or_type,
            age_note=pet_data.age_note,
        )
        db.add(pet)
        db.commit()
        db.refresh(pet)

        logger.info(
            f"先住ペットを追加しました: 申込者ID={applicant_id}, "
            f"種別={pet_data.pet_category}, 頭数={pet_data.count}, "
            f"user_id={user_id}"
        )
        return pet

    except Exception as e:
        db.rollback()
        logger.error(f"先住ペットの追加に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="先住ペットの追加に失敗しました",
        ) from e


def delete_household_member(
    db: Session,
    applicant_id: int,
    member_id: int,
    user_id: int | None = None,
) -> None:
    """
    家族構成メンバーを削除

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID
        member_id: 家族メンバーID
        user_id: 操作ユーザーID

    Raises:
        HTTPException: 家族メンバーが見つからない、または削除失敗時
    """
    # 里親希望者の存在確認
    get_applicant(db, applicant_id)

    member = (
        db.query(ApplicantHouseholdMember)
        .filter(
            ApplicantHouseholdMember.id == member_id,
            ApplicantHouseholdMember.applicant_id == applicant_id,
        )
        .first()
    )

    if not member:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"家族メンバーが見つかりません: ID={member_id}",
        )

    try:
        db.delete(member)
        db.commit()
        logger.info(
            f"家族構成メンバーを削除しました: 申込者ID={applicant_id}, "
            f"メンバーID={member_id}, user_id={user_id}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"家族構成メンバーの削除に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="家族構成メンバーの削除に失敗しました",
        ) from e


def delete_pet(
    db: Session,
    applicant_id: int,
    pet_id: int,
    user_id: int | None = None,
) -> None:
    """
    先住ペットを削除

    Args:
        db: データベースセッション
        applicant_id: 里親希望者ID
        pet_id: ペットID
        user_id: 操作ユーザーID

    Raises:
        HTTPException: ペットが見つからない、または削除失敗時
    """
    # 里親希望者の存在確認
    get_applicant(db, applicant_id)

    pet = (
        db.query(ApplicantPet)
        .filter(
            ApplicantPet.id == pet_id,
            ApplicantPet.applicant_id == applicant_id,
        )
        .first()
    )

    if not pet:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"先住ペットが見つかりません: ID={pet_id}",
        )

    try:
        db.delete(pet)
        db.commit()
        logger.info(
            f"先住ペットを削除しました: 申込者ID={applicant_id}, "
            f"ペットID={pet_id}, user_id={user_id}"
        )
    except Exception as e:
        db.rollback()
        logger.error(f"先住ペットの削除に失敗しました: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="先住ペットの削除に失敗しました",
        ) from e
