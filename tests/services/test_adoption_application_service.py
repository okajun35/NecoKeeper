"""
里親申込サービスのテスト

Issue #91: 譲渡記録の充実化
里親申込フォームの詳細情報をテストします。
"""

from __future__ import annotations

import pytest
from pydantic import ValidationError

from app.schemas.adoption import (
    ApplicantCreateExtended,
    ApplicantHouseholdMemberCreate,
    ApplicantPetCreate,
)
from app.services import adoption_service

# ========================================
# 拡張Applicant（里親申込）テスト
# ========================================


class TestCreateApplicantExtended:
    """拡張里親申込登録のテスト"""

    def test_create_applicant_with_full_data_success(self, test_db, test_user):
        """正常系: 全項目を入力して里親申込を登録できる"""
        # Given
        applicant_data = ApplicantCreateExtended(
            # 基本情報
            name_kana="ヤマダタロウ",
            name="山田太郎",
            age=35,
            phone="090-1234-5678",
            # 連絡手段
            contact_type="line",
            contact_line_id="yamada_taro",
            contact_email=None,
            # 住所
            postal_code="150-0001",
            address1="東京都渋谷区神宮前1-1-1",
            address2="マンション101号室",
            # 職業
            occupation="company_employee",
            occupation_other=None,
            # 希望猫
            desired_cat_alias="たま",
            # 緊急連絡先
            emergency_relation="parents",
            emergency_relation_other=None,
            emergency_name="山田一郎",
            emergency_phone="090-9876-5432",
            # 家族の飼育意向
            family_intent="all_positive",
            # ペット飼育可否
            pet_permission="allowed",
            pet_limit_type="limited",
            pet_limit_count=2,
            # 住居
            housing_type="apartment",
            housing_ownership="rented",
            # 転居予定
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            # アレルギー
            allergy_status="none",
            # 喫煙者
            smoker_in_household="no",
            # 月々の予算
            monthly_budget_yen=10000,
            # お留守番
            alone_time_status="sometimes",
            alone_time_weekly_days=2,
            alone_time_hours=4.0,
            # 先住猫・ペット
            has_existing_cat="no",
            has_other_pets="no",
            # 家族構成
            household_members=[
                ApplicantHouseholdMemberCreate(
                    relation="wife",
                    relation_other=None,
                    age=32,
                ),
            ],
            # 先住ペット
            pets=[],
        )

        # When
        result = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert result.id is not None
        assert result.name == "山田太郎"
        assert result.name_kana == "ヤマダタロウ"
        assert result.age == 35
        assert result.contact_type == "line"
        assert result.contact_line_id == "yamada_taro"
        assert result.family_intent == "all_positive"
        assert result.monthly_budget_yen == 10000
        assert result.created_at is not None

    def test_create_applicant_with_email_contact_success(self, test_db, test_user):
        """正常系: メール連絡で里親申込を登録できる"""
        # Given
        applicant_data = ApplicantCreateExtended(
            name_kana="サトウハナコ",
            name="佐藤花子",
            age=28,
            phone="080-1111-2222",
            contact_type="email",
            contact_line_id=None,
            contact_email="sato@example.com",
            postal_code="160-0022",
            address1="東京都新宿区新宿3-3-3",
            address2=None,
            occupation="public_servant",
            occupation_other=None,
            desired_cat_alias="未定",
            emergency_relation="siblings",
            emergency_relation_other=None,
            emergency_name="佐藤次郎",
            emergency_phone="080-3333-4444",
            family_intent="single_household",
            pet_permission="allowed",
            pet_limit_type="unlimited",
            pet_limit_count=None,
            housing_type="apartment",
            housing_ownership="owned",
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            allergy_status="unknown",
            smoker_in_household="no",
            monthly_budget_yen=15000,
            alone_time_status="regular",
            alone_time_weekly_days=5,
            alone_time_hours=8.0,
            has_existing_cat="no",
            has_other_pets="no",
            household_members=[],
            pets=[],
        )

        # When
        result = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert result.contact_type == "email"
        assert result.contact_email == "sato@example.com"
        assert result.contact_line_id is None

    def test_create_applicant_with_existing_cat_success(self, test_db, test_user):
        """正常系: 先住猫がいる場合の登録"""
        # Given
        applicant_data = ApplicantCreateExtended(
            name_kana="タナカジロウ",
            name="田中次郎",
            age=40,
            phone="070-5555-6666",
            contact_type="line",
            contact_line_id="tanaka_j",
            contact_email=None,
            postal_code="171-0022",
            address1="東京都豊島区南池袋2-2-2",
            address2=None,
            occupation="self_employed",
            occupation_other=None,
            desired_cat_alias="ミケ",
            emergency_relation="parents",
            emergency_relation_other=None,
            emergency_name="田中一郎",
            emergency_phone="070-7777-8888",
            family_intent="all_positive",
            pet_permission="allowed",
            pet_limit_type="unlimited",
            pet_limit_count=None,
            housing_type="house",
            housing_ownership="owned",
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            allergy_status="none",
            smoker_in_household="no",
            monthly_budget_yen=20000,
            alone_time_status="none",
            alone_time_weekly_days=None,
            alone_time_hours=None,
            has_existing_cat="yes",
            has_other_pets="no",
            household_members=[
                ApplicantHouseholdMemberCreate(
                    relation="wife", relation_other=None, age=38
                ),
                ApplicantHouseholdMemberCreate(
                    relation="son", relation_other=None, age=10
                ),
            ],
            pets=[
                ApplicantPetCreate(
                    pet_category="cat",
                    count=1,
                    breed_or_type="雑種",
                    age_note="3歳",
                ),
            ],
        )

        # When
        result = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert result.has_existing_cat == "yes"
        assert len(result.household_members) == 2
        assert len(result.pets) == 1
        assert result.pets[0].pet_category == "cat"
        assert result.pets[0].breed_or_type == "雑種"


