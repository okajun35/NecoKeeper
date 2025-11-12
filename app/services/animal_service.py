"""
猫管理サービス

猫の個体情報のCRUD操作を提供します。
"""

from fastapi import HTTPException, status
from sqlalchemy import or_
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.status_history import StatusHistory
from app.schemas.animal import AnimalCreate, AnimalListResponse, AnimalUpdate


def create_animal(db: Session, animal_data: AnimalCreate, user_id: int) -> Animal:
    """
    猫を登録

    Args:
        db: データベースセッション
        animal_data: 猫登録データ
        user_id: 登録者のユーザーID

    Returns:
        Animal: 登録された猫
    """
    # 猫を作成
    animal = Animal(**animal_data.model_dump())
    db.add(animal)
    db.flush()  # IDを取得するためにflush

    # ステータス履歴を記録
    status_history = StatusHistory(
        animal_id=animal.id,
        old_status=None,
        new_status=animal.status,
        changed_by=user_id,
        reason="初回登録",
    )
    db.add(status_history)

    db.commit()
    db.refresh(animal)

    return animal


def get_animal(db: Session, animal_id: int) -> Animal:
    """
    猫の詳細を取得

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        Animal: 猫情報

    Raises:
        HTTPException: 猫が見つからない場合
    """
    animal = db.query(Animal).filter(Animal.id == animal_id).first()

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {animal_id} の猫が見つかりません",
        )

    return animal


def update_animal(
    db: Session, animal_id: int, animal_data: AnimalUpdate, user_id: int
) -> Animal:
    """
    猫情報を更新

    Args:
        db: データベースセッション
        animal_id: 猫ID
        animal_data: 更新データ
        user_id: 更新者のユーザーID

    Returns:
        Animal: 更新された猫

    Raises:
        HTTPException: 猫が見つからない場合
    """
    animal = get_animal(db, animal_id)

    # ステータスが変更された場合は履歴を記録
    update_dict = animal_data.model_dump(exclude_unset=True)
    if "status" in update_dict and update_dict["status"] != animal.status:
        status_history = StatusHistory(
            animal_id=animal.id,
            old_status=animal.status,
            new_status=update_dict["status"],
            changed_by=user_id,
            reason="ステータス更新",
        )
        db.add(status_history)

    # 猫情報を更新
    for key, value in update_dict.items():
        setattr(animal, key, value)

    db.commit()
    db.refresh(animal)

    return animal


def delete_animal(db: Session, animal_id: int) -> None:
    """
    猫を削除（物理削除）

    Note: 実際のアプリケーションでは論理削除を推奨

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Raises:
        HTTPException: 猫が見つからない場合
    """
    animal = get_animal(db, animal_id)
    db.delete(animal)
    db.commit()


def list_animals(
    db: Session, page: int = 1, page_size: int = 20, status_filter: str | None = None
) -> AnimalListResponse:
    """
    猫一覧を取得（ページネーション付き）

    Args:
        db: データベースセッション
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数
        status_filter: ステータスフィルター

    Returns:
        AnimalListResponse: 猫一覧とページネーション情報
    """
    # クエリを構築
    query = db.query(Animal)

    # ステータスフィルター
    if status_filter:
        query = query.filter(Animal.status == status_filter)

    # 総件数を取得
    total = query.count()

    # ページネーション
    offset = (page - 1) * page_size
    animals = (
        query.order_by(Animal.created_at.desc()).offset(offset).limit(page_size).all()
    )

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return AnimalListResponse(
        items=animals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )


def search_animals(
    db: Session, query: str, page: int = 1, page_size: int = 20
) -> AnimalListResponse:
    """
    猫を検索

    名前、柄、特徴で部分一致検索を行います。

    Args:
        db: データベースセッション
        query: 検索クエリ
        page: ページ番号
        page_size: 1ページあたりの件数

    Returns:
        AnimalListResponse: 検索結果とページネーション情報
    """
    # 検索クエリを構築
    search_query = db.query(Animal).filter(
        or_(
            Animal.name.ilike(f"%{query}%"),
            Animal.pattern.ilike(f"%{query}%"),
            Animal.features.ilike(f"%{query}%"),
        )
    )

    # 総件数を取得
    total = search_query.count()

    # ページネーション
    offset = (page - 1) * page_size
    animals = (
        search_query.order_by(Animal.created_at.desc())
        .offset(offset)
        .limit(page_size)
        .all()
    )

    # 総ページ数を計算
    total_pages = (total + page_size - 1) // page_size

    return AnimalListResponse(
        items=animals,
        total=total,
        page=page,
        page_size=page_size,
        total_pages=total_pages,
    )
