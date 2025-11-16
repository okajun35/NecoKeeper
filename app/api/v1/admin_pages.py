"""
Admin Pages API

管理画面のHTMLページを提供するエンドポイント。
認証が必要な管理画面。
"""

from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/admin", tags=["admin-pages"])

# テンプレートディレクトリを設定
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):  # type: ignore[no-untyped-def]
    """
    ログインページを表示

    管理画面へのログインフォームを表示。
    JWT認証を使用してアクセストークンを取得。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: ログインページのHTML

    Example:
        GET /admin/login
    """
    return templates.TemplateResponse("admin/login.html", {"request": request})


@router.get("", response_class=HTMLResponse)
async def dashboard_page(request: Request):  # type: ignore[no-untyped-def]
    """
    ダッシュボードページを表示

    管理画面のトップページ。
    統計情報、最近の活動、記録が必要な猫などを表示。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: ダッシュボードページのHTML

    Example:
        GET /admin
    """
    return templates.TemplateResponse("admin/dashboard.html", {"request": request})


@router.get("/animals", response_class=HTMLResponse)
async def animals_list_page(request: Request):  # type: ignore[no-untyped-def]
    """
    猫一覧ページを表示

    保護猫の一覧を表示。
    検索、フィルター、ページネーション機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 猫一覧ページのHTML

    Example:
        GET /admin/animals
    """
    return templates.TemplateResponse("admin/animals/list.html", {"request": request})


@router.get("/animals/new", response_class=HTMLResponse)
async def animal_new_page(request: Request):  # type: ignore[no-untyped-def]
    """
    猫新規登録ページを表示

    新しい猫を登録するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 猫新規登録ページのHTML

    Example:
        GET /admin/animals/new
    """
    return templates.TemplateResponse("admin/animals/new.html", {"request": request})


@router.get("/animals/{animal_id}", response_class=HTMLResponse)
async def animal_detail_page(request: Request, animal_id: int):  # type: ignore[no-untyped-def]
    """
    猫詳細ページを表示

    指定された猫の詳細情報を表示。
    世話記録、画像ギャラリー、ステータス履歴などを含む。

    Args:
        request: FastAPIリクエストオブジェクト
        animal_id: 猫のID

    Returns:
        HTMLResponse: 猫詳細ページのHTML

    Example:
        GET /admin/animals/123
    """
    from app.database import SessionLocal
    from app.models.animal import Animal

    db = SessionLocal()
    try:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            # 猫が見つからない場合は一覧ページにリダイレクト
            from fastapi.responses import RedirectResponse

            return RedirectResponse(url="/admin/animals", status_code=302)

        return templates.TemplateResponse(
            "admin/animals/detail.html", {"request": request, "animal": animal}
        )
    finally:
        db.close()


@router.get("/animals/{animal_id}/edit", response_class=HTMLResponse)
async def animal_edit_page(request: Request, animal_id: int):  # type: ignore[no-untyped-def]
    """
    猫編集ページを表示

    指定された猫の情報を編集するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト
        animal_id: 猫のID

    Returns:
        HTMLResponse: 猫編集ページのHTML

    Example:
        GET /admin/animals/123/edit
    """
    return templates.TemplateResponse(
        "admin/animals/edit.html", {"request": request, "animal_id": animal_id}
    )


@router.get("/care-logs", response_class=HTMLResponse)
async def care_logs_list_page(request: Request):  # type: ignore[no-untyped-def]
    """
    世話記録一覧ページを表示

    世話記録の一覧を表示。
    フィルター、検索、CSVエクスポート機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 世話記録一覧ページのHTML

    Example:
        GET /admin/care-logs
    """
    return templates.TemplateResponse("admin/care_logs/list.html", {"request": request})


@router.get("/care-logs/{care_log_id}", response_class=HTMLResponse)
async def care_log_detail_page(request: Request, care_log_id: int):  # type: ignore[no-untyped-def]
    """
    世話記録詳細ページを表示

    指定されたIDの世話記録の詳細を表示。

    Args:
        request: FastAPIリクエストオブジェクト
        care_log_id: 世話記録ID

    Returns:
        HTMLResponse: 世話記録詳細ページのHTML

    Example:
        GET /admin/care-logs/1
    """
    return templates.TemplateResponse(
        "admin/care_logs/detail.html",
        {"request": request, "care_log_id": care_log_id},
    )


@router.get("/volunteers", response_class=HTMLResponse)
async def volunteers_list_page(request: Request):  # type: ignore[no-untyped-def]
    """
    ボランティア一覧ページを表示

    ボランティアの一覧を表示。
    活動履歴、記録回数などを含む。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: ボランティア一覧ページのHTML

    Example:
        GET /admin/volunteers
    """
    return templates.TemplateResponse(
        "admin/volunteers/list.html", {"request": request}
    )


@router.get("/medical-records", response_class=HTMLResponse)
async def medical_records_list_page(request: Request):  # type: ignore[no-untyped-def]
    """
    診療記録一覧ページを表示

    診療記録の一覧を表示。
    フィルター、検索機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 診療記録一覧ページのHTML

    Example:
        GET /admin/medical-records
    """
    return templates.TemplateResponse(
        "admin/medical_records/list.html", {"request": request}
    )


@router.get("/medical-records/new", response_class=HTMLResponse)
async def medical_record_new_page(request: Request):  # type: ignore[no-untyped-def]
    """
    診療記録新規登録ページを表示

    新しい診療記録を登録するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 診療記録新規登録ページのHTML

    Example:
        GET /admin/medical-records/new
    """
    return templates.TemplateResponse(
        "admin/medical_records/new.html", {"request": request}
    )


@router.get("/medical-records/{record_id}", response_class=HTMLResponse)
async def medical_record_detail_page(request: Request, record_id: int):  # type: ignore[no-untyped-def]
    """
    診療記録詳細ページを表示

    指定された診療記録の詳細情報を表示。

    Args:
        request: FastAPIリクエストオブジェクト
        record_id: 診療記録のID

    Returns:
        HTMLResponse: 診療記録詳細ページのHTML

    Example:
        GET /admin/medical-records/123
    """
    return templates.TemplateResponse(
        "admin/medical_records/detail.html",
        {"request": request, "record_id": record_id},
    )


@router.get("/medical-actions", response_class=HTMLResponse)
async def medical_actions_list_page(request: Request):  # type: ignore[no-untyped-def]
    """
    診療行為マスター一覧ページを表示

    診療行為（薬剤、ワクチン、検査等）のマスターデータ一覧を表示。
    期間別価格管理、通貨単位設定機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 診療行為マスター一覧ページのHTML

    Example:
        GET /admin/medical-actions
    """
    return templates.TemplateResponse(
        "admin/medical_actions/list.html", {"request": request}
    )


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request):  # type: ignore[no-untyped-def]
    """
    設定ページを表示

    システム設定を管理。
    画像制限、バックアップ設定などを含む。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 設定ページのHTML

    Example:
        GET /admin/settings
    """
    return templates.TemplateResponse("admin/settings/index.html", {"request": request})