class TestApplicantContactValidation:
    """連絡先バリデーションのテスト"""

    def test_line_contact_requires_line_id(self, test_db, test_user):
        """異常系: LINE連絡選択時にLINE IDが必須"""
        # When / Then - Pydanticのバリデーションで例外が発生
        with pytest.raises(ValidationError, match=r"LINE.*必須"):
            ApplicantCreateExtended(
                name_kana="テストタロウ",
                name="テスト太郎",
                age=30,
                phone="090-0000-0000",
                contact_type="line",
                contact_line_id=None,  # LINE ID未入力
                contact_email=None,
                postal_code="100-0001",
                address1="東京都千代田区",
                address2=None,
                occupation="company_employee",
                occupation_other=None,
                desired_cat_alias="未定",
                emergency_relation="parents",
                emergency_relation_other=None,
                emergency_name="テスト一郎",
                emergency_phone="090-1111-1111",
                family_intent="all_positive",
                pet_permission="allowed",
                pet_limit_type="unlimited",
                pet_limit_count=None,
                housing_type="house",
                housing_ownership="owned",
                relocation_plan="none",
                relocation_time_note=None,
                relocation_cat_plan=None,
                allergy_status="none",
                smoker_in_household="no",
                monthly_budget_yen=10000,
                alone_time_status="none",
                alone_time_weekly_days=None,
                alone_time_hours=None,
                has_existing_cat="no",
                has_other_pets="no",
                household_members=[],
                pets=[],
            )

    def test_email_contact_requires_email(self, test_db, test_user):
        """異常系: メール連絡選択時にメールアドレスが必須"""
        # When / Then - Pydanticのバリデーションで例外が発生
        with pytest.raises(ValidationError, match=r"メール.*必須"):
            ApplicantCreateExtended(
                name_kana="テストハナコ",
                name="テスト花子",
                age=25,
                phone="080-0000-0000",
                contact_type="email",
                contact_line_id=None,
                contact_email=None,  # メール未入力
                postal_code="100-0002",
                address1="東京都千代田区",
                address2=None,
                occupation="company_employee",
                occupation_other=None,
                desired_cat_alias="未定",
                emergency_relation="parents",
                emergency_relation_other=None,
                emergency_name="テスト一郎",
                emergency_phone="080-1111-1111",
                family_intent="all_positive",
                pet_permission="allowed",
                pet_limit_type="unlimited",
                pet_limit_count=None,
                housing_type="house",
                housing_ownership="owned",
                relocation_plan="none",
                relocation_time_note=None,
                relocation_cat_plan=None,
                allergy_status="none",
                smoker_in_household="no",
                monthly_budget_yen=10000,
                alone_time_status="none",
                alone_time_weekly_days=None,
                alone_time_hours=None,
                has_existing_cat="no",
                has_other_pets="no",
                household_members=[],
                pets=[],
            )


