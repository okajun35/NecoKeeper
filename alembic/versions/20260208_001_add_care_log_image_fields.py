"""add care log image columns

Revision ID: 20260208_001
Revises: issue83_medical_info
Create Date: 2026-02-08 00:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260208_001"
down_revision: str | None = "issue83_medical_info"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Add private care-log image management columns."""
    op.add_column(
        "care_logs",
        sa.Column(
            "care_image_path",
            sa.String(length=255),
            nullable=True,
            comment="世話記録画像の保存キー（非公開ストレージ）",
        ),
    )
    op.add_column(
        "care_logs",
        sa.Column(
            "care_image_uploaded_at",
            sa.DateTime(),
            nullable=True,
            comment="世話記録画像アップロード日時（JST）",
        ),
    )
    op.add_column(
        "care_logs",
        sa.Column(
            "care_image_deleted_at",
            sa.DateTime(),
            nullable=True,
            comment="世話記録画像論理削除日時（JST）",
        ),
    )
    op.create_index(
        "ix_care_logs_care_image_deleted_at",
        "care_logs",
        ["care_image_deleted_at"],
    )


def downgrade() -> None:
    """Remove private care-log image management columns."""
    op.drop_index("ix_care_logs_care_image_deleted_at", table_name="care_logs")
    op.drop_column("care_logs", "care_image_deleted_at")
    op.drop_column("care_logs", "care_image_uploaded_at")
    op.drop_column("care_logs", "care_image_path")
