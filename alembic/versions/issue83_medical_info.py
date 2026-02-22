"""Add medical info to Animal and create VaccinationRecord table

Issue #83: プロフィールに医療情報を追加

Revision ID: issue83_medical_info
Revises: 20260125_003
Create Date: 2026-01-27

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "issue83_medical_info"
down_revision: str | None = "20260125_003"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade database schema."""
    # 1. Add medical info columns to animals table
    op.add_column(
        "animals",
        sa.Column(
            "fiv_positive",
            sa.Boolean(),
            nullable=True,
            comment="FIV検査結果（True=陽性, False=陰性, None=不明）",
        ),
    )
    op.add_column(
        "animals",
        sa.Column(
            "felv_positive",
            sa.Boolean(),
            nullable=True,
            comment="FeLV検査結果（True=陽性, False=陰性, None=不明）",
        ),
    )
    op.add_column(
        "animals",
        sa.Column(
            "is_sterilized",
            sa.Boolean(),
            nullable=True,
            comment="避妊・去勢状態（True=済, False=未, None=不明）",
        ),
    )
    op.add_column(
        "animals",
        sa.Column(
            "sterilized_on",
            sa.Date(),
            nullable=True,
            comment="避妊・去勢実施日",
        ),
    )

    # 2. Create indexes for medical info columns
    op.create_index("ix_animals_fiv_positive", "animals", ["fiv_positive"])
    op.create_index("ix_animals_felv_positive", "animals", ["felv_positive"])
    op.create_index("ix_animals_is_sterilized", "animals", ["is_sterilized"])

    # 3. Create vaccination_records table
    op.create_table(
        "vaccination_records",
        sa.Column(
            "id", sa.Integer(), autoincrement=True, nullable=False, comment="主キー"
        ),
        sa.Column(
            "animal_id",
            sa.Integer(),
            nullable=False,
            comment="猫ID",
        ),
        sa.Column(
            "vaccine_category",
            sa.String(20),
            nullable=False,
            comment="ワクチン種別（3core/4core/5core）",
        ),
        sa.Column(
            "administered_on",
            sa.Date(),
            nullable=False,
            comment="接種日",
        ),
        sa.Column(
            "next_due_on",
            sa.Date(),
            nullable=True,
            comment="次回予定日（任意）",
        ),
        sa.Column(
            "memo",
            sa.Text(),
            nullable=True,
            comment="備考（ロット番号等）",
        ),
        sa.Column(
            "created_at",
            sa.DateTime(),
            nullable=False,
            comment="作成日時（JST）",
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(),
            nullable=False,
            comment="更新日時（JST）",
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.ForeignKeyConstraint(
            ["animal_id"],
            ["animals.id"],
            ondelete="CASCADE",
        ),
    )

    # 4. Create indexes for vaccination_records
    op.create_index(
        "ix_vaccination_records_animal_id", "vaccination_records", ["animal_id"]
    )
    op.create_index(
        "ix_vaccination_records_administered_on",
        "vaccination_records",
        ["administered_on"],
    )


def downgrade() -> None:
    """Downgrade database schema."""
    # 1. Drop vaccination_records table and indexes
    op.drop_index(
        "ix_vaccination_records_administered_on", table_name="vaccination_records"
    )
    op.drop_index("ix_vaccination_records_animal_id", table_name="vaccination_records")
    op.drop_table("vaccination_records")

    # 2. Drop medical info indexes
    op.drop_index("ix_animals_is_sterilized", table_name="animals")
    op.drop_index("ix_animals_felv_positive", table_name="animals")
    op.drop_index("ix_animals_fiv_positive", table_name="animals")

    # 3. Drop medical info columns from animals
    op.drop_column("animals", "sterilized_on")
    op.drop_column("animals", "is_sterilized")
    op.drop_column("animals", "felv_positive")
    op.drop_column("animals", "fiv_positive")
