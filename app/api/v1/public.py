"""
Public APIエンドポイント

認証不要の世話記録入力フォーム用APIを提供します。
QRコードからアクセスするPublicフォームで使用されます。

Requirements: Requirement 3, Requirement 13, Requirement 18
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.animal import Animal
from app.models.care_log import CareLog
from app.schemas.care_log import (
    AllAnimalsStatusResponse,
    AnimalCareLogListResponse,
    AnimalStatusSummary,
    CareLogCreate,
    CareLogResponse,
    CareLogSummary,
    CareLogUpdate,
)
from app.schemas.volunteer import VolunteerResponse
from app.services import care_log_service, volunteer_service
from app.utils.enums import AnimalStatus

router = APIRouter(prefix="/public", tags=["Public API（認証不要）"])


@router.put("/care-logs/animal/{animal_id}/{log_id}", response_model=CareLogResponse)
def update_care_log_public(
    animal_id: int,
    log_id: int,
    care_log_data: CareLogUpdate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> CareLogResponse:
    """
    世話記録を更新（認証不要）

    公開フォームから既存の世話記録を更新します。
    猫ID・時点は変更不可で、IP/UAを再記録します。

    Args:
        animal_id: 猫のID
        log_id: 世話記録ID
        care_log_data: 更新データ（任意項目のみ指定可）
        request: HTTPリクエスト（IPアドレス、User-Agent取得用）
        db: データベースセッション

    Returns:
        CareLogResponse: 更新された世話記録

    Raises:
        HTTPException: 猫または記録が見つからない場合（404）、不正入力（422）
    """

    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    # 元の記録を取得して「時点」不変を担保
    care_log = db.query(CareLog).filter(CareLog.id == log_id).first()
    if not care_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"ID {log_id} の世話記録が見つかりません",
        )

    care_log_data.ip_address = request.client.host if request.client else None
    care_log_data.user_agent = request.headers.get("user-agent")

    return care_log_service.update_care_log(
        db=db,
        care_log_id=log_id,
        care_log_data=care_log_data,
        user_id=None,
        expected_animal_id=animal_id,
        enforce_time_slot=care_log.time_slot,
        care_log=care_log,
    )


@router.get("/animals/{animal_id}")
def get_animal_info(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> dict[str, int | str | None]:
    """
    猫の基本情報を取得（認証不要）

    Publicフォームで猫の名前と顔写真を表示するために使用します。

    Args:
        animal_id: 猫のID
        db: データベースセッション

    Returns:
        dict: 猫の基本情報（id, name, photo）

    Raises:
        HTTPException: 猫が見つからない場合（404）

    Example:
        GET /api/v1/public/animals/123
        Response: {"id": 123, "name": "たま", "photo": "tama.jpg"}
    """
    animal = db.query(Animal).filter(Animal.id == animal_id).first()

    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    return {
        "id": animal.id,
        "name": animal.name,
        "photo": animal.photo,
    }


@router.get("/volunteers", response_model=list[VolunteerResponse])
def get_active_volunteers(
    db: Annotated[Session, Depends(get_db)],
) -> list[VolunteerResponse]:
    """
    アクティブなボランティア一覧を取得（認証不要）

    Publicフォームのボランティア選択リストで使用します。

    Args:
        db: データベースセッション

    Returns:
        list[VolunteerResponse]: アクティブなボランティアのリスト

    Example:
        GET /api/v1/public/volunteers
        Response: [{"id": 1, "name": "田中太郎", ...}, ...]
    """
    volunteers = volunteer_service.get_active_volunteers(db=db)
    return [VolunteerResponse.model_validate(volunteer) for volunteer in volunteers]


@router.post(
    "/care-logs", response_model=CareLogResponse, status_code=status.HTTP_201_CREATED
)
def create_care_log_public(
    care_log_data: CareLogCreate,
    request: Request,
    db: Annotated[Session, Depends(get_db)],
) -> CareLog:
    """
    世話記録を登録（認証不要）

    Publicフォームから世話記録を登録します。
    IPアドレス、User-Agent、デバイスタグを自動記録します。

    Args:
        care_log_data: 世話記録データ
        request: HTTPリクエスト（IPアドレス、User-Agent取得用）
        db: データベースセッション

    Returns:
        CareLogResponse: 登録された世話記録

    Raises:
        HTTPException: 猫が見つからない場合（404）、またはデータベースエラー（500）

    Example:
        POST /api/v1/public/care-logs
        Body: {
            "animal_id": 123,
            "recorder_id": 1,
            "time_slot": "朝",
            "appetite": 5,
            "energy": 5,
            "urination": true,
            "cleaning": true,
            "memo": "元気です"
        }
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == care_log_data.animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {care_log_data.animal_id} が見つかりません",
        )

    # IPアドレスとUser-Agentを取得して設定
    care_log_data.ip_address = request.client.host if request.client else None
    care_log_data.user_agent = request.headers.get("user-agent")

    # 世話記録を作成
    care_log = care_log_service.create_care_log(
        db=db,
        care_log_data=care_log_data,
    )

    return care_log


