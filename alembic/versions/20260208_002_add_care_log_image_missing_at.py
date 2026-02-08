"""add care log image missing timestamp

Revision ID: 20260208_002
Revises: 20260208_001
Create Date: 2026-02-08 00:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260208_002"
down_revision: str | None = "20260208_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add care log image missing detection timestamp column."""
    op.add_column(
        "care_logs",
        sa.Column(
            "care_image_missing_at",
            sa.DateTime(),
            nullable=True,
            comment="世話記録画像欠損検知日時（JST）",
        ),
    )
    op.create_index(
        "ix_care_logs_care_image_missing_at",
        "care_logs",
        ["care_image_missing_at"],
    )


def downgrade() -> None:
    """Remove care log image missing detection timestamp column."""
    op.drop_index("ix_care_logs_care_image_missing_at", table_name="care_logs")
    op.drop_column("care_logs", "care_image_missing_at")
