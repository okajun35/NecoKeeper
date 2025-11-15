"""
診療行為マスターAPI

診療行為（薬剤、ワクチン、検査等）のCRUD操作を提供するAPIエンドポイント。
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.medical_action import MedicalAction
from app.models.user import User
from app.schemas.medical_action import (
    BillingCalculation,
    MedicalActionCreate,
    MedicalActionListResponse,
    MedicalActionResponse,
    MedicalActionUpdate,
)
from app.services import medical_action_service

router = APIRouter(prefix="/medical-actions", tags=["診療行為マスター"])


@router.get("", response_model=MedicalActionListResponse)
async def list_medical_actions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: Annotated[int, Query(ge=1)] = 1,
    page_size: Annotated[int, Query(ge=1, le=100)] = 20,
    valid_on: Annotated[date | None, Query()] = None,
    name_filter: Annotated[str | None, Query(max_length=100)] = None,
) -> MedicalActionListResponse:
    """
    診療行為マスター一覧を取得

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（デフォルト: 1）
        page_size: 1ページあたりの件数（デフォルト: 20、最大: 100）
        valid_on: 指定日に有効な診療行為のみ取得（任意）
        name_filter: 名称で部分一致検索（任意）

    Returns:
        MedicalActionListResponse: 診療行為マスター一覧とページネーション情報
    """
    return medical_action_service.list_medical_actions(
        db=db,
        page=page,
        page_size=page_size,
        valid_on=valid_on,
        name_filter=name_filter,
    )


@router.post(
    "", response_model=MedicalActionResponse, status_code=status.HTTP_201_CREATED
)
async def create_medical_action(
    medical_action_data: MedicalActionCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> MedicalAction:
    """
    診療行為マスターを登録

    管理者または獣医師が診療行為マスターを登録します。

    Args:
        medical_action_data: 診療行為マスターデータ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        MedicalActionResponse: 登録された診療行為マスター
    """
    return medical_action_service.create_medical_action(
        db=db, medical_action_data=medical_action_data, user_id=current_user.id
    )


@router.get("/{medical_action_id}", response_model=MedicalActionResponse)
async def get_medical_action(
    medical_action_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> MedicalAction:
    """
    診療行為マスターの詳細を取得

    Args:
        medical_action_id: 診療行為マスターID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        MedicalActionResponse: 診療行為マスター

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）
    """
    return medical_action_service.get_medical_action(
        db=db, medical_action_id=medical_action_id
    )


@router.put("/{medical_action_id}", response_model=MedicalActionResponse)
async def update_medical_action(
    medical_action_id: int,
    medical_action_data: MedicalActionUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("medical:write"))],
) -> MedicalAction:
    """
    診療行為マスターを更新

    Args:
        medical_action_id: 診療行為マスターID
        medical_action_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（medical:write権限が必要）

    Returns:
        MedicalActionResponse: 更新された診療行為マスター

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）
    """
    return medical_action_service.update_medical_action(
        db=db,
        medical_action_id=medical_action_id,
        medical_action_data=medical_action_data,
        user_id=current_user.id,
    )


@router.get("/{medical_action_id}/calculate", response_model=BillingCalculation)
async def calculate_billing(
    medical_action_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    dosage: Annotated[int, Query(ge=1)] = 1,
) -> BillingCalculation:
    """
    診療行為の料金を計算

    計算式: (請求価格 × 投薬量) + 投薬・処置料金

    Args:
        medical_action_id: 診療行為マスターID
        dosage: 投薬量・回数（デフォルト: 1）
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        BillingCalculation: 料金計算結果

    Raises:
        HTTPException: 診療行為マスターが見つからない場合（404）
    """
    return medical_action_service.calculate_billing(
        db=db, medical_action_id=medical_action_id, dosage=dosage
    )


@router.get("/active/list", response_model=list[MedicalActionResponse])
async def get_active_medical_actions(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    target_date: Annotated[date | None, Query()] = None,
) -> list[MedicalAction]:
    """
    指定日に有効な診療行為マスター一覧を取得

    診療記録入力時の選択リスト用。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        target_date: 対象日（デフォルト: 今日）

    Returns:
        list[MedicalActionResponse]: 有効な診療行為マスター一覧
    """
    return medical_action_service.get_active_medical_actions(
        db=db, target_date=target_date
    )
