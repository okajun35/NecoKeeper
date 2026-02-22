"""issue134 adoptions consultations and care log scale update

Revision ID: 20260218_001
Revises: 20260208_002
Create Date: 2026-02-18 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260218_001"
down_revision: str | None = "20260208_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Apply issue #134 schema and data changes."""
    op.create_table(
        "adoption_consultations",
        sa.Column(
            "id", sa.Integer(), primary_key=True, autoincrement=True, comment="主キー"
        ),
        sa.Column(
            "name_kana", sa.String(length=100), nullable=False, comment="ふりがな"
        ),
        sa.Column("name", sa.String(length=100), nullable=False, comment="氏名"),
        sa.Column("phone", sa.String(length=50), nullable=False, comment="電話番号"),
        sa.Column(
            "contact_type",
            sa.String(length=20),
            nullable=False,
            comment="連絡手段（line/email）",
        ),
        sa.Column(
            "contact_line_id", sa.String(length=100), nullable=True, comment="LINE ID"
        ),
        sa.Column(
            "contact_email",
            sa.String(length=255),
            nullable=True,
            comment="メールアドレス",
        ),
        sa.Column("consultation_note", sa.Text(), nullable=False, comment="相談内容"),
        sa.Column(
            "status",
            sa.String(length=20),
            nullable=False,
            server_default="open",
            comment="相談ステータス（open/converted/closed）",
        ),
        sa.Column(
            "applicant_id",
            sa.Integer(),
            sa.ForeignKey("applicants.id", ondelete="SET NULL"),
            nullable=True,
            comment="変換先の里親申込ID",
        ),
        sa.Column(
            "created_at", sa.DateTime(), nullable=False, comment="作成日時（JST）"
        ),
        sa.Column(
            "updated_at", sa.DateTime(), nullable=False, comment="更新日時（JST）"
        ),
    )
    op.create_index(
        "ix_adoption_consultations_name",
        "adoption_consultations",
        ["name"],
        unique=False,
    )
    op.create_index(
        "ix_adoption_consultations_phone",
        "adoption_consultations",
        ["phone"],
        unique=False,
    )
    op.create_index(
        "ix_adoption_consultations_status",
        "adoption_consultations",
        ["status"],
        unique=False,
    )
    op.create_index(
        "ix_adoption_consultations_created_at",
        "adoption_consultations",
        ["created_at"],
        unique=False,
    )

    with op.batch_alter_table("care_logs") as batch_op:
        batch_op.add_column(
            sa.Column(
                "vomiting",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
                comment="嘔吐有無（True=有り、False=無し）",
            )
        )

    op.execute(
        """
        UPDATE care_logs
        SET appetite = CASE appetite
            WHEN 1.0 THEN 1.0
            WHEN 0.75 THEN 1.0
            WHEN 0.5 THEN 0.5
            WHEN 0.25 THEN 0.0
            WHEN 0.0 THEN 0.0
            ELSE appetite
        END
        """
    )

    op.execute(
        """
        UPDATE care_logs
        SET energy = CASE energy
            WHEN 1 THEN 1
            WHEN 2 THEN 1
            WHEN 3 THEN 2
            WHEN 4 THEN 3
            WHEN 5 THEN 3
            ELSE energy
        END
        """
    )


def downgrade() -> None:
    """Revert issue #134 schema and data changes."""
    op.execute(
        """
        UPDATE care_logs
        SET appetite = CASE appetite
            WHEN 1.0 THEN 1.0
            WHEN 0.5 THEN 0.5
            WHEN 0.0 THEN 0.0
            ELSE appetite
        END
        """
    )

    op.execute(
        """
        UPDATE care_logs
        SET energy = CASE energy
            WHEN 1 THEN 1
            WHEN 2 THEN 3
            WHEN 3 THEN 5
            ELSE energy
        END
        """
    )

    with op.batch_alter_table("care_logs") as batch_op:
        batch_op.drop_column("vomiting")

    op.drop_index(
        "ix_adoption_consultations_created_at", table_name="adoption_consultations"
    )
    op.drop_index(
        "ix_adoption_consultations_status", table_name="adoption_consultations"
    )
    op.drop_index(
        "ix_adoption_consultations_phone", table_name="adoption_consultations"
    )
    op.drop_index("ix_adoption_consultations_name", table_name="adoption_consultations")
    op.drop_table("adoption_consultations")
