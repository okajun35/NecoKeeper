"""
Admin Pages API

管理画面のHTMLページを提供するエンドポイント。
認証が必要な管理画面。

Context7参照: /fastapi/fastapi - Security Dependencies
"""

from __future__ import annotations

import logging
from pathlib import Path

from fastapi import APIRouter, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from starlette.responses import Response

from app.auth.dependencies import (
    get_current_user_optional,
)
from app.config import get_settings
from app.database import get_db
from app.models.user import User

router = APIRouter(tags=["admin-pages"])

# テンプレートディレクトリを設定
templates_dir = Path(__file__).parent.parent.parent / "templates"
templates = Jinja2Templates(directory=str(templates_dir))

# 設定を取得
settings = get_settings()
admin_base_path = settings.admin_base_path
admin_login_path = f"{admin_base_path}/login"

# ロガー設定
logger = logging.getLogger(__name__)


@router.get("/login", response_class=HTMLResponse)
def login_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    ログインページを表示

    既にログイン済みの場合はダッシュボードにリダイレクト。

    Context7参照: /fastapi/fastapi - RedirectResponse

    Args:
        request: FastAPIリクエストオブジェクト
        current_user: 現在のユーザー（オプショナル）

    Returns:
        HTMLResponse | RedirectResponse: ログインページまたはリダイレクト

    Example:
        GET /admin/login
    """
    # 既にログイン済みの場合はダッシュボードにリダイレクト
    if current_user:
        return RedirectResponse(url=admin_base_path, status_code=302)

    return templates.TemplateResponse(
        "admin/login.html", {"request": request, "settings": settings}
    )


@router.get("", response_class=HTMLResponse)
def dashboard_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    ダッシュボードページを表示（認証必須）

    管理画面のトップページ。
    統計情報、最近の活動、記録が必要な猫などを表示。

    Context7参照: /fastapi/fastapi - Security Dependencies

    Args:
        request: FastAPIリクエストオブジェクト
        current_user: 認証済みユーザー

    Returns:
        HTMLResponse: ダッシュボードページのHTML

    Example:
        GET /admin
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/animals", response_class=HTMLResponse)
def animals_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    猫一覧ページを表示（認証必須）

    保護猫の一覧を表示。
    検索、フィルター、ページネーション機能付き。

    Args:
        request: FastAPIリクエストオブジェクト
        current_user: 認証済みユーザー

    Returns:
        HTMLResponse: 猫一覧ページのHTML

    Example:
        GET /admin/animals
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/animals/list.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/animals/new", response_class=HTMLResponse)
def animal_new_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    猫新規登録ページを表示（認証必須）

    新しい猫を登録するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト
        current_user: 認証済みユーザー

    Returns:
        HTMLResponse: 猫新規登録ページのHTML

    Example:
        GET /admin/animals/new
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/animals/new.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/animals/{animal_id}", response_class=HTMLResponse)
def animal_detail_page(
    request: Request,
    animal_id: int,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Response:
    """
    猫詳細ページを表示（認証必須）

    指定された猫の詳細情報を表示。
    世話記録、画像ギャラリー、ステータス履歴などを含む。

    Args:
        request: FastAPIリクエストオブジェクト
        animal_id: 猫のID
        current_user: 認証済みユーザー

    Returns:
        HTMLResponse: 猫詳細ページのHTML

    Example:
        GET /admin/animals/123
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    from app.models.animal import Animal
    from app.services import animal_service

    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        # 猫が見つからない場合は一覧ページにリダイレクト
        return RedirectResponse(url=f"{admin_base_path}/animals", status_code=302)

    # 表示用の画像パスを取得
    display_image = animal_service.get_display_image(db, animal_id)

    return templates.TemplateResponse(
        "admin/animals/detail.html",
        {
            "request": request,
            "animal": animal,
            "display_image": display_image,
            "settings": settings,
        },
    )


