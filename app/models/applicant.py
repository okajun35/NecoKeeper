"""
里親希望者（Applicant）モデル

里親希望者を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base
from app.utils.timezone import get_jst_now


class Applicant(Base):
    """
    里親希望者モデル

    猫の里親を希望する人の情報を管理します。

    Attributes:
        id: 主キー（自動採番）
        name: 氏名（必須）
        contact: 連絡先（必須）
        address: 住所（任意）
        family: 家族構成（任意）
        environment: 飼育環境（任意）
        conditions: 希望条件（任意）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "applicants"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 基本情報
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="氏名")

    contact: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="連絡先（電話番号、メールアドレス等）"
    )

    address: Mapped[str | None] = mapped_column(Text, nullable=True, comment="住所")

    family: Mapped[str | None] = mapped_column(Text, nullable=True, comment="家族構成")

    environment: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="飼育環境"
    )

    conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="希望条件"
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_jst_now,
        comment="作成日時（JST）",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=get_jst_now,
        onupdate=get_jst_now,
        comment="更新日時（JST）",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_applicants_name", "name"),
        Index("ix_applicants_contact", "contact"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return f"<Applicant(id={self.id}, name={self.name!r})>"

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return self.name
