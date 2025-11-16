"""make_animal_photo_optional

Revision ID: 5dcf554c0141
Revises: 06bdb1979ddf
Create Date: 2025-11-16 16:56:13.965193

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "5dcf554c0141"
down_revision: str | None = "06bdb1979ddf"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """プロフィール画像を任意項目に変更"""
    # SQLiteではALTER COLUMNがサポートされていないため、バッチ操作を使用
    with op.batch_alter_table("animals", schema=None) as batch_op:
        batch_op.alter_column("photo", existing_type=sa.String(255), nullable=True)


def downgrade() -> None:
    """プロフィール画像を必須項目に戻す"""
    # NULL値をデフォルト値に置き換え
    op.execute(
        "UPDATE animals SET photo = '/static/images/default-cat.svg' WHERE photo IS NULL"
    )

    # SQLiteではALTER COLUMNがサポートされていないため、バッチ操作を使用
    with op.batch_alter_table("animals", schema=None) as batch_op:
        batch_op.alter_column("photo", existing_type=sa.String(255), nullable=False)
