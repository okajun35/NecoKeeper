"""merge heads after coat_color and status_history nullable

Revision ID: 20260125_001
Revises: 20260120_1206_coat_color, 20260124_001
Create Date: 2026-01-25 00:00:00.000000

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "20260125_001"
down_revision: str | Sequence[str] | None = (
    "20260120_1206_coat_color",
    "20260124_001",
)
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Merge heads."""
    pass


def downgrade() -> None:
    """Unmerge heads."""
    pass
