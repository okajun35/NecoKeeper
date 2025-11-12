"""
ボランティア（Volunteer）モデル

記録者（ボランティア）を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Volunteer(Base):
    """
    ボランティアモデル

    世話記録を入力するボランティア記録者を管理します。
    Publicフォームの記録者選択リストに表示されます。

    Attributes:
        id: 主キー（自動採番）
        name: 氏名（必須）
        contact: 連絡先（任意）
        affiliation: 所属（任意）
        status: 活動状態（active/inactive、デフォルト: active）
        started_at: 活動開始日（デフォルト: 本日）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "volunteers"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # ボランティア情報
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="氏名")

    contact: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="連絡先（電話番号、メールアドレス等）"
    )

    affiliation: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="所属（団体名等）"
    )

    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        server_default="active",
        comment="活動状態（active/inactive）",
    )

    started_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        server_default=func.current_date(),
        comment="活動開始日",
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

    # インデックス定義
    __table_args__ = (
        Index("ix_volunteers_status", "status"),
        Index("ix_volunteers_name", "name"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<Volunteer(id={self.id}, name={self.name!r}, " f"status={self.status!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.name}（{self.status}）"

    def is_active(self) -> bool:
        """
        アクティブ状態かチェック

        Returns:
            bool: アクティブな場合True
        """
        return self.status == "active"
