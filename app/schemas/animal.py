"""
猫（Animal）関連のPydanticスキーマ

猫の個体情報のリクエスト・レスポンススキーマを定義します。
"""

from __future__ import annotations

from datetime import date as date_type
from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, field_validator

from app.utils.enums import AnimalStatus, LocationType


class AnimalBase(BaseModel):
    """猫の基本情報スキーマ"""

    name: str | None = Field(None, max_length=100, description="猫の名前")
    photo: str | None = Field(
        None, max_length=255, description="プロフィール画像のファイルパス（任意）"
    )
    microchip_number: str | None = Field(
        None,
        max_length=20,
        description="マイクロチップ番号（15桁の半角数字、または10桁の英数字）",
    )
    pattern: str = Field(
        ..., max_length=100, description="柄・色（例: キジトラ、三毛、黒猫）"
    )
    tail_length: str = Field(
        ..., max_length=50, description="尻尾の長さ（例: 長い、短い、なし）"
    )
    collar: str | None = Field(None, max_length=100, description="首輪の有無と色")
    age_months: int | None = Field(None, ge=0, description="月齢（null=不明）")
    age_is_estimated: bool = Field(
        False, description="推定月齢フラグ（月齢がnullの場合は年齢不明扱い）"
    )
    gender: str = Field(..., max_length=10, description="性別（male/female/unknown）")
    ear_cut: bool = Field(False, description="耳カットの有無（TNR済みの印）")
    features: str | None = Field(None, description="外傷・特徴・性格（自由記述）")
    rescue_source: str | None = Field(None, max_length=200, description="レスキュー元")
    breed: str | None = Field(None, max_length=100, description="品種")
    status: str = Field(
        "QUARANTINE",
        description="ステータス（QUARANTINE, IN_CARE, TRIAL, ADOPTED, DECEASED）",
    )
    location_type: str = Field(
        "FACILITY",
        description="ロケーションタイプ（FACILITY, FOSTER_HOME, ADOPTER_HOME）",
    )
    current_location_note: str | None = Field(
        None,
        description="所在地詳細（「◯◯さん宅」「カフェ2F」「隔離室A」など）",
    )
    protected_at: date_type = Field(
        default_factory=date_type.today, description="保護日"
    )

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: str) -> str:
        """ステータスの検証"""
        if v not in {s.value for s in AnimalStatus}:
            allowed = [s.value for s in AnimalStatus]
            raise ValueError(
                f"ステータスは {', '.join(allowed)} のいずれかである必要があります"
            )
        return v

    @field_validator("location_type", mode="before")
    @classmethod
    def validate_location_type(cls, v: str) -> str:
        """ロケーションタイプの検証"""
        if v not in {lt.value for lt in LocationType}:
            allowed = [lt.value for lt in LocationType]
            raise ValueError(
                f"ロケーションタイプは {', '.join(allowed)} のいずれかである必要があります"
            )
        return v

    @field_validator("microchip_number", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        """空文字列をNoneに変換"""
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("microchip_number")
    @classmethod
    def validate_microchip_number(cls, v: str | None) -> str | None:
        """マイクロチップ番号の検証"""
        if v is None:
            return None

        # 空白を除去
        v = v.strip()

        # 15桁の半角数字チェック（ISO 11784/11785準拠）
        if len(v) == 15 and v.isdigit():
            return v

        # 10桁の英数字チェック（旧規格対応）
        if len(v) == 10 and v.isalnum():
            return v

        raise ValueError(
            "マイクロチップ番号は15桁の半角数字、または10桁の英数字である必要があります"
        )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str) -> str:
        """性別の検証"""
        allowed = ["male", "female", "unknown"]
        if v not in allowed:
            raise ValueError(
                f"性別は {', '.join(allowed)} のいずれかである必要があります"
            )
        return v


class AnimalCreate(AnimalBase):
    """猫登録リクエストスキーマ"""

    pass


class AnimalUpdate(BaseModel):
    """猫更新リクエストスキーマ（全フィールド任意）"""

    name: str | None = Field(None, max_length=100)
    photo: str | None = Field(None, max_length=255)
    microchip_number: str | None = Field(None, max_length=20)
    pattern: str | None = Field(None, max_length=100)
    tail_length: str | None = Field(None, max_length=50)
    collar: str | None = Field(None, max_length=100)
    age_months: int | None = Field(None, ge=0)
    age_is_estimated: bool | None = Field(
        None, description="推定月齢フラグ（月齢がnullの場合は年齢不明扱い）"
    )
    gender: str | None = Field(None, max_length=10)
    ear_cut: bool | None = None
    features: str | None = None
    rescue_source: str | None = Field(None, max_length=200)
    breed: str | None = Field(None, max_length=100)
    status: str | None = Field(None, description="ステータス")
    location_type: str | None = Field(None, description="ロケーションタイプ")
    current_location_note: str | None = Field(None, description="所在地詳細")
    protected_at: date_type | None = None
    confirm: bool = Field(
        False,
        description="終端ステータスからの復帰確認フラグ（409 → confirm=true で再送）",
    )
    reason: str | None = Field(
        None, max_length=500, description="ステータス変更理由（任意）"
    )

    @field_validator("status", mode="before")
    @classmethod
    def validate_status(cls, v: str | None) -> str | None:
        """ステータスの検証"""
        if v is None:
            return None
        if v not in {s.value for s in AnimalStatus}:
            allowed = [s.value for s in AnimalStatus]
            raise ValueError(
                f"ステータスは {', '.join(allowed)} のいずれかである必要があります"
            )
        return v

    @field_validator("location_type", mode="before")
    @classmethod
    def validate_location_type(cls, v: str | None) -> str | None:
        """ロケーションタイプの検証"""
        if v is None:
            return None
        if v not in {lt.value for lt in LocationType}:
            allowed = [lt.value for lt in LocationType]
            raise ValueError(
                f"ロケーションタイプは {', '.join(allowed)} のいずれかである必要があります"
            )
        return v

    @field_validator("microchip_number", mode="before")
    @classmethod
    def empty_string_to_none(cls, v: str | None) -> str | None:
        """空文字列をNoneに変換"""
        if v == "" or (isinstance(v, str) and v.strip() == ""):
            return None
        return v

    @field_validator("microchip_number")
    @classmethod
    def validate_microchip_number(cls, v: str | None) -> str | None:
        """マイクロチップ番号の検証"""
        if v is None:
            return None

        v = v.strip()

        if len(v) == 15 and v.isdigit():
            return v

        if len(v) == 10 and v.isalnum():
            return v

        raise ValueError(
            "マイクロチップ番号は15桁の半角数字、または10桁の英数字である必要があります"
        )

    @field_validator("gender")
    @classmethod
    def validate_gender(cls, v: str | None) -> str | None:
        """性別の検証"""
        if v is not None:
            allowed = ["male", "female", "unknown"]
            if v not in allowed:
                raise ValueError(
                    f"性別は {', '.join(allowed)} のいずれかである必要があります"
                )
        return v


class AnimalResponse(AnimalBase):
    """猫レスポンススキーマ"""

    model_config = ConfigDict(from_attributes=True)

    id: int
    created_at: datetime
    updated_at: datetime


class AnimalListResponse(BaseModel):
    """猫一覧レスポンススキーマ"""

    items: list[AnimalResponse]
    total: int
    page: int
    page_size: int
    total_pages: int
