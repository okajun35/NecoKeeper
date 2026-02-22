"""
里親相談（AdoptionConsultation）モデル

里親相談の受付情報を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.timezone import get_jst_now

if TYPE_CHECKING:
    from app.models.applicant import Applicant


class AdoptionConsultation(Base):
    """
    里親相談モデル

    相談時点の最小情報（ふりがな・氏名・電話・連絡手段・相談内容）を保持します。
    """

    __tablename__ = "adoption_consultations"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )
    name_kana: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="ふりがな"
    )
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="氏名")
    phone: Mapped[str] = mapped_column(String(50), nullable=False, comment="電話番号")
    contact_type: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="連絡手段（line/email）"
    )
    contact_line_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="LINE ID"
    )
    contact_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="メールアドレス"
    )
    consultation_note: Mapped[str] = mapped_column(
        Text, nullable=False, comment="相談内容"
    )
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="open",
        server_default="open",
        comment="相談ステータス（open/converted/closed）",
    )
    applicant_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("applicants.id", ondelete="SET NULL"),
        nullable=True,
        comment="変換先の里親申込ID",
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_jst_now,
        nullable=False,
        comment="作成日時（JST）",
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_jst_now,
        onupdate=get_jst_now,
        nullable=False,
        comment="更新日時（JST）",
    )

    applicant: Mapped[Applicant | None] = relationship(
        "Applicant",
        back_populates="consultations",
        lazy="joined",
    )

    __table_args__ = (
        Index("ix_adoption_consultations_name", "name"),
        Index("ix_adoption_consultations_phone", "phone"),
        Index("ix_adoption_consultations_status", "status"),
        Index("ix_adoption_consultations_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        return (
            f"<AdoptionConsultation(id={self.id}, name={self.name!r}, "
            f"status={self.status!r})>"
        )
