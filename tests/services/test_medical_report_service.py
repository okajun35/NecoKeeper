"""Tests for medical report domain logic.

DDD/t-wada style:
- Focus on behavior (prices selected by validity period)
- Keep tests small and intention-revealing (Given/When/Then)
"""

from __future__ import annotations

from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session

from app.models.medical_action import MedicalAction
from app.models.medical_record import MedicalRecord
from app.services.medical_report_service import get_medical_summary_rows


class TestMedicalSummaryPricingSelection:
    def test_selects_action_version_valid_on_record_date(
        self, test_db: Session, test_animal
    ) -> None:
        """有効期間で価格改定があっても、診療日当日の価格を採用する"""
        # Given: 同名の診療行為が価格改定で2バージョンある
        action_old = MedicalAction(
            name="ワクチン",
            valid_from=date(2024, 1, 1),
            valid_to=date(2024, 6, 30),
            cost_price=Decimal("100"),
            selling_price=Decimal("300"),
            procedure_fee=Decimal("10"),
            currency="JPY",
            unit="回",
        )
        action_new = MedicalAction(
            name="ワクチン",
            valid_from=date(2024, 7, 1),
            valid_to=None,
            cost_price=Decimal("200"),
            selling_price=Decimal("500"),
            procedure_fee=Decimal("20"),
            currency="JPY",
            unit="回",
        )
        test_db.add(action_old)
        test_db.add(action_new)
        test_db.commit()

        # 参照は旧IDでも、診療日には新価格が有効
        record = MedicalRecord(
            animal_id=test_animal.id,
            vet_id=1,
            date=date(2024, 11, 15),
            symptoms="テスト",
            medical_action_id=action_old.id,
            dosage=2,
        )
        test_db.add(record)
        test_db.commit()

        # When
        rows, totals = get_medical_summary_rows(
            db=test_db,
            start_date=date(2024, 11, 1),
            end_date=date(2024, 11, 30),
            animal_id=None,
        )

        # Then
        assert totals.total_records == 1
        row = rows[0]
        assert row.medical_action_name == "ワクチン"
        assert row.selling_price == Decimal("500")
        assert row.procedure_fee == Decimal("20")
        # (500*2)+20
        assert row.billing_amount == Decimal("1020")
