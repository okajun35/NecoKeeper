"""
画像ギャラリーサービス

猫の複数画像管理機能を提供します。
"""

from __future__ import annotations

import logging
from collections.abc import Sequence
from datetime import date
from pathlib import Path

from fastapi import HTTPException, UploadFile, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.config import get_settings
from app.models.animal import Animal
from app.models.animal_image import AnimalImage
from app.utils.image import (
    delete_image_file,
    save_and_optimize_image,
    validate_image_file,
)

settings = get_settings()
logger = logging.getLogger(__name__)

# デフォルト設定
DEFAULT_MAX_IMAGES_PER_ANIMAL = 20
DEFAULT_MAX_IMAGE_SIZE_MB = 5


def get_image_limits(db: Session) -> tuple[int, int]:
    """
    画像制限設定を取得

    Args:
        db: データベースセッション

    Returns:
        tuple[int, int]: (最大画像枚数, 最大ファイルサイズ（バイト）)

    Example:
        >>> max_images, max_size = get_image_limits(db)
        >>> print(f"最大{max_images}枚、最大{max_size / (1024 * 1024)}MB")
    """
    from app.models.setting import Setting

    # 最大画像枚数を取得
    stmt = select(Setting).where(Setting.key == "max_images_per_animal")
    result = db.execute(stmt)
    max_images_setting = result.scalar_one_or_none()

    if max_images_setting and max_images_setting.value:
        try:
            max_images = int(max_images_setting.value)
        except ValueError:
            logger.warning(
                f"max_images_per_animalの値が不正です: {max_images_setting.value}"
            )
            max_images = DEFAULT_MAX_IMAGES_PER_ANIMAL
    else:
        max_images = DEFAULT_MAX_IMAGES_PER_ANIMAL

    # 最大ファイルサイズを取得
    stmt = select(Setting).where(Setting.key == "max_image_size_mb")
    result = db.execute(stmt)
    max_size_setting = result.scalar_one_or_none()

    if max_size_setting and max_size_setting.value:
        try:
            max_size_mb = float(max_size_setting.value)
            max_size_bytes = int(max_size_mb * 1024 * 1024)
        except ValueError:
            logger.warning(f"max_image_size_mbの値が不正です: {max_size_setting.value}")
            max_size_bytes = DEFAULT_MAX_IMAGE_SIZE_MB * 1024 * 1024
    else:
        max_size_bytes = DEFAULT_MAX_IMAGE_SIZE_MB * 1024 * 1024

    return max_images, max_size_bytes


def count_animal_images(db: Session, animal_id: int) -> int:
    """
    猫の画像枚数をカウント

    Args:
        db: データベースセッション
        animal_id: 猫ID

    Returns:
        int: 画像枚数

    Example:
        >>> count = count_animal_images(db, 1)
        >>> print(f"猫ID 1の画像枚数: {count}")
    """
    stmt = select(AnimalImage).where(AnimalImage.animal_id == animal_id)
    result = db.execute(stmt)
    return len(result.scalars().all())


