"""
CSVサービスのテスト（多言語対応）

Requirements: Requirement 9, Requirement 25
"""

from __future__ import annotations

from datetime import date

from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.models.care_log import CareLog
from app.services.csv_service import generate_care_log_csv, generate_report_csv


class TestGenerateCareLogCSV:
    """ケアログCSV生成のテスト"""

    def test_generate_care_log_csv_japanese(
        self, test_db: Session, test_care_logs: list[CareLog]
    ):
        """正常系: 日本語でケアログCSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_care_log_csv(test_db, start_date, end_date, locale="ja")

        # Then
        assert csv_content is not None
        assert "記録日時" in csv_content  # 日本語ヘッダー
        assert "猫名" in csv_content
        assert "時点" in csv_content

    def test_generate_care_log_csv_english(
        self, test_db: Session, test_care_logs: list[CareLog]
    ):
        """正常系: 英語でケアログCSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_care_log_csv(test_db, start_date, end_date, locale="en")

        # Then
        assert csv_content is not None
        assert "Created At" in csv_content  # 英語ヘッダー
        assert "Animal Name" in csv_content
        assert "Time Slot" in csv_content

    def test_generate_care_log_csv_no_data(self, test_db: Session):
        """境界値: データなしでも正常にCSV生成できる"""
        # Given
        start_date = date(2025, 1, 1)
        end_date = date(2025, 1, 31)

        # When
        csv_content = generate_care_log_csv(test_db, start_date, end_date, locale="ja")

        # Then
        assert csv_content is not None
        assert "記録日時" in csv_content  # ヘッダーは存在


class TestGenerateReportCSV:
    """帳票CSV生成のテスト"""

    def test_generate_daily_report_csv_japanese(
        self, test_db: Session, test_care_logs: list[CareLog]
    ):
        """正常系: 日本語で日報CSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_report_csv(
            test_db, "daily", start_date, end_date, locale="ja"
        )

        # Then
        assert csv_content is not None
        assert "記録日時" in csv_content

    def test_generate_weekly_report_csv_english(
        self, test_db: Session, test_care_logs: list[CareLog]
    ):
        """正常系: 英語で週報CSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_report_csv(
            test_db, "weekly", start_date, end_date, locale="en"
        )

        # Then
        assert csv_content is not None
        assert "Created At" in csv_content

    def test_generate_monthly_report_csv(
        self, test_db: Session, test_care_logs: list[CareLog]
    ):
        """正常系: 月次集計CSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_report_csv(
            test_db, "monthly", start_date, end_date, locale="ja"
        )

        # Then
        assert csv_content is not None

    def test_generate_individual_report_csv_with_animal(
        self,
        test_db: Session,
        test_animal: Animal,
        test_care_logs: list[CareLog],
    ):
        """正常系: 個別帳票CSVを生成できる"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When
        csv_content = generate_report_csv(
            test_db,
            "individual",
            start_date,
            end_date,
            animal_id=test_animal.id,
            locale="ja",
        )

        # Then
        assert csv_content is not None

    def test_generate_report_csv_invalid_type(self, test_db: Session):
        """異常系: 不正な帳票種別で例外発生"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When/Then
        import pytest

        with pytest.raises(ValueError):
            generate_report_csv(test_db, "invalid", start_date, end_date, locale="ja")

    def test_generate_individual_report_csv_missing_animal_id(self, test_db: Session):
        """異常系: 個別帳票で猫ID未指定で例外発生"""
        # Given
        start_date = date(2024, 11, 1)
        end_date = date(2024, 11, 30)

        # When/Then
        import pytest

        with pytest.raises(ValueError):
            generate_report_csv(
                test_db, "individual", start_date, end_date, locale="ja"
            )
