"""
里親管理（Adoption）Pydanticスキーマ

Issue #91: 譲渡記録の充実化
里親希望者と譲渡記録のバリデーションスキーマです。
"""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Literal

from pydantic import BaseModel, ConfigDict, Field, model_validator

# ========================================
# Applicant（里親希望者）スキーマ - 既存（後方互換）
# ========================================


class ApplicantBase(BaseModel):
    """里親希望者の共通フィールド（後方互換用）"""

    name: str = Field(..., max_length=100, description="氏名")
    contact: str = Field(..., max_length=255, description="連絡先")
    address: str | None = Field(None, description="住所")
    family: str | None = Field(None, description="家族構成")
    environment: str | None = Field(None, description="飼育環境")
    conditions: str | None = Field(None, description="希望条件")


class ApplicantResponse(ApplicantBase):
    """里親希望者レスポンススキーマ（後方互換用）"""

    id: int = Field(..., description="里親希望者ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# ========================================
# 拡張Applicant（里親申込）スキーマ - Issue #91
# ========================================


# 選択肢の型定義
ContactType = Literal["line", "email"]
ConsultationStatusType = Literal["open", "converted", "closed"]
IntakeRequestType = Literal["all", "application", "consultation"]
IntakeEntryType = Literal["application", "consultation", "both"]
OccupationType = Literal["company_employee", "public_servant", "self_employed", "other"]
EmergencyRelationType = Literal["parents", "siblings", "other"]
FamilyIntentType = Literal["all_positive", "some_not_positive", "single_household"]
PetPermissionType = Literal["allowed", "not_allowed", "tolerated"]
PetLimitType = Literal["limited", "unlimited", "unknown"]
HousingType = Literal["house", "apartment", "other"]
HousingOwnershipType = Literal["owned", "rented"]
RelocationPlanType = Literal["none", "planned"]
AllergyStatusType = Literal["none", "exists", "unknown"]
SmokerType = Literal["yes", "no"]
AloneTimeStatusType = Literal["none", "sometimes", "regular"]
YesNoType = Literal["yes", "no"]
HouseholdRelationType = Literal[
    "husband", "wife", "father", "mother", "son", "daughter", "other"
]
PetCategoryType = Literal["cat", "other"]


class ApplicantHouseholdMemberCreate(BaseModel):
    """家族構成メンバー作成用スキーマ"""

    relation: HouseholdRelationType = Field(..., description="続柄")
    relation_other: str | None = Field(
        None, max_length=100, description="続柄（その他）"
    )
    age: int = Field(..., ge=0, le=150, description="年齢")

    @model_validator(mode="after")
    def validate_relation_other(self) -> ApplicantHouseholdMemberCreate:
        """続柄が「その他」の場合、詳細が必須"""
        if self.relation == "other" and not self.relation_other:
            raise ValueError("続柄が「その他」の場合、詳細の入力が必須です")
        return self


class ApplicantHouseholdMemberResponse(ApplicantHouseholdMemberCreate):
    """家族構成メンバーレスポンススキーマ"""

    id: int = Field(..., description="家族構成ID")
    applicant_id: int = Field(..., description="里親希望者ID")

    model_config = ConfigDict(from_attributes=True)


class ApplicantPetCreate(BaseModel):
    """先住ペット作成用スキーマ"""

    pet_category: PetCategoryType = Field(..., description="ペット種別（cat/other）")
    count: int = Field(1, ge=1, description="頭数")
    breed_or_type: str | None = Field(None, max_length=100, description="品種・種類")
    age_note: str | None = Field(None, max_length=100, description="年齢（自由表現）")


class ApplicantPetResponse(ApplicantPetCreate):
    """先住ペットレスポンススキーマ"""

    id: int = Field(..., description="先住ペットID")
    applicant_id: int = Field(..., description="里親希望者ID")

    model_config = ConfigDict(from_attributes=True)


class ApplicantCreateExtended(BaseModel):
    """
    拡張里親申込作成用スキーマ

    Issue #91の仕様に基づく全項目入力フォーム
    """

    # 基本情報
    name_kana: str = Field(..., max_length=100, description="ふりがな")
    name: str = Field(..., max_length=100, description="氏名")
    age: int = Field(..., ge=0, le=150, description="年齢")
    phone: str = Field(..., max_length=50, description="電話番号")

    # 連絡手段
    contact_type: ContactType = Field(..., description="連絡手段（line/email）")
    contact_line_id: str | None = Field(None, max_length=100, description="LINE ID")
    contact_email: str | None = Field(
        None, max_length=255, description="メールアドレス"
    )

    # 住所
    postal_code: str = Field(..., max_length=20, description="郵便番号")
    address1: str = Field(..., description="住所1（都道府県・市区町村・番地）")
    address2: str | None = Field(None, description="住所2（建物名・部屋番号）")

    # 職業
    occupation: OccupationType = Field(..., description="職業")
    occupation_other: str | None = Field(
        None, max_length=100, description="職業（その他）"
    )

    # 希望猫
    desired_cat_alias: str = Field("未定", max_length=100, description="希望猫の仮名")

    # 緊急連絡先
    emergency_relation: EmergencyRelationType = Field(..., description="緊急連絡先続柄")
    emergency_relation_other: str | None = Field(
        None, max_length=100, description="緊急連絡先続柄（その他）"
    )
    emergency_name: str = Field(..., max_length=100, description="緊急連絡先氏名")
    emergency_phone: str = Field(..., max_length=50, description="緊急連絡先電話番号")

    # 家族の飼育意向
    family_intent: FamilyIntentType = Field(..., description="家族の飼育意向")

    # ペット飼育可否
    pet_permission: PetPermissionType = Field(..., description="ペット飼育可否")
    pet_limit_type: PetLimitType | None = Field(None, description="ペット上限タイプ")
    pet_limit_count: int | None = Field(None, ge=0, description="ペット上限数")

    # 住居
    housing_type: HousingType = Field(..., description="住居形態")
    housing_ownership: HousingOwnershipType = Field(..., description="住居所有")

    # 転居予定
    relocation_plan: RelocationPlanType = Field(..., description="転居予定")
    relocation_time_note: str | None = Field(None, description="転居時期")
    relocation_cat_plan: str | None = Field(None, description="転居時の猫の処遇")

    # アレルギー
    allergy_status: AllergyStatusType = Field(..., description="アレルギー")

    # 喫煙者
    smoker_in_household: SmokerType = Field(..., description="喫煙者")

    # 月々の予算
    monthly_budget_yen: int = Field(..., ge=0, description="月々の予算（円）")

    # お留守番
    alone_time_status: AloneTimeStatusType = Field(..., description="お留守番")
    alone_time_weekly_days: int | None = Field(None, ge=0, le=7, description="週何回")
    alone_time_hours: float | None = Field(
        None, ge=0, le=24, description="1回あたり時間"
    )

    # 先住猫・ペット
    has_existing_cat: YesNoType = Field(..., description="先住猫")
    has_other_pets: YesNoType = Field(..., description="その他ペット")

    # 関連データ
    household_members: list[ApplicantHouseholdMemberCreate] = Field(
        default_factory=list, description="家族構成"
    )
    pets: list[ApplicantPetCreate] = Field(
        default_factory=list, description="先住ペット"
    )
    source_consultation_id: int | None = Field(
        None,
        ge=1,
        description="変換元の相談ID（相談→申込導線で利用）",
    )

    @model_validator(mode="before")
    @classmethod
    def normalize_phone_and_postal(cls, data: dict[str, Any]) -> dict[str, Any]:
        """電話番号と郵便番号のハイフンを除去"""
        if isinstance(data, dict):
            # 電話番号のハイフン除去
            if data.get("phone"):
                data["phone"] = data["phone"].replace("-", "").replace(" ", "")
            if data.get("emergency_phone"):
                data["emergency_phone"] = (
                    data["emergency_phone"].replace("-", "").replace(" ", "")
                )
            # 郵便番号のハイフン除去
            if data.get("postal_code"):
                data["postal_code"] = (
                    data["postal_code"].replace("-", "").replace(" ", "")
                )
        return data

    @model_validator(mode="after")
    def validate_contact_info(self) -> ApplicantCreateExtended:
        """連絡手段の整合性チェック"""
        if self.contact_type == "line" and not self.contact_line_id:
            raise ValueError("LINE連絡を選択した場合、LINE IDの入力が必須です")
        if self.contact_type == "email" and not self.contact_email:
            raise ValueError("メール連絡を選択した場合、メールアドレスの入力が必須です")
        return self

    @model_validator(mode="after")
    def validate_occupation_other(self) -> ApplicantCreateExtended:
        """職業「その他」の整合性チェック"""
        if self.occupation == "other" and not self.occupation_other:
            raise ValueError("職業が「その他」の場合、詳細の入力が必須です")
        return self

    @model_validator(mode="after")
    def validate_emergency_relation_other(self) -> ApplicantCreateExtended:
        """緊急連絡先続柄「その他」の整合性チェック"""
        if self.emergency_relation == "other" and not self.emergency_relation_other:
            raise ValueError("緊急連絡先続柄が「その他」の場合、詳細の入力が必須です")
        return self

    @model_validator(mode="after")
    def validate_relocation_details(self) -> ApplicantCreateExtended:
        """転居予定ありの場合の整合性チェック"""
        if self.relocation_plan == "planned" and (
            not self.relocation_time_note or not self.relocation_cat_plan
        ):
            raise ValueError("転居予定がある場合、時期と猫の処遇の入力が必須です")
        return self

    @model_validator(mode="after")
    def validate_alone_time_details(self) -> ApplicantCreateExtended:
        """お留守番の整合性チェック"""
        if self.alone_time_status in ("sometimes", "regular") and (
            self.alone_time_weekly_days is None or self.alone_time_hours is None
        ):
            raise ValueError(
                "お留守番がある場合、週何回と1回あたりの時間の入力が必須です"
            )
        return self

    @model_validator(mode="after")
    def validate_pet_limit_details(self) -> ApplicantCreateExtended:
        """ペット上限の整合性チェック"""
        if (
            self.pet_permission == "allowed"
            and self.pet_limit_type == "limited"
            and self.pet_limit_count is None
        ):
            raise ValueError("ペット上限ありの場合、上限数の入力が必須です")
        return self


class ApplicantUpdateExtended(BaseModel):
    """拡張里親申込更新用スキーマ（全フィールド任意）"""

    @model_validator(mode="before")
    @classmethod
    def normalize_phone_and_postal(cls, data: dict[str, Any]) -> dict[str, Any]:
        """電話番号と郵便番号のハイフンを除去"""
        if isinstance(data, dict):
            # 電話番号のハイフン除去
            if data.get("phone"):
                data["phone"] = data["phone"].replace("-", "").replace(" ", "")
            if data.get("emergency_phone"):
                data["emergency_phone"] = (
                    data["emergency_phone"].replace("-", "").replace(" ", "")
                )
            # 郵便番号のハイフン除去
            if data.get("postal_code"):
                data["postal_code"] = (
                    data["postal_code"].replace("-", "").replace(" ", "")
                )
        return data

    # 基本情報
    name_kana: str | None = Field(None, max_length=100, description="ふりがな")
    name: str | None = Field(None, max_length=100, description="氏名")
    age: int | None = Field(None, ge=0, le=150, description="年齢")
    phone: str | None = Field(None, max_length=50, description="電話番号")

    # 連絡手段
    contact_type: ContactType | None = Field(None, description="連絡手段")
    contact_line_id: str | None = Field(None, max_length=100, description="LINE ID")
    contact_email: str | None = Field(
        None, max_length=255, description="メールアドレス"
    )

    # 住所
    postal_code: str | None = Field(None, max_length=20, description="郵便番号")
    address1: str | None = Field(None, description="住所1")
    address2: str | None = Field(None, description="住所2")

    # 職業
    occupation: OccupationType | None = Field(None, description="職業")
    occupation_other: str | None = Field(
        None, max_length=100, description="職業（その他）"
    )

    # 希望猫
    desired_cat_alias: str | None = Field(
        None, max_length=100, description="希望猫の仮名"
    )

    # 緊急連絡先
    emergency_relation: EmergencyRelationType | None = Field(
        None, description="緊急連絡先続柄"
    )
    emergency_relation_other: str | None = Field(None, max_length=100)
    emergency_name: str | None = Field(
        None, max_length=100, description="緊急連絡先氏名"
    )
    emergency_phone: str | None = Field(
        None, max_length=50, description="緊急連絡先電話番号"
    )

    # 家族の飼育意向
    family_intent: FamilyIntentType | None = Field(None, description="家族の飼育意向")

    # ペット飼育可否
    pet_permission: PetPermissionType | None = Field(None, description="ペット飼育可否")
    pet_limit_type: PetLimitType | None = Field(None, description="ペット上限タイプ")
    pet_limit_count: int | None = Field(None, ge=0, description="ペット上限数")

    # 住居
    housing_type: HousingType | None = Field(None, description="住居形態")
    housing_ownership: HousingOwnershipType | None = Field(None, description="住居所有")

    # 転居予定
    relocation_plan: RelocationPlanType | None = Field(None, description="転居予定")
    relocation_time_note: str | None = Field(None, description="転居時期")
    relocation_cat_plan: str | None = Field(None, description="転居時の猫の処遇")

    # アレルギー
    allergy_status: AllergyStatusType | None = Field(None, description="アレルギー")

    # 喫煙者
    smoker_in_household: SmokerType | None = Field(None, description="喫煙者")

    # 月々の予算
    monthly_budget_yen: int | None = Field(None, ge=0, description="月々の予算（円）")

    # お留守番
    alone_time_status: AloneTimeStatusType | None = Field(None, description="お留守番")
    alone_time_weekly_days: int | None = Field(None, ge=0, le=7)
    alone_time_hours: float | None = Field(None, ge=0, le=24)

    # 先住猫・ペット
    has_existing_cat: YesNoType | None = Field(None, description="先住猫")
    has_other_pets: YesNoType | None = Field(None, description="その他ペット")


class ApplicantResponseExtended(BaseModel):
    """拡張里親申込レスポンススキーマ"""

    id: int = Field(..., description="里親希望者ID")

    # 基本情報
    name_kana: str | None = Field(None, description="ふりがな")
    name: str = Field(..., description="氏名")
    age: int | None = Field(None, description="年齢")
    phone: str | None = Field(None, description="電話番号")

    # 連絡手段
    contact_type: str | None = Field(None, description="連絡手段")
    contact_line_id: str | None = Field(None, description="LINE ID")
    contact_email: str | None = Field(None, description="メールアドレス")

    # 住所
    postal_code: str | None = Field(None, description="郵便番号")
    address1: str | None = Field(None, description="住所1")
    address2: str | None = Field(None, description="住所2")

    # 職業
    occupation: str | None = Field(None, description="職業")
    occupation_other: str | None = Field(None, description="職業（その他）")

    # 希望猫
    desired_cat_alias: str | None = Field(None, description="希望猫の仮名")

    # 緊急連絡先
    emergency_relation: str | None = Field(None, description="緊急連絡先続柄")
    emergency_relation_other: str | None = Field(None)
    emergency_name: str | None = Field(None, description="緊急連絡先氏名")
    emergency_phone: str | None = Field(None, description="緊急連絡先電話番号")

    # 家族の飼育意向
    family_intent: str | None = Field(None, description="家族の飼育意向")

    # ペット飼育可否
    pet_permission: str | None = Field(None, description="ペット飼育可否")
    pet_limit_type: str | None = Field(None, description="ペット上限タイプ")
    pet_limit_count: int | None = Field(None, description="ペット上限数")

    # 住居
    housing_type: str | None = Field(None, description="住居形態")
    housing_ownership: str | None = Field(None, description="住居所有")

    # 転居予定
    relocation_plan: str | None = Field(None, description="転居予定")
    relocation_time_note: str | None = Field(None, description="転居時期")
    relocation_cat_plan: str | None = Field(None, description="転居時の猫の処遇")

    # アレルギー
    allergy_status: str | None = Field(None, description="アレルギー")

    # 喫煙者
    smoker_in_household: str | None = Field(None, description="喫煙者")

    # 月々の予算
    monthly_budget_yen: int | None = Field(None, description="月々の予算（円）")

    # お留守番
    alone_time_status: str | None = Field(None, description="お留守番")
    alone_time_weekly_days: int | None = Field(None)
    alone_time_hours: float | None = Field(None)

    # 先住猫・ペット
    has_existing_cat: str | None = Field(None, description="先住猫")
    has_other_pets: str | None = Field(None, description="その他ペット")

    # 関連データ
    household_members: list[ApplicantHouseholdMemberResponse] = Field(
        default_factory=list, description="家族構成"
    )
    pets: list[ApplicantPetResponse] = Field(
        default_factory=list, description="先住ペット"
    )

    # タイムスタンプ
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# ========================================
# AdoptionConsultation（里親相談）スキーマ
# ========================================


class AdoptionConsultationBase(BaseModel):
    """里親相談の共通フィールド"""

    name_kana: str = Field(..., max_length=100, description="ふりがな")
    name: str = Field(..., max_length=100, description="氏名")
    phone: str = Field(..., max_length=50, description="電話番号")
    contact_type: ContactType = Field(..., description="連絡手段（line/email）")
    contact_line_id: str | None = Field(None, max_length=100, description="LINE ID")
    contact_email: str | None = Field(
        None, max_length=255, description="メールアドレス"
    )
    consultation_note: str = Field(..., description="相談内容")

    @model_validator(mode="before")
    @classmethod
    def normalize_phone(cls, data: dict[str, Any]) -> dict[str, Any]:
        """電話番号のハイフンを除去"""
        if isinstance(data, dict) and data.get("phone"):
            data["phone"] = data["phone"].replace("-", "").replace(" ", "")
        return data

    @model_validator(mode="after")
    def validate_contact_info(self) -> AdoptionConsultationBase:
        """連絡手段の整合性チェック"""
        if self.contact_type == "line" and not self.contact_line_id:
            raise ValueError("LINE連絡を選択した場合、LINE IDの入力が必須です")
        if self.contact_type == "email" and not self.contact_email:
            raise ValueError("メール連絡を選択した場合、メールアドレスの入力が必須です")
        return self


class AdoptionConsultationCreate(AdoptionConsultationBase):
    """里親相談作成スキーマ"""

    pass


class AdoptionConsultationUpdate(BaseModel):
    """里親相談更新スキーマ（全フィールド任意）"""

    name_kana: str | None = Field(None, max_length=100, description="ふりがな")
    name: str | None = Field(None, max_length=100, description="氏名")
    phone: str | None = Field(None, max_length=50, description="電話番号")
    contact_type: ContactType | None = Field(None, description="連絡手段（line/email）")
    contact_line_id: str | None = Field(None, max_length=100, description="LINE ID")
    contact_email: str | None = Field(
        None, max_length=255, description="メールアドレス"
    )
    consultation_note: str | None = Field(None, description="相談内容")
    status: ConsultationStatusType | None = Field(None, description="相談ステータス")

    @model_validator(mode="before")
    @classmethod
    def normalize_phone(cls, data: dict[str, Any]) -> dict[str, Any]:
        """電話番号のハイフンを除去"""
        if isinstance(data, dict) and data.get("phone"):
            data["phone"] = data["phone"].replace("-", "").replace(" ", "")
        return data


class AdoptionConsultationResponse(AdoptionConsultationBase):
    """里親相談レスポンススキーマ"""

    id: int = Field(..., description="相談ID")
    status: ConsultationStatusType = Field(..., description="相談ステータス")
    applicant_id: int | None = Field(None, description="変換先の里親申込ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)


# ========================================
# IntakeEntry（受付統合一覧）スキーマ
# ========================================


class AdoptionIntakeEntryResponse(BaseModel):
    """受付統合一覧レスポンススキーマ"""

    id: int = Field(..., description="一覧表示用ID")
    request_type: IntakeEntryType = Field(
        ...,
        description="受付種別（application/consultation/both）",
    )
    application_id: int | None = Field(None, description="譲渡申込ID")
    consultation_id: int | None = Field(None, description="相談ID")
    name_kana: str | None = Field(None, description="ふりがな")
    name: str = Field(..., description="氏名")
    phone: str | None = Field(None, description="電話番号")
    contact_type: ContactType | None = Field(None, description="連絡手段")
    contact_line_id: str | None = Field(None, description="LINE ID")
    contact_email: str | None = Field(None, description="メールアドレス")
    consultation_note: str | None = Field(None, description="相談内容")
    status: ConsultationStatusType | None = Field(None, description="相談ステータス")
    created_at: datetime = Field(..., description="作成日時")


# ========================================
# AdoptionRecord（譲渡記録）スキーマ
# ========================================


class AdoptionRecordBase(BaseModel):
    """譲渡記録の共通フィールド"""

    animal_id: int = Field(..., description="猫ID")
    applicant_id: int = Field(..., description="里親希望者ID")
    interview_date: date | None = Field(None, description="面談日")
    interview_note: str | None = Field(None, description="面談内容")
    decision: str | None = Field(
        None,
        pattern="^(approved|rejected|pending)$",
        description="判定結果（approved/rejected/pending）",
    )
    adoption_date: date | None = Field(None, description="譲渡日")
    follow_up: str | None = Field(None, description="譲渡後フォロー")


class AdoptionRecordCreate(AdoptionRecordBase):
    """譲渡記録作成用スキーマ"""

    pass


class AdoptionRecordUpdate(BaseModel):
    """譲渡記録更新用スキーマ（全フィールド任意）"""

    interview_date: date | None = Field(None, description="面談日")
    interview_note: str | None = Field(None, description="面談内容")
    decision: str | None = Field(
        None,
        pattern="^(approved|rejected|pending)$",
        description="判定結果（approved/rejected/pending）",
    )
    adoption_date: date | None = Field(None, description="譲渡日")
    follow_up: str | None = Field(None, description="譲渡後フォロー")


class AdoptionRecordResponse(AdoptionRecordBase):
    """譲渡記録レスポンススキーマ"""

    id: int = Field(..., description="譲渡記録ID")
    created_at: datetime = Field(..., description="作成日時")
    updated_at: datetime = Field(..., description="更新日時")

    model_config = ConfigDict(from_attributes=True)
