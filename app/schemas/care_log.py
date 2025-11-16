"""
世話記録（CareLog）関連のPydanticスキーマ

世話記録のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator


class CareLogBase(BaseModel):
    """世話記録の基本情報スキーマ"""

    animal_id: int = Field(..., description="猫ID")
    recorder_name: str = Field(..., max_length=100, description="記録者名")
    log_date: date_type = Field(..., description="記録日（年月日）")
    time_slot: str = Field(..., description="時点（morning/noon/evening）")
    appetite: int = Field(3, ge=1, le=5, description="食欲（1〜5段階、5が最良）")
    energy: int = Field(3, ge=1, le=5, description="元気（1〜5段階、5が最良）")
    urination: bool = Field(False, description="排尿有無")
    cleaning: bool = Field(False, description="清掃済み")
    memo: str | None = Field(None, description="メモ")
    from_paper: bool = Field(False, description="紙記録からの転記フラグ")

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot(cls, v: str) -> str:
        """時点の検証"""
        allowed = ["morning", "noon", "evening"]
        if v not in allowed:
            raise ValueError(
                f"時点は {', '.join(allowed)} のいずれかである必要があります"
            )
        return v


class CareLogCreate(CareLogBase):
    """世話記録登録リクエストスキーマ"""

    recorder_id: int | None = Field(
        None, description="記録者ID（ボランティアテーブル）"
    )
    ip_address: str | None = Field(None, max_length=45, description="IPアドレス")
    user_agent: str | None = Field(
        None, max_length=255, description="ユーザーエージェント"
    )
    device_tag: str | None = Field(None, max_length=100, description="デバイスタグ")


class CareLogUpdate(BaseModel):
    """世話記録更新リクエストスキーマ（全フィールド任意）"""

    recorder_name: str | None = Field(None, max_length=100)
    log_date: date_type | None = None
    time_slot: str | None = None
    appetite: int | None = Field(None, ge=1, le=5)
    energy: int | None = Field(None, ge=1, le=5)
    urination: bool | None = None
    cleaning: bool | None = None
    memo: str | None = None
    from_paper: bool | None = None

    @field_validator("time_slot")
    @classmethod
    def validate_time_slot(cls, v: str | None) -> str | None:
        """時点の検証"""
        if v is not None:
            allowed = ["morning", "noon", "evening"]
            if v not in allowed:
                raise ValueError(
                    f"時点は {', '.join(allowed)} のいずれかである必要があります"
                )
        return v


class CareLogResponse(CareLogBase):
    """世話記録レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    recorder_id: int | None
    animal_name: str | None = Field(None, description="猫の名前")
    ip_address: str | None
    user_agent: str | None
    device_tag: str | None
    created_at: datetime
    last_updated_at: datetime
    last_updated_by: int | None


class CareLogListResponse(BaseModel):
    """世話記録一覧レスポンススキーマ"""

    items: list[CareLogResponse]
    total: int
    page: int
    page_size: int
    total_pages: int


class CareLogSummary(BaseModel):
    """世話記録サマリースキーマ（一覧表示用）"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    log_date: date_type
    time_slot: str
    recorder_name: str
    has_record: bool = Field(True, description="記録済みフラグ（常にTrue）")


class AnimalCareLogListResponse(BaseModel):
    """個別猫の記録一覧レスポンススキーマ"""

    animal_id: int
    animal_name: str
    animal_photo: str | None
    today_status: dict[str, bool] = Field(
        ..., description="当日の記録状況（morning/noon/evening: True/False）"
    )
    recent_logs: list[CareLogSummary] = Field(..., description="直近7日間の記録一覧")


class AnimalStatusSummary(BaseModel):
    """猫の記録状況サマリースキーマ"""

    animal_id: int
    animal_name: str
    animal_photo: str | None
    morning_recorded: bool = Field(..., description="朝の記録済みフラグ")
    noon_recorded: bool = Field(..., description="昼の記録済みフラグ")
    evening_recorded: bool = Field(..., description="夕の記録済みフラグ")


class AllAnimalsStatusResponse(BaseModel):
    """全猫の記録状況一覧レスポンススキーマ"""

    target_date: date_type = Field(..., description="対象日（当日）")
    animals: list[AnimalStatusSummary] = Field(..., description="全猫の記録状況")


class TimeSlotRecord(BaseModel):
    """時点ごとの記録情報"""

    exists: bool = Field(..., description="記録の有無")
    log_id: int | None = Field(None, description="記録ID（記録がある場合）")
    appetite: int | None = Field(None, ge=1, le=5, description="食欲")
    energy: int | None = Field(None, ge=1, le=5, description="元気")
    urination: bool | None = Field(None, description="排尿有無")
    cleaning: bool | None = Field(None, description="清掃済み")


class DailyViewRecord(BaseModel):
    """日次ビューの1レコード"""

    date: date_type = Field(..., description="日付")
    animal_id: int = Field(..., description="猫ID")
    animal_name: str = Field(..., description="猫の名前")
    morning: TimeSlotRecord = Field(..., description="朝の記録")
    noon: TimeSlotRecord = Field(..., description="昼の記録")
    evening: TimeSlotRecord = Field(..., description="夕の記録")


class DailyViewResponse(BaseModel):
    """日次ビュー一覧レスポンススキーマ"""

    items: list[DailyViewRecord] = Field(..., description="日次ビューレコードのリスト")
    total: int = Field(..., description="総レコード数")
    page: int = Field(..., description="現在のページ番号")
    page_size: int = Field(..., description="ページサイズ")
    total_pages: int = Field(..., description="総ページ数")