@router.get("/care-logs/latest/{animal_id}")
def get_latest_care_log(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> CareLogResponse | None:
    """
    最新の世話記録を取得（認証不要）

    前回入力値コピー機能で使用します。
    指定された猫の最新の世話記録を返します。

    Args:
        animal_id: 猫のID
        db: データベースセッション

    Returns:
        CareLogResponse | None: 最新の世話記録（存在しない場合はNone）

    Example:
        GET /api/v1/public/care-logs/latest/123
        Response: {
            "id": 456,
            "animal_id": 123,
            "time_slot": "朝",
            "appetite": 5,
            ...
        }
    """
    latest_log = care_log_service.get_latest_care_log(db=db, animal_id=animal_id)

    if not latest_log:
        return None

    return CareLogResponse.model_validate(latest_log)


@router.get("/care-logs/animal/{animal_id}", response_model=AnimalCareLogListResponse)
def get_animal_care_logs(
    animal_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> AnimalCareLogListResponse:
    """
    個別猫の記録一覧を取得（認証不要）

    指定された猫の直近7日間の世話記録一覧と、当日の記録状況を返します。
    ボランティアが記録状況を確認するために使用します。

    Args:
        animal_id: 猫のID
        db: データベースセッション

    Returns:
        AnimalCareLogListResponse: 猫の記録一覧と当日の記録状況

    Raises:
        HTTPException: 猫が見つからない場合（404）

    Example:
        GET /api/v1/public/care-logs/animal/123
        Response: {
            "animal_id": 123,
            "animal_name": "たま",
            "animal_photo": "tama.jpg",
            "today_status": {
                "morning": true,
                "noon": false,
                "evening": true
            },
            "recent_logs": [
                {
                    "id": 1,
                    "log_date": "2025-11-15",
                    "time_slot": "morning",
                    "recorder_name": "田中太郎",
                    "has_record": true
                },
                ...
            ]
        }
    """
    from datetime import date, timedelta

    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    # 直近7日間の記録を取得
    today = date.today()
    seven_days_ago = today - timedelta(days=7)

    recent_logs = (
        db.query(CareLog)
        .filter(
            CareLog.animal_id == animal_id,
            CareLog.log_date >= seven_days_ago,
            CareLog.log_date <= today,
        )
        .order_by(CareLog.log_date.desc(), CareLog.time_slot.desc())
        .all()
    )

    # 当日の記録状況を集計
    today_logs = [log for log in recent_logs if log.log_date == today]
    today_status = {
        "morning": any(log.time_slot == "morning" for log in today_logs),
        "noon": any(log.time_slot == "noon" for log in today_logs),
        "evening": any(log.time_slot == "evening" for log in today_logs),
    }

    # レスポンスを構築
    return AnimalCareLogListResponse(
        animal_id=animal.id,
        animal_name=animal.name or "名前なし",
        animal_photo=animal.photo,
        today_status=today_status,
        recent_logs=[CareLogSummary.model_validate(log) for log in recent_logs],
    )


@router.get("/care-logs/animal/{animal_id}/{log_id}", response_model=CareLogResponse)
def get_care_log_detail(
    animal_id: int,
    log_id: int,
    db: Annotated[Session, Depends(get_db)],
) -> CareLogResponse:
    """
    特定の世話記録の詳細を取得（認証不要）

    指定された猫の特定の世話記録の詳細情報を返します。
    記録一覧から詳細を確認するために使用します。

    Args:
        animal_id: 猫のID
        log_id: 世話記録のID
        db: データベースセッション

    Returns:
        CareLogResponse: 世話記録の詳細

    Raises:
        HTTPException: 猫または記録が見つからない場合（404）

    Example:
        GET /api/v1/public/care-logs/animal/123/456
        Response: {
            "id": 456,
            "animal_id": 123,
            "recorder_name": "田中太郎",
            "log_date": "2025-11-15",
            "time_slot": "morning",
            "appetite": 5,
            "energy": 5,
            "urination": true,
            "cleaning": true,
            "memo": "元気です",
            ...
        }
    """
    # 猫の存在確認
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"猫ID {animal_id} が見つかりません",
        )

    # 記録の取得
    care_log = (
        db.query(CareLog)
        .filter(CareLog.id == log_id, CareLog.animal_id == animal_id)
        .first()
    )

    if not care_log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"記録ID {log_id} が見つかりません",
        )

    return CareLogResponse.model_validate(care_log)


