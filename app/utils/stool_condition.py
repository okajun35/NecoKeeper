"""Stool condition definitions.

`CareLog.stool_condition` is stored as an integer 1..5 in the database.
This module centralizes the meaning of those values.
"""

from __future__ import annotations

from enum import IntEnum


class StoolCondition(IntEnum):
    HARD = 1
    GOOD = 2
    SLIGHTLY_SOFT = 3
    DIARRHEA = 4
    WATERY = 5

    @classmethod
    def is_valid_value(cls, value: int) -> bool:
        return value in cls._value2member_map_


def stool_condition_image_path(condition: StoolCondition | int) -> str:
    """Return the static image path for the given stool condition."""

    value = int(condition)
    if not StoolCondition.is_valid_value(value):
        raise ValueError(f"Invalid stool condition: {condition}")
    return f"/static/images/cat_poops/cat_poop_{value}.png"
