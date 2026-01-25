"""add coat color to animals

Issue #81: プロフィールに毛色を追加
- animalsテーブルにcoat_colorカラムを追加（String(100)、nullable）
- animalsテーブルにcoat_color_noteカラムを追加（Text、nullable）

Revision ID: 20260120_1206_coat_color
Revises: aff301b23380
Create Date: 2026-01-20

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260120_1206_coat_color"
down_revision: str | None = "aff301b23380"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add coat_color and coat_color_note columns to animals table"""
    # Add coat_color column
    op.add_column(
        "animals",
        sa.Column(
            "coat_color",
            sa.String(100),
            nullable=True,
            comment="毛色（選択肢から選択）",
        ),
    )

    # Add coat_color_note column
    op.add_column(
        "animals",
        sa.Column(
            "coat_color_note",
            sa.Text(),
            nullable=True,
            comment="毛色の補足情報（例: 淡い、パステル、黒少なめ）",
        ),
    )


def downgrade() -> None:
    """Remove coat_color and coat_color_note columns from animals table"""
    op.drop_column("animals", "coat_color_note")
    op.drop_column("animals", "coat_color")
