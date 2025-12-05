"""convert_timestamps_to_jst

Revision ID: 32ea14574f86
Revises: 5dcf554c0141
Create Date: 2025-12-03 20:55:52.539729

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "32ea14574f86"
down_revision: str | None = "5dcf554c0141"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """既存データのタイムスタンプをUTC→JSTに変換（+9時間）"""

    # 1. care_logs テーブル
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 2. animals テーブル
    op.execute("""
        UPDATE animals
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)

    # 3. medical_records テーブル
    op.execute("""
        UPDATE medical_records
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 4. medical_actions テーブル
    op.execute("""
        UPDATE medical_actions
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours'),
            last_updated_at = datetime(last_updated_at, '+9 hours')
    """)

    # 5. users テーブル
    op.execute("""
        UPDATE users
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)

    # 6. volunteers テーブル
    op.execute("""
        UPDATE volunteers
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)

    # 7. status_history テーブル
    op.execute("""
        UPDATE status_history
        SET changed_at = datetime(changed_at, '+9 hours')
    """)

    # 8. adoption_records テーブル
    op.execute("""
        UPDATE adoption_records
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)

    # 9. applicants テーブル
    op.execute("""
        UPDATE applicants
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)

    # 10. animal_images テーブル
    op.execute("""
        UPDATE animal_images
        SET created_at = datetime(created_at, '+9 hours')
    """)

    # 11. audit_logs テーブル
    op.execute("""
        UPDATE audit_logs
        SET created_at = datetime(created_at, '+9 hours')
    """)

    # 12. settings テーブル
    op.execute("""
        UPDATE settings
        SET created_at = datetime(created_at, '+9 hours'),
            updated_at = datetime(updated_at, '+9 hours')
    """)


def downgrade() -> None:
    """ロールバック: JST→UTCに戻す（-9時間）"""

    # 1. care_logs テーブル
    op.execute("""
        UPDATE care_logs
        SET created_at = datetime(created_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)

    # 2. animals テーブル
    op.execute("""
        UPDATE animals
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)

    # 3. medical_records テーブル
    op.execute("""
        UPDATE medical_records
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)

    # 4. medical_actions テーブル
    op.execute("""
        UPDATE medical_actions
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours'),
            last_updated_at = datetime(last_updated_at, '-9 hours')
    """)

    # 5. users テーブル
    op.execute("""
        UPDATE users
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)

    # 6. volunteers テーブル
    op.execute("""
        UPDATE volunteers
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)

    # 7. status_history テーブル
    op.execute("""
        UPDATE status_history
        SET changed_at = datetime(changed_at, '-9 hours')
    """)

    # 8. adoption_records テーブル
    op.execute("""
        UPDATE adoption_records
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)

    # 9. applicants テーブル
    op.execute("""
        UPDATE applicants
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)

    # 10. animal_images テーブル
    op.execute("""
        UPDATE animal_images
        SET created_at = datetime(created_at, '-9 hours')
    """)

    # 11. audit_logs テーブル
    op.execute("""
        UPDATE audit_logs
        SET created_at = datetime(created_at, '-9 hours')
    """)

    # 12. settings テーブル
    op.execute("""
        UPDATE settings
        SET created_at = datetime(created_at, '-9 hours'),
            updated_at = datetime(updated_at, '-9 hours')
    """)
