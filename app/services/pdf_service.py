"""
PDF生成サービス

QRカード、紙記録フォーム、診療明細、帳票のPDF生成機能を提供します。

Requirements: Requirement 2.1-2.2, Requirement 2.5-2.8, Requirement 7.2-7.3, Requirement 9
Context7: /websites/doc_courtbouillon_weasyprint_stable
"""

from __future__ import annotations

import base64
from datetime import date, datetime
from io import BytesIO
from pathlib import Path

from jinja2 import Environment, FileSystemLoader, select_autoescape
from sqlalchemy.orm import Session
from weasyprint import HTML

from app.config import get_settings
from app.models.animal import Animal
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
) -> bytes:
    """
    QRカードPDFを生成（A6サイズ）

    Args:
        db: データベースセッション
        animal_id: 猫のID
        base_url: ベースURL（省略時は設定から取得）

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

    # テンプレートをレンダリング
    template = jinja_env.get_template("qr_card.html")
    html_content = template.render(
        animal=animal,
        qr_code_base64=qr_code_base64,
        base_url=base_url,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf(pdf_identifier=False)

    return pdf_bytes


def generate_qr_card_grid_pdf(
    db: Session,
    animal_ids: list[int],
    base_url: str | None = None,
) -> bytes:
    """
    面付けQRカードPDFを生成（A4サイズ、2×5枚）

    Args:
        db: データベースセッション
        animal_ids: 猫のIDリスト（最大10個）
        base_url: ベースURL（省略時は設定から取得）

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
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf(pdf_identifier=False)

    return pdf_bytes


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
        month=month,
        dates=dates,
    )

    # PDFを生成
    html_doc = HTML(string=html_content, base_url=str(template_dir))
    pdf_bytes = html_doc.write_pdf(pdf_identifier=False)

    return pdf_bytes


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
) -> bytes:
    """
    帳票PDFを生成（日報・週報・月次集計）

    Args:
        db: データベースセッション
        report_type: 帳票種別（daily/weekly/monthly）
        start_date: 開始日
        end_date: 終了日

    Returns:
        bytes: 生成されたPDFのバイト列

    Raises:
        ValueError: 不正な帳票種別の場合
        NotImplementedError: 帳票機能が未実装の場合

    Example:
        >>> from datetime import date
        >>> pdf_bytes = generate_report_pdf(db, "daily", date(2024, 11, 1), date(2024, 11, 30))
        >>> with open("report.pdf", "wb") as f:
        ...     f.write(pdf_bytes)
    """
    # TODO: Phase 6で帳票機能を実装後に実装
    raise NotImplementedError("帳票機能は未実装です")
