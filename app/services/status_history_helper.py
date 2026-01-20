"""
ステータス・ロケーション変更履歴の記録ヘルパー

animals_service.py と adoption_service.py で統一的に使用する共通関数
"""

from sqlalchemy.orm import Session

from app.models.status_history import StatusHistory


def record_status_change(
    db: Session,
    animal_id: int,
    old_status: str | None,
    new_status: str,
    user_id: int,
    reason: str | None = None,
) -> StatusHistory:
    """
    ステータス変更履歴を統一フォーマットで記録

    新フォーマット（field/old_value/new_value）と
    旧フォーマット（old_status/new_status）の両方を設定して、
    後方互換性を保ちながら新APIに対応

    Args:
        db: データベースセッション
        animal_id: 猫ID
        old_status: 変更前のステータス値
        new_status: 変更後のステータス値
        user_id: 変更者ID
        reason: 変更理由（任意）

    Returns:
        StatusHistory: 作成された履歴レコード
    """
    status_history = StatusHistory(
        animal_id=animal_id,
        field="status",
        old_value=old_status,
        new_value=new_status,
        reason=reason,
        changed_by=user_id,
        # 後方互換性のための旧カラム設定
        old_status=old_status,
        new_status=new_status,
    )
    db.add(status_history)
    return status_history


def record_location_change(
    db: Session,
    animal_id: int,
    old_location_type: str | None,
    new_location_type: str,
    user_id: int,
    reason: str | None = None,
) -> StatusHistory:
    """
    ロケーションタイプ変更履歴を統一フォーマットで記録

    新フォーマット（field/old_value/new_value）で記録

    Args:
        db: データベースセッション
        animal_id: 猫ID
        old_location_type: 変更前のロケーションタイプ
        new_location_type: 変更後のロケーションタイプ
        user_id: 変更者ID
        reason: 変更理由（任意）

    Returns:
        StatusHistory: 作成された履歴レコード
    """
    location_history = StatusHistory(
        animal_id=animal_id,
        field="location_type",
        old_value=old_location_type,
        new_value=new_location_type,
        reason=reason,
        changed_by=user_id,
    )
    db.add(location_history)
    return location_history
