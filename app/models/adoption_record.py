"""
譲渡記録（AdoptionRecord）モデル

猫の譲渡プロセスと記録を管理するORMモデルです。
"""

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class AdoptionRecord(Base):
    """
    譲渡記録モデル

    猫の譲渡プロセス（面談、判定、譲渡、フォロー）を管理します。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        applicant_id: 里親希望者ID（外部キー）
        interview_date: 面談日（任意）
        interview_note: 面談内容（任意）
        decision: 判定結果（approved/rejected/pending、任意）
        adoption_date: 譲渡日（任意）
        follow_up: 譲渡後フォロー（任意）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "adoption_records"

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

    applicant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("applicants.id", ondelete="RESTRICT"),
        nullable=False,
        comment="里親希望者ID",
    )

    # 面談情報
    interview_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="面談日"
    )

    interview_note: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="面談内容"
    )

    decision: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="判定結果（approved/rejected/pending）"
    )

    # 譲渡情報
    adoption_date: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="譲渡日"
    )

    follow_up: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="譲渡後フォロー"
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        server_default=func.current_timestamp(),
        comment="作成日時",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=datetime.now,
        onupdate=datetime.now,
        server_default=func.current_timestamp(),
        server_onupdate=func.current_timestamp(),
        comment="更新日時",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_adoption_records_animal_id", "animal_id"),
        Index("ix_adoption_records_applicant_id", "applicant_id"),
        Index("ix_adoption_records_adoption_date", "adoption_date"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<AdoptionRecord(id={self.id}, animal_id={self.animal_id}, "
            f"applicant_id={self.applicant_id}, decision={self.decision!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        if self.adoption_date:
            return f"譲渡済み（{self.adoption_date}）"
        elif self.decision == "approved":
            return "承認済み"
        elif self.decision == "rejected":
            return "不承認"
        else:
            return "審査中"
