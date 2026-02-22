"""replace animal age with months

Revision ID: f4e98ee7ca5a
Revises: 8b1e0d7b7b6f
Create Date: 2026-01-14 21:53:25.581996

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f4e98ee7ca5a"
down_revision: str | None = "8b1e0d7b7b6f"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("animals") as batch_op:
        batch_op.add_column(
            sa.Column(
                "age_months", sa.Integer(), nullable=True, comment="月齢（null=不明）"
            )
        )
        batch_op.add_column(
            sa.Column(
                "age_is_estimated",
                sa.Boolean(),
                nullable=False,
                server_default="0",
                comment="推定月齢フラグ",
            )
        )
        batch_op.drop_column("age")


def downgrade() -> None:
    with op.batch_alter_table("animals") as batch_op:
        batch_op.add_column(
            sa.Column(
                "age",
                sa.String(length=50),
                nullable=False,
                server_default="成猫",
                comment="年齢・大きさ（例: 子猫、成猫、老猫）",
            )
        )
        batch_op.drop_column("age_is_estimated")
        batch_op.drop_column("age_months")
