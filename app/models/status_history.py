"""
ステータス変更履歴（StatusHistory）モデル

猫のステータス変更履歴を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.timezone import get_jst_now


class StatusHistory(Base):
    """
    変更履歴モデル（汎用化）

    猫のステータス・ロケーションタイプ変更履歴を一元管理。
    初期対応: status と location_type を記録。
    将来: 他フィールド変更にも対応可能。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        field: 変更対象フィールド（'status' or 'location_type'）
        old_value: 変更前値（任意）
        new_value: 変更後値（必須）
        reason: 変更理由（任意）
        changed_by: 変更者ID（外部キー、任意）
        changed_at: 変更日時（自動設定）

        【廃止予定列】（互換性のため暫定保持）
        old_status: 廃止予定（new_value に統一）
        new_status: 廃止予定（old_value に統一）
    """

    __tablename__ = "status_history"

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

    # 変更対象フィールド（汎用化）
    field: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="変更対象フィールド（'status' or 'location_type'）",
    )

    # 変更前後の値（汎用化）
    old_value: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="変更前値"
    )

    new_value: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="変更後値"
    )

    # ステータス変更情報（廃止予定・互換性保持）
    old_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="変更前ステータス（廃止予定。old_value を使用）",
    )

    new_status: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        comment="変更後ステータス（廃止予定。new_value を使用）",
    )

    reason: Mapped[str | None] = mapped_column(Text, nullable=True, comment="変更理由")

    changed_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="変更者ID",
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        comment="変更日時（JST）",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_status_history_animal_id", "animal_id"),
        Index("ix_status_history_field", "field"),
        Index("ix_status_history_changed_at", "changed_at"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<StatusHistory(id={self.id}, animal_id={self.animal_id}, "
            f"field={self.field!r}, old_value={self.old_value!r}, "
            f"new_value={self.new_value!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        if self.old_value:
            return f"{self.field}: {self.old_value} → {self.new_value}"
        else:
            return f"{self.field}: 初期値 = {self.new_value}"
