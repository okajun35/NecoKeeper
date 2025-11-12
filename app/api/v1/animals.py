"""
猫管理APIエンドポイント

猫の個体情報のCRUD操作を提供します。
"""

from typing import Annotated

from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.database import get_db
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
):
    """
    猫一覧を取得

    ページネーション付きで猫の一覧を取得します。
    ステータスでフィルタリングすることも可能です。
    """
    return animal_service.list_animals(
        db=db, page=page, page_size=page_size, status_filter=status
    )


@router.post("", response_model=AnimalResponse, status_code=status.HTTP_201_CREATED)
async def create_animal(
    animal_data: AnimalCreate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
):
    """
    猫を登録

    新しい猫の個体情報を登録します。
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
):
    """
    猫を検索

    名前、柄、特徴で部分一致検索を行います。
    """
    return animal_service.search_animals(db=db, query=q, page=page, page_size=page_size)


@router.get("/{animal_id}", response_model=AnimalResponse)
async def get_animal(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
):
    """
    猫の詳細を取得

    指定されたIDの猫の詳細情報を取得します。
    """
    return animal_service.get_animal(db=db, animal_id=animal_id)


@router.put("/{animal_id}", response_model=AnimalResponse)
async def update_animal(
    animal_id: int,
    animal_data: AnimalUpdate,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:write"))],
):
    """
    猫情報を更新

    指定されたIDの猫の情報を更新します。
    """
    return animal_service.update_animal(
        db=db, animal_id=animal_id, animal_data=animal_data, user_id=current_user.id
    )


@router.delete("/{animal_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_animal(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(require_permission("animal:delete"))],
):
    """
    猫を削除

    指定されたIDの猫を削除します。
    """
    animal_service.delete_animal(db=db, animal_id=animal_id)