class TestApplicantConditionalValidation:
    """条件付き必須フィールドのバリデーションテスト"""

    def test_relocation_planned_requires_details(self, test_db, test_user):
        """異常系: 転居予定ありの場合、詳細が必須"""
        # When / Then - Pydanticのバリデーションで例外が発生
        with pytest.raises(ValidationError, match=r"転居予定.*必須"):
            ApplicantCreateExtended(
                name_kana="テストジロウ",
                name="テスト次郎",
                age=35,
                phone="070-0000-0000",
                contact_type="line",
                contact_line_id="test_j",
                contact_email=None,
                postal_code="100-0003",
                address1="東京都千代田区",
                address2=None,
                occupation="company_employee",
                occupation_other=None,
                desired_cat_alias="未定",
                emergency_relation="parents",
                emergency_relation_other=None,
                emergency_name="テスト一郎",
                emergency_phone="070-1111-1111",
                family_intent="all_positive",
                pet_permission="allowed",
                pet_limit_type="unlimited",
                pet_limit_count=None,
                housing_type="house",
                housing_ownership="owned",
                relocation_plan="planned",  # 転居予定あり
                relocation_time_note=None,  # 時期未入力
                relocation_cat_plan=None,  # 猫の処遇未入力
                allergy_status="none",
                smoker_in_household="no",
                monthly_budget_yen=10000,
                alone_time_status="none",
                alone_time_weekly_days=None,
                alone_time_hours=None,
                has_existing_cat="no",
                has_other_pets="no",
                household_members=[],
                pets=[],
            )

    def test_alone_time_regular_requires_details(self, test_db, test_user):
        """異常系: お留守番が定期的の場合、詳細が必須"""
        # When / Then - Pydanticバリデーションでスキーマ生成時にエラーが発生する
        with pytest.raises(ValidationError, match=r"お留守番.*必須"):
            ApplicantCreateExtended(
                name_kana="テストサブロウ",
                name="テスト三郎",
                age=45,
                phone="060-0000-0000",
                contact_type="email",
                contact_line_id=None,
                contact_email="test3@example.com",
                postal_code="100-0004",
                address1="東京都千代田区",
                address2=None,
                occupation="company_employee",
                occupation_other=None,
                desired_cat_alias="未定",
                emergency_relation="parents",
                emergency_relation_other=None,
                emergency_name="テスト一郎",
                emergency_phone="060-1111-1111",
                family_intent="all_positive",
                pet_permission="allowed",
                pet_limit_type="unlimited",
                pet_limit_count=None,
                housing_type="house",
                housing_ownership="owned",
                relocation_plan="none",
                relocation_time_note=None,
                relocation_cat_plan=None,
                allergy_status="none",
                smoker_in_household="no",
                monthly_budget_yen=10000,
                alone_time_status="regular",  # 定期的にお留守番
                alone_time_weekly_days=None,  # 週何回未入力
                alone_time_hours=None,  # 時間未入力
                has_existing_cat="no",
                has_other_pets="no",
                household_members=[],
                pets=[],
            )


class TestApplicantHouseholdMember:
    """家族構成のテスト"""

    def test_add_household_member_success(self, test_db, test_user):
        """正常系: 家族メンバーを追加できる"""
        # Given: 先に申込者を作成
        applicant_data = ApplicantCreateExtended(
            name_kana="カゾクタロウ",
            name="家族太郎",
            age=40,
            phone="090-1234-5678",
            contact_type="line",
            contact_line_id="kazoku_t",
            contact_email=None,
            postal_code="150-0001",
            address1="東京都渋谷区",
            address2=None,
            occupation="company_employee",
            occupation_other=None,
            desired_cat_alias="未定",
            emergency_relation="parents",
            emergency_relation_other=None,
            emergency_name="家族一郎",
            emergency_phone="090-9999-8888",
            family_intent="all_positive",
            pet_permission="allowed",
            pet_limit_type="unlimited",
            pet_limit_count=None,
            housing_type="house",
            housing_ownership="owned",
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            allergy_status="none",
            smoker_in_household="no",
            monthly_budget_yen=15000,
            alone_time_status="none",
            alone_time_weekly_days=None,
            alone_time_hours=None,
            has_existing_cat="no",
            has_other_pets="no",
            household_members=[
                ApplicantHouseholdMemberCreate(
                    relation="wife", relation_other=None, age=38
                ),
                ApplicantHouseholdMemberCreate(
                    relation="son", relation_other=None, age=12
                ),
                ApplicantHouseholdMemberCreate(
                    relation="daughter", relation_other=None, age=8
                ),
            ],
            pets=[],
        )

        # When
        result = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert len(result.household_members) == 3
        relations = [m.relation for m in result.household_members]
        assert "wife" in relations
        assert "son" in relations
        assert "daughter" in relations

    def test_household_member_other_relation_requires_detail(self, test_db, test_user):
        """異常系: 続柄「その他」の場合、詳細が必須"""
        # When / Then - ネストされたスキーマのバリデーションでもValidationErrorがスローされる
        with pytest.raises(ValidationError, match=r"続柄.*その他.*必須"):
            ApplicantCreateExtended(
                name_kana="テストゴロウ",
                name="テスト五郎",
                age=50,
                phone="090-5555-5555",
                contact_type="line",
                contact_line_id="test5",
                contact_email=None,
                postal_code="150-0002",
                address1="東京都渋谷区",
                address2=None,
                occupation="company_employee",
                occupation_other=None,
                desired_cat_alias="未定",
                emergency_relation="parents",
                emergency_relation_other=None,
                emergency_name="テスト一郎",
                emergency_phone="090-1111-1111",
                family_intent="all_positive",
                pet_permission="allowed",
                pet_limit_type="unlimited",
                pet_limit_count=None,
                housing_type="house",
                housing_ownership="owned",
                relocation_plan="none",
                relocation_time_note=None,
                relocation_cat_plan=None,
                allergy_status="none",
                smoker_in_household="no",
                monthly_budget_yen=10000,
                alone_time_status="none",
                alone_time_weekly_days=None,
                alone_time_hours=None,
                has_existing_cat="no",
                has_other_pets="no",
                household_members=[
                    ApplicantHouseholdMemberCreate(
                        relation="other",
                        relation_other=None,  # その他の詳細未入力
                        age=70,
                    ),
                ],
                pets=[],
            )


