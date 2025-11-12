"""
ステータス変更履歴（StatusHistory）モデル

猫のステータス変更履歴を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class StatusHistory(Base):
    """
    ステータス変更履歴モデル

    猫のステータス変更（保護中→譲渡可能→譲渡済み等）の履歴を記録します。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        old_status: 変更前ステータス（任意）
        new_status: 変更後ステータス（必須）
        reason: 変更理由（任意）
        changed_by: 変更者ID（外部キー、任意）
        changed_at: 変更日時（自動設定）
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

    # ステータス変更情報
    old_status: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="変更前ステータス"
    )

    new_status: Mapped[str] = mapped_column(
        String(20), nullable=False, comment="変更後ステータス"
    )

    reason: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="変更理由"
    )

    changed_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="変更者ID",
    )

    changed_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="変更日時",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_status_history_animal_id", "animal_id"),
        Index("ix_status_history_changed_at", "changed_at"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<StatusHistory(id={self.id}, animal_id={self.animal_id}, "
            f"old_status={self.old_status!r}, new_status={self.new_status!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        if self.old_status:
            return f"{self.old_status} → {self.new_status}"
        else:
            return f"初期状態: {self.new_status}"
