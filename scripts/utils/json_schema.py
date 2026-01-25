"""
JSON Schema Validator for Care Log Data

This module provides validation for care log JSON data extracted from OCR.
It validates the structure, types, ranges, and formats according to the
Care Log data model requirements.

Requirements:
- 8.1: Validate all required fields are present
- 8.2: Ensure appetite/energy values are within valid range
- 8.3: Ensure boolean fields are valid boolean values
- 8.4: Ensure date fields are valid dates
- 8.5: Return detailed validation errors
"""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any


class ValidationError:
    """Represents a validation error with details"""

    def __init__(
        self,
        field: str,
        message: str,
        value: Any = None,
        record_index: int | None = None,
    ):
        self.field = field
        self.message = message
        self.value = value
        self.record_index = record_index

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        result: dict[str, Any] = {
            "field": self.field,
            "message": self.message,
        }
        if self.value is not None:
            result["value"] = self.value
        if self.record_index is not None:
            result["record_index"] = self.record_index
        return result

    def __repr__(self) -> str:
        return f"ValidationError(field={self.field}, message={self.message})"


class ValidationResult:
    """Result of validation with success status and errors"""

    def __init__(self, is_valid: bool, errors: list[ValidationError] | None = None):
        self.is_valid = is_valid
        self.errors = errors or []

    def add_error(self, error: ValidationError) -> None:
        """Add a validation error"""
        self.errors.append(error)
        self.is_valid = False

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary format"""
        return {
            "is_valid": self.is_valid,
            "errors": [error.to_dict() for error in self.errors],
            "error_count": len(self.errors),
        }


# Care Log JSON Schema Definition
CARE_LOG_SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "array",
    "items": {
        "type": "object",
        "required": [
            "animal_id",
            "log_date",
            "time_slot",
            "appetite",
            "energy",
            "urination",
            "cleaning",
            "recorder_name",
            "from_paper",
        ],
        "properties": {
            "animal_id": {"type": "integer", "minimum": 1},
            "log_date": {
                "type": "string",
                "format": "date",
                "pattern": r"^\d{4}-\d{2}-\d{2}$",
            },
            "time_slot": {"type": "string", "enum": ["morning", "noon", "evening"]},
            "appetite": {"type": "number", "enum": [1.0, 0.75, 0.5, 0.25, 0.0]},
            "energy": {"type": "integer", "minimum": 1, "maximum": 5},
            "urination": {"type": "boolean"},
            "cleaning": {"type": "boolean"},
            "memo": {"type": ["string", "null"], "maxLength": 1000},
            "recorder_name": {"type": "string", "maxLength": 100},
            "from_paper": {"type": "boolean", "const": True},
            "recorder_id": {"type": ["integer", "null"]},
            "ip_address": {"type": ["string", "null"]},
            "user_agent": {"type": ["string", "null"]},
            "device_tag": {"type": ["string", "null"]},
        },
    },
}


def validate_care_log_json(
    data: Any, year: int | None = None, month: int | None = None
) -> ValidationResult:
    """
    Validate care log JSON data against the schema.

    Args:
        data: JSON data to validate (should be a list of care log records)
        year: Expected year for date validation (optional)
        month: Expected month for date validation (optional)

    Returns:
        ValidationResult: Validation result with errors if any

    Example:
        >>> data = [{"animal_id": 1, "log_date": "2025-11-04", ...}]
        >>> result = validate_care_log_json(data, year=2025, month=11)
        >>> if result.is_valid:
        ...     print("Valid!")
        ... else:
        ...     for error in result.errors:
        ...         print(error.message)
    """
    result = ValidationResult(is_valid=True)

    # Check if data is a list
    if not isinstance(data, list):
        result.add_error(
            ValidationError(
                field="root",
                message="Data must be an array of care log records",
                value=type(data).__name__,
            )
        )
        return result

    # Validate each record
    for index, record in enumerate(data):
        _validate_record(record, index, result, year, month)

    return result


def _validate_record(
    record: Any,
    index: int,
    result: ValidationResult,
    year: int | None,
    month: int | None,
) -> None:
    """Validate a single care log record"""
    # Check if record is a dictionary
    if not isinstance(record, dict):
        result.add_error(
            ValidationError(
                field="record",
                message="Each record must be an object",
                value=type(record).__name__,
                record_index=index,
            )
        )
        return

    # Validate required fields
    _validate_required_fields(record, index, result)

    # Validate field types and values
    _validate_animal_id(record, index, result)
    _validate_log_date(record, index, result, year, month)
    _validate_time_slot(record, index, result)
    _validate_appetite(record, index, result)
    _validate_energy(record, index, result)
    _validate_urination(record, index, result)
    _validate_cleaning(record, index, result)
    _validate_memo(record, index, result)
    _validate_recorder_name(record, index, result)
    _validate_from_paper(record, index, result)
    _validate_optional_fields(record, index, result)


def _validate_required_fields(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate that all required fields are present"""
    required_fields = [
        "animal_id",
        "log_date",
        "time_slot",
        "appetite",
        "energy",
        "urination",
        "cleaning",
        "recorder_name",
        "from_paper",
    ]

    for field in required_fields:
        if field not in record:
            result.add_error(
                ValidationError(
                    field=field,
                    message=f"Required field '{field}' is missing",
                    record_index=index,
                )
            )


