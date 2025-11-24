#!/usr/bin/env python3
"""
Data Registration Hook Script

This script registers care log data to the NecoKeeper API.
It handles authentication, batch registration, error handling,
and generates a summary of the registration process.

Requirements:
- 6.3: Invoke data registration Hook with JSON data
- 6.4: Accept JSON data and register via API with admin privileges
- 6.5: Authenticate with API by calling authentication endpoint
- 7.2: Log processing status
- 7.4: Display summary with success/failed counts
- 7.5: List skipped records with reasons

Usage:
    python scripts/hooks/register_care_logs.py <json_file_path>

Example:
    python scripts/hooks/register_care_logs.py tmp/care_logs.json

Environment Variables:
    NECOKEEPER_API_URL: Base URL of NecoKeeper API (default: http://localhost:8000)
    NECOKEEPER_ADMIN_USERNAME: Admin username for authentication
    NECOKEEPER_ADMIN_PASSWORD: Admin password for authentication
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
        dict: API configuration with base_url, username, and password

    Raises:
        ValueError: If required environment variables are not set
    """
    api_url = os.getenv("NECOKEEPER_API_URL", "http://localhost:8000")
    username = os.getenv("NECOKEEPER_ADMIN_USERNAME")
    password = os.getenv("NECOKEEPER_ADMIN_PASSWORD")

    if not username or not password:
        raise ValueError(
            "NECOKEEPER_ADMIN_USERNAME and NECOKEEPER_ADMIN_PASSWORD "
            "environment variables must be set"
        )

    return {
        "base_url": api_url.rstrip("/"),
        "username": username,
        "password": password,
    }


def authenticate(base_url: str, username: str, password: str) -> str:
    """
    Authenticate with the NecoKeeper API and get access token.

    Args:
        base_url: Base URL of the API
        username: Admin username
        password: Admin password

    Returns:
        str: Access token

    Raises:
        AuthenticationError: If authentication fails
    """
    logger.info("Authenticating with NecoKeeper API...")

    auth_url = f"{base_url}/api/v1/auth/token"

    try:
        # OAuth2 Password Flow requires form data
        response = requests.post(
            auth_url,
            data={
                "username": username,
                "password": password,
            },
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            timeout=30,
        )

        if response.status_code == 200:
            token_data = response.json()
            access_token = token_data.get("access_token")

            if not access_token:
                raise AuthenticationError("No access token in response")

            logger.info("Authentication successful")
            return access_token

        else:
            error_detail = response.json().get("detail", "Unknown error")
            raise AuthenticationError(
                f"Authentication failed (status {response.status_code}): {error_detail}"
            )

    except requests.exceptions.RequestException as e:
        raise AuthenticationError(f"Network error during authentication: {e}") from e


def register_care_log(
    base_url: str, access_token: str, care_log_data: dict[str, Any]
) -> dict[str, Any]:
    """
    Register a single care log record via API.

    Args:
        base_url: Base URL of the API
        access_token: Authentication token
        care_log_data: Care log data to register

    Returns:
        dict: Response data from API

    Raises:
        RegistrationError: If registration fails
    """
    register_url = f"{base_url}/api/v1/care-logs"

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json",
    }

    try:
        response = requests.post(
            register_url, json=care_log_data, headers=headers, timeout=30
        )

        if response.status_code == 201:
            return response.json()
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
    admin_username: str,
    admin_password: str,
) -> dict[str, Any]:
    """
    Register care log records via NecoKeeper API.

    This function:
    1. Authenticates with the API
    2. Registers each record in a batch loop
    3. Continues processing on individual failures
    4. Generates a summary with success/failed counts

    Args:
        care_logs: List of care log data dictionaries
        api_base_url: Base URL of NecoKeeper API
        admin_username: Administrator username
        admin_password: Administrator password

    Returns:
        dict: Summary with success_count, failed_count, errors

    Example:
        >>> summary = register_care_logs_batch(
        ...     care_logs=[{"animal_id": 1, ...}],
        ...     api_base_url="http://localhost:8000",
        ...     admin_username="admin",
        ...     admin_password="password"
        ... )
        >>> print(summary["summary"]["successful"])
        10
    """
    summary = RegistrationSummary()
    summary.total_records = len(care_logs)

    logger.info(f"Starting batch registration of {summary.total_records} records...")

    # Step 1: Authenticate
    try:
        access_token = authenticate(api_base_url, admin_username, admin_password)
    except AuthenticationError as e:
        logger.error(f"Authentication failed: {e}")
        # If authentication fails, all records fail
        for index, record in enumerate(care_logs):
            summary.add_failure(
                record_index=index,
                record=record,
                error_message=str(e),
                error_type="authentication_error",
            )
        return summary.to_dict()

    # Step 2: Register each record
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
            result = register_care_log(api_base_url, access_token, care_log_data)

            # Success
            summary.add_success()
            logger.info(
                f"  ✓ Successfully registered record {index + 1} (ID: {result.get('id')})"
            )

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
            admin_username=config["username"],
            admin_password=config["password"],
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
