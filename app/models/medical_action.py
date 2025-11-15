"""
診療行為マスター（MedicalAction）モデル

診療行為（薬剤、ワクチン、検査等）のマスターデータを管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class MedicalAction(Base):
    """
    診療行為マスターモデル

    診療行為（薬剤、ワクチン、検査、処置等）のマスターデータを管理します。
    期間別の価格管理と通貨単位に対応しています。

    Attributes:
        id: 主キー（自動採番）
        name: 診療名称（必須、例: ワクチン、駆虫薬、血液検査）
        valid_from: 適用開始日（必須）
        valid_to: 適用終了日（任意）
        cost_price: 原価（小数点2桁、デフォルト: 0.00）
        selling_price: 請求価格（小数点2桁、デフォルト: 0.00）
        procedure_fee: 投薬・処置料金（小数点2桁、デフォルト: 0.00）
        currency: 通貨単位（JPY/USD、デフォルト: JPY）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
        last_updated_at: 最終更新日時（自動更新）
        last_updated_by: 最終更新者ID（外部キー、任意）

    Note:
        料金計算式: 実際の請求価格 = (請求価格 × 投薬量) + 投薬・処置料金
    """

    __tablename__ = "medical_actions"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 診療行為情報
    name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="診療名称（薬剤、ワクチン、検査等）"
    )

    # 適用期間
    valid_from: Mapped[date] = mapped_column(Date, nullable=False, comment="適用開始日")

    valid_to: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="適用終了日"
    )

    # 価格情報
    cost_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="原価（小数点2桁）",
    )

    selling_price: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="請求価格（小数点2桁）",
    )

    procedure_fee: Mapped[Decimal] = mapped_column(
        Numeric(10, 2),
        nullable=False,
        default=Decimal("0.00"),
        server_default="0.00",
        comment="投薬・処置料金（小数点2桁）",
    )

    currency: Mapped[str] = mapped_column(
        String(3),
        nullable=False,
        default="JPY",
        server_default="JPY",
        comment="通貨単位（JPY/USD）",
    )

    unit: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="投薬単位（ml、錠、回等）",
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
        Index("ix_medical_actions_name", "name"),
        Index("ix_medical_actions_valid_from", "valid_from"),
        Index("ix_medical_actions_valid_to", "valid_to"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<MedicalAction(id={self.id}, name={self.name!r}, "
            f"selling_price={self.selling_price}, currency={self.currency!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.name}（{self.selling_price} {self.currency}）"

    def calculate_total_price(self, dosage: int = 1) -> Decimal:
        """
        合計請求価格を計算

        Args:
            dosage: 投薬量・回数（デフォルト: 1）

        Returns:
            Decimal: 合計請求価格

        Note:
            計算式: (請求価格 × 投薬量) + 投薬・処置料金
        """
        return (self.selling_price * dosage) + self.procedure_fee

    def is_valid_on(self, target_date: date) -> bool:
        """
        指定日に有効な診療行為かチェック

        Args:
            target_date: チェック対象日

        Returns:
            bool: 有効な場合True
        """
        if target_date < self.valid_from:
            return False
        return not (self.valid_to and target_date > self.valid_to)