@router.get("/care-logs/status/today", response_model=AllAnimalsStatusResponse)
def get_all_animals_status_today(
    db: Annotated[Session, Depends(get_db)],
) -> AllAnimalsStatusResponse:
    """
    全猫の当日記録状況一覧を取得（認証不要）

    全猫の当日の朝・昼・夕の記録状況を返します。
    ボランティアが記録漏れを確認するために使用します。

    Args:
        db: データベースセッション

    Returns:
        AllAnimalsStatusResponse: 全猫の当日記録状況

    Example:
        GET /api/v1/public/care-logs/status/today
        Response: {
            "target_date": "2025-11-15",
            "animals": [
                {
                    "animal_id": 123,
                    "animal_name": "たま",
                    "animal_photo": "tama.jpg",
                    "morning_recorded": true,
                    "noon_recorded": false,
                    "evening_recorded": true
                },
                ...
            ]
        }
    """
    from datetime import date

    today = date.today()

    # 保護中・治療中・譲渡可能な猫のみを取得
    animals = (
        db.query(Animal)
        .filter(
            Animal.status.in_(
                [
                    AnimalStatus.QUARANTINE.value,
                    AnimalStatus.IN_CARE.value,
                    AnimalStatus.TRIAL.value,
                ]
            )
        )
        .order_by(Animal.name)
        .all()
    )

    # 当日の全記録を取得
    today_logs = db.query(CareLog).filter(CareLog.log_date == today).all()

    # 猫ごとの記録状況を集計
    animal_statuses: list[AnimalStatusSummary] = []
    for animal in animals:
        animal_logs = [log for log in today_logs if log.animal_id == animal.id]

        animal_statuses.append(
            AnimalStatusSummary(
                animal_id=animal.id,
                animal_name=animal.name or "名前なし",
                animal_photo=animal.photo,
                morning_recorded=any(log.time_slot == "morning" for log in animal_logs),
                noon_recorded=any(log.time_slot == "noon" for log in animal_logs),
                evening_recorded=any(log.time_slot == "evening" for log in animal_logs),
            )
        )

    return AllAnimalsStatusResponse(
        target_date=today,
        animals=animal_statuses,
    )