async def upload_image(
    db: Session,
    animal_id: int,
    file: UploadFile,
    taken_at: date | None = None,
    description: str | None = None,
) -> AnimalImage:
    """
    猫の画像をアップロード

    Args:
        db: データベースセッション
        animal_id: 猫ID
        file: アップロードファイル
        taken_at: 撮影日（任意）
        description: 説明（任意）

    Returns:
        AnimalImage: 保存された画像レコード

    Raises:
        HTTPException: 猫が存在しない、枚数制限超過、ファイルサイズ超過の場合

    Example:
        >>> from fastapi import UploadFile
        >>> file = UploadFile(filename="cat.jpg", file=open("cat.jpg", "rb"))
        >>> image = await upload_image(db, 1, file, description="元気な様子")
        >>> print(f"画像ID: {image.id}")
    """
    # 猫の存在確認
    stmt = select(Animal).where(Animal.id == animal_id)
    result = db.execute(stmt)
    animal = result.scalar_one_or_none()

    if not animal:
        logger.warning(f"猫が見つかりません: animal_id={animal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    # 画像制限を取得
    max_images, max_size_bytes = get_image_limits(db)

    # 枚数制限チェック
    current_count = count_animal_images(db, animal_id)
    if current_count >= max_images:
        logger.warning(
            f"画像枚数制限超過: animal_id={animal_id}, current={current_count}, max={max_images}"
        )
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"画像枚数が上限（{max_images}枚）に達しています",
        )

    # ファイル検証
    validate_image_file(file, max_size=max_size_bytes)

    # ファイルサイズを取得
    file.file.seek(0, 2)
    file_size = file.file.tell()
    file.file.seek(0)

    try:
        # 画像を保存・最適化
        relative_path = await save_and_optimize_image(
            file, destination_dir=f"animals/{animal_id}/gallery"
        )

        # データベースに記録
        animal_image = AnimalImage(
            animal_id=animal_id,
            image_path=relative_path,
            taken_at=taken_at,
            description=description,
            file_size=file_size,
        )
        db.add(animal_image)
        db.commit()
        db.refresh(animal_image)

        logger.info(
            f"画像をアップロードしました: animal_id={animal_id}, image_id={animal_image.id}"
        )
        return animal_image

    except Exception as e:
        db.rollback()
        logger.error(f"画像アップロードに失敗しました: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像のアップロードに失敗しました",
        ) from e


def list_images(
    db: Session,
    animal_id: int,
    sort_by: str = "created_at",
    ascending: bool = False,
) -> Sequence[AnimalImage]:
    """
    猫の画像一覧を取得

    Args:
        db: データベースセッション
        animal_id: 猫ID
        sort_by: ソート基準（"created_at" または "taken_at"）
        ascending: 昇順の場合True、降順の場合False

    Returns:
        Sequence[AnimalImage]: 画像一覧

    Raises:
        HTTPException: 猫が存在しない場合

    Example:
        >>> images = list_images(db, 1, sort_by="taken_at", ascending=False)
        >>> for img in images:
        ...     print(f"画像ID: {img.id}, 撮影日: {img.taken_at}")
    """
    # 猫の存在確認
    animal_stmt = select(Animal).where(Animal.id == animal_id)
    animal_result = db.execute(animal_stmt)
    animal = animal_result.scalar_one_or_none()

    if not animal:
        logger.warning(f"猫が見つかりません: animal_id={animal_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    # 画像一覧を取得
    stmt = select(AnimalImage).where(AnimalImage.animal_id == animal_id)

    # ソート
    if sort_by == "taken_at":
        if ascending:
            stmt = stmt.order_by(AnimalImage.taken_at.asc())
        else:
            stmt = stmt.order_by(AnimalImage.taken_at.desc())
    else:  # created_at
        if ascending:
            stmt = stmt.order_by(AnimalImage.created_at.asc())
        else:
            stmt = stmt.order_by(AnimalImage.created_at.desc())

    result = db.execute(stmt)
    images = result.scalars().all()

    logger.info(f"画像一覧を取得しました: animal_id={animal_id}, count={len(images)}")
    return images


def get_image(db: Session, image_id: int) -> AnimalImage:
    """
    画像を取得

    Args:
        db: データベースセッション
        image_id: 画像ID

    Returns:
        AnimalImage: 画像レコード

    Raises:
        HTTPException: 画像が存在しない場合

    Example:
        >>> image = get_image(db, 1)
        >>> print(f"画像パス: {image.image_path}")
    """
    stmt = select(AnimalImage).where(AnimalImage.id == image_id)
    result = db.execute(stmt)
    image = result.scalar_one_or_none()

    if not image:
        logger.warning(f"画像が見つかりません: image_id={image_id}")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"画像ID {image_id} が見つかりません",
        )

    return image


