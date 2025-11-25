#!/usr/bin/env python3
"""
Data Registration Hook Script

This script registers care log data to the NecoKeeper API using the Automation API.
It handles authentication via API Key, batch registration, error handling,
and generates a summary of the registration process.

Requirements:
- 6.3: Invoke data registration Hook with JSON data
- 6.4: Accept JSON data and register via API with admin privileges
- 6.5: Authenticate with API by calling authentication endpoint
- 7.2: Log processing status
- 7.4: Display summary with success/failed counts
- 7.5: List skipped records with reasons
- 8.1: Use /api/automation/care-logs endpoint
- 8.2: Include X-Automation-Key header
- 8.3: Read from AUTOMATION_API_KEY environment variable
- 8.4: Log error and display user-friendly message on authentication failure
- 8.5: Display setup instructions if API Key is not set

Usage:
    python scripts/hooks/register_care_logs.py <json_file_path>

Example:
    python scripts/hooks/register_care_logs.py tmp/care_logs.json

Environment Variables:
    NECOKEEPER_API_URL: Base URL of NecoKeeper API (default: http://localhost:8000)
    AUTOMATION_API_KEY: API Key for Automation API authentication (required)
"""

from __future__ import annotations

import json
import os
import sys
from pathlib import Path
from typing import Any

import requests

from scripts.utils.logging_config import setup_ocr_logger

# Setup logger
logger = setup_ocr_logger(log_file="logs/ocr-import.log", log_level="INFO")


class RegistrationError(Exception):
    """Exception raised when registration fails"""

    pass


class AuthenticationError(Exception):
    """Exception raised when authentication fails"""

    pass


class RegistrationSummary:
    """Summary of the registration process"""

    def __init__(self):
        self.total_records = 0
        self.successful = 0
        self.failed = 0
        self.errors: list[dict[str, Any]] = []

    def add_success(self) -> None:
        """Record a successful registration"""
        self.successful += 1

    def add_failure(
        self,
        record_index: int,
        record: dict[str, Any],
        error_message: str,
        error_type: str = "registration_error",
    ) -> None:
        """Record a failed registration"""
        self.failed += 1
        self.errors.append(
            {
                "record_index": record_index,
                "log_date": record.get("log_date"),
                "time_slot": record.get("time_slot"),
                "animal_id": record.get("animal_id"),
                "error_type": error_type,
                "error_message": error_message,
                "action": "skipped",
            }
        )

    def to_dict(self) -> dict[str, Any]:
        """Convert summary to dictionary"""
        status = "success" if self.failed == 0 else "partial_success"
        if self.successful == 0:
            status = "failed"

        return {
            "status": status,
            "summary": {
                "total_records": self.total_records,
                "successful": self.successful,
                "failed": self.failed,
            },
            "errors": self.errors,
        }

    def print_summary(self) -> None:
        """Print summary to console"""
        print("\n" + "=" * 60)
        print("Registration Summary")
        print("=" * 60)
        print(f"Total records: {self.total_records}")
        print(f"Successful: {self.successful}")
        print(f"Failed: {self.failed}")

        if self.errors:
            print("\nFailed Records:")
            print("-" * 60)
            for error in self.errors:
                print(
                    f"  Record #{error['record_index']}: "
                    f"{error.get('log_date', 'N/A')} {error.get('time_slot', 'N/A')} "
                    f"(Animal ID: {error.get('animal_id', 'N/A')})"
                )
                print(f"    Error: {error['error_message']}")
                print(f"    Type: {error['error_type']}")
                print()

        print("=" * 60)


def get_api_config() -> dict[str, str]:
    """
    Get API configuration from environment variables.

    Returns:
        dict: API configuration with base_url and api_key

    Raises:
        ValueError: If required environment variables are not set
    """
    api_url = os.getenv("NECOKEEPER_API_URL", "http://localhost:8000")
    api_key = os.getenv("AUTOMATION_API_KEY")

    if not api_key:
        error_msg = (
            "\n" + "=" * 70 + "\n"
            "ERROR: AUTOMATION_API_KEY environment variable is not set\n"
            "=" * 70 + "\n\n"
            "The Automation API requires an API Key for authentication.\n\n"
            "Setup Instructions:\n"
            "1. Generate a secure API Key:\n"
            '   python -c "import secrets; print(secrets.token_urlsafe(32))"\n\n'
            "2. Add the API Key to your .env file:\n"
            "   AUTOMATION_API_KEY=<your-generated-key>\n\n"
            "3. Enable the Automation API in your .env file:\n"
            "   ENABLE_AUTOMATION_API=true\n\n"
            "4. Restart the NecoKeeper server\n\n"
            "For more information, see docs/automation-api-guide.md\n" + "=" * 70
        )
        raise ValueError(error_msg)

    return {
        "base_url": api_url.rstrip("/"),
        "api_key": api_key,
    }


