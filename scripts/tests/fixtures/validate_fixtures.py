#!/usr/bin/env python3
"""
Validate test fixture files

This script validates that all test fixture files are properly formatted
and conform to the expected schemas.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

# Add parent directories to path to import utilities
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.json_schema import validate_care_log_json


def validate_json_file(file_path: Path) -> tuple[bool, str]:
    """
    Validate a JSON file.

    Args:
        file_path: Path to the JSON file

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        with file_path.open() as f:
            data = json.load(f)

        # Validate against schema
        result = validate_care_log_json(data)
        is_valid = result.is_valid
        errors = [e.to_dict() for e in result.errors]

        if is_valid:
            return True, f"✓ {file_path.name}: Valid ({len(data)} records)"
        else:
            return False, f"✗ {file_path.name}: Invalid\n  Errors: {errors}"

    except json.JSONDecodeError as e:
        return False, f"✗ {file_path.name}: Invalid JSON - {e}"
    except Exception as e:
        return False, f"✗ {file_path.name}: Error - {e}"


def validate_image_file(file_path: Path) -> tuple[bool, str]:
    """
    Validate an image file exists and has reasonable size.

    Args:
        file_path: Path to the image file

    Returns:
        Tuple of (is_valid, message)
    """
    try:
        if not file_path.exists():
            return False, f"✗ {file_path.name}: File not found"

        size_kb = file_path.stat().st_size / 1024

        if size_kb < 1:
            return False, f"✗ {file_path.name}: File too small ({size_kb:.1f} KB)"

        if size_kb > 10000:  # 10 MB
            return False, f"✗ {file_path.name}: File too large ({size_kb:.1f} KB)"

        return True, f"✓ {file_path.name}: Valid ({size_kb:.1f} KB)"

    except Exception as e:
        return False, f"✗ {file_path.name}: Error - {e}"


def main() -> None:
    """Validate all test fixtures."""
    fixtures_dir = Path(__file__).parent

    print("Validating OCR Care Log Import Test Fixtures")
    print("=" * 60)

    all_valid = True

    # Validate JSON files
    print("\nJSON Files:")
    json_files = [
        "sample_care_logs.json",
        "sample_edge_cases.json",
    ]

    for filename in json_files:
        file_path = fixtures_dir / filename
        is_valid, message = validate_json_file(file_path)
        print(f"  {message}")
        all_valid = all_valid and is_valid

    # Validate invalid data file (should have validation errors)
    print("\nInvalid Data File (should fail validation):")
    invalid_file = fixtures_dir / "sample_invalid_data.json"
    is_valid, message = validate_json_file(invalid_file)
    # For invalid data, we expect validation to fail
    if not is_valid:
        print(f"  ✓ {invalid_file.name}: Correctly identified as invalid")
    else:
        print(f"  ✗ {invalid_file.name}: Should be invalid but passed validation")
        all_valid = False

    # Validate image files
    print("\nImage Files:")
    image_files = [
        "sample_care_log.png",
        "sample_edge_case.png",
        "sample_poor_quality.png",
    ]

    for filename in image_files:
        file_path = fixtures_dir / filename
        is_valid, message = validate_image_file(file_path)
        print(f"  {message}")
        all_valid = all_valid and is_valid

    # Validate PDF file
    print("\nPDF Files:")
    pdf_file = fixtures_dir / "sample_care_log.pdf"
    is_valid, message = validate_image_file(pdf_file)
    print(f"  {message}")
    all_valid = all_valid and is_valid

    # Summary
    print("\n" + "=" * 60)
    if all_valid:
        print("✓ All test fixtures are valid!")
        sys.exit(0)
    else:
        print("✗ Some test fixtures have issues")
        sys.exit(1)


if __name__ == "__main__":
    main()
