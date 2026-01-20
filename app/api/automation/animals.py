"""
猫登録Automation API

Kiro Hook、MCP、自動化スクリプト専用の猫登録エンドポイントを提供します。

Context7参照: /fastapi/fastapi - APIRouter, HTTPException
Requirements: 4.1, 4.2, 4.3, 4.4, 4.5, 4.6, 3.3, 3.4
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.schemas.animal import AnimalCreate, AnimalResponse
from app.schemas.animal_image import AnimalImageResponse
from app.services import image_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/animals",
    response_model=AnimalResponse,
    status_code=status.HTTP_201_CREATED,
    summary="猫を登録（Automation API）",
    description="""
    猫を登録します（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    猫登録に使用されます。API Key認証が必要です。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **特徴**:
    - recorder_id は None（自動化を示す）
    - ステータス履歴は記録されない（自動化のため）

    **Requirements**: 4.1, 4.2, 4.6
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "猫が正常に登録されました",
            "content": {
                "application/json": {
                    "example": {
                        "id": 13,
                        "name": "たま",
                        "photo": None,
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "collar": None,
                        "age_months": 12,
                        "age_is_estimated": False,
                        "gender": "male",
                        "ear_cut": False,
                        "features": None,
                        "status": "QUARANTINE",
                        "protected_at": "2025-11-24",
                        "created_at": "2025-11-24T10:00:00Z",
                        "updated_at": "2025-11-24T10:00:00Z",
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "リクエストデータが不正です",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "性別は male, female, unknown のいずれかである必要があります"
                    }
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "サーバーエラーが発生しました",
            "content": {
                "application/json": {"example": {"detail": "猫の登録に失敗しました"}}
            },
        },
    },
)
def create_animal_automation(
    animal_data: AnimalCreate,
    db: Session = Depends(get_db),
) -> AnimalResponse:
    """
    猫を登録（Automation API）

    Args:
        animal_data: 猫登録データ
        db: データベースセッション

    Returns:
        AnimalResponse: 登録された猫

    Raises:
        HTTPException: データベースエラーが発生した場合（500）
    """
    try:
        # 猫を作成（ステータス履歴は記録しない）
        animal = Animal(**animal_data.model_dump())
        db.add(animal)
        db.commit()
        db.refresh(animal)

        logger.info(
            f"Automation API: 猫を登録しました - "
            f"id={animal.id}, name={animal.name}, pattern={animal.pattern}"
        )

        return AnimalResponse.model_validate(animal)

    except Exception as e:
        db.rollback()
        logger.error(
            f"Automation API: 猫の登録に失敗しました - "
            f"name={animal_data.name}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫の登録に失敗しました",
        ) from e


