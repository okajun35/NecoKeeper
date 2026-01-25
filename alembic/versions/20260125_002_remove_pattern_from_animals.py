"""remove pattern column from animals

- Move pattern values into coat_color when missing
- Drop pattern column
- Make coat_color NOT NULL

Revision ID: 20260125_002
Revises: 20260125_001
Create Date: 2026-01-25 00:10:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260125_002"
down_revision: str | None = "20260125_001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Remove pattern column and require coat_color."""
    op.execute(
        "UPDATE animals SET coat_color = pattern "
        "WHERE coat_color IS NULL AND pattern IS NOT NULL"
    )

    with op.batch_alter_table("animals") as batch_op:
        batch_op.drop_column("pattern")
        batch_op.alter_column(
            "coat_color",
            existing_type=sa.String(100),
            nullable=False,
        )


def downgrade() -> None:
    """Restore pattern column and make coat_color nullable."""
    with op.batch_alter_table("animals") as batch_op:
        batch_op.add_column(
            sa.Column(
                "pattern",
                sa.String(100),
                nullable=True,
                comment="柄・色（例: キジトラ、三毛、黒猫）",
            )
        )
        batch_op.alter_column(
            "coat_color",
            existing_type=sa.String(100),
            nullable=True,
        )

    op.execute(
        "UPDATE animals SET pattern = coat_color "
        "WHERE pattern IS NULL AND coat_color IS NOT NULL"
    )

    with op.batch_alter_table("animals") as batch_op:
        batch_op.alter_column(
            "pattern",
            existing_type=sa.String(100),
            nullable=False,
        )
