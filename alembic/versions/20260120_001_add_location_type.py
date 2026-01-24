"""Add location_type and unify status_history schema for issue 85

Revision ID: 20260120_001_add_location_type
Revises: aff301b23380
Create Date: 2026-01-20 22:00:00.000000

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "20260120_001_add_location_type"
down_revision: str | None = "aff301b23380"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """
    マイグレーション手順:
    1. animals テーブルに location_type 列を追加
    2. status_history テーブルを汎用化（field, old_value, new_value 追加）
    3. インデックス追加
    """

    # 1. animals.location_type を追加（デフォルト FACILITY）
    op.add_column(
        "animals",
        sa.Column(
            "location_type", sa.String(20), nullable=False, server_default="FACILITY"
        ),
    )

    # 2. status_history テーブルを汎用化
    # 新列追加（既存列は互換性保持のため保留）
    op.add_column("status_history", sa.Column("field", sa.String(50), nullable=True))
    op.add_column(
        "status_history", sa.Column("old_value", sa.String(100), nullable=True)
    )
    op.add_column(
        "status_history", sa.Column("new_value", sa.String(100), nullable=True)
    )

    # 既存 old_status/new_status データを新列に移行（互換性処理）
    op.execute("""
        UPDATE status_history
        SET field = 'status', old_value = old_status, new_value = new_status
        WHERE field IS NULL AND new_status IS NOT NULL
    """)

    # 3. インデックス追加
    op.create_index("ix_animals_location_type", "animals", ["location_type"])
    op.create_index("ix_status_history_field", "status_history", ["field"])


def downgrade() -> None:
    """ロールバック処理"""

    # インデックス削除
    op.drop_index("ix_status_history_field", table_name="status_history")
    op.drop_index("ix_animals_location_type", table_name="animals")

    # status_history 新列削除
    op.drop_column("status_history", "new_value")
    op.drop_column("status_history", "old_value")
    op.drop_column("status_history", "field")

    # animals.location_type 削除
    op.drop_column("animals", "location_type")
