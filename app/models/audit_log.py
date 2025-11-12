"""
監査ログ（AuditLog）モデル

重要な操作の監査ログを管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class AuditLog(Base):
    """
    監査ログモデル

    重要な操作（猫Status変更、譲渡決定、ユーザー登録・削除、
    マスターデータ変更等）の監査ログを記録します。

    Attributes:
        id: 主キー（自動採番）
        user_id: 操作者ID（外部キー、任意）
        action: 操作種別（必須、例: create_animal, update_status）
        target_type: 対象テーブル（必須、例: animals, users）
        target_id: 対象レコードID（任意）
        details: 詳細情報（JSON形式、任意）
        ip_address: IPアドレス（任意）
        user_agent: ユーザーエージェント（任意）
        created_at: 操作日時（自動設定）
    """

    __tablename__ = "audit_logs"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 操作者情報
    user_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="操作者ID",
    )

    # 操作情報
    action: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="操作種別（create_animal, update_status等）"
    )

    target_type: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="対象テーブル（animals, users等）"
    )

    target_id: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="対象レコードID"
    )

    details: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="詳細情報（JSON形式）"
    )

    # メタデータ
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True, comment="IPアドレス（IPv6対応）"
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="ユーザーエージェント"
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="操作日時",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_audit_logs_user_id", "user_id"),
        Index("ix_audit_logs_action", "action"),
        Index("ix_audit_logs_target_type", "target_type"),
        Index("ix_audit_logs_created_at", "created_at"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<AuditLog(id={self.id}, action={self.action!r}, "
            f"target_type={self.target_type!r}, target_id={self.target_id})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.created_at.strftime('%Y-%m-%d %H:%M:%S')} - {self.action}"
