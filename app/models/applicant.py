"""
里親希望者（Applicant）モデル

Issue #91: 譲渡記録の充実化
里親希望者と申込フォームの詳細情報を管理するORMモデルです。
"""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    CheckConstraint,
    DateTime,
    Float,
    ForeignKey,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.utils.timezone import get_jst_now

if TYPE_CHECKING:
    pass


class Applicant(Base):
    """
    里親希望者モデル（拡張版）

    Issue #91に基づき、猫の里親を希望する人の詳細情報を管理します。

    Attributes:
        # 基本情報（旧フィールド - 後方互換性）
        id: 主キー（自動採番）
        name: 氏名（必須）
        contact: 連絡先（必須）- 後方互換用
        address: 住所（任意）- 後方互換用
        family: 家族構成（任意）- 後方互換用
        environment: 飼育環境（任意）- 後方互換用
        conditions: 希望条件（任意）- 後方互換用

        # 拡張フィールド（Issue #91）
        name_kana: ふりがな
        age: 年齢
        phone: 電話番号
        contact_type: 連絡手段（line/email）
        contact_line_id: LINE ID
        contact_email: メールアドレス
        postal_code: 郵便番号
        address1: 住所1
        address2: 住所2
        occupation: 職業
        occupation_other: 職業その他
        desired_cat_alias: 希望猫の仮名
        emergency_*: 緊急連絡先
        family_intent: 家族の飼育意向
        pet_permission: ペット飼育可否
        pet_limit_*: ペット上限
        housing_*: 住居情報
        relocation_*: 転居予定
        allergy_status: アレルギー
        smoker_in_household: 喫煙者
        monthly_budget_yen: 月々の予算
        alone_time_*: お留守番
        has_existing_cat: 先住猫
        has_other_pets: その他ペット
    """

    __tablename__ = "applicants"

    # 主キー
    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    # ========================================
    # 旧フィールド（後方互換性のため維持）
    # ========================================
    name: Mapped[str] = mapped_column(String(100), nullable=False, comment="氏名")

    contact: Mapped[str] = mapped_column(
        String(255), nullable=False, default="", comment="連絡先（後方互換用）"
    )

    address: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="住所（後方互換用）"
    )

    family: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="家族構成（後方互換用）"
    )

    environment: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="飼育環境（後方互換用）"
    )

    conditions: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="希望条件（後方互換用）"
    )

    # ========================================
    # 拡張フィールド（Issue #91）
    # ========================================

    # 基本情報
    name_kana: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="ふりがな"
    )

    age: Mapped[int | None] = mapped_column(Integer, nullable=True, comment="年齢")

    phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="電話番号"
    )

    # 連絡手段
    contact_type: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="連絡手段（line/email）"
    )

    contact_line_id: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="LINE ID"
    )

    contact_email: Mapped[str | None] = mapped_column(
        String(255), nullable=True, comment="メールアドレス"
    )

    # 住所（詳細）
    postal_code: Mapped[str | None] = mapped_column(
        String(20), nullable=True, comment="郵便番号"
    )

    address1: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="住所1（都道府県・市区町村・番地）"
    )

    address2: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="住所2（建物名・部屋番号）"
    )

    # 職業
    occupation: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="職業（company_employee/public_servant/self_employed/other）",
    )

    occupation_other: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="職業（その他の場合の詳細）"
    )

    # 希望猫
    desired_cat_alias: Mapped[str | None] = mapped_column(
        String(100), nullable=True, default="未定", comment="希望猫の仮名"
    )

    # 緊急連絡先
    emergency_relation: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="緊急連絡先続柄（parents/siblings/other）"
    )

    emergency_relation_other: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="緊急連絡先続柄（その他の場合の詳細）"
    )

    emergency_name: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="緊急連絡先氏名"
    )

    emergency_phone: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="緊急連絡先電話番号"
    )

    # 家族の飼育意向
    family_intent: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="家族の飼育意向（all_positive/some_not_positive/single_household）",
    )

    # ペット飼育可否
    pet_permission: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="ペット飼育可否（allowed/not_allowed/tolerated）",
    )

    pet_limit_type: Mapped[str | None] = mapped_column(
        String(50),
        nullable=True,
        comment="ペット上限タイプ（limited/unlimited/unknown）",
    )

    pet_limit_count: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="ペット上限数"
    )

    # 住居
    housing_type: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="住居形態（house/apartment/other）"
    )

    housing_ownership: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="住居所有（owned/rented）"
    )

    # 転居予定
    relocation_plan: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="転居予定（none/planned）"
    )

    relocation_time_note: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="転居時期"
    )

    relocation_cat_plan: Mapped[str | None] = mapped_column(
        Text, nullable=True, comment="転居時の猫の処遇"
    )

    # アレルギー
    allergy_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="アレルギー（none/exists/unknown）"
    )

    # 喫煙者
    smoker_in_household: Mapped[str | None] = mapped_column(
        String(10), nullable=True, comment="喫煙者（yes/no）"
    )

    # 月々の予算
    monthly_budget_yen: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="月々の猫にかける予算（円）"
    )

    # お留守番
    alone_time_status: Mapped[str | None] = mapped_column(
        String(50), nullable=True, comment="お留守番（none/sometimes/regular）"
    )

    alone_time_weekly_days: Mapped[int | None] = mapped_column(
        Integer, nullable=True, comment="お留守番週何回"
    )

    alone_time_hours: Mapped[float | None] = mapped_column(
        Float, nullable=True, comment="お留守番1回あたり時間"
    )

    # 先住猫・ペット
    has_existing_cat: Mapped[str | None] = mapped_column(
        String(10), nullable=True, comment="先住猫（yes/no）"
    )

    has_other_pets: Mapped[str | None] = mapped_column(
        String(10), nullable=True, comment="その他ペット（yes/no）"
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

    # リレーション
    household_members: Mapped[list[ApplicantHouseholdMember]] = relationship(
        "ApplicantHouseholdMember",
        back_populates="applicant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    pets: Mapped[list[ApplicantPet]] = relationship(
        "ApplicantPet",
        back_populates="applicant",
        cascade="all, delete-orphan",
        lazy="selectin",
    )

    # インデックス定義
    __table_args__ = (
        Index("ix_applicants_name", "name"),
        Index("ix_applicants_contact", "contact"),
        Index("ix_applicants_name_kana", "name_kana"),
        Index("ix_applicants_phone", "phone"),
        # NOTE: CHECK制約はSQLiteのALTER TABLEで追加不可のためアプリケーション層で担保
        # 連絡手段の整合性はサービス層の_validate_contact_infoで検証
    )

    def __repr__(self) -> str:
        """文字列表現"""
        return f"<Applicant(id={self.id}, name={self.name!r})>"

    def __str__(self) -> str:
        """人間が読みやすい文字列表現"""
        return self.name


class ApplicantHouseholdMember(Base):
    """
    家族構成モデル

    里親希望者の家族メンバー情報を管理します。

    Attributes:
        id: 主キー
        applicant_id: 里親希望者ID（外部キー）
        relation: 続柄（husband/wife/father/mother/son/daughter/other）
        relation_other: 続柄（その他の場合の詳細）
        age: 年齢
    """

    __tablename__ = "applicant_household_members"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    applicant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("applicants.id", ondelete="CASCADE"),
        nullable=False,
        comment="里親希望者ID",
    )

    relation: Mapped[str] = mapped_column(
        String(50),
        nullable=False,
        comment="続柄（husband/wife/father/mother/son/daughter/other）",
    )

    relation_other: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="続柄（その他の場合の詳細）"
    )

    age: Mapped[int] = mapped_column(Integer, nullable=False, comment="年齢")

    # リレーション
    applicant: Mapped[Applicant] = relationship(
        "Applicant", back_populates="household_members"
    )

    # インデックス・制約
    __table_args__ = (
        Index("ix_applicant_household_members_applicant_id", "applicant_id"),
        CheckConstraint(
            "relation IN ('husband','wife','father','mother','son','daughter','other')",
            name="ck_household_member_relation",
        ),
    )

    def __repr__(self) -> str:
        return f"<ApplicantHouseholdMember(id={self.id}, relation={self.relation!r}, age={self.age})>"