@router.get("/animals/{animal_id}/edit", response_class=HTMLResponse)
def animal_edit_page(
    request: Request,
    animal_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/animals/edit.html",
        {
            "request": request,
            "animal_id": animal_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/care-logs", response_class=HTMLResponse)
def care_logs_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/care_logs/list.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/care-logs/new", response_class=HTMLResponse)
def care_log_new_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    世話記録新規登録ページを表示

    新しい世話記録を登録するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 世話記録新規登録ページのHTML

    Example:
        GET /admin/care-logs/new
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/care_logs/new.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/care-logs/{care_log_id}", response_class=HTMLResponse)
def care_log_detail_page(
    request: Request,
    care_log_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/care_logs/detail.html",
        {
            "request": request,
            "care_log_id": care_log_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/care-logs/{care_log_id}/edit", response_class=HTMLResponse)
def care_log_edit_page(
    request: Request,
    care_log_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    世話記録編集ページを表示

    指定されたIDの世話記録を編集するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト
        care_log_id: 世話記録ID

    Returns:
        HTMLResponse: 世話記録編集ページのHTML

    Example:
        GET /admin/care-logs/1/edit
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/care_logs/edit.html",
        {
            "request": request,
            "care_log_id": care_log_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/volunteers", response_class=HTMLResponse)
def volunteers_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/volunteers/list.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/volunteers/new", response_class=HTMLResponse)
def volunteer_new_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """ボランティア新規作成ページ"""
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/volunteers/new.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/volunteers/{volunteer_id}/edit", response_class=HTMLResponse)
def volunteer_edit_page(
    request: Request,
    volunteer_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """ボランティア編集ページ"""
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/volunteers/edit.html",
        {
            "request": request,
            "volunteer_id": volunteer_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/volunteers/{volunteer_id}", response_class=HTMLResponse)
def volunteer_detail_page(
    request: Request,
    volunteer_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """ボランティア詳細ページ"""
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/volunteers/detail.html",
        {
            "request": request,
            "volunteer_id": volunteer_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/medical-records", response_class=HTMLResponse)
def medical_records_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/medical_records/list.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/medical-records/new", response_class=HTMLResponse)
def medical_record_new_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/medical_records/new.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/medical-records/{record_id}", response_class=HTMLResponse)
def medical_record_detail_page(
    request: Request,
    record_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/medical_records/detail.html",
        {
            "request": request,
            "record_id": record_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/medical-records/{record_id}/edit", response_class=HTMLResponse)
def medical_record_edit_page(
    request: Request,
    record_id: int,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    診療記録修正ページを表示

    指定された診療記録を修正するフォームを表示。

    Args:
        request: FastAPIリクエストオブジェクト
        record_id: 診療記録のID

    Returns:
        HTMLResponse: 診療記録修正ページのHTML

    Example:
        GET /admin/medical-records/123/edit
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/medical_records/edit.html",
        {
            "request": request,
            "record_id": record_id,
            "user": current_user,
            "settings": settings,
        },
    )


@router.get("/medical-actions", response_class=HTMLResponse)
def medical_actions_list_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/medical_actions/list.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/adoptions/applicants", response_class=HTMLResponse)
def adoptions_applicants_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    里親希望者一覧ページを表示

    里親希望者の一覧を表示。
    登録、編集、検索機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 里親希望者一覧ページのHTML

    Example:
        GET /admin/adoptions/applicants
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/adoptions/applicants.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/adoptions/applicants/new", response_class=HTMLResponse)
def adoptions_applicants_new_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    里親申込フォーム（新規登録）ページを表示

    詳細な申込情報を入力し、申込を登録する。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 里親申込フォームページのHTML

    Example:
        GET /admin/adoptions/applicants/new
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/adoptions/applicant_extended_form.html",
        {
            "request": request,
            "user": current_user,
            "settings": settings,
            "mode": "new",
        },
    )


@router.get(
    "/adoptions/applicants/{applicant_id}/edit",
    response_class=HTMLResponse,
)
def adoptions_applicants_edit_page(
    applicant_id: int,
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
    db: Session = Depends(get_db),
) -> Response:
    """
    里親申込フォーム（編集）ページを表示

    既存の申込情報を編集する。

    Args:
        applicant_id: 申込者ID
        request: FastAPIリクエストオブジェクト
        db: データベースセッション

    Returns:
        HTMLResponse: 里親申込フォームページのHTML

    Example:
        GET /admin/adoptions/applicants/1/edit
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    # 申込者データを取得
    from app.schemas.adoption import ApplicantResponseExtended
    from app.services import adoption_service

    try:
        applicant_model = adoption_service.get_applicant_extended(db, applicant_id)
        # スキーマに変換
        applicant = ApplicantResponseExtended.model_validate(applicant_model)
    except HTTPException as e:
        # 404の場合は一覧ページにリダイレクト
        if e.status_code == 404:
            return RedirectResponse(
                url=f"{admin_base_path}/adoptions/applicants", status_code=302
            )
        # その他のHTTPExceptionは再送出
        raise
    except Exception as e:
        # 予期しないエラーはログに記録して500エラー
        logger.error(
            f"Failed to load applicant {applicant_id} for edit: {e}", exc_info=True
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="申込者データの取得に失敗しました",
        ) from e

    return templates.TemplateResponse(
        "admin/adoptions/applicant_extended_form.html",
        {
            "request": request,
            "user": current_user,
            "settings": settings,
            "mode": "edit",
            "applicant": applicant,
        },
    )


@router.get("/adoptions/records", response_class=HTMLResponse)
def adoptions_records_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    譲渡記録一覧ページを表示

    面談記録と譲渡記録の一覧を表示。
    フィルター、検索機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 譲渡記録一覧ページのHTML

    Example:
        GET /admin/adoptions/records
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/adoptions/records.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/reports", response_class=HTMLResponse)
def reports_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """
    帳票出力ページを表示

    日報、週報、月次集計、個別帳票の生成画面。
    期間指定、形式選択（PDF/CSV/Excel）機能付き。

    Args:
        request: FastAPIリクエストオブジェクト

    Returns:
        HTMLResponse: 帳票出力ページのHTML

    Example:
        GET /admin/reports
    """
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/reports/index.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/reports/care", response_class=HTMLResponse)
def care_reports_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """世話記録帳票ページを表示（認証必須）"""
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/reports/care.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/reports/medical", response_class=HTMLResponse)
def medical_reports_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
    """診療記録帳票ページを表示（認証必須）"""
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/reports/medical.html",
        {"request": request, "user": current_user, "settings": settings},
    )


@router.get("/settings", response_class=HTMLResponse)
def settings_page(
    request: Request,
    current_user: User | None = Depends(get_current_user_optional),
) -> Response:
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
    if not current_user:
        return RedirectResponse(url=admin_login_path, status_code=302)

    return templates.TemplateResponse(
        "admin/settings/index.html",
        {"request": request, "user": current_user, "settings": settings},
    )