class TestApplicantPet:
    """先住ペットのテスト"""

    def test_add_existing_cat_details_success(self, test_db, test_user):
        """正常系: 先住猫の詳細を登録できる"""
        # Given
        applicant_data = ApplicantCreateExtended(
            name_kana="ネコズキタロウ",
            name="猫好太郎",
            age=35,
            phone="090-2222-3333",
            contact_type="line",
            contact_line_id="nekozuki",
            contact_email=None,
            postal_code="160-0001",
            address1="東京都新宿区",
            address2=None,
            occupation="company_employee",
            occupation_other=None,
            desired_cat_alias="未定",
            emergency_relation="parents",
            emergency_relation_other=None,
            emergency_name="猫好一郎",
            emergency_phone="090-4444-5555",
            family_intent="all_positive",
            pet_permission="allowed",
            pet_limit_type="unlimited",
            pet_limit_count=None,
            housing_type="house",
            housing_ownership="owned",
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            allergy_status="none",
            smoker_in_household="no",
            monthly_budget_yen=20000,
            alone_time_status="none",
            alone_time_weekly_days=None,
            alone_time_hours=None,
            has_existing_cat="yes",
            has_other_pets="yes",
            household_members=[],
            pets=[
                ApplicantPetCreate(
                    pet_category="cat",
                    count=2,
                    breed_or_type="アメリカンショートヘア",
                    age_note="5歳と3歳",
                ),
                ApplicantPetCreate(
                    pet_category="other",
                    count=1,
                    breed_or_type="うさぎ",
                    age_note="2歳",
                ),
            ],
        )

        # When
        result = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # Then
        assert len(result.pets) == 2
        cat_pet = next(p for p in result.pets if p.pet_category == "cat")
        assert cat_pet.count == 2
        assert cat_pet.breed_or_type == "アメリカンショートヘア"


class TestGetApplicantExtended:
    """拡張里親申込取得のテスト"""

    def test_get_applicant_with_relations_success(self, test_db, test_user):
        """正常系: 関連データ含めて里親申込を取得できる"""
        # Given: 先に申込者を作成
        applicant_data = ApplicantCreateExtended(
            name_kana="シュトクタロウ",
            name="取得太郎",
            age=30,
            phone="090-6666-7777",
            contact_type="email",
            contact_line_id=None,
            contact_email="shutoku@example.com",
            postal_code="170-0001",
            address1="東京都豊島区",
            address2=None,
            occupation="company_employee",
            occupation_other=None,
            desired_cat_alias="未定",
            emergency_relation="siblings",
            emergency_relation_other=None,
            emergency_name="取得次郎",
            emergency_phone="090-8888-9999",
            family_intent="all_positive",
            pet_permission="allowed",
            pet_limit_type="unlimited",
            pet_limit_count=None,
            housing_type="apartment",
            housing_ownership="rented",
            relocation_plan="none",
            relocation_time_note=None,
            relocation_cat_plan=None,
            allergy_status="none",
            smoker_in_household="no",
            monthly_budget_yen=12000,
            alone_time_status="sometimes",
            alone_time_weekly_days=1,
            alone_time_hours=3.0,
            has_existing_cat="yes",
            has_other_pets="no",
            household_members=[
                ApplicantHouseholdMemberCreate(
                    relation="wife", relation_other=None, age=28
                ),
            ],
            pets=[
                ApplicantPetCreate(
                    pet_category="cat", count=1, breed_or_type="雑種", age_note="1歳"
                ),
            ],
        )
        created = adoption_service.create_applicant_extended(
            test_db, applicant_data, user_id=test_user.id
        )

        # When
        result = adoption_service.get_applicant_extended(test_db, created.id)

        # Then
        assert result.id == created.id
        assert result.name == "取得太郎"
        assert len(result.household_members) == 1
        assert len(result.pets) == 1
