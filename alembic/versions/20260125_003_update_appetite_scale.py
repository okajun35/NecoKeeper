"""update appetite scale to fraction values

Revision ID: 20260125_003
Revises: 20260125_002
Create Date: 2026-01-25 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260125_003"
down_revision: str | None = "20260125_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Convert appetite values to fraction scale (1.0 -> 0.0) and update column type."""
    op.execute(
        """
        UPDATE care_logs
        SET appetite = CASE appetite
            WHEN 5 THEN 1.0
            WHEN 4 THEN 0.75
            WHEN 3 THEN 0.5
            WHEN 2 THEN 0.25
            WHEN 1 THEN 0.0
            ELSE appetite
        END
        """
    )

    with op.batch_alter_table("care_logs") as batch_op:
        batch_op.alter_column(
            "appetite",
            existing_type=sa.Integer(),
            type_=sa.Numeric(3, 2),
            nullable=False,
            existing_server_default="3",
            server_default=sa.text("1.0"),
        )


def downgrade() -> None:
    """Revert appetite values to 1-5 scale and restore integer column."""
    op.execute(
        """
        UPDATE care_logs
        SET appetite = CASE appetite
            WHEN 1.0 THEN 5
            WHEN 0.75 THEN 4
            WHEN 0.5 THEN 3
            WHEN 0.25 THEN 2
            WHEN 0.0 THEN 1
            ELSE appetite
        END
        """
    )

    with op.batch_alter_table("care_logs") as batch_op:
        batch_op.alter_column(
            "appetite",
            existing_type=sa.Numeric(3, 2),
            type_=sa.Integer(),
            nullable=False,
            existing_server_default="1.0",
            server_default=sa.text("3"),
        )
