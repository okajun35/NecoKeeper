"""Medical report helpers.

This module provides shared query + aggregation logic for medical report exports
(PDF/CSV/Excel).

We intentionally compute prices based on the MedicalAction version that is valid
on each MedicalRecord.date (by matching MedicalAction.name and valid_from/to).
This mitigates price revision issues when actions are versioned by period.
"""

from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from datetime import date
from decimal import Decimal

from sqlalchemy.orm import Session, aliased

from app.models.animal import Animal
from app.models.medical_action import MedicalAction
from app.models.medical_record import MedicalRecord


@dataclass(frozen=True)
class MedicalSummaryRow:
    medical_record_id: int
    medical_date: date
    animal_id: int
    animal_name: str
    medical_action_name: str | None
    dosage: int
    dosage_unit: str | None
    cost_price: Decimal | None
    selling_price: Decimal | None
    procedure_fee: Decimal | None
    billing_amount: Decimal | None
    currency: str | None


@dataclass(frozen=True)
class MedicalSummaryTotals:
    total_records: int
    total_animals: int
    totals_by_currency: dict[str, dict[str, Decimal]]


def _decimal_or_none(value: Decimal | None) -> Decimal | None:
    return value if value is not None else None


def get_medical_summary_rows(
    db: Session,
    start_date: date,
    end_date: date,
    animal_id: int | None = None,
) -> tuple[list[MedicalSummaryRow], MedicalSummaryTotals]:
    """Fetch medical records and compute per-row pricing fields.

    Pricing is chosen from the MedicalAction version valid on record.date,
    selected by (name, valid_from/to). If no valid version is found, falls back
    to the action row referenced by medical_action_id.
    """

    ActionRef = aliased(MedicalAction)

    query = (
        db.query(MedicalRecord, Animal, ActionRef)
        .join(Animal, Animal.id == MedicalRecord.animal_id)
        .outerjoin(ActionRef, ActionRef.id == MedicalRecord.medical_action_id)
        .filter(MedicalRecord.date >= start_date)
        .filter(MedicalRecord.date <= end_date)
    )

    if animal_id:
        query = query.filter(MedicalRecord.animal_id == animal_id)

    base_rows = query.order_by(MedicalRecord.date.desc(), MedicalRecord.id.desc()).all()

    # Collect action names for version lookup
    action_names: set[str] = {
        action_ref.name
        for (_, _, action_ref) in base_rows
        if action_ref is not None and action_ref.name
    }

    actions_by_name: dict[str, list[MedicalAction]] = defaultdict(list)
    if action_names:
        actions = (
            db.query(MedicalAction)
            .filter(MedicalAction.name.in_(sorted(action_names)))
            .filter(MedicalAction.valid_from <= end_date)
            .filter(
                (MedicalAction.valid_to.is_(None))
                | (MedicalAction.valid_to >= start_date)
            )
            .order_by(MedicalAction.name.asc(), MedicalAction.valid_from.desc())
            .all()
        )
        for action in actions:
            actions_by_name[action.name].append(action)

    result_rows: list[MedicalSummaryRow] = []
    totals_by_currency: dict[str, dict[str, Decimal]] = defaultdict(
        lambda: {"billing_amount": Decimal("0"), "cost_amount": Decimal("0")}
    )

    for record, animal, action_ref in base_rows:
        animal_name = animal.name or f"ID:{animal.id}"
        dosage = record.dosage if record.dosage and record.dosage > 0 else 1

        selected_action: MedicalAction | None = None
        action_name: str | None = None

        if action_ref is not None:
            action_name = action_ref.name
            for candidate in actions_by_name.get(action_ref.name, []):
                if candidate.is_valid_on(record.date):
                    selected_action = candidate
                    break
            if selected_action is None:
                selected_action = action_ref

        if selected_action is None:
            result_rows.append(
                MedicalSummaryRow(
                    medical_record_id=record.id,
                    medical_date=record.date,
                    animal_id=record.animal_id,
                    animal_name=animal_name,
                    medical_action_name=None,
                    dosage=dosage,
                    dosage_unit=None,
                    cost_price=None,
                    selling_price=None,
                    procedure_fee=None,
                    billing_amount=None,
                    currency=None,
                )
            )
            continue

        billing_amount = selected_action.calculate_total_price(dosage)
        cost_amount = selected_action.cost_price * Decimal(dosage)
        currency = selected_action.currency or "JPY"

        totals_by_currency[currency]["billing_amount"] += billing_amount
        totals_by_currency[currency]["cost_amount"] += cost_amount

        result_rows.append(
            MedicalSummaryRow(
                medical_record_id=record.id,
                medical_date=record.date,
                animal_id=record.animal_id,
                animal_name=animal_name,
                medical_action_name=action_name,
                dosage=dosage,
                dosage_unit=selected_action.unit,
                cost_price=_decimal_or_none(selected_action.cost_price),
                selling_price=_decimal_or_none(selected_action.selling_price),
                procedure_fee=_decimal_or_none(selected_action.procedure_fee),
                billing_amount=_decimal_or_none(billing_amount),
                currency=currency,
            )
        )

    totals = MedicalSummaryTotals(
        total_records=len(result_rows),
        total_animals=len({row.animal_id for row in result_rows}),
        totals_by_currency=dict(totals_by_currency),
    )

    return result_rows, totals
