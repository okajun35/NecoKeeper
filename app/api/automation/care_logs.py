"""
世話記録登録Automation API

Kiro Hook、MCP、自動化スクリプト専用の世話記録登録エンドポイントを提供します。

Context7参照: /fastapi/fastapi - APIRouter, HTTPException
Requirements: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
"""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.schemas.care_log import CareLogCreate, CareLogResponse
from app.services.care_log_service import create_care_log

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post(
    "/care-logs",
    response_model=CareLogResponse,
    status_code=status.HTTP_201_CREATED,
    summary="世話記録を登録（Automation API）",
    description="""
    世話記録を登録します（Automation API専用）。

    このエンドポイントは、Kiro Hook、MCP、自動化スクリプトからの
    世話記録登録に使用されます。API Key認証が必要です。

    **認証**: X-Automation-Key ヘッダーでAPI Keyを送信

    **特徴**:
    - recorder_id は None（自動化を示す）
    - recorder_name はリクエストから受け取る（例: "OCR自動取込"）
    - from_paper フラグをサポート
    - device_tag をサポート（例: "OCR-Import"）

    **Requirements**: 5.1, 5.2, 5.3, 5.4, 5.5, 5.6
    """,
    responses={
        status.HTTP_201_CREATED: {
            "description": "世話記録が正常に登録されました",
            "content": {
                "application/json": {
                    "example": {
                        "id": 178,
                        "animal_id": 12,
                        "animal_name": "たま",
                        "recorder_id": None,
                        "recorder_name": "OCR自動取込",
                        "log_date": "2025-11-24",
                        "time_slot": "morning",
                        "appetite": 1.0,
                        "energy": 3,
                        "vomiting": False,
                        "urination": True,
                        "cleaning": False,
                        "memo": "排便: あり, 嘔吐: なし, 投薬: なし",
                        "from_paper": True,
                        "ip_address": None,
                        "user_agent": None,
                        "device_tag": "OCR-Import",
                        "created_at": "2025-11-24T10:00:00Z",
                        "last_updated_at": "2025-11-24T10:00:00Z",
                        "last_updated_by": None,
                    }
                }
            },
        },
        status.HTTP_400_BAD_REQUEST: {
            "description": "リクエストデータが不正です",
            "content": {
                "application/json": {
                    "example": {
                        "detail": "時点は morning, noon, evening のいずれかである必要があります"
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
                    "example": {"detail": "世話記録の登録に失敗しました"}
                }
            },
        },
    },
)
def create_care_log_automation(
    care_log_data: CareLogCreate,
    db: Session = Depends(get_db),
) -> CareLogResponse:
    """
    世話記録を登録（Automation API）

    Args:
        care_log_data: 世話記録データ
        db: データベースセッション

    Returns:
        CareLogResponse: 登録された世話記録

    Raises:
        HTTPException: 猫が存在しない場合（404）、またはデータベースエラーが発生した場合（500）
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == care_log_data.animal_id).first()
    if not animal:
        logger.warning(
            f"Automation API: 猫が見つかりません - animal_id={care_log_data.animal_id}"
        )
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {care_log_data.animal_id} の猫が見つかりません",
        )

    # 世話記録を登録
    try:
        care_log = create_care_log(db, care_log_data)

        logger.info(
            f"Automation API: 世話記録を登録しました - "
            f"id={care_log.id}, animal_id={care_log.animal_id}, "
            f"recorder_name={care_log.recorder_name}, device_tag={care_log.device_tag}"
        )

        # レスポンスを作成
        return CareLogResponse(
            id=care_log.id,
            animal_id=care_log.animal_id,
            animal_name=animal.name,
            recorder_id=care_log.recorder_id,
            recorder_name=care_log.recorder_name,
            log_date=care_log.log_date,
            time_slot=care_log.time_slot,
            appetite=care_log.appetite,
            energy=care_log.energy,
            vomiting=care_log.vomiting,
            urination=care_log.urination,
            cleaning=care_log.cleaning,
            memo=care_log.memo,
            from_paper=care_log.from_paper,
            ip_address=care_log.ip_address,
            user_agent=care_log.user_agent,
            device_tag=care_log.device_tag,
            created_at=care_log.created_at,
            last_updated_at=care_log.last_updated_at,
            last_updated_by=care_log.last_updated_by,
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Automation API: 世話記録の登録に失敗しました - "
            f"animal_id={care_log_data.animal_id}, error={e}"
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="世話記録の登録に失敗しました",
        ) from e
