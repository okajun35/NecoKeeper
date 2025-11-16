"""
画像管理APIエンドポイント

猫の複数画像管理のためのAPIエンドポイントです。
"""

from __future__ import annotations

import logging
from datetime import date

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.schemas.animal_image import (
    AnimalImageResponse,
    AnimalImageUpdate,
    ImageLimitsResponse,
)
from app.services import image_service

router = APIRouter(tags=["images"])
logger = logging.getLogger(__name__)


@router.post(
    "/animals/{animal_id}/images",
    response_model=AnimalImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="画像をアップロード",
    description="猫の画像をアップロードします。枚数制限とファイルサイズ制限があります。",
)
async def upload_animal_image(
    animal_id: int,
    file: UploadFile = File(..., description="画像ファイル"),
    taken_at: date | None = Form(None, description="撮影日"),
    description: str | None = Form(None, description="説明"),
    db: Session = Depends(get_db),
) -> AnimalImageResponse:
    """
    猫の画像をアップロード

    Args:
        animal_id: 猫ID
        file: 画像ファイル
        taken_at: 撮影日（任意）
        description: 説明（任意）
        db: データベースセッション

    Returns:
        AnimalImageResponse: アップロードされた画像情報

    Raises:
        HTTPException: 猫が存在しない、枚数制限超過、ファイルサイズ超過の場合
    """
    logger.info(
        f"画像アップロードリクエスト: animal_id={animal_id}, filename={file.filename}"
    )

    image = await image_service.upload_image(
        db=db,
        animal_id=animal_id,
        file=file,
        taken_at=taken_at,
        description=description,
    )

    return AnimalImageResponse.model_validate(image)


@router.get(
    "/animals/{animal_id}/images",
    response_model=list[AnimalImageResponse],
    summary="画像一覧を取得",
    description="猫の画像一覧を取得します。ソート順を指定できます。",
)
def get_animal_images(
    animal_id: int,
    sort_by: str = "created_at",
    ascending: bool = False,
    db: Session = Depends(get_db),
) -> list[AnimalImageResponse]:
    """
    猫の画像一覧を取得

    Args:
        animal_id: 猫ID
        sort_by: ソート基準（"created_at" または "taken_at"）
        ascending: 昇順の場合True、降順の場合False
        db: データベースセッション

    Returns:
        list[AnimalImageResponse]: 画像一覧

    Raises:
        HTTPException: 猫が存在しない場合
    """
    logger.info(f"画像一覧取得リクエスト: animal_id={animal_id}")

    images = image_service.list_images(
        db=db,
        animal_id=animal_id,
        sort_by=sort_by,
        ascending=ascending,
    )

    return [AnimalImageResponse.model_validate(img) for img in images]


@router.get(
    "/animals/{animal_id}/images/limits",
    response_model=ImageLimitsResponse,
    summary="画像制限情報を取得",
    description="猫の画像制限情報（最大枚数、残り枚数など）を取得します。",
)
def get_image_limits(
    animal_id: int,
    db: Session = Depends(get_db),
) -> ImageLimitsResponse:
    """
    画像制限情報を取得

    Args:
        animal_id: 猫ID
        db: データベースセッション

    Returns:
        ImageLimitsResponse: 画像制限情報
    """
    logger.info(f"画像制限情報取得リクエスト: animal_id={animal_id}")

    max_images, max_size_bytes = image_service.get_image_limits(db)
    current_count = image_service.count_animal_images(db, animal_id)
    remaining_count = max(0, max_images - current_count)

    return ImageLimitsResponse(
        max_images_per_animal=max_images,
        max_image_size_mb=max_size_bytes / (1024 * 1024),
        current_count=current_count,
        remaining_count=remaining_count,
    )


@router.get(
    "/{image_id}",
    response_model=AnimalImageResponse,
    summary="画像を取得",
    description="画像IDを指定して画像情報を取得します。",
)
def get_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> AnimalImageResponse:
    """
    画像を取得

    Args:
        image_id: 画像ID
        db: データベースセッション

    Returns:
        AnimalImageResponse: 画像情報

    Raises:
        HTTPException: 画像が存在しない場合
    """
    logger.info(f"画像取得リクエスト: image_id={image_id}")

    image = image_service.get_image(db, image_id)
    return AnimalImageResponse.model_validate(image)


@router.patch(
    "/{image_id}",
    response_model=AnimalImageResponse,
    summary="画像情報を更新",
    description="画像の撮影日や説明を更新します。",
)
def update_image(
    image_id: int,
    image_update: AnimalImageUpdate,
    db: Session = Depends(get_db),
) -> AnimalImageResponse:
    """
    画像情報を更新

    Args:
        image_id: 画像ID
        image_update: 更新内容
        db: データベースセッション

    Returns:
        AnimalImageResponse: 更新後の画像情報

    Raises:
        HTTPException: 画像が存在しない場合
    """
    logger.info(f"画像更新リクエスト: image_id={image_id}")

    # 画像を取得
    image = image_service.get_image(db, image_id)

    # 更新
    if image_update.taken_at is not None:
        image.taken_at = image_update.taken_at
    if image_update.description is not None:
        image.description = image_update.description

    try:
        db.commit()
        db.refresh(image)
        logger.info(f"画像を更新しました: image_id={image_id}")
        return AnimalImageResponse.model_validate(image)
    except Exception as e:
        db.rollback()
        logger.error(f"画像更新に失敗しました: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像の更新に失敗しました",
        ) from e


@router.delete(
    "/{image_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="画像を削除",
    description="画像を削除します。ファイルとデータベースレコードの両方が削除されます。",
    response_model=None,
)
def delete_image(
    image_id: int,
    db: Session = Depends(get_db),
) -> None:
    """
    画像を削除

    Args:
        image_id: 画像ID
        db: データベースセッション

    Raises:
        HTTPException: 画像が存在しない、または削除に失敗した場合
    """
    logger.info(f"画像削除リクエスト: image_id={image_id}")

    image_service.delete_image(db, image_id)


# 設定管理エンドポイント
@router.put(
    "/settings/limits",
    response_model=ImageLimitsResponse,
    summary="画像制限設定を更新",
    description="画像制限設定（最大枚数、最大ファイルサイズ）を更新します。",
)
def update_image_limits_settings(
    max_images_per_animal: int | None = None,
    max_image_size_mb: float | None = None,
    db: Session = Depends(get_db),
) -> ImageLimitsResponse:
    """
    画像制限設定を更新

    Args:
        max_images_per_animal: 1猫あたりの最大画像枚数（任意）
        max_image_size_mb: 1画像あたりの最大ファイルサイズ（MB、任意）
        db: データベースセッション

    Returns:
        ImageLimitsResponse: 更新後の画像制限情報

    Raises:
        HTTPException: 設定値が不正な場合
    """
    logger.info(
        f"画像制限設定更新リクエスト: max_images={max_images_per_animal}, max_size_mb={max_image_size_mb}"
    )

    max_images, max_size_bytes = image_service.update_image_limits(
        db=db,
        max_images_per_animal=max_images_per_animal,
        max_image_size_mb=max_image_size_mb,
    )

    return ImageLimitsResponse(
        max_images_per_animal=max_images,
        max_image_size_mb=max_size_bytes / (1024 * 1024),
        current_count=0,  # 全体の設定なので0
        remaining_count=0,  # 全体の設定なので0
    )