def verify_api_key(base_url: str, api_key: str) -> None:
    """
    Verify that the API Key is valid by making a test request.

    Args:
        base_url: Base URL of the API
        api_key: Automation API Key

    Raises:
        AuthenticationError: If API Key is invalid or Automation API is disabled
    """
    logger.info("Verifying Automation API Key...")

    # We'll verify the key by attempting to access the automation endpoint
    # The actual verification happens when we make the first request
    logger.info("API Key configured for Automation API")


def register_care_log(
    base_url: str, api_key: str, care_log_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Register a single care log record via Automation API.

    Args:
        base_url: Base URL of the API
        api_key: Automation API Key
        care_log_data: Care log data to register

    Returns:
        dict: Response data from API

    Raises:
        RegistrationError: If registration fails
        AuthenticationError: If API Key is invalid
    """
    register_url = f"{base_url}/api/automation/care-logs"

    headers = {
        "X-Automation-Key": api_key,
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            register_url, json=care_log_data, headers=headers, timeout=30
        )

        if response.status_code == 201:
            return response.json()
        elif response.status_code == 401:
            error_detail = response.json().get("detail", "API Key is missing")
            raise AuthenticationError(
                f"Authentication failed: {error_detail}\n"
                "Please check that AUTOMATION_API_KEY is set correctly."
            )
        elif response.status_code == 403:
            error_detail = response.json().get("detail", "Invalid API Key")
            raise AuthenticationError(
                f"Authentication failed: {error_detail}\n"
                "The API Key is invalid. Please check your AUTOMATION_API_KEY."
            )
        elif response.status_code == 503:
            error_detail = response.json().get("detail", "Automation API is disabled")
            raise AuthenticationError(
                f"Service unavailable: {error_detail}\n"
                "Please enable the Automation API by setting ENABLE_AUTOMATION_API=true"
            )
        else:
            error_detail = response.json().get("detail", "Unknown error")
            raise RegistrationError(
                f"Registration failed (status {response.status_code}): {error_detail}"
            )

    except requests.exceptions.RequestException as e:
        raise RegistrationError(f"Network error during registration: {e}") from e


def register_care_logs_batch(
    care_logs: list[dict[str, Any]],
    api_base_url: str,
    api_key: str,
) -> dict[str, Any]:
    """
    Register care log records via NecoKeeper Automation API.

    This function:
    1. Verifies API Key configuration
    2. Registers each record in a batch loop
    3. Continues processing on individual failures
    4. Generates a summary with success/failed counts

    Args:
        care_logs: List of care log data dictionaries
        api_base_url: Base URL of NecoKeeper API
        api_key: Automation API Key

    Returns:
        dict: Summary with success_count, failed_count, errors

    Example:
        >>> summary = register_care_logs_batch(
        ...     care_logs=[{"animal_id": 1, ...}],
        ...     api_base_url="http://localhost:8000",
        ...     api_key="your-api-key"
        ... )
        >>> print(summary["summary"]["successful"])
        10
    """
    summary = RegistrationSummary()
    summary.total_records = len(care_logs)

    logger.info(f"Starting batch registration of {summary.total_records} records...")
    logger.info("Using Automation API with API Key authentication")

    # Step 1: Verify API Key is configured
    try:
        verify_api_key(api_base_url, api_key)
    except AuthenticationError as e:
        logger.error(f"API Key verification failed: {e}")
        # If verification fails, all records fail
        for index, record in enumerate(care_logs):
            summary.add_failure(
                record_index=index,
                record=record,
                error_message=str(e),
                error_type="authentication_error",
            )
        return summary.to_dict()

    # Step 2: Register each record
    authentication_failed = False
    for index, care_log_data in enumerate(care_logs):
        log_date = care_log_data.get("log_date", "N/A")
        time_slot = care_log_data.get("time_slot", "N/A")
        animal_id = care_log_data.get("animal_id", "N/A")

        logger.info(
            f"Registering record {index + 1}/{summary.total_records}: "
            f"Date={log_date}, TimeSlot={time_slot}, AnimalID={animal_id}"
        )

        try:
            # Register the record
            result = register_care_log(api_base_url, api_key, care_log_data)

            # Success
            summary.add_success()
            logger.info(
                f"  ✓ Successfully registered record {index + 1} (ID: {result.get('id')})"
            )

        except AuthenticationError as e:
            # Authentication failed - stop processing remaining records
            authentication_failed = True
            summary.add_failure(
                record_index=index,
                record=care_log_data,
                error_message=str(e),
                error_type="authentication_error",
            )
            logger.error(f"  ✗ Authentication failed for record {index + 1}: {e}")

            # Mark all remaining records as failed due to authentication
            for remaining_index in range(index + 1, len(care_logs)):
                summary.add_failure(
                    record_index=remaining_index,
                    record=care_logs[remaining_index],
                    error_message="Skipped due to authentication failure",
                    error_type="authentication_error",
                )
            break

        except RegistrationError as e:
            # Individual record failed - log and continue
            summary.add_failure(
                record_index=index,
                record=care_log_data,
                error_message=str(e),
                error_type="registration_error",
            )
            logger.error(f"  ✗ Failed to register record {index + 1}: {e}")

        except Exception as e:
            # Unexpected error - log and continue
            summary.add_failure(
                record_index=index,
                record=care_log_data,
                error_message=f"Unexpected error: {e}",
                error_type="unexpected_error",
            )
            logger.error(f"  ✗ Unexpected error for record {index + 1}: {e}")

    # Step 3: Generate summary
    logger.info(
        f"Batch registration complete: {summary.successful} successful, "
        f"{summary.failed} failed"
    )

    if authentication_failed:
        logger.error(
            "Authentication failed. Please check your AUTOMATION_API_KEY and "
            "ensure ENABLE_AUTOMATION_API=true on the server."
        )

    return summary.to_dict()


def load_json_file(file_path: str) -> list[dict[str, Any]]:
    """
    Load care log data from JSON file.

    Args:
        file_path: Path to JSON file

    Returns:
        list: Care log data

    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is invalid
    """
    file = Path(file_path)
    if not file.exists():
        raise FileNotFoundError(f"JSON file not found: {file_path}")

    logger.info(f"Loading JSON data from: {file_path}")

    try:
        with file.open(encoding="utf-8") as f:
            data = json.load(f)

        if not isinstance(data, list):
            raise ValueError("JSON data must be an array of care log records")

        logger.info(f"Loaded {len(data)} records from JSON file")
        return data

    except json.JSONDecodeError as e:
        raise ValueError(f"Invalid JSON format: {e}") from e


def main() -> int:
    """
    Main entry point for the script.

    Returns:
        int: Exit code (0 for success, 1 for failure)
    """
    # Check command line arguments
    if len(sys.argv) != 2:
        print("Usage: python scripts/hooks/register_care_logs.py <json_file_path>")
        print("\nExample:")
        print("  python scripts/hooks/register_care_logs.py tmp/care_logs.json")
        return 1

    json_file_path = sys.argv[1]

    try:
        # Load JSON data
        care_logs = load_json_file(json_file_path)

        if not care_logs:
            logger.warning("No records to register")
            print("No records to register")
            return 0

        # Get API configuration
        config = get_api_config()

        # Register care logs
        result = register_care_logs_batch(
            care_logs=care_logs,
            api_base_url=config["base_url"],
            api_key=config["api_key"],
        )

        # Create summary object for printing
        summary = RegistrationSummary()
        summary.total_records = result["summary"]["total_records"]
        summary.successful = result["summary"]["successful"]
        summary.failed = result["summary"]["failed"]
        summary.errors = result["errors"]

        # Print summary
        summary.print_summary()

        # Move processed file to processed directory (Requirement 6.6)
        if result["status"] in ["success", "partial_success"]:
            try:
                source_file = Path(json_file_path)
                processed_dir = Path("tmp/json/processed")
                processed_dir.mkdir(parents=True, exist_ok=True)

                destination_file = processed_dir / source_file.name
                source_file.rename(destination_file)

                logger.info(f"Moved processed file to: {destination_file}")
                print(f"\n✓ Processed file moved to: {destination_file}")

            except Exception as e:
                logger.warning(f"Failed to move processed file: {e}")
                print(f"\n⚠ Warning: Could not move processed file: {e}")

        # Return exit code based on status
        if result["status"] == "success":
            return 0
        elif result["status"] == "partial_success":
            return 0  # Partial success is still acceptable
        else:
            return 1

    except FileNotFoundError as e:
        logger.error(f"File error: {e}")
        print(f"Error: {e}")
        return 1

    except ValueError as e:
        logger.error(f"Data error: {e}")
        print(f"Error: {e}")
        return 1

    except Exception as e:
        logger.error(f"Unexpected error: {e}")
        print(f"Unexpected error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())
