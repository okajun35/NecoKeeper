"""add current_location_note to animals

Revision ID: 8cd9c91fa71c
Revises: 20260120_001_add_location_type
Create Date: 2026-01-20 23:50:40.321044

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "8cd9c91fa71c"
down_revision: str | None = "20260120_001_add_location_type"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # Add current_location_note column to animals table
    op.add_column(
        "animals", sa.Column("current_location_note", sa.Text(), nullable=True)
    )


def downgrade() -> None:
    # Remove current_location_note column from animals table
    op.drop_column("animals", "current_location_note")
