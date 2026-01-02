"""
Public Pages API

認証不要のHTMLページを提供するエンドポイント。
QRコードからアクセスされる世話記録入力フォームなど。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import get_settings

router = APIRouter(prefix="/public", tags=["public-pages"])

# テンプレートディレクトリを設定
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# 設定を取得
settings = get_settings()


@router.get("/", response_class=HTMLResponse)
def landing_page(request: Request):  # type: ignore[no-untyped-def]
    """
    公開ランディングページを表示

    ハッカソン訪問者向けのプロジェクト紹介ページ。
    認証不要で、プロジェクトの概要、機能、デモを紹介。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: ランディングページのHTML

    Example:
        GET /public/
    """
    # 環境変数から設定を読み込み
    github_url = settings.github_repo_url
    demo_video_url = f"https://www.youtube.com/embed/{settings.demo_video_id}"

    return templates.TemplateResponse(
        "public/landing.html",
        {
            "request": request,
            "settings": settings,
            "github_url": github_url,
            "demo_video_url": demo_video_url,
        },
    )


@router.get("/care", response_class=HTMLResponse)
def care_form_page(request: Request, animal_id: int):  # type: ignore[no-untyped-def]
    """
    世話記録入力フォームページを表示

    QRコードからアクセスされる認証不要の記録入力フォーム。
    猫の情報を表示し、世話記録を入力できる。

    Args:
        request: FastAPIリクエストオブジェクト
        animal_id: 猫のID（クエリパラメータ）

    Returns:
        HTMLResponse: 世話記録入力フォームのHTML

    Example:
        GET /public/care?animal_id=1
    """
    return templates.TemplateResponse(
        "public/care_form.html",
        {"request": request, "animal_id": animal_id, "settings": settings},
    )


@router.get("/care-logs", response_class=HTMLResponse)
def care_log_list_page(request: Request, animal_id: int):  # type: ignore[no-untyped-def]
    """
    個別猫の記録一覧ページを表示

    指定された猫の直近7日間の世話記録一覧と、当日の記録状況を表示します。
    ボランティアが記録状況を確認するために使用します。

    Args:
        request: FastAPIリクエストオブジェクト
        animal_id: 猫のID（クエリパラメータ）

    Returns:
        HTMLResponse: 記録一覧ページのHTML

    Example:
        GET /public/care-logs?animal_id=1
    """
    return templates.TemplateResponse(
        "public/care_log_list.html",
        {"request": request, "animal_id": animal_id, "settings": settings},
    )


@router.get("/animals/status", response_class=HTMLResponse)
def all_animals_status_page(request: Request):  # type: ignore[no-untyped-def]
    """
    全猫の記録状況一覧ページを表示

    全猫の当日の朝・昼・夕の記録状況を一覧表示します。
    ボランティアが記録漏れを確認するために使用します。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 全猫記録状況一覧ページのHTML

    Example:
        GET /public/animals/status
    """
    return templates.TemplateResponse(
        "public/all_animals_status.html", {"request": request, "settings": settings}
    )
