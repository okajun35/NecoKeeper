"""extend applicant model issue 91

Issue #91: 譲渡記録の充実化
- applicantsテーブルに拡張フィールドを追加
- applicant_household_membersテーブルを新規作成（家族構成）
- applicant_petsテーブルを新規作成（先住ペット）

Revision ID: b91_extend_applicant
Revises: f4e98ee7ca5a
Create Date: 2026-01-15

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "b91_extend_applicant"
down_revision: str | None = "f4e98ee7ca5a"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # ==================================
    # applicantsテーブルに拡張カラムを追加
    # ==================================

    # 基本情報
    op.add_column(
        "applicants",
        sa.Column("name_kana", sa.String(100), nullable=True, comment="ふりがな"),
    )
    op.add_column(
        "applicants",
        sa.Column("age", sa.Integer(), nullable=True, comment="年齢"),
    )
    op.add_column(
        "applicants",
        sa.Column("phone", sa.String(50), nullable=True, comment="電話番号"),
    )

    # 連絡手段
    op.add_column(
        "applicants",
        sa.Column(
            "contact_type",
            sa.String(20),
            nullable=True,
            comment="連絡手段（line/email）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column("contact_line_id", sa.String(100), nullable=True, comment="LINE ID"),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "contact_email", sa.String(255), nullable=True, comment="メールアドレス"
        ),
    )

    # 住所（詳細）
    op.add_column(
        "applicants",
        sa.Column("postal_code", sa.String(20), nullable=True, comment="郵便番号"),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "address1",
            sa.Text(),
            nullable=True,
            comment="住所1（都道府県・市区町村・番地）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "address2", sa.Text(), nullable=True, comment="住所2（建物名・部屋番号）"
        ),
    )

    # 職業
    op.add_column(
        "applicants",
        sa.Column(
            "occupation",
            sa.String(50),
            nullable=True,
            comment="職業（company_employee/public_servant/self_employed/other）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "occupation_other",
            sa.String(100),
            nullable=True,
            comment="職業（その他の場合の詳細）",
        ),
    )

    # 希望猫
    op.add_column(
        "applicants",
        sa.Column(
            "desired_cat_alias",
            sa.String(100),
            nullable=True,
            server_default="未定",
            comment="希望猫の仮名",
        ),
    )

    # 緊急連絡先
    op.add_column(
        "applicants",
        sa.Column(
            "emergency_relation",
            sa.String(50),
            nullable=True,
            comment="緊急連絡先続柄（parents/siblings/other）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "emergency_relation_other",
            sa.String(100),
            nullable=True,
            comment="緊急連絡先続柄（その他の場合の詳細）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "emergency_name", sa.String(100), nullable=True, comment="緊急連絡先氏名"
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "emergency_phone",
            sa.String(50),
            nullable=True,
            comment="緊急連絡先電話番号",
        ),
    )

    # 家族の飼育意向
    op.add_column(
        "applicants",
        sa.Column(
            "family_intent",
            sa.String(50),
            nullable=True,
            comment="家族の飼育意向（all_positive/some_not_positive/single_household）",
        ),
    )

    # ペット飼育可否
    op.add_column(
        "applicants",
        sa.Column(
            "pet_permission",
            sa.String(50),
            nullable=True,
            comment="ペット飼育可否（allowed/not_allowed/tolerated）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "pet_limit_type",
            sa.String(50),
            nullable=True,
            comment="ペット上限タイプ（limited/unlimited/unknown）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "pet_limit_count", sa.Integer(), nullable=True, comment="ペット上限数"
        ),
    )

    # 住居
    op.add_column(
        "applicants",
        sa.Column(
            "housing_type",
            sa.String(50),
            nullable=True,
            comment="住居形態（house/apartment/other）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "housing_ownership",
            sa.String(50),
            nullable=True,
            comment="住居所有（owned/rented）",
        ),
    )

    # 転居予定
    op.add_column(
        "applicants",
        sa.Column(
            "relocation_plan",
            sa.String(50),
            nullable=True,
            comment="転居予定（none/planned）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column("relocation_time_note", sa.Text(), nullable=True, comment="転居時期"),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "relocation_cat_plan", sa.Text(), nullable=True, comment="転居時の猫の処遇"
        ),
    )

    # アレルギー
    op.add_column(
        "applicants",
        sa.Column(
            "allergy_status",
            sa.String(50),
            nullable=True,
            comment="アレルギー（none/exists/unknown）",
        ),
    )

    # 喫煙者
    op.add_column(
        "applicants",
        sa.Column(
            "smoker_in_household",
            sa.String(10),
            nullable=True,
            comment="喫煙者（yes/no）",
        ),
    )

    # 月々の予算
    op.add_column(
        "applicants",
        sa.Column(
            "monthly_budget_yen",
            sa.Integer(),
            nullable=True,
            comment="月々の猫にかける予算（円）",
        ),
    )

    # お留守番
    op.add_column(
        "applicants",
        sa.Column(
            "alone_time_status",
            sa.String(50),
            nullable=True,
            comment="お留守番（none/sometimes/regular）",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "alone_time_weekly_days",
            sa.Integer(),
            nullable=True,
            comment="お留守番週何回",
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "alone_time_hours",
            sa.Float(),
            nullable=True,
            comment="お留守番1回あたり時間",
        ),
    )

    # 先住猫・ペット
    op.add_column(
        "applicants",
        sa.Column(
            "has_existing_cat", sa.String(10), nullable=True, comment="先住猫（yes/no）"
        ),
    )
    op.add_column(
        "applicants",
        sa.Column(
            "has_other_pets",
            sa.String(10),
            nullable=True,
            comment="その他ペット（yes/no）",
        ),
    )

    # インデックス追加
    op.create_index(
        "ix_applicants_name_kana", "applicants", ["name_kana"], unique=False
    )
    op.create_index("ix_applicants_phone", "applicants", ["phone"], unique=False)

    # ==================================
    # applicant_household_membersテーブル（家族構成）
    # ==================================
    op.create_table(
        "applicant_household_members",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "applicant_id",
            sa.Integer(),
            sa.ForeignKey("applicants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "relation",
            sa.String(50),
            nullable=False,
            comment="続柄（husband/wife/father/mother/son/daughter/other）",
        ),
        sa.Column(
            "relation_other",
            sa.String(100),
            nullable=True,
            comment="続柄（その他の場合の詳細）",
        ),
        sa.Column("age", sa.Integer(), nullable=False, comment="年齢"),
        sa.CheckConstraint(
            "relation IN ('husband','wife','father','mother','son','daughter','other')",
            name="ck_household_member_relation",
        ),
    )
    op.create_index(
        "ix_applicant_household_members_applicant_id",
        "applicant_household_members",
        ["applicant_id"],
        unique=False,
    )

    # ==================================
    # applicant_petsテーブル（先住ペット）
    # ==================================
    op.create_table(
        "applicant_pets",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column(
            "applicant_id",
            sa.Integer(),
            sa.ForeignKey("applicants.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "pet_category",
            sa.String(50),
            nullable=False,
            comment="ペット種別（cat/other）",
        ),
        sa.Column(
            "count", sa.Integer(), nullable=False, server_default="1", comment="頭数"
        ),
        sa.Column("breed_or_type", sa.String(100), nullable=True, comment="品種・種類"),
        sa.Column(
            "age_note",
            sa.String(100),
            nullable=True,
            comment="年齢（自由表現：3歳、推定2歳など）",
        ),
        sa.CheckConstraint(
            "pet_category IN ('cat','other')", name="ck_applicant_pet_category"
        ),
    )
    op.create_index(
        "ix_applicant_pets_applicant_id",
        "applicant_pets",
        ["applicant_id"],
        unique=False,
    )


def downgrade() -> None:
    # テーブル削除
    op.drop_index("ix_applicant_pets_applicant_id", table_name="applicant_pets")
    op.drop_table("applicant_pets")

    op.drop_index(
        "ix_applicant_household_members_applicant_id",
        table_name="applicant_household_members",
    )
    op.drop_table("applicant_household_members")

    # インデックス削除
    op.drop_index("ix_applicants_phone", table_name="applicants")
    op.drop_index("ix_applicants_name_kana", table_name="applicants")

    # カラム削除
    columns_to_drop = [
        "name_kana",
        "age",
        "phone",
        "contact_type",
        "contact_line_id",
        "contact_email",
        "postal_code",
        "address1",
        "address2",
        "occupation",
        "occupation_other",
        "desired_cat_alias",
        "emergency_relation",
        "emergency_relation_other",
        "emergency_name",
        "emergency_phone",
        "family_intent",
        "pet_permission",
        "pet_limit_type",
        "pet_limit_count",
        "housing_type",
        "housing_ownership",
        "relocation_plan",
        "relocation_time_note",
        "relocation_cat_plan",
        "allergy_status",
        "smoker_in_household",
        "monthly_budget_yen",
        "alone_time_status",
        "alone_time_weekly_days",
        "alone_time_hours",
        "has_existing_cat",
        "has_other_pets",
    ]
    for col in columns_to_drop:
        op.drop_column("applicants", col)
