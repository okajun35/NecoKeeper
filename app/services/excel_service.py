"""
Excel出力サービス

世話記録、診療記録などのExcel出力機能を提供します。

Requirements: Requirement 7.5, Requirement 9.4
Context7: /openpyxl/openpyxl
"""

from __future__ import annotations

from datetime import date
from io import BytesIO

from openpyxl import Workbook  # type: ignore[import-untyped]
from openpyxl.styles import Alignment, Font, PatternFill  # type: ignore[import-untyped]
from openpyxl.utils import get_column_letter  # type: ignore[import-untyped]
from sqlalchemy.orm import Session

from app.models.care_log import CareLog


def generate_care_log_excel(
    db: Session,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
) -> bytes:
    """
    世話記録のExcelファイルを生成

    Args:
        db: データベースセッション
        start_date: 開始日
        end_date: 終了日
        animal_id: 猫のID（指定時は特定の猫のみ）

    Returns:
        bytes: Excel形式のバイト列

    Example:
        >>> from datetime import date
        >>> excel_data = generate_care_log_excel(db, date(2024, 11, 1), date(2024, 11, 30))
        >>> with open("care_logs.xlsx", "wb") as f:
        ...     f.write(excel_data)
    """
    # 世話記録を取得（実際の記録日でフィルタリング）
    query = db.query(CareLog).filter(
        CareLog.log_date >= start_date,
        CareLog.log_date <= end_date,
    )

    # 個別猫の場合はフィルター
    if animal_id:
        query = query.filter(CareLog.animal_id == animal_id)

    records = query.order_by(CareLog.log_date.desc(), CareLog.created_at.desc()).all()

    # 時点の表示名マッピング
    time_slot_map = {
        "morning": "朝",
        "noon": "昼",
        "evening": "夕",
    }

    # Excelワークブックを作成
    wb = Workbook()
    ws = wb.active
    ws.title = "世話記録"

    # ヘッダースタイル
    header_fill = PatternFill(
        start_color="4472C4", end_color="4472C4", fill_type="solid"
    )
    header_font = Font(bold=True, color="FFFFFF")
    header_alignment = Alignment(horizontal="center", vertical="center")

    # ヘッダー行
    headers = [
        "記録日時",
        "記録日",
        "猫ID",
        "猫名",
        "時点",
        "食欲",
        "元気",
        "排尿",
        "清掃",
        "記録者ID",
        "記録者名",
        "メモ",
        "IPアドレス",
        "デバイスタグ",
        "紙記録からの転記",
        "最終更新日時",
        "最終更新者ID",
    ]

    for col_num, header in enumerate(headers, 1):
        cell = ws.cell(row=1, column=col_num)
        cell.value = header
        cell.fill = header_fill
        cell.font = header_font
        cell.alignment = header_alignment

    # データ行
    for row_num, record in enumerate(records, 2):
        # 猫名を取得
        animal_name = ""
        if record.animal:
            animal_name = record.animal.name or f"ID:{record.animal_id}"
        else:
            animal_name = f"ID:{record.animal_id}"

        row_data = [
            record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
            record.log_date.strftime("%Y-%m-%d"),
            record.animal_id,
            animal_name,
            time_slot_map.get(record.time_slot, record.time_slot),
            record.appetite,
            record.energy,
            "○" if record.urination else "×",
            "○" if record.cleaning else "×",
            record.recorder_id or "",
            record.recorder_name,
            record.memo or "",
            record.ip_address or "",
            record.device_tag or "",
            "○" if record.from_paper else "×",
            record.last_updated_at.strftime("%Y-%m-%d %H:%M:%S"),
            record.last_updated_by or "",
        ]

        for col_num, value in enumerate(row_data, 1):
            cell = ws.cell(row=row_num, column=col_num)
            cell.value = value
            # 中央揃え（一部のカラム）
            if col_num in [5, 6, 7, 8, 9, 15]:  # 時点、食欲、元気、排尿、清掃、紙記録
                cell.alignment = Alignment(horizontal="center")

    # 列幅を自動調整
    for col_num in range(1, len(headers) + 1):
        column_letter = get_column_letter(col_num)
        # 最大幅を設定（見やすさのため）
        max_width = 15
        if col_num == 12:  # メモ列
            max_width = 30
        elif col_num in [1, 2, 16]:  # 日時列
            max_width = 20

        ws.column_dimensions[column_letter].width = max_width

    # フリーズペイン（ヘッダー行を固定）
    ws.freeze_panes = "A2"

    # Excelファイルをバイト列として出力
    output = BytesIO()
    wb.save(output)
    output.seek(0)

    return output.getvalue()


def generate_report_excel(
    db: Session,
    report_type: str,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
) -> bytes:
    """
    帳票Excelファイルを生成（日報・週報・月次集計・個別帳票）

    Args:
        db: データベースセッション
        report_type: 帳票種別（daily/weekly/monthly/individual）
        start_date: 開始日
        end_date: 終了日
        animal_id: 猫のID（個別帳票の場合のみ必須）

    Returns:
        bytes: Excel形式のバイト列

    Raises:
        ValueError: 不正な帳票種別の場合、または個別帳票で猫IDが未指定の場合

    Example:
        >>> from datetime import date
        >>> excel_data = generate_report_excel(
        ...     db, "daily", date(2024, 11, 1), date(2024, 11, 30)
        ... )
        >>> with open("report.xlsx", "wb") as f:
        ...     f.write(excel_data)
    """
    # 帳票種別のバリデーション
    valid_types = ["daily", "weekly", "monthly", "individual"]
    if report_type not in valid_types:
        raise ValueError(
            f"不正な帳票種別です: {report_type}。有効な値: {', '.join(valid_types)}"
        )

    # 個別帳票の場合は猫IDが必須
    if report_type == "individual" and not animal_id:
        raise ValueError("個別帳票の生成には猫IDが必要です")

    # 世話記録Excelを生成（全帳票種別で共通）
    return generate_care_log_excel(db, start_date, end_date, animal_id)
