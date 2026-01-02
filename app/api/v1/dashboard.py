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
from app.models.volunteer import Volunteer

router = APIRouter(prefix="/dashboard", tags=["ダッシュボード"])


class DashboardStats(BaseModel):
    """ダッシュボード統計情報"""

    protected_count: int = Field(..., description="保護中の猫数")
    adoptable_count: int = Field(..., description="譲渡可能な猫数")
    today_logs_count: int = Field(..., description="今日の記録数")
    active_volunteers_count: int = Field(..., description="アクティブボランティア数")
    total_animals: int = Field(..., description="総猫数")
    treatment_count: int = Field(..., description="治療中の猫数")


@router.get("/stats", response_model=DashboardStats)
def get_dashboard_stats(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> DashboardStats:
    """
    ダッシュボード統計情報を取得

    保護中の猫数、譲渡可能な猫数、今日の記録数、
    アクティブボランティア数などの統計情報を返します。

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

    protected_count = (
        db.query(func.count(Animal.id)).filter(Animal.status == "保護中").scalar() or 0
    )

    adoptable_count = (
        db.query(func.count(Animal.id)).filter(Animal.status == "譲渡可能").scalar()
        or 0
    )

    treatment_count = (
        db.query(func.count(Animal.id)).filter(Animal.status == "治療中").scalar() or 0
    )

    # 今日の記録数
    today = date.today()
    today_logs_count = (
        db.query(func.count(CareLog.id)).filter(CareLog.log_date == today).scalar() or 0
    )

    # アクティブボランティア数
    active_volunteers_count = (
        db.query(func.count(Volunteer.id)).filter(Volunteer.status == "active").scalar()
        or 0
    )

    return DashboardStats(
        protected_count=protected_count,
        adoptable_count=adoptable_count,
        today_logs_count=today_logs_count,
        active_volunteers_count=active_volunteers_count,
        total_animals=total_animals,
        treatment_count=treatment_count,
    )