@router.get(
    "/animals/{animal_id}",
    response_model=AnimalResponse,
    summary="猫情報を取得（Automation API）",
    description="""
    猫情報を取得します（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    猫情報取得に使用されます。API Key認証が必要です。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **Requirements**: 4.4, 4.5, 4.6
    """,
    responses={
        status.HTTP_200_OK: {
            "description": "猫情報が正常に取得されました",
            "content": {
                "application/json": {
                    "example": {
                        "id": 13,
                        "name": "たま",
                        "photo": None,
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "collar": None,
                        "age_months": 12,
                        "age_is_estimated": False,
                        "gender": "male",
                        "ear_cut": False,
                        "features": None,
                        "status": "QUARANTINE",
                        "protected_at": "2025-11-24",
                        "created_at": "2025-11-24T10:00:00Z",
                        "updated_at": "2025-11-24T10:00:00Z",
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "指定された猫が存在しません",
            "content": {
                "application/json": {
                    "example": {"detail": "ID 999 の猫が見つかりません"}
                }
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "サーバーエラーが発生しました",
            "content": {
                "application/json": {
                    "example": {"detail": "猫情報の取得に失敗しました"}
                }
            },
        },
    },
)
def get_animal_automation(
    animal_id: int,
    db: Session = Depends(get_db),
) -> AnimalResponse:
    """
    猫情報を取得（Automation API）

    Args:
        animal_id: 猫ID
        db: データベースセッション

    Returns:
        AnimalResponse: 猫情報

    Raises:
        HTTPException: 猫が見つからない場合（404）、またはデータベースエラーが発生した場合（500）
    """
    try:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()

        if not animal:
            logger.warning(
                f"Automation API: 猫が見つかりません - animal_id={animal_id}"
            )
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"ID {animal_id} の猫が見つかりません",
            )

        logger.info(
            f"Automation API: 猫情報を取得しました - id={animal.id}, name={animal.name}"
        )

        return AnimalResponse.model_validate(animal)

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Automation API: 猫情報の取得に失敗しました - "
            f"animal_id={animal_id}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="猫情報の取得に失敗しました",
        ) from e


@router.post(
    "/animals/{animal_id}/images",
    response_model=AnimalImageResponse,
    status_code=status.HTTP_201_CREATED,
    summary="猫の画像をアップロード（Automation API）",
    description="""
    猫の画像をアップロードします（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    画像アップロードに使用されます。API Key認証が必要です。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **特徴**:
    - 画像は `media/animals/{animal_id}/gallery/` に保存されます
    - ファイル名はUUIDベースで自動生成されます
    - 画像は自動的に最適化されます

    **Requirements**: 3.3, 3.4
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "画像が正常にアップロードされました",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "animal_id": 42,
                        "image_path": "animals/42/gallery/550e8400-e29b-41d4-a716-446655440000.jpg",
                        "file_size": 102400,
                        "taken_at": None,
                        "description": None,
                        "created_at": "2025-11-24T10:00:00Z",
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "リクエストデータが不正です",
            "content": {
                "application/json": {
                    "examples": {
                        "invalid_file": {
                            "summary": "Invalid File Type",
                            "value": {
                                "detail": "サポートされていないファイル形式です。JPEG、PNG、WebPのみ対応しています"
                            },
                        },
                        "file_too_large": {
                            "summary": "File Too Large",
                            "value": {
                                "detail": "ファイルサイズが上限（5MB）を超えています"
                            },
                        },
                        "too_many_images": {
                            "summary": "Too Many Images",
                            "value": {"detail": "画像枚数が上限（20枚）に達しています"},
                        },
                    }
                }
            },
        },
        status.HTTP_404_NOT_FOUND: {
            "description": "指定された猫が存在しません",
            "content": {
                "application/json": {"example": {"detail": "猫ID 999 が見つかりません"}}
            },
        },
        status.HTTP_500_INTERNAL_SERVER_ERROR: {
            "description": "サーバーエラーが発生しました",
            "content": {
                "application/json": {
                    "example": {"detail": "画像のアップロードに失敗しました"}
                }
            },
        },
    },
)
def upload_animal_image_automation(
    animal_id: int,
    file: UploadFile = File(..., description="アップロードする画像ファイル"),
    db: Session = Depends(get_db),
) -> AnimalImageResponse:
    """
    猫の画像をアップロード（Automation API）

    Args:
        animal_id: 猫ID
        file: アップロードする画像ファイル
        db: データベースセッション

    Returns:
        AnimalImageResponse: アップロードされた画像情報

    Raises:
        HTTPException: 猫が見つからない場合（404）、
                      ファイルが不正な場合（400）、
                      アップロードに失敗した場合（500）
    """
    try:
        # image_service.upload_image を使用して画像をアップロード
        animal_image = image_service.upload_image(
            db=db,
            animal_id=animal_id,
            file=file,
            taken_at=None,
            description=None,
        )

        logger.info(
            f"Automation API: 画像をアップロードしました - "
            f"animal_id={animal_id}, image_id={animal_image.id}, "
            f"path={animal_image.image_path}"
        )

        return AnimalImageResponse.model_validate(animal_image)

    except HTTPException:
        # image_service から発生した HTTPException をそのまま再送出
        raise
    except Exception as e:
        logger.error(
            f"Automation API: 画像のアップロードに失敗しました - "
            f"animal_id={animal_id}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="画像のアップロードに失敗しました",
        ) from e
