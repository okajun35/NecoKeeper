"""add_defecation_and_stool_condition_to_care_logs

Revision ID: 8b1e0d7b7b6f
Revises: 32ea14574f86
Create Date: 2026-01-05 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8b1e0d7b7b6f"
down_revision: str | None = "32ea14574f86"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add defecation + stool_condition with CHECK constraint."""

    # SQLiteではCHECK制約の追加等でALTERが制限されるため、バッチ操作を使用
    with op.batch_alter_table("care_logs", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "defecation",
                sa.Boolean(),
                nullable=False,
                server_default=sa.text("0"),
                comment="排便有無（True=有り、False=無し）",
            )
        )
        batch_op.add_column(
            sa.Column(
                "stool_condition",
                sa.SmallInteger(),
                nullable=True,
                comment="便の状態（1〜5）",
            )
        )
        batch_op.create_check_constraint(
            op.f("ck_care_logs_defecation_stool_condition"),
            "(defecation = 0 AND stool_condition IS NULL) "
            "OR (defecation = 1 AND stool_condition IS NOT NULL AND stool_condition BETWEEN 1 AND 5)",
        )


def downgrade() -> None:
    """Drop defecation + stool_condition."""

    with op.batch_alter_table("care_logs", schema=None) as batch_op:
        batch_op.drop_constraint(
            op.f("ck_care_logs_defecation_stool_condition"), type_="check"
        )
        batch_op.drop_column("stool_condition")
        batch_op.drop_column("defecation")
