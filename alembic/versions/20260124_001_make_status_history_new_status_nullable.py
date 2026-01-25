"""make status_history.new_status nullable

Revision ID: 20260124_001
Revises: 20260121_002
Create Date: 2026-01-24 09:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260124_001"
down_revision: str | None = "20260121_002"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Allow NULL for status_history.new_status to support non-status changes"""
    with op.batch_alter_table("status_history") as batch_op:
        batch_op.alter_column(
            "new_status",
            existing_type=sa.String(20),
            nullable=True,
        )


def downgrade() -> None:
    """Revert status_history.new_status to NOT NULL"""
    op.execute("UPDATE status_history SET new_status = 'N/A' WHERE new_status IS NULL")
    with op.batch_alter_table("status_history") as batch_op:
        batch_op.alter_column(
            "new_status",
            existing_type=sa.String(20),
            nullable=False,
        )
