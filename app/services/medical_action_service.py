"""
診療行為マスターサービス

診療行為（薬剤、ワクチン、検査等）のビジネスロジックを実装します。
"""

from __future__ import annotations

from datetime import date
from math import ceil

from fastapi import HTTPException, status
from sqlalchemy.orm import Session

from app.models.medical_action import MedicalAction
from app.schemas.medical_action import (
    BillingCalculation,
    MedicalActionCreate,
    MedicalActionListResponse,
    MedicalActionUpdate,
)


def create_medical_action(
    db: Session, medical_action_data: MedicalActionCreate, user_id: int
) -> MedicalAction:
    """
    診療行為マスターを登録

    Args:
        db: データベースセッション
        medical_action_data: 診療行為マスターデータ
        user_id: 登録者のユーザーID

    Returns:
        MedicalAction: 登録された診療行為マスター

    Raises:
        HTTPException: 登録に失敗した場合（500）

    Example:
        >>> action_data = MedicalActionCreate(
        ...     name="ワクチン接種",
        ...     valid_from=date(2025, 1, 1),
        ...     selling_price=Decimal("3000.00"),
        ... )
        >>> action = create_medical_action(db, action_data, user_id=1)
    """
    try:
        medical_action = MedicalAction(
            **medical_action_data.model_dump(), last_updated_by=user_id
        )
        db.add(medical_action)
        db.commit()
        db.refresh(medical_action)
        return medical_action
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"診療行為マスターの登録に失敗しました: {e!s}",
        ) from e


def get_medical_action(db: Session, medical_action_id: int) -> MedicalAction:
    """
    診療行為マスターを取得

    Args:
        db: データベースセッション
        medical_action_id: 診療行為マスターID

    Returns:
        MedicalAction: 診療行為マスター

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）

    Example:
        >>> action = get_medical_action(db, medical_action_id=1)
    """
    medical_action = (
        db.query(MedicalAction).filter(MedicalAction.id == medical_action_id).first()
    )

    if not medical_action:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"診療行為マスターID {medical_action_id} が見つかりません",
        )

    return medical_action


def list_medical_actions(
    db: Session,
    page: int = 1,
    page_size: int = 20,
    valid_on: date | None = None,
    name_filter: str | None = None,
) -> MedicalActionListResponse:
    """
    診療行為マスター一覧を取得

    Args:
        db: データベースセッション
        page: ページ番号（デフォルト: 1）
        page_size: 1ページあたりの件数（デフォルト: 20）
        valid_on: 指定日に有効な診療行為のみ取得（任意）
        name_filter: 名称で部分一致検索（任意）

    Returns:
        MedicalActionListResponse: 診療行為マスター一覧とページネーション情報

    Example:
        >>> result = list_medical_actions(db, page=1, page_size=20)
        >>> result = list_medical_actions(db, valid_on=date.today())
    """
    query = db.query(MedicalAction)

    # 有効期間フィルター
    if valid_on:
        query = query.filter(MedicalAction.valid_from <= valid_on).filter(
            (MedicalAction.valid_to.is_(None)) | (MedicalAction.valid_to >= valid_on)
        )

    # 名称フィルター
    if name_filter:
        query = query.filter(MedicalAction.name.contains(name_filter))

    # 総件数取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * page_size
    items = (
        query.order_by(MedicalAction.valid_from.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 総ページ数計算
    total_pages = ceil(total / page_size) if total > 0 else 0

    return MedicalActionListResponse(
        items=items,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def update_medical_action(
    db: Session,
    medical_action_id: int,
    medical_action_data: MedicalActionUpdate,
    user_id: int,
) -> MedicalAction:
    """
    診療行為マスターを更新

    Args:
        db: データベースセッション
        medical_action_id: 診療行為マスターID
        medical_action_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        MedicalAction: 更新された診療行為マスター

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）
        HTTPException: 更新に失敗した場合（500）

    Example:
        >>> update_data = MedicalActionUpdate(selling_price=Decimal("3500.00"))
        >>> action = update_medical_action(db, 1, update_data, user_id=1)
    """
    medical_action = get_medical_action(db, medical_action_id)

    try:
        # 更新データを適用
        update_dict = medical_action_data.model_dump(exclude_unset=True)
        for key, value in update_dict.items():
            setattr(medical_action, key, value)

        medical_action.last_updated_by = user_id

        db.commit()
        db.refresh(medical_action)
        return medical_action
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"診療行為マスターの更新に失敗しました: {e!s}",
        ) from e


def calculate_billing(
    db: Session, medical_action_id: int, dosage: int = 1
) -> BillingCalculation:
    """
    診療行為の料金を計算

    計算式: (請求価格 × 投薬量) + 投薬・処置料金

    Args:
        db: データベースセッション
        medical_action_id: 診療行為マスターID
        dosage: 投薬量・回数（デフォルト: 1）

    Returns:
        BillingCalculation: 料金計算結果

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）
        HTTPException: 投薬量が不正な場合（400）

    Example:
        >>> billing = calculate_billing(db, medical_action_id=1, dosage=2)
        >>> print(f"合計: {billing.total} {billing.currency}")
    """
    if dosage < 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="投薬量は1以上でなければなりません",
        )

    medical_action = get_medical_action(db, medical_action_id)

    subtotal = medical_action.selling_price * dosage
    total = subtotal + medical_action.procedure_fee

    return BillingCalculation(
        medical_action_id=medical_action.id,
        medical_action_name=medical_action.name,
        dosage=dosage,
        selling_price=medical_action.selling_price,
        procedure_fee=medical_action.procedure_fee,
        subtotal=subtotal,
        total=total,
        currency=medical_action.currency,
    )


def get_active_medical_actions(
    db: Session, target_date: date | None = None
) -> list[MedicalAction]:
    """
    指定日に有効な診療行為マスター一覧を取得

    Args:
        db: データベースセッション
        target_date: 対象日（デフォルト: 今日）

    Returns:
        list[MedicalAction]: 有効な診療行為マスター一覧

    Example:
        >>> actions = get_active_medical_actions(db)
        >>> actions = get_active_medical_actions(db, date(2025, 12, 31))
    """
    if target_date is None:
        target_date = date.today()

    return (
        db.query(MedicalAction)
        .filter(MedicalAction.valid_from <= target_date)
        .filter(
            (MedicalAction.valid_to.is_(None)) | (MedicalAction.valid_to >= target_date)
        )
        .order_by(MedicalAction.name)
        .all()
    )
