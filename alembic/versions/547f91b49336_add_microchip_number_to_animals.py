"""add_microchip_number_to_animals

Revision ID: 547f91b49336
Revises: b91_extend_applicant
Create Date: 2026-01-18 01:45:18.581302

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "547f91b49336"
down_revision: str | None = "b91_extend_applicant"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """マイクロチップ番号カラムを追加"""
    op.add_column(
        "animals",
        sa.Column(
            "microchip_number",
            sa.String(length=20),
            nullable=True,
            comment="マイクロチップ番号（15桁の半角数字、または10桁の英数字）",
        ),
    )

    # UNIQUE制約を持つインデックスを追加
    with op.batch_alter_table("animals") as batch_op:
        batch_op.create_index(
            "ix_animals_microchip_number", ["microchip_number"], unique=True
        )


def downgrade() -> None:
    """マイクロチップ番号カラムを削除"""
    with op.batch_alter_table("animals") as batch_op:
        batch_op.drop_index("ix_animals_microchip_number")
    op.drop_column("animals", "microchip_number")
