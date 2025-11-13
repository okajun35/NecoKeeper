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

router = APIRouter(prefix="/public", tags=["public-pages"])

# テンプレートディレクトリを設定
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/care-form", response_class=HTMLResponse)
async def care_form_page(request: Request, animal_id: int):  # type: ignore[no-untyped-def]
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
        GET /public/care-form?animal_id=1
    """
    return templates.TemplateResponse(
        "public/care_form.html", {"request": request, "animal_id": animal_id}
    )
