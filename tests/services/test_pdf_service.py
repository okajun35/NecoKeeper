"""
PDF生成サービスのテスト

Requirements: Requirement 2, Requirement 7, Requirement 9, Requirement 28.3
"""

from __future__ import annotations

import pytest
from sqlalchemy.orm import Session

from app.models.animal import Animal
from app.services import pdf_service


def _extract_pdf_text(pdf_bytes: bytes) -> str:
    import fitz  # PyMuPDF

    doc = fitz.open(stream=pdf_bytes, filetype="pdf")
    try:
        raw_text = "\n".join(page.get_text() for page in doc)
    finally:
        doc.close()

    # PDF text extraction may insert unpredictable whitespace/newlines depending on
    # fonts/layout/environment. Normalize whitespace so tests are stable.
    return " ".join(raw_text.split())


class TestGenerateQRCardPDF:
    """QRカードPDF生成のテスト"""

    def test_generate_qr_card_pdf_success(self, test_db: Session, test_animal: Animal):
        """正常系: QRカードPDFを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_qr_card_pdf(
            db=test_db,
            animal_id=test_animal.id,
            base_url="https://test.example.com",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        # PDFヘッダーの確認
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_qr_card_pdf_nonexistent_animal(self, test_db: Session):
        """異常系: 存在しない猫IDでエラー"""
        # When/Then
        with pytest.raises(ValueError, match="猫ID 99999 が見つかりません"):
            pdf_service.generate_qr_card_pdf(
                db=test_db,
                animal_id=99999,
                base_url="https://test.example.com",
            )

    def test_generate_qr_card_pdf_with_japanese_locale(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 日本語ロケールでQRカードPDFを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_qr_card_pdf(
            db=test_db,
            animal_id=test_animal.id,
            base_url="https://test.example.com",
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_qr_card_pdf_with_english_locale(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 英語ロケールでQRカードPDFを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_qr_card_pdf(
            db=test_db,
            animal_id=test_animal.id,
            base_url="https://test.example.com",
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


class TestGenerateQRCardGridPDF:
    """面付けQRカードPDF生成のテスト"""

    def test_generate_qr_card_grid_pdf_success(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 面付けQRカードPDFを生成できる"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:5]]

        # When
        pdf_bytes = pdf_service.generate_qr_card_grid_pdf(
            db=test_db,
            animal_ids=animal_ids,
            base_url="https://test.example.com",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_qr_card_grid_pdf_max_10_cards(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 最大10枚のQRカードを生成できる"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:10]]

        # When
        pdf_bytes = pdf_service.generate_qr_card_grid_pdf(
            db=test_db,
            animal_ids=animal_ids,
            base_url="https://test.example.com",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_qr_card_grid_pdf_exceeds_limit(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """異常系: 11枚以上のQRカードでエラー"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:11]]

        # When/Then
        with pytest.raises(ValueError, match="一度に生成できるQRカードは最大10枚です"):
            pdf_service.generate_qr_card_grid_pdf(
                db=test_db,
                animal_ids=animal_ids,
                base_url="https://test.example.com",
            )

    def test_generate_qr_card_grid_pdf_nonexistent_animal(self, test_db: Session):
        """異常系: 存在しない猫IDでエラー"""
        # When/Then
        with pytest.raises(ValueError, match="猫ID 99999 が見つかりません"):
            pdf_service.generate_qr_card_grid_pdf(
                db=test_db,
                animal_ids=[99999],
                base_url="https://test.example.com",
            )

    def test_generate_qr_card_grid_pdf_with_japanese_locale(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 日本語ロケールで面付けQRカードPDFを生成できる"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:3]]

        # When
        pdf_bytes = pdf_service.generate_qr_card_grid_pdf(
            db=test_db,
            animal_ids=animal_ids,
            base_url="https://test.example.com",
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_qr_card_grid_pdf_with_english_locale(
        self, test_db: Session, test_animals_bulk: list[Animal]
    ):
        """正常系: 英語ロケールで面付けQRカードPDFを生成できる"""
        # Given
        animal_ids = [animal.id for animal in test_animals_bulk[:3]]

        # When
        pdf_bytes = pdf_service.generate_qr_card_grid_pdf(
            db=test_db,
            animal_ids=animal_ids,
            base_url="https://test.example.com",
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")


class TestGeneratePaperFormPDF:
    """紙記録フォームPDF生成のテスト"""

    def test_generate_paper_form_pdf_success(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 紙記録フォームPDFを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_paper_form_pdf(
            db=test_db,
            animal_id=test_animal.id,
            year=2024,
            month=11,
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_paper_form_pdf_february_leap_year(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: うるう年の2月（29日）のフォームを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_paper_form_pdf(
            db=test_db,
            animal_id=test_animal.id,
            year=2024,  # うるう年
            month=2,
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_paper_form_pdf_february_non_leap_year(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 平年の2月（28日）のフォームを生成できる"""
        # When
        pdf_bytes = pdf_service.generate_paper_form_pdf(
            db=test_db,
            animal_id=test_animal.id,
            year=2023,  # 平年
            month=2,
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_paper_form_pdf_nonexistent_animal(self, test_db: Session):
        """異常系: 存在しない猫IDでエラー"""
        # When/Then
        with pytest.raises(ValueError, match="猫ID 99999 が見つかりません"):
            pdf_service.generate_paper_form_pdf(
                db=test_db,
                animal_id=99999,
                year=2024,
                month=11,
            )


class TestGenerateMedicalDetailPDF:
    """診療明細PDF生成のテスト"""

    def test_generate_medical_detail_pdf_not_implemented(self, test_db: Session):
        """異常系: 診療記録機能が未実装"""
        # When/Then
        with pytest.raises(NotImplementedError, match="診療記録機能は未実装です"):
            pdf_service.generate_medical_detail_pdf(
                db=test_db,
                medical_record_id=1,
            )


class TestGenerateReportPDF:
    """帳票PDF生成のテスト"""

    def test_generate_report_pdf_daily_success(self, test_db: Session):
        """正常系: 日報PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="daily",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
        )

        # Then
        assert pdf_bytes is not None
        assert isinstance(pdf_bytes, bytes)
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_report_pdf_daily_japanese(self, test_db: Session):
        """正常系: 日本語で日報PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="daily",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert pdf_bytes.startswith(b"%PDF")

    def test_generate_report_pdf_daily_english(self, test_db: Session):
        """正常系: 英語で日報PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="daily",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert pdf_bytes.startswith(b"%PDF")

        text = _extract_pdf_text(pdf_bytes)
        assert "Care Logs" in text
        assert "Daily Report" in text
        assert "Log Date" in text
        assert "Animal Name" in text
        assert "Time Slot" in text

    def test_generate_report_pdf_weekly_japanese(self, test_db: Session):
        """正常系: 日本語で週報PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="weekly",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_weekly_english(self, test_db: Session):
        """正常系: 英語で週報PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="weekly",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_monthly_japanese(self, test_db: Session):
        """正常系: 日本語で月次集計PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="monthly",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_monthly_english(self, test_db: Session):
        """正常系: 英語で月次集計PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="monthly",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_individual_with_animal_japanese(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 日本語で個別帳票PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="individual",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            animal_id=test_animal.id,
            locale="ja",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_individual_with_animal_english(
        self, test_db: Session, test_animal: Animal
    ):
        """正常系: 英語で個別帳票PDFを生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type="individual",
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            animal_id=test_animal.id,
            locale="en",
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0

    def test_generate_report_pdf_invalid_type(self, test_db: Session):
        """異常系: 不正な帳票種別でエラー"""
        # Given
        from datetime import date

        # When/Then
        with pytest.raises(ValueError, match="不正な帳票種別です"):
            pdf_service.generate_report_pdf(
                db=test_db,
                report_type="invalid",
                start_date=date(2024, 11, 1),
                end_date=date(2024, 11, 30),
            )

    def test_generate_report_pdf_individual_without_animal_id(self, test_db: Session):
        """異常系: 個別帳票で猫ID未指定でエラー"""
        # Given
        from datetime import date

        # When/Then
        with pytest.raises(ValueError, match="個別帳票の生成には猫IDが必要です"):
            pdf_service.generate_report_pdf(
                db=test_db,
                report_type="individual",
                start_date=date(2024, 11, 1),
                end_date=date(2024, 11, 30),
            )

    @pytest.mark.parametrize(
        "report_type,locale",
        [
            ("daily", "ja"),
            ("daily", "en"),
            ("weekly", "ja"),
            ("weekly", "en"),
            ("monthly", "ja"),
            ("monthly", "en"),
            ("medical_summary", "ja"),
            ("medical_summary", "en"),
        ],
    )
    def test_generate_report_pdf_all_types_and_locales(
        self, test_db: Session, report_type, locale
    ):
        """パラメータ化テスト: 全帳票種別×全ロケールで生成できる"""
        # Given
        from datetime import date

        # When
        pdf_bytes = pdf_service.generate_report_pdf(
            db=test_db,
            report_type=report_type,
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            locale=locale,
        )

        # Then
        assert pdf_bytes is not None
        assert len(pdf_bytes) > 0
        assert pdf_bytes.startswith(b"%PDF")
