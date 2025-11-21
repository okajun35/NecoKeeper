"""
CSV出力サービス

世話記録、診療記録などのCSV出力機能を提供します。

Requirements: Requirement 8.1, Requirement 9.3, Requirement 25.2-25.3
"""

from __future__ import annotations

import csv
from datetime import date
from io import StringIO

from sqlalchemy.orm import Session

from app.models.care_log import CareLog
from app.utils.i18n import tj


def generate_care_log_csv(
    db: Session,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
    locale: str = "ja",
) -> str:
    """
    世話記録のCSVを生成

    Args:
        db: データベースセッション
        start_date: 開始日
        end_date: 終了日
        animal_id: 猫のID（指定時は特定の猫のみ）

    Returns:
        str: CSV形式の文字列（UTF-8 BOM付き）

    Example:
        >>> from datetime import date
        >>> csv_data = generate_care_log_csv(db, date(2024, 11, 1), date(2024, 11, 30))
        >>> with open("care_logs.csv", "w", encoding="utf-8-sig") as f:
        ...     f.write(csv_data)
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

    # CSVデータを生成
    output = StringIO()
    # UTF-8 BOM を追加（Excelで正しく開くため）
    output.write("\ufeff")

    writer = csv.writer(output)

    # ヘッダー行（多言語化）
    writer.writerow(
        [
            tj("headers.created_at", locale=locale),
            tj("headers.log_date", locale=locale),
            tj("headers.animal_id", locale=locale),
            tj("headers.animal_name", locale=locale),
            tj("headers.time_slot", locale=locale),
            tj("headers.appetite", locale=locale),
            tj("headers.energy", locale=locale),
            tj("headers.urination", locale=locale),
            tj("headers.cleaning", locale=locale),
            tj("headers.recorder_id", locale=locale),
            tj("headers.recorder_name", locale=locale),
            tj("headers.memo", locale=locale),
            tj("headers.ip_address", locale=locale),
            tj("headers.device_tag", locale=locale),
            tj("headers.from_paper", locale=locale),
            tj("headers.last_updated_at", locale=locale),
            tj("headers.last_updated_by", locale=locale),
        ]
    )

    # データ行
    for record in records:
        # 猫名を取得
        animal_name = ""
        if record.animal:
            animal_name = record.animal.name or tj(
                "animal.no_name", locale=locale, id=record.animal_id
            )
        else:
            animal_name = tj("animal.no_name", locale=locale, id=record.animal_id)

        writer.writerow(
            [
                record.created_at.strftime("%Y-%m-%d %H:%M:%S"),
                record.log_date.strftime("%Y-%m-%d"),
                record.animal_id,
                animal_name,
                tj(
                    f"time_slots.{record.time_slot}",
                    locale=locale,
                ),
                record.appetite,
                record.energy,
                tj(
                    "boolean.yes" if record.urination else "boolean.no",
                    locale=locale,
                ),
                tj(
                    "boolean.yes" if record.cleaning else "boolean.no",
                    locale=locale,
                ),
                record.recorder_id or "",
                record.recorder_name,
                record.memo or "",
                record.ip_address or "",
                record.device_tag or "",
                tj(
                    "boolean.yes" if record.from_paper else "boolean.no",
                    locale=locale,
                ),
                record.last_updated_at.strftime("%Y-%m-%d %H:%M:%S"),
                record.last_updated_by or "",
            ]
        )

    return output.getvalue()


def generate_report_csv(
    db: Session,
    report_type: str,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
    locale: str = "ja",
) -> str:
    """
    帳票CSVを生成（日報・週報・月次集計・個別帳票）

    Args:
        db: データベースセッション
        report_type: 帳票種別（daily/weekly/monthly/individual）
        start_date: 開始日
        end_date: 終了日
        animal_id: 猫のID（個別帳票の場合のみ必須）
        locale: ロケール（ja/en）

    Returns:
        str: CSV形式の文字列（UTF-8 BOM付き）

    Raises:
        ValueError: 不正な帳票種別の場合、または個別帳票で猫IDが未指定の場合

    Example:
        >>> from datetime import date
        >>> csv_data = generate_report_csv(
        ...     db, "daily", date(2024, 11, 1), date(2024, 11, 30)
        ... )
        >>> with open("report.csv", "w", encoding="utf-8-sig") as f:
        ...     f.write(csv_data)
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

    # 世話記録CSVを生成（全帳票種別で共通）
    return generate_care_log_csv(db, start_date, end_date, animal_id, locale)
