"""
PDF生成サービス

QRカード、紙記録フォーム、診療明細、帳票のPDF生成機能を提供します。

Requirements: Requirement 2.1-2.2, Requirement 2.5-2.8, Requirement 7.2-7.3, Requirement 9
Context7: /websites/doc_courtbouillon_weasyprint_stable
"""

from __future__ import annotations

import base64
from datetime import date
from decimal import Decimal
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from weasyprint import HTML

from app.config import get_settings
from app.models.animal import Animal
from app.services.medical_report_service import get_medical_summary_rows
from app.utils.appetite import appetite_label
from app.utils.i18n import tj
from app.utils.qr_code import generate_animal_qr_code_bytes

settings = get_settings()

# Jinja2環境の設定
template_dir = Path("app/templates/pdf")
jinja_env = Environment(
    loader=FileSystemLoader(str(template_dir)),
    autoescape=select_autoescape(["html", "xml"]),
)


def generate_qr_card_pdf(
    db: Session,
    animal_id: int,
    base_url: str | None = None,
    locale: str = "ja",
) -> bytes:
    """
    QRカードPDFを生成（A6サイズ）

    Args:
        db: データベースセッション
        animal_id: 猫のID
        base_url: ベースURL（省略時は設定から取得）
        locale: ロケール（ja/en）

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 猫が見つからない場合

    Example:
        >>> pdf_bytes = generate_qr_card_pdf(db, 123)
        >>> with open("qr_card.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    # 猫情報を取得
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise ValueError(f"猫ID {animal_id} が見つかりません")

    # ベースURLの設定
    if base_url is None:
        base_url = settings.base_url

    # QRコードを生成
    qr_code_bytes = generate_animal_qr_code_bytes(base_url, animal_id, box_size=8)
    qr_code_base64 = base64.b64encode(qr_code_bytes).decode("utf-8")

    # 写真をbase64エンコード
    photo_base64 = None
    photo_mime_type = "image/jpeg"  # デフォルト
    if animal.photo:
        try:
            # photoパスから実際のファイルパスを構築
            # DBに /media/animals/... と保存されている場合と animals/... の場合の両方に対応
            photo_path_str = animal.photo.lstrip("/")

            # /media/ で始まる場合は、そのまま使用
            if photo_path_str.startswith("media/"):
                photo_path = Path(photo_path_str)
            else:
                # media/ プレフィックスを追加
                photo_path = Path("media") / photo_path_str

            if photo_path.exists():
                photo_bytes = photo_path.read_bytes()
                photo_base64 = base64.b64encode(photo_bytes).decode("utf-8")

                # 拡張子からMIMEタイプを判定
                suffix = photo_path.suffix.lower()
                if suffix == ".png":
                    photo_mime_type = "image/png"
                elif suffix == ".webp":
                    photo_mime_type = "image/webp"
                elif suffix == ".gif":
                    photo_mime_type = "image/gif"
                else:
                    photo_mime_type = "image/jpeg"
        except Exception as e:
            print(f"写真の読み込みに失敗: {e}")

    # テンプレートをレンダリング
    template = jinja_env.get_template("qr_card.html")
    html_content = template.render(
        animal=animal,
        photo_base64=photo_base64,
        photo_mime_type=photo_mime_type,
        qr_code_base64=qr_code_base64,
        font_family=settings.pdf_font_family,
        base_url=base_url,
        kiroween_mode=settings.kiroween_mode,
        locale=locale,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf()

    return pdf_bytes  # type: ignore[no-any-return]


def generate_qr_card_grid_pdf(
    db: Session,
    animal_ids: list[int],
    base_url: str | None = None,
    locale: str = "ja",
) -> bytes:
    """
    面付けQRカードPDFを生成（A4サイズ、2×5枚）

    Args:
        db: データベースセッション
        animal_ids: 猫のIDリスト（最大10個）
        base_url: ベースURL（省略時は設定から取得）
        locale: ロケール（ja/en）

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 猫が見つからない場合、またはIDが10個を超える場合

    Example:
        >>> pdf_bytes = generate_qr_card_grid_pdf(db, [1, 2, 3, 4, 5])
        >>> with open("qr_card_grid.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    # ベースURLの設定
    if base_url is None:
        base_url = settings.base_url

    # 枚数チェック
    if len(animal_ids) > 10:
        raise ValueError("一度に生成できるQRカードは最大10枚です")

    # 猫情報とQRコードを取得
    animals_with_qr: list[dict[str, Animal | str]] = []
    for animal_id in animal_ids:
        animal = db.query(Animal).filter(Animal.id == animal_id).first()
        if not animal:
            raise ValueError(f"猫ID {animal_id} が見つかりません")

        qr_code_bytes = generate_animal_qr_code_bytes(base_url, animal_id, box_size=8)
        qr_code_base64 = base64.b64encode(qr_code_bytes).decode("utf-8")

        animals_with_qr.append(
            {
                "animal": animal,
                "qr_code_base64": qr_code_base64,
            }
        )

    # テンプレートをレンダリング
    template = jinja_env.get_template("qr_card_grid.html")
    html_content = template.render(
        animals_with_qr=animals_with_qr,
        base_url=base_url,
        font_family=settings.pdf_font_family,
        kiroween_mode=settings.kiroween_mode,
        locale=locale,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf()

    return pdf_bytes  # type: ignore[no-any-return]


def generate_paper_form_pdf(
    db: Session,
    animal_id: int,
    year: int,
    month: int,
) -> bytes:
    """
    紙記録フォームPDFを生成（A4サイズ、1ヶ月分）

    Args:
        db: データベースセッション
        animal_id: 猫のID
        year: 年
        month: 月

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 猫が見つからない場合

    Example:
        >>> pdf_bytes = generate_paper_form_pdf(db, 123, 2024, 11)
        >>> with open("paper_form.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    # 猫情報を取得
    animal = db.query(Animal).filter(Animal.id == animal_id).first()
    if not animal:
        raise ValueError(f"猫ID {animal_id} が見つかりません")

    # 月の日数を計算
    import calendar

    _, days_in_month = calendar.monthrange(year, month)

    # 日付リストを生成
    dates: list[date] = []
    for day in range(1, days_in_month + 1):
        dates.append(date(year, month, day))

    # テンプレートをレンダリング
    template = jinja_env.get_template("paper_form.html")
    html_content = template.render(
        animal=animal,
        year=year,
        font_family=settings.pdf_font_family,
        month=month,
        dates=dates,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf()

    return pdf_bytes  # type: ignore[no-any-return]


def generate_medical_detail_pdf(
    db: Session,
    medical_record_id: int,
) -> bytes:
    """
    診療明細PDFを生成（A4縦サイズ）

    Args:
        db: データベースセッション
        medical_record_id: 診療記録ID

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 診療記録が見つからない場合
        NotImplementedError: 診療記録機能が未実装の場合

    Example:
        >>> pdf_bytes = generate_medical_detail_pdf(db, 456)
        >>> with open("medical_detail.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    # TODO: Phase 5で診療記録機能を実装後に実装
    raise NotImplementedError("診療記録機能は未実装です")


def generate_report_pdf(
    db: Session,
    report_type: str,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
    locale: str = "ja",
) -> bytes:
    """
    帳票PDFを生成（日報・週報・月次集計・個別帳票）

    Args:
        db: データベースセッション
        report_type: 帳票種別（daily/weekly/monthly/individual）
        start_date: 開始日
        end_date: 終了日
        animal_id: 猫のID（個別帳票の場合のみ必須）

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 不正な帳票種別の場合、または個別帳票で猫IDが未指定の場合

    Example:
        >>> from datetime import date
        >>> pdf_bytes = generate_report_pdf(
        ...     db, "daily", date(2024, 11, 1), date(2024, 11, 30)
        ... )
        >>> with open("report.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    from datetime import datetime

    from app.models.care_log import CareLog

    # 帳票種別のバリデーション
    valid_types = ["daily", "weekly", "monthly", "individual", "medical_summary"]
    if report_type not in valid_types:
        raise ValueError(
            f"不正な帳票種別です: {report_type}。有効な値: {', '.join(valid_types)}"
        )

    # 個別帳票の場合は猫IDが必須
    if report_type == "individual" and not animal_id:
        raise ValueError("個別帳票の生成には猫IDが必要です")

    if report_type == "medical_summary":
        return generate_medical_summary_report_pdf(
            db=db,
            start_date=start_date,
            end_date=end_date,
            animal_id=animal_id,
            locale=locale,
        )

    # 世話記録を取得（実際の記録日でフィルタリング）
    query = db.query(CareLog).filter(
        CareLog.log_date >= start_date,
        CareLog.log_date <= end_date,
    )

    # 個別帳票の場合は猫でフィルター
    if animal_id:
        query = query.filter(CareLog.animal_id == animal_id)

    records = query.order_by(CareLog.log_date.desc(), CareLog.created_at.desc()).all()

    # 統計情報を計算
    total_records = len(records)
    total_animals = len({record.animal_id for record in records})
    total_recorders = len(
        {record.recorder_name for record in records if record.recorder_name}
    )

    # レコードに表示用データを追加
    for record in records:
        record.time_slot_display = tj(  # type: ignore[attr-defined]
            f"time_slots.{record.time_slot}", locale=locale
        )
        record.appetite_label = appetite_label(  # type: ignore[attr-defined]
            record.appetite, locale=locale
        )
        # 猫名を取得
        if record.animal:
            record.animal_name = record.animal.name or tj(  # type: ignore[attr-defined]
                "animal.no_name", locale=locale, id=record.animal_id
            )
        else:
            record.animal_name = tj(  # type: ignore[attr-defined]
                "animal.no_name", locale=locale, id=record.animal_id
            )

    # テンプレートをレンダリング
    template = jinja_env.get_template("report_daily.html")

    title = tj(f"report_titles.{report_type}", locale=locale)
    report_kind = tj("report_kinds.care_logs", locale=locale)
    section_title_by_type = {
        "daily": tj("sections.daily_records_list", locale=locale),
        "weekly": tj("sections.weekly_records_list", locale=locale),
        "monthly": tj("sections.monthly_records_list", locale=locale),
        "individual": tj("sections.individual_records_list", locale=locale),
    }
    section_title = section_title_by_type.get(
        report_type, tj("sections.records_list", locale=locale)
    )

    # 日付フォーマット（多言語化）
    date_fmt = tj("date_format.date_full", locale=locale)
    datetime_fmt = tj("date_format.datetime_full", locale=locale)

    html_content = template.render(
        report_type=report_type,
        title=title,
        report_kind=report_kind,
        section_title=section_title,
        start_date=start_date.strftime(date_fmt),
        font_family=settings.pdf_font_family,
        end_date=end_date.strftime(date_fmt),
        generated_at=datetime.now().strftime(datetime_fmt),
        total_records=total_records,
        total_animals=total_animals,
        total_recorders=total_recorders,
        records=records,
        locale=locale,
        t=tj,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf()

    return pdf_bytes  # type: ignore[no-any-return]


def generate_medical_summary_report_pdf(
    db: Session,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
    locale: str = "ja",
) -> bytes:
    from datetime import datetime

    rows, totals = get_medical_summary_rows(
        db=db, start_date=start_date, end_date=end_date, animal_id=animal_id
    )

    # 日付フォーマット（多言語化）
    date_fmt = tj("date_format.date_full", locale=locale)
    datetime_fmt = tj("date_format.datetime_full", locale=locale)

    # totals_by_currency: include profit for template
    totals_by_currency: dict[str, dict[str, str]] = {}
    for currency, amounts in totals.totals_by_currency.items():
        # Defensive: treat missing/None as 0 to avoid runtime + mypy issues
        billing = amounts.get("billing_amount") or Decimal("0")
        cost = amounts.get("cost_amount") or Decimal("0")
        profit = billing - cost
        totals_by_currency[currency] = {
            "billing_amount": str(billing),
            "cost_amount": str(cost),
            "profit_amount": str(profit),
        }

    template = jinja_env.get_template("report_medical_summary.html")
    html_content = template.render(
        title=tj("report_titles.medical_summary", locale=locale),
        start_date=start_date.strftime(date_fmt),
        end_date=end_date.strftime(date_fmt),
        generated_at=datetime.now().strftime(datetime_fmt),
        total_records=totals.total_records,
        total_animals=totals.total_animals,
        totals_by_currency=totals_by_currency,
        rows=[
            {
                "medical_date": r.medical_date.strftime("%Y-%m-%d"),
                "animal_name": r.animal_name,
                "medical_action_name": r.medical_action_name,
                "dosage": r.dosage,
                "dosage_unit": r.dosage_unit,
                "cost_price": str(r.cost_price) if r.cost_price is not None else None,
                "selling_price": str(r.selling_price)
                if r.selling_price is not None
                else None,
                "procedure_fee": str(r.procedure_fee)
                if r.procedure_fee is not None
                else None,
                "billing_amount": str(r.billing_amount)
                if r.billing_amount is not None
                else None,
                "currency": r.currency,
            }
            for r in rows
        ],
        font_family=settings.pdf_font_family,
        locale=locale,
        t=tj,
    )

    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf()
    return pdf_bytes  # type: ignore[no-any-return]
