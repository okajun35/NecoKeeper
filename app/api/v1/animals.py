"""
猫管理APIエンドポイント

猫の個体情報のCRUD操作を提供します。
"""

from __future__ import annotations

from io import BytesIO
from typing import Annotated

import qrcode  # type: ignore[import-untyped]
from fastapi import APIRouter, Depends, Query, UploadFile, status
from fastapi.responses import Response
from sqlalchemy.orm import Session

from app.auth.dependencies import get_current_active_user
from app.auth.permissions import require_permission
from app.config import get_settings
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
def list_animals(
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
def create_animal(
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
def search_animals(
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
def get_animal(
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
def update_animal(
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
def delete_animal(  # type: ignore[no-untyped-def]
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


@router.get("/{animal_id}/qr")
def get_animal_qr_code(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> Response:
    """
    猫のQRコード画像を生成

    指定された猫の世話記録入力画面へのQRコードを生成します。
    QRコードをスキャンすると、公開世話記録入力画面が開きます。

    このエンドポイントは認証不要です（QRコードは公開情報のため）。

    Args:
        animal_id: 猫ID
        db: データベースセッション

    Returns:
        Response: QRコード画像（PNG形式）

    Raises:
        HTTPException: 猫が見つからない場合（404）
    """
    # 猫の存在確認
    animal = animal_service.get_animal(db=db, animal_id=animal_id)

    # 設定から基本URLを取得
    settings = get_settings()
    base_url = (
        settings.base_url if hasattr(settings, "base_url") else "http://localhost:8000"
    )

    # 世話記録入力画面のURL
    care_log_url = f"{base_url}/public/care?animal_id={animal.id}"

    # QRコード生成
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(care_log_url)
    qr.make(fit=True)

    # 画像生成
    img = qr.make_image(fill_color="black", back_color="white")

    # BytesIOに保存
    img_io = BytesIO()
    img.save(img_io, "PNG")
    img_io.seek(0)

    return Response(content=img_io.getvalue(), media_type="image/png")


@router.get("/{animal_id}/display-image")
def get_animal_display_image(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    猫の表示用画像パスを取得

    優先順位:
    1. プロフィール画像（animal.photo）
    2. 画像ギャラリーの1枚目
    3. デフォルト画像

    Args:
        animal_id: 猫ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 画像パス {"image_path": "/path/to/image.jpg"}
    """
    image_path = animal_service.get_display_image(db=db, animal_id=animal_id)
    return {"image_path": image_path}


@router.post("/{animal_id}/profile-image")
def upload_profile_image(
    animal_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    プロフィール画像をアップロード

    Args:
        animal_id: 猫ID
        file: 画像ファイル
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: アップロード結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫が見つからない、またはアップロードに失敗した場合
    """
    from app.services import image_service

    # 画像をアップロード（画像ギャラリーに追加）
    image = image_service.upload_image(
        db=db,
        animal_id=animal_id,
        file=file,
        taken_at=None,
        description="プロフィール画像",
    )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}


@router.put("/{animal_id}/profile-image")
def update_profile_image(
    animal_id: int,
    file: UploadFile,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    プロフィール画像を変更

    Args:
        animal_id: 猫ID
        file: 画像ファイル
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 更新結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫が見つからない、またはアップロードに失敗した場合
    """
    from app.services import image_service

    # 画像をアップロード（画像ギャラリーに追加）
    image = image_service.upload_image(
        db=db,
        animal_id=animal_id,
        file=file,
        taken_at=None,
        description="プロフィール画像",
    )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}


@router.put("/{animal_id}/profile-image/from-gallery/{image_id}")
def set_profile_image_from_gallery(
    animal_id: int,
    image_id: int,
    db: Annotated[Session, Depends(get_db)],
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> dict[str, str]:
    """
    画像ギャラリーからプロフィール画像を選択

    Args:
        animal_id: 猫ID
        image_id: 画像ID
        db: データベースセッション
        current_user: 現在のユーザー

    Returns:
        dict: 更新結果 {"image_path": "/path/to/image.jpg"}

    Raises:
        HTTPException: 猫または画像が見つからない場合
    """
    from app.services import image_service

    # 画像の存在確認
    image = image_service.get_image(db, image_id)

    # 画像が指定された猫のものか確認
    if image.animal_id != animal_id:
        from fastapi import HTTPException

        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="指定された画像は別の猫のものです",
        )

    # プロフィール画像として設定
    animal = animal_service.get_animal(db, animal_id)
    animal.photo = f"/media/{image.image_path}"
    db.commit()
    db.refresh(animal)

    return {"image_path": animal.photo}
