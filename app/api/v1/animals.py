"""
猫管理APIエンドポイント

猫の個体情報のCRUD操作を提供します。
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
from app.models.animal import Animal
from app.models.user import User
from app.schemas.animal import (
    AnimalCreate,
    AnimalListResponse,
    AnimalResponse,
    AnimalUpdate,
)
from app.services import animal_service

router = APIRouter(prefix="/animals", tags=["猫管理"])


@router.get("", response_model=AnimalListResponse)
async def list_animals(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
    status: str | None = Query(None, description="ステータスフィルター"),
) -> AnimalListResponse:
    """
    猫一覧を取得

    ページネーション付きで猫の一覧を取得します。
    ステータスでフィルタリングすることも可能です。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）
        status: ステータスフィルター（保護中、譲渡可能、譲渡済み等）

    Returns:
        AnimalListResponse: 猫一覧とページネーション情報
    """
    return animal_service.list_animals(
        db=db, page=page, page_size=page_size, status_filter=status
    )


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_animal(
    animal_data: AnimalCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
) -> Animal:
    """
    猫を登録

    新しい猫の個体情報を登録します。
    登録時にステータス履歴も自動的に作成されます。

    Args:
        animal_data: 猫登録データ
        db: データベースセッション
        current_user: 現在のユーザー（animal:write権限が必要）

    Returns:
        AnimalResponse: 登録された猫の情報
    """
    return animal_service.create_animal(
        db=db, animal_data=animal_data, user_id=current_user.id
    )


@router.get("/search", response_model=AnimalListResponse)
async def search_animals(
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
    q: str = Query(..., min_length=1, description="検索クエリ"),
    page: int = Query(1, ge=1, description="ページ番号"),
    page_size: int = Query(20, ge=1, le=100, description="1ページあたりの件数"),
) -> AnimalListResponse:
    """
    猫を検索

    名前、柄、特徴で部分一致検索を行います。

    Args:
        db: データベースセッション
        current_user: 現在のユーザー
        q: 検索クエリ（最低1文字）
        page: ページ番号（1から開始）
        page_size: 1ページあたりの件数（最大100）

    Returns:
        AnimalListResponse: 検索結果とページネーション情報
    """
    return animal_service.search_animals(db=db, query=q, page=page, page_size=page_size)


@router.get("/{animal_id}", response_model=AnimalResponse)
async def get_animal(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> Animal:
    """
    猫の詳細を取得

    指定されたIDの猫の詳細情報を取得します。

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        AnimalResponse: 猫の詳細情報

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    return animal_service.get_animal(db=db, animal_id=animal_id)


@router.put("/{animal_id}", response_model=AnimalResponse)
async def update_animal(
    animal_id: int,
    animal_data: AnimalUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
) -> Animal:
    """
    猫情報を更新

    指定されたIDの猫の情報を更新します。
    ステータスが変更された場合は履歴も自動的に記録されます。

    Args:
        animal_id: 猫ID
        animal_data: 更新データ
        db: データベースセッション
        current_user: 現在のユーザー（animal:write権限が必要）

    Returns:
        AnimalResponse: 更新された猫の情報

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    return animal_service.update_animal(
        db=db, animal_id=animal_id, animal_data=animal_data, user_id=current_user.id
    )


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(  # type: ignore[no-untyped-def]
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:delete"))],
):
    """
    猫を削除

    指定されたIDの猫を削除します（物理削除）。

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー（animal:delete権限が必要）

    Raises:
        HTTPException: 猫が見つからない場合（404）

    Note:
        実際のアプリケーションでは論理削除を推奨
    """
    animal_service.delete_animal(db=db, animal_id=animal_id)
