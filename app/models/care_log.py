"""
世話記録（CareLog）モデル

日々の世話記録を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    SmallInteger,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.timezone import get_jst_date, get_jst_now

if TYPE_CHECKING:
    from app.models.animal import Animal


class CareLog(Base):
    """
    世話記録モデル

    猫の日々の世話記録（食欲、元気、排尿、清掃など）を管理します。
    ボランティアがPublicフォームから入力した記録を保存します。

    Attributes:
        id: 主キー（自動採番）
        animal_id: 猫ID（外部キー）
        recorder_id: 記録者ID（外部キー、任意）
        recorder_name: 記録者名（必須）
        time_slot: 時点（morning/noon/evening）
        appetite: 食欲（1〜5段階、5が最良、デフォルト: 3）
        energy: 元気（1〜5段階、5が最良、デフォルト: 3）
        urination: 排尿有無（True=有り、False=無し）
        defecation: 排便有無（True=有り、False=無し）
        stool_condition: 便の状態（1〜5、排便が有りの場合のみ）
        cleaning: 清掃済み（True=済、False=未）
        memo: メモ（任意）
        ip_address: IPアドレス（記録時の接続元）
        user_agent: ユーザーエージェント（ブラウザ情報）
        device_tag: デバイスタグ（端末識別用）
        from_paper: 紙記録からの転記フラグ
        created_at: 記録日時（自動設定）
        last_updated_at: 最終更新日時（自動更新）
        last_updated_by: 最終更新者ID（外部キー、任意）
    """

    __tablename__ = "care_logs"

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

    recorder_id: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("volunteers.id", ondelete="SET NULL"),
        nullable=True,
        comment="記録者ID（ボランティアテーブル）",
    )

    # 記録者情報
    recorder_name: Mapped[str] = mapped_column(
        String(100), nullable=False, comment="記録者名"
    )

    # 記録内容
    log_date: Mapped[date] = mapped_column(
        Date,
        nullable=False,
        default=get_jst_date,
        comment="記録日（年月日、JST）",
    )

    time_slot: Mapped[str] = mapped_column(
        String(10), nullable=False, comment="時点（morning/noon/evening）"
    )

    appetite: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
        comment="食欲（1〜5段階、5が最良）",
    )

    energy: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=3,
        server_default="3",
        comment="元気（1〜5段階、5が最良）",
    )

    urination: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="排尿有無（True=有り、False=無し）",
    )

    defecation: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="排便有無（True=有り、False=無し）",
    )

    stool_condition: Mapped[int | None] = mapped_column(
        SmallInteger,
        nullable=True,
        comment="便の状態（1〜5、排便が有りの場合のみ）",
    )

    cleaning: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="清掃済み（True=済、False=未）",
    )

    memo: Mapped[str | None] = mapped_column(Text, nullable=True, comment="メモ")

    # メタデータ（記録時の情報）
    ip_address: Mapped[str | None] = mapped_column(
        String(45), nullable=True, comment="IPアドレス（IPv6対応）"
    )

    user_agent: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="ユーザーエージェント"
    )

    device_tag: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="デバイスタグ（端末識別用）"
    )

    from_paper: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        default=False,
        server_default="0",
        comment="紙記録からの転記フラグ",
    )

    # タイムスタンプ
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        comment="記録日時（JST）",
    )

    last_updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        default=get_jst_now,
        onupdate=get_jst_now,
        comment="最終更新日時（JST）",
    )

    last_updated_by: Mapped[int | None] = mapped_column(
        Integer,
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
        comment="最終更新者ID（管理者による修正時）",
    )

    # リレーションシップ
    animal: Mapped[Animal] = relationship("Animal", back_populates="care_logs")

    # インデックス定義
    __table_args__ = (
        Index("ix_care_logs_animal_id", "animal_id"),
        Index("ix_care_logs_log_date", "log_date"),
        Index("ix_care_logs_created_at", "created_at"),
        Index("ix_care_logs_recorder_id", "recorder_id"),
        Index("ix_care_logs_time_slot", "time_slot"),
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return (
            f"<CareLog(id={self.id}, animal_id={self.animal_id}, "
            f"recorder_name={self.recorder_name!r}, time_slot={self.time_slot!r}, "
            f"created_at={self.created_at})>"
        )

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return (
            f"{self.created_at.strftime('%Y-%m-%d %H:%M')} - "
            f"{self.recorder_name}（{self.time_slot}）"
        )
