"""
設定（Setting）モデル

システム設定を管理するORMモデルです。
"""

from datetime import datetime

from sqlalchemy import DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class Setting(Base):
    """
    設定モデル

    システム全体の設定（団体情報、画像制限、言語設定等）を
    キー・バリュー形式で管理します。

    Attributes:
        id: 主キー（自動採番）
        key: 設定キー（ユニーク、必須）
        value: 設定値（任意）
        description: 説明（任意）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "settings"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 設定情報
    key: Mapped[str] = mapped_column(
        String(100), nullable=False, unique=True, comment="設定キー（ユニーク）"
    )

    value: Mapped[str | None] = mapped_column(Text, nullable=True, comment="設定値")

    description: Mapped[str | None] = mapped_column(Text, nullable=True, comment="説明")

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
    __table_args__ = (Index("ix_settings_key", "key", unique=True),)

    def __repr__(self) -> str:
        """文字列表現"""
        return f"<Setting(id={self.id}, key={self.key!r}, value={self.value!r})>"

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return f"{self.key}: {self.value}"
