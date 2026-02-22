"""migrate status values from Japanese to English

Revision ID: 20260121_002
Revises: 8cd9c91fa71c
Create Date: 2026-01-21 10:00:00.000000

This migration converts existing status values from Japanese to English:
- 保護中 → QUARANTINE
- 治療中 → IN_CARE
- 譲渡可能 → TRIAL
- 譲渡済み → ADOPTED
- 死亡 → DECEASED
"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260121_002"
down_revision: str | None = "8cd9c91fa71c"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None

# Status value mappings
STATUS_MAPPINGS = {
    "保護中": "QUARANTINE",
    "治療中": "IN_CARE",
    "譲渡可能": "TRIAL",
    "譲渡済み": "ADOPTED",
    "死亡": "DECEASED",
}

REVERSE_MAPPINGS = {v: k for k, v in STATUS_MAPPINGS.items()}


def upgrade() -> None:
    """Migrate status values from Japanese to English"""
    connection = op.get_bind()

    # Update animals table
    for old_status, new_status in STATUS_MAPPINGS.items():
        connection.execute(
            sa.text(
                "UPDATE animals SET status = :new_status WHERE status = :old_status"
            ),
            {"new_status": new_status, "old_status": old_status},
        )

    # Update StatusHistory table if old_status/new_status columns exist
    # Check if columns exist by attempting an update (gracefully handle if not present)
    try:
        for old_status, new_status in STATUS_MAPPINGS.items():
            connection.execute(
                sa.text(
                    "UPDATE status_history SET old_status = :new_status WHERE old_status = :old_status"
                ),
                {"new_status": new_status, "old_status": old_status},
            )
            connection.execute(
                sa.text(
                    "UPDATE status_history SET new_status = :new_status WHERE new_status = :old_status"
                ),
                {"new_status": new_status, "old_status": old_status},
            )
    except Exception:
        # Columns might not exist or table might not have these columns yet
        pass


def downgrade() -> None:
    """Revert status values from English back to Japanese"""
    connection = op.get_bind()

    # Update animals table
    for new_status, old_status in REVERSE_MAPPINGS.items():
        connection.execute(
            sa.text(
                "UPDATE animals SET status = :old_status WHERE status = :new_status"
            ),
            {"old_status": old_status, "new_status": new_status},
        )

    # Update StatusHistory table if old_status/new_status columns exist
    try:
        for new_status, old_status in REVERSE_MAPPINGS.items():
            connection.execute(
                sa.text(
                    "UPDATE status_history SET old_status = :old_status WHERE old_status = :new_status"
                ),
                {"old_status": old_status, "new_status": new_status},
            )
            connection.execute(
                sa.text(
                    "UPDATE status_history SET new_status = :old_status WHERE new_status = :new_status"
                ),
                {"old_status": old_status, "new_status": new_status},
            )
    except Exception:
        # Columns might not exist or table might not have these columns yet
        pass
