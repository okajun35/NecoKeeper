"""
ダッシュボードAPIエンドポイント

ダッシュボード用の統計情報を提供します。

Requirements: Requirement 16.1-16.4
"""

from __future__ import annotations

from datetime import date
from typing import Annotated

from fastapi import APIRouter, Depends
from pydantic import BaseModel, Field
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.database import get_db
from app.models.animal import Animal
from app.models.care_log import CareLog
from app.models.user import User
from app.utils.enums import AnimalStatus

router = APIRouter(prefix="/dashboard", tags=["ダッシュボード"])

# ステータス定義
RESIDENT_STATUSES = [
    AnimalStatus.QUARANTINE.value,
    AnimalStatus.IN_CARE.value,
    AnimalStatus.TRIAL.value,
]

ADOPTABLE_STATUSES = [
    AnimalStatus.IN_CARE.value,
    AnimalStatus.TRIAL.value,
]


class DashboardStats(BaseModel):
    """ダッシュボード統計情報"""

    resident_count: int = Field(..., description="在籍中の猫数")
    adoptable_count: int = Field(..., description="譲渡可能な猫数")
    today_logs_count: int = Field(..., description="今日の記録数")
    fiv_positive_count: int = Field(..., description="FIV陽性の猫数")
    felv_positive_count: int = Field(..., description="FeLV陽性の猫数")
    total_animals: int = Field(..., description="総猫数")
    treatment_count: int = Field(..., description="治療中の猫数")


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardStats:
    """
    ダッシュボード統計情報を取得

    在籍中の猫数、譲渡可能な猫数、今日の記録数、
    FIV陽性・FeLV陽性猫数などの統計情報を返します。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        DashboardStats: ダッシュボード統計情報

    Example:
        GET /api/v1/dashboard/stats
    """
    # 猫の統計
    total_animals = db.query(func.count(Animal.id)).scalar() or 0

    # 在籍中（QUARANTINE + IN_CARE + TRIAL）
    resident_count = (
        db.query(func.count(Animal.id))
        .filter(Animal.status.in_(RESIDENT_STATUSES))
        .scalar()
        or 0
    )

    # 譲渡可能（IN_CARE + TRIAL）
    adoptable_count = (
        db.query(func.count(Animal.id))
        .filter(Animal.status.in_(ADOPTABLE_STATUSES))
        .scalar()
        or 0
    )

    # 治療中（IN_CARE）
    treatment_count = (
        db.query(func.count(Animal.id))
        .filter(Animal.status == AnimalStatus.IN_CARE.value)
        .scalar()
        or 0
    )

    # FIV陽性（在籍中かつ FIV 陽性）
    fiv_positive_count = (
        db.query(func.count(Animal.id))
        .filter(
            Animal.status.in_(RESIDENT_STATUSES),
            Animal.fiv_positive == True,  # noqa: E712
        )
        .scalar()
        or 0
    )

    # FeLV陽性（在籍中かつ FeLV 陽性）
    felv_positive_count = (
        db.query(func.count(Animal.id))
        .filter(
            Animal.status.in_(RESIDENT_STATUSES),
            Animal.felv_positive == True,  # noqa: E712
        )
        .scalar()
        or 0
    )

    # 今日の記録数
    today = date.today()
    today_logs_count = (
        db.query(func.count(CareLog.id)).filter(CareLog.log_date == today).scalar() or 0
    )

    return DashboardStats(
        resident_count=resident_count,
        adoptable_count=adoptable_count,
        today_logs_count=today_logs_count,
        fiv_positive_count=fiv_positive_count,
        felv_positive_count=felv_positive_count,
        total_animals=total_animals,
        treatment_count=treatment_count,
    )
