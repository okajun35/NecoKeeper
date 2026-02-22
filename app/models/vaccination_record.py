"""
ワクチン接種記録（VaccinationRecord）モデル

Issue #83: プロフィールに医療情報を追加
ワクチン接種履歴を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.timezone import get_jst_now

if TYPE_CHECKING:
    from app.models.animal import Animal


class VaccinationRecord(Base):
    """
    ワクチン接種記録モデル

    猫のワクチン接種履歴を管理します。
    「どの病気のワクチンを打ったか」ではなく「どのワクチンを打ったか」を記録する設計。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        vaccine_category: ワクチン種別（3core/4core/5core）
        administered_on: 接種日（核となるフィールド）
        next_due_on: 次回予定日（任意、自動計算なし）
        memo: 備考（ロット番号等）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "vaccination_records"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 外部キー
    animal_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("animals.id", ondelete="CASCADE"),
        nullable=False,
        comment="猫ID",
    )

    # ワクチン情報
    vaccine_category: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        comment="ワクチン種別（3core/4core/5core）",
    )

    administered_on: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        comment="接種日",
    )

    next_due_on: Mapped[date | None] = mapped_column(
        Date,
        nullable=True,
        comment="次回予定日（任意）",
    )

    memo: Mapped[str | None] = mapped_column(
        Text,
        nullable=True,
        comment="備考（ロット番号等）",
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        comment="作成日時（JST）",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        onupdate=get_jst_now,
        comment="更新日時（JST）",
    )

    # リレーションシップ
    animal: Mapped[Animal] = relationship(
        "Animal", back_populates="vaccination_records"
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_vaccination_records_animal_id", "animal_id"),
        Index("ix_vaccination_records_administered_on", "administered_on"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<VaccinationRecord(id={self.id}, animal_id={self.animal_id}, "
            f"vaccine_category={self.vaccine_category!r}, "
            f"administered_on={self.administered_on})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.vaccine_category} - {self.administered_on}"
