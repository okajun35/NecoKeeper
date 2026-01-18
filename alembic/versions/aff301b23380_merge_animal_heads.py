"""merge animal heads

Revision ID: aff301b23380
Revises: 547f91b49336, 72a47062ea9d
Create Date: 2026-01-18 16:25:14.646247

"""

from collections.abc import Sequence

# revision identifiers, used by Alembic.
revision: str = "aff301b23380"
down_revision: str | None = ("547f91b49336", "72a47062ea9d")
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