def delete_image(db: Session, image_id: int) -> bool:
    """
    画像を削除

    Args:
        db: データベースセッション
        image_id: 画像ID

    Returns:
        bool: 削除に成功した場合True

    Raises:
        HTTPException: 画像が存在しない場合

    Example:
        >>> success = delete_image(db, 1)
        >>> if success:
        ...     print("画像を削除しました")
    """
    # 画像を取得
    image = get_image(db, image_id)

    try:
        # ファイルを削除
        file_deleted = delete_image_file(image.image_path)
        if not file_deleted:
            logger.warning(
                f"画像ファイルの削除に失敗しました: image_id={image_id}, path={image.image_path}"
            )

        # データベースから削除
        db.delete(image)
        db.commit()

        logger.info(f"画像を削除しました: image_id={image_id}")
        return True

    except Exception as e:
        db.rollback()
        logger.error(f"画像削除に失敗しました: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像の削除に失敗しました",
        ) from e


def get_image_path(image: AnimalImage) -> Path:
    """
    画像の絶対パスを取得

    Args:
        image: 画像レコード

    Returns:
        Path: 画像ファイルの絶対パス

    Example:
        >>> image = get_image(db, 1)
        >>> path = get_image_path(image)
        >>> print(f"絶対パス: {path}")
    """
    return Path(settings.media_dir) / image.image_path


def update_image_limits(
    db: Session,
    max_images_per_animal: int | None = None,
    max_image_size_mb: float | None = None,
) -> tuple[int, int]:
    """
    画像制限設定を更新

    Args:
        db: データベースセッション
        max_images_per_animal: 1猫あたりの最大画像枚数（任意）
        max_image_size_mb: 1画像あたりの最大ファイルサイズ（MB、任意）

    Returns:
        tuple[int, int]: (最大画像枚数, 最大ファイルサイズ（バイト）)

    Raises:
        HTTPException: 設定値が不正な場合

    Example:
        >>> max_images, max_size = update_image_limits(
        ...     db, max_images_per_animal=30, max_image_size_mb=10.0
        ... )
        >>> print(f"更新後: 最大{max_images}枚、最大{max_size / (1024 * 1024)}MB")
    """
    from app.models.setting import Setting

    try:
        # 最大画像枚数を更新
        if max_images_per_animal is not None:
            if max_images_per_animal < 1 or max_images_per_animal > 100:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="最大画像枚数は1〜100の範囲で指定してください",
                )

            stmt = select(Setting).where(Setting.key == "max_images_per_animal")
            result = db.execute(stmt)
            setting = result.scalar_one_or_none()

            if setting:
                setting.value = str(max_images_per_animal)
            else:
                setting = Setting(
                    key="max_images_per_animal",
                    value=str(max_images_per_animal),
                    description="1猫あたりの最大画像枚数",
                )
                db.add(setting)

        # 最大ファイルサイズを更新
        if max_image_size_mb is not None:
            if max_image_size_mb < 0.1 or max_image_size_mb > 50.0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="最大ファイルサイズは0.1〜50.0MBの範囲で指定してください",
                )

            stmt = select(Setting).where(Setting.key == "max_image_size_mb")
            result = db.execute(stmt)
            setting = result.scalar_one_or_none()

            if setting:
                setting.value = str(max_image_size_mb)
            else:
                setting = Setting(
                    key="max_image_size_mb",
                    value=str(max_image_size_mb),
                    description="1画像あたりの最大ファイルサイズ（MB）",
                )
                db.add(setting)

        db.commit()
        logger.info(
            f"画像制限設定を更新しました: max_images={max_images_per_animal}, max_size_mb={max_image_size_mb}"
        )

        # 更新後の設定を返す
        return get_image_limits(db)

    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        logger.error(f"画像制限設定の更新に失敗しました: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像制限設定の更新に失敗しました",
        ) from e
