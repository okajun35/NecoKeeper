"""
診療記録（MedicalRecord）モデル

獣医による診療記録を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class MedicalRecord(Base):
    """
    診療記録モデル

    獣医による診療内容（体重、体温、症状、診療行為など）を管理します。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        vet_id: 獣医師ID（外部キー）
        date: 診療日（必須）
        time_slot: 時間帯（任意）
        weight: 体重（kg、必須）
        temperature: 体温（℃、任意）
        symptoms: 症状（必須）
        medical_action_id: 診療行為ID（外部キー、任意）
        dosage: 投薬量・回数（任意）
        other: その他（ロット番号等、任意）
        comment: コメント（任意）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
        last_updated_at: 最終更新日時（自動更新）
        last_updated_by: 最終更新者ID（外部キー、任意）
    """

    __tablename__ = "medical_records"

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

    vet_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
        comment="獣医師ID",
    )

    # 診療情報
    date: Mapped[date] = mapped_column(Date, nullable=False, comment="診療日")

    time_slot: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="時間帯"
    )

    weight: Mapped[Decimal] = mapped_column(
        Numeric(5, 2), nullable=False, comment="体重（kg、小数点2桁）"
    )

    temperature: Mapped[Decimal | None] = mapped_column(
        Numeric(4, 1), nullable=True, comment="体温（℃、小数点1桁）"
    )

    symptoms: Mapped[str] = mapped_column(Text, nullable=False, comment="症状")

    # 診療行為
    medical_action_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("medical_actions.id", ondelete="SET NULL"),
        nullable=True,
        comment="診療行為ID（マスターテーブル）",
    )

    dosage: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="投薬量・回数"
    )

    other: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="その他（ロット番号等）"
    )

    comment: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="コメント"
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="作成日時",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="更新日時",
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        onupdate=func.now(),
        comment="最終更新日時",
    )

    last_updated_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="最終更新者ID",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_medical_records_animal_id", "animal_id"),
        Index("ix_medical_records_date", "date"),
        Index("ix_medical_records_vet_id", "vet_id"),
        Index("ix_medical_records_medical_action_id", "medical_action_id"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<MedicalRecord(id={self.id}, animal_id={self.animal_id}, "
            f"date={self.date}, weight={self.weight})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.date} - 体重: {self.weight}kg"