class ApplicantPet(Base):
    """
    先住ペットモデル

    里親希望者の先住ペット情報を管理します。

    Attributes:
        id: 主キー
        applicant_id: 里親希望者ID（外部キー）
        pet_category: ペット種別（cat/other）
        count: 頭数
        breed_or_type: 品種・種類
        age_note: 年齢（自由表現）
    """

    __tablename__ = "applicant_pets"

    id: Mapped[int] = mapped_column(
        Integer, primary_key=True, autoincrement=True, comment="主キー"
    )

    applicant_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("applicants.id", ondelete="CASCADE"),
        nullable=False,
        comment="里親希望者ID",
    )

    pet_category: Mapped[str] = mapped_column(
        String(50), nullable=False, comment="ペット種別（cat/other）"
    )

    count: Mapped[int] = mapped_column(
        Integer, nullable=False, default=1, comment="頭数"
    )

    breed_or_type: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="品種・種類"
    )

    age_note: Mapped[str | None] = mapped_column(
        String(100), nullable=True, comment="年齢（自由表現：3歳、推定2歳など）"
    )

    # リレーション
    applicant: Mapped[Applicant] = relationship("Applicant", back_populates="pets")

    # インデックス・制約
    __table_args__ = (
        Index("ix_applicant_pets_applicant_id", "applicant_id"),
        CheckConstraint(
            "pet_category IN ('cat','other')", name="ck_applicant_pet_category"
        ),
    )
