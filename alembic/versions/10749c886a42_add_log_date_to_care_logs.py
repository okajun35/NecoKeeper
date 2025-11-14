"""add_log_date_to_care_logs

Revision ID: 10749c886a42
Revises: 3014b3fef0cf
Create Date: 2025-11-15 01:20:42.254437

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "10749c886a42"
down_revision: str | None = "3014b3fef0cf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # care_logs テーブルに log_date カラムを追加
    op.add_column(
        "care_logs",
        sa.Column(
            "log_date",
            sa.Date(),
            nullable=False,
            server_default=sa.text("CURRENT_DATE"),
            comment="記録日（年月日）",
        ),
    )

    # インデックスを追加
    op.create_index(
        op.f("ix_care_logs_log_date"), "care_logs", ["log_date"], unique=False
    )


def downgrade() -> None:
    # インデックスを削除
    op.drop_index(op.f("ix_care_logs_log_date"), table_name="care_logs")

    # log_date カラムを削除
    op.drop_column("care_logs", "log_date")