def _validate_animal_id(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate animal_id field"""
    if "animal_id" not in record:
        return

    animal_id = record["animal_id"]

    if not isinstance(animal_id, int):
        result.add_error(
            ValidationError(
                field="animal_id",
                message="animal_id must be an integer",
                value=animal_id,
                record_index=index,
            )
        )
        return

    if animal_id < 1:
        result.add_error(
            ValidationError(
                field="animal_id",
                message="animal_id must be at least 1",
                value=animal_id,
                record_index=index,
            )
        )


def _validate_log_date(
    record: dict[str, Any],
    index: int,
    result: ValidationResult,
    year: int | None,
    month: int | None,
) -> None:
    """Validate log_date field with optional year-month range check"""
    if "log_date" not in record:
        return

    log_date = record["log_date"]

    if not isinstance(log_date, str):
        result.add_error(
            ValidationError(
                field="log_date",
                message="log_date must be a string",
                value=log_date,
                record_index=index,
            )
        )
        return

    # Check date format (YYYY-MM-DD)
    date_pattern = r"^\d{4}-\d{2}-\d{2}$"
    if not re.match(date_pattern, log_date):
        result.add_error(
            ValidationError(
                field="log_date",
                message="log_date must be in YYYY-MM-DD format",
                value=log_date,
                record_index=index,
            )
        )
        return

    # Validate date is valid
    try:
        parsed_date = datetime.strptime(log_date, "%Y-%m-%d")
    except ValueError as e:
        result.add_error(
            ValidationError(
                field="log_date",
                message=f"log_date is not a valid date: {e}",
                value=log_date,
                record_index=index,
            )
        )
        return

    # Validate year-month range if specified
    if year is not None and parsed_date.year != year:
        result.add_error(
            ValidationError(
                field="log_date",
                message=f"log_date year {parsed_date.year} does not match expected year {year}",
                value=log_date,
                record_index=index,
            )
        )

    if month is not None and parsed_date.month != month:
        result.add_error(
            ValidationError(
                field="log_date",
                message=f"log_date month {parsed_date.month} does not match expected month {month}",
                value=log_date,
                record_index=index,
            )
        )


def _validate_time_slot(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate time_slot field"""
    if "time_slot" not in record:
        return

    time_slot = record["time_slot"]

    if not isinstance(time_slot, str):
        result.add_error(
            ValidationError(
                field="time_slot",
                message="time_slot must be a string",
                value=time_slot,
                record_index=index,
            )
        )
        return

    valid_slots = ["morning", "noon", "evening"]
    if time_slot not in valid_slots:
        result.add_error(
            ValidationError(
                field="time_slot",
                message=f"time_slot must be one of {valid_slots}",
                value=time_slot,
                record_index=index,
            )
        )


def _validate_appetite(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate appetite field (allowed fraction scale)"""
    if "appetite" not in record:
        return

    appetite = record["appetite"]

    if not isinstance(appetite, (int, float)):
        result.add_error(
            ValidationError(
                field="appetite",
                message="appetite must be a number",
                value=appetite,
                record_index=index,
            )
        )
        return

    allowed_values = {1.0, 0.75, 0.5, 0.25, 0.0}
    normalized = round(float(appetite), 2)
    if normalized not in allowed_values:
        result.add_error(
            ValidationError(
                field="appetite",
                message="appetite must be one of 1.0, 0.75, 0.5, 0.25, 0.0",
                value=appetite,
                record_index=index,
            )
        )


def _validate_energy(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate energy field (1-5 range)"""
    if "energy" not in record:
        return

    energy = record["energy"]

    if not isinstance(energy, int):
        result.add_error(
            ValidationError(
                field="energy",
                message="energy must be an integer",
                value=energy,
                record_index=index,
            )
        )
        return

    if energy < 1 or energy > 5:
        result.add_error(
            ValidationError(
                field="energy",
                message="energy must be between 1 and 5",
                value=energy,
                record_index=index,
            )
        )


def _validate_urination(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate urination field (boolean)"""
    if "urination" not in record:
        return

    urination = record["urination"]

    if not isinstance(urination, bool):
        result.add_error(
            ValidationError(
                field="urination",
                message="urination must be a boolean",
                value=urination,
                record_index=index,
            )
        )


def _validate_cleaning(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate cleaning field (boolean)"""
    if "cleaning" not in record:
        return

    cleaning = record["cleaning"]

    if not isinstance(cleaning, bool):
        result.add_error(
            ValidationError(
                field="cleaning",
                message="cleaning must be a boolean",
                value=cleaning,
                record_index=index,
            )
        )


def _validate_memo(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate memo field (optional string with max length)"""
    if "memo" not in record:
        return

    memo = record["memo"]

    if memo is not None and not isinstance(memo, str):
        result.add_error(
            ValidationError(
                field="memo",
                message="memo must be a string or null",
                value=type(memo).__name__,
                record_index=index,
            )
        )
        return

    if isinstance(memo, str) and len(memo) > 1000:
        result.add_error(
            ValidationError(
                field="memo",
                message="memo must not exceed 1000 characters",
                value=f"{len(memo)} characters",
                record_index=index,
            )
        )


def _validate_recorder_name(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate recorder_name field"""
    if "recorder_name" not in record:
        return

    recorder_name = record["recorder_name"]

    if not isinstance(recorder_name, str):
        result.add_error(
            ValidationError(
                field="recorder_name",
                message="recorder_name must be a string",
                value=recorder_name,
                record_index=index,
            )
        )
        return

    if len(recorder_name) > 100:
        result.add_error(
            ValidationError(
                field="recorder_name",
                message="recorder_name must not exceed 100 characters",
                value=f"{len(recorder_name)} characters",
                record_index=index,
            )
        )


def _validate_from_paper(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate from_paper field (must be True for OCR imports)"""
    if "from_paper" not in record:
        return

    from_paper = record["from_paper"]

    if not isinstance(from_paper, bool):
        result.add_error(
            ValidationError(
                field="from_paper",
                message="from_paper must be a boolean",
                value=from_paper,
                record_index=index,
            )
        )
        return

    if from_paper is not True:
        result.add_error(
            ValidationError(
                field="from_paper",
                message="from_paper must be True for OCR imports",
                value=from_paper,
                record_index=index,
            )
        )


def _validate_optional_fields(
    record: dict[str, Any], index: int, result: ValidationResult
) -> None:
    """Validate optional fields if present"""
    # recorder_id: integer or null
    if "recorder_id" in record:
        recorder_id = record["recorder_id"]
        if recorder_id is not None and not isinstance(recorder_id, int):
            result.add_error(
                ValidationError(
                    field="recorder_id",
                    message="recorder_id must be an integer or null",
                    value=recorder_id,
                    record_index=index,
                )
            )

    # ip_address: string or null
    if "ip_address" in record:
        ip_address = record["ip_address"]
        if ip_address is not None and not isinstance(ip_address, str):
            result.add_error(
                ValidationError(
                    field="ip_address",
                    message="ip_address must be a string or null",
                    value=ip_address,
                    record_index=index,
                )
            )

    # user_agent: string or null
    if "user_agent" in record:
        user_agent = record["user_agent"]
        if user_agent is not None and not isinstance(user_agent, str):
            result.add_error(
                ValidationError(
                    field="user_agent",
                    message="user_agent must be a string or null",
                    value=user_agent,
                    record_index=index,
                )
            )

    # device_tag: string or null
    if "device_tag" in record:
        device_tag = record["device_tag"]
        if device_tag is not None and not isinstance(device_tag, str):
            result.add_error(
                ValidationError(
                    field="device_tag",
                    message="device_tag must be a string or null",
                    value=device_tag,
                    record_index=index,
                )
            )
