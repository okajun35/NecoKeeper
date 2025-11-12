"""
猫画像ギャラリー（AnimalImage）モデル

猫の複数画像を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime

from sqlalchemy import Date, DateTime, ForeignKey, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.database import Base


class AnimalImage(Base):
    """
    猫画像ギャラリーモデル

    猫の複数画像（最大20枚）を管理します。
    顔写真以外の追加画像を保存します。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        image_path: 画像ファイルパス（必須）
        taken_at: 撮影日（任意）
        description: 説明（任意）
        file_size: ファイルサイズ（bytes、デフォルト: 0）
        created_at: 作成日時（自動設定）
    """

    __tablename__ = "animal_images"

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

    # 画像情報
    image_path: Mapped[str] = mapped_column(
        String(255), nullable=False, comment="画像ファイルパス"
    )

    taken_at: Mapped[date | None] = mapped_column(
        Date, nullable=True, comment="撮影日"
    )

    description: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="説明"
    )

    file_size: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        server_default="0",
        comment="ファイルサイズ（bytes）",
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        server_default=func.now(),
        comment="作成日時",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_animal_images_animal_id", "animal_id"),
        Index("ix_animal_images_taken_at", "taken_at"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<AnimalImage(id={self.id}, animal_id={self.animal_id}, "
            f"image_path={self.image_path!r})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        if self.taken_at:
            return f"画像 ({self.taken_at})"
        else:
            return f"画像 (ID: {self.id})"

    def get_file_size_mb(self) -> float:
        """
        ファイルサイズをMB単位で取得

        Returns:
            float: ファイルサイズ（MB）
        """
        return self.file_size / (1024 * 1024)
