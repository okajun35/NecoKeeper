"""
猫（Animal）モデル

保護猫の個体情報を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import Boolean, Date, DateTime, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.timezone import get_jst_date, get_jst_now

if TYPE_CHECKING:
    from app.models.care_log import CareLog


class Animal(Base):
    """
    猫マスターモデル

    保護猫の個体情報を管理します。
    各猫は一意のIDで識別され、顔写真、柄・色、尻尾の長さなどの
    物理的特徴と、ステータス、保護日などの管理情報を持ちます。

    Attributes:
        id: 主キー（自動採番）
        name: 猫の名前（任意）
        photo: 顔写真のファイルパス（必須）
        microchip_number: マイクロチップ番号（任意、15桁の半角数字または10桁の英数字）
        pattern: 柄・色（必須、例: キジトラ、三毛、黒猫）
        tail_length: 尻尾の長さ（必須、例: 長い、短い、なし）
        collar: 首輪の有無と色（任意、例: 赤い首輪、首輪なし）
        age_months: 月齢（任意、null=不明）
        age_is_estimated: 推定月齢フラグ（デフォルト: False）
        gender: 性別（必須、male/female/unknown）
        ear_cut: 耳カットの有無（デフォルト: False）
        features: 外傷・特徴・性格（任意、自由記述）
        status: ステータス（デフォルト: '保護中'）
        protected_at: 保護日（デフォルト: 本日）
        created_at: 作成日時（自動設定）
        updated_at: 更新日時（自動更新）
    """

    __tablename__ = "animals"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # 基本情報
    name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="猫の名前"
    )

    photo: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="プロフィール画像のファイルパス（任意）"
    )

    microchip_number: Mapped[str | None] = mapped_column(
        String(20),
        nullable=True,
        unique=True,
        comment="マイクロチップ番号（15桁の半角数字、または10桁の英数字）",
    )

    # 物理的特徴（識別情報）
    pattern: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="柄・色（例: キジトラ、三毛、黒猫）"
    )

    tail_length: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="尻尾の長さ（例: 長い、短い、なし）"
    )

    collar: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="首輪の有無と色（例: 赤い首輪、首輪なし）"
    )

    age_months: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="月齢（null=不明）"
    )

    age_is_estimated: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="推定月齢フラグ",
    )

    gender: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="性別（male/female/unknown）"
    )

    ear_cut: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="耳カットの有無（TNR済みの印）",
    )

    features: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="外傷・特徴・性格（自由記述）"
    )

    rescue_source: Mapped[str | None] = mapped_column(
        String(200), nullable=True, comment="レスキュー元"
    )

    breed: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="品種"
    )

    # 管理情報
    status: Mapped[str] = mapped_column(
        String(20),
        nullable=False,
        default="保護中",
        server_default="保護中",
        comment="ステータス（保護中、譲渡可能、譲渡済み、治療中など）",
    )

    protected_at: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=get_jst_date,
        comment="保護日（JST）",
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        comment="作成日時（JST）",
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        onupdate=get_jst_now,
        comment="更新日時（JST）",
    )

    # リレーションシップ
    care_logs: Mapped[list[CareLog]] = relationship(
        "CareLog", back_populates="animal", cascade="all, delete-orphan"
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_animals_status", "status"),
        Index("ix_animals_protected_at", "protected_at"),
        Index("ix_animals_name", "name"),
        Index("ix_animals_microchip_number", "microchip_number"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return f"<Animal(id={self.id}, name={self.name!r}, pattern={self.pattern!r}, status={self.status!r})>"

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        name_display = self.name if self.name else "名前未設定"
        return f"{name_display}（{self.pattern}、{self.status}）"
