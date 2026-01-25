"""
メタエンドポイント: ステータス・ロケーション定義配布

Accept-Language ヘッダに応じた多言語対応。
"""

from __future__ import annotations

from typing import Annotated

from fastapi import APIRouter, Header
from pydantic import BaseModel

from app.utils.enums import AnimalStatus, LocationType

router = APIRouter(prefix="/api/v1/meta", tags=["meta"])


class StatusMetaItem(BaseModel):
    """ステータスメタ情報"""

    code: str
    label: str
    is_terminal: bool


class LocationTypeMetaItem(BaseModel):
    """ロケーションタイプメタ情報"""

    code: str
    label: str


@router.get("/statuses", response_model=list[StatusMetaItem])
def get_statuses(
    accept_language: Annotated[str | None, Header()] = None,
) -> list[StatusMetaItem]:
    """
    ステータス定義を取得

    Accept-Language ヘッダに応じて表示言語を切り替え。
    - ja: 日本語
    - en: 英語
    - デフォルト: 日本語

    Returns:
        list[StatusMetaItem]: ステータス定義リスト
    """
    # Accept-Language パース（簡易版）
    is_en = accept_language and accept_language.startswith("en")

    statuses = []
    for status in AnimalStatus:
        statuses.append(
            StatusMetaItem(
                code=status.value,
                label=status.display_name_en() if is_en else status.display_name_ja(),
                is_terminal=status.is_terminal(),
            )
        )
    return statuses


@router.get("/location-types", response_model=list[LocationTypeMetaItem])
def get_location_types(
    accept_language: Annotated[str | None, Header()] = None,
) -> list[LocationTypeMetaItem]:
    """
    ロケーション定義を取得

    Accept-Language ヘッダに応じて表示言語を切り替え。

    Returns:
        list[LocationTypeMetaItem]: ロケーション定義リスト
    """
    # Accept-Language パース（簡易版）
    is_en = accept_language and accept_language.startswith("en")

    locations = []
    for loc_type in LocationType:
        locations.append(
            LocationTypeMetaItem(
                code=loc_type.value,
                label=loc_type.display_name_en()
                if is_en
                else loc_type.display_name_ja(),
            )
        )
    return locations
