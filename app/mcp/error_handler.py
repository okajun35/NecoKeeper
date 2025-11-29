"""
Centralized Error Handling for MCP Server

This module provides centralized error handling and logging configuration
for the NecoKeeper MCP server, ensuring consistent error messages and
proper error categorization.

Requirements: 6.3, 7.1, 7.2, 7.3, 7.4, 7.5
"""

from __future__ import annotations

import logging
from collections.abc import Callable
from typing import Any, TypeVar

import httpx
from fastmcp.exceptions import ToolError

logger = logging.getLogger(__name__)

# Type variable for generic function wrapping
T = TypeVar("T")


class ErrorCategory:
    """Error category constants for consistent error handling"""

    NETWORK = "network"
    AUTHENTICATION = "authentication"
    VALIDATION = "validation"
    NOT_FOUND = "not_found"
    FILE_SYSTEM = "file_system"
    UNEXPECTED = "unexpected"


def configure_logging(log_level: str = "INFO", log_file: str | None = None) -> None:
    """
    Configure logging for the MCP server

    Sets up logging with appropriate format, level, and handlers.
    Logs are written to stderr (for MCP stdio transport) and optionally
    to a file.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path. If None, only logs to stderr.

    Requirements 7.5: Add logging configuration

    Example:
        >>> configure_logging(log_level="DEBUG", log_file="logs/mcp-server.log")
    """
    # Convert log level string to logging constant
    numeric_level = getattr(logging, log_level.upper(), logging.INFO)

    # Create handlers
    handlers: list[logging.Handler] = [
        logging.StreamHandler(),  # stderr for MCP stdio transport
    ]

    # Add file handler if log_file is specified
    if log_file:
        try:
            from pathlib import Path

            log_path = Path(log_file)
            log_path.parent.mkdir(parents=True, exist_ok=True)
            file_handler = logging.FileHandler(log_file)
            handlers.append(file_handler)
        except Exception as e:
            logger.warning(f"Could not create log file handler: {e}")

    # Configure root logger
    logging.basicConfig(
        level=numeric_level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=handlers,
        force=True,  # Override any existing configuration
    )

    logger.info(f"Logging configured: level={log_level}, file={log_file}")


def map_http_error_to_message(exc: httpx.HTTPStatusError) -> tuple[str, str]:
    """
    Map HTTP status errors to user-friendly messages

    Converts HTTP status codes to descriptive error messages with
    appropriate error categories.

    Args:
        exc: HTTP status error exception

    Returns:
        tuple: (error_category, user_friendly_message)

    Requirements 6.3, 7.3: Map HTTP errors to user-friendly messages,
    ensure authentication errors are clear

    Example:
        >>> exc = httpx.HTTPStatusError(...)
        >>> category, message = map_http_error_to_message(exc)
        >>> print(category)
        'authentication'
    """
    status_code = exc.response.status_code
    url = exc.request.url

    # Try to extract error detail from response
    try:
        error_detail = exc.response.json().get("detail", exc.response.text)
    except Exception:
        error_detail = exc.response.text

    # Map status codes to categories and messages
    if status_code == 401:
        # Requirements 6.3, 7.3: Authentication errors are clear
        return (
            ErrorCategory.AUTHENTICATION,
            "Authentication failed: Invalid or missing Automation API Key. "
            "Please check your AUTOMATION_API_KEY environment variable. "
            "You can generate a new key with: "
            'python -c "import secrets; print(secrets.token_urlsafe(32))"',
        )

    elif status_code == 403:
        return (
            ErrorCategory.AUTHENTICATION,
            f"Authorization failed: Insufficient permissions to access {url}. "
            f"Details: {error_detail}",
        )

    elif status_code == 400:
        # Requirements 7.2: Return specific validation error details
        return (
            ErrorCategory.VALIDATION,
            f"Validation error: {error_detail}",
        )

    elif status_code == 404:
        return (
            ErrorCategory.NOT_FOUND,
            f"Resource not found: {error_detail}",
        )

    elif status_code == 422:
        return (
            ErrorCategory.VALIDATION,
            f"Validation error: Request data is invalid. {error_detail}",
        )

    elif status_code == 429:
        return (
            ErrorCategory.NETWORK,
            "Rate limit exceeded. Please try again later.",
        )

    elif status_code >= 500:
        return (
            ErrorCategory.UNEXPECTED,
            f"Server error ({status_code}): The NecoKeeper API encountered an error. "
            f"Please try again later or contact support. Details: {error_detail}",
        )

    else:
        return (
            ErrorCategory.UNEXPECTED,
            f"HTTP error ({status_code}): {error_detail}",
        )


def handle_api_error(exc: Exception, operation: str) -> ToolError:
    """
    Centralized error handling for API calls

    Converts various exception types to ToolError with user-friendly
    messages and appropriate logging.

    Args:
        exc: The exception that occurred
        operation: Description of the operation being performed (e.g., "registering cat")

    Returns:
        ToolError: Formatted error for MCP client

    Requirements 7.1, 7.2, 7.3, 7.4: Handle all error categories with
    descriptive messages

    Example:
        >>> try:
        ...     await api_client.create_animal(data)
        ... except Exception as e:
        ...     raise handle_api_error(e, "registering cat")
    """
    # Handle ToolError - pass through as-is
    if isinstance(exc, ToolError):
        return exc

    # Handle HTTP status errors
    if isinstance(exc, httpx.HTTPStatusError):
        category, message = map_http_error_to_message(exc)

        if category == ErrorCategory.AUTHENTICATION:
            # Requirements 6.3, 7.3: Authentication errors are clear
            logger.error(f"Authentication error while {operation}: {message}")
        elif category == ErrorCategory.VALIDATION:
            # Requirements 7.2: Specific validation error details
            logger.error(f"Validation error while {operation}: {message}")
        else:
            logger.error(f"HTTP error while {operation}: {message}")

        return ToolError(message)

    # Handle connection errors
    # Requirements 7.1: User-friendly network error messages
    if isinstance(exc, httpx.ConnectError):
        logger.error(f"Connection error while {operation}: {exc}")
        return ToolError(
            f"Network error: Could not connect to NecoKeeper API. "
            f"Please ensure the server is running at the configured URL. "
            f"Details: {exc}"
        )

    # Handle timeout errors
    # Requirements 7.1: User-friendly network error messages
    if isinstance(exc, (httpx.TimeoutException, TimeoutError)):
        logger.error(f"Timeout error while {operation}: {exc}")
        return ToolError(
            f"Network error: Request timed out while {operation}. "
            f"The server may be overloaded or your network connection may be slow. "
            f"Please try again."
        )

    # Handle network errors
    # Requirements 7.1: User-friendly network error messages
    if isinstance(exc, (httpx.NetworkError, ConnectionError)):
        logger.error(f"Network error while {operation}: {exc}")
        return ToolError(
            f"Network error: Communication with NecoKeeper API failed. "
            f"Please check your network connection. Details: {exc}"
        )

    # Handle permission errors (authentication/authorization)
    # Requirements 6.3, 7.3: Authentication errors are clear
    if isinstance(exc, PermissionError):
        logger.error(f"Permission error while {operation}: {exc}")
        return ToolError(
            f"Authentication error: {exc}. "
            f"Please check your AUTOMATION_API_KEY environment variable."
        )

    # Handle validation errors
    # Requirements 7.2: Specific validation error details
    if isinstance(exc, ValueError):
        logger.error(f"Validation error while {operation}: {exc}")
        return ToolError(f"Validation error: {exc}")

    # Handle file not found errors
    if isinstance(exc, FileNotFoundError):
        logger.error(f"File not found while {operation}: {exc}")
        return ToolError(f"File error: {exc}")

    # Handle file system errors
    if isinstance(exc, OSError):
        logger.error(f"File system error while {operation}: {exc}", exc_info=True)
        return ToolError(
            f"File system error: {exc}. Please check file permissions and disk space."
        )

    # Handle unexpected errors
    # Requirements 7.4: Log full error and return generic message
    logger.error(f"Unexpected error while {operation}: {exc}", exc_info=True)
    return ToolError(
        f"Unexpected error occurred while {operation}. "
        f"Please check server logs for details. Error type: {type(exc).__name__}"
    )


async def with_error_handling(operation: str, func: Callable[[], Any]) -> Any:
    """
    Execute a function with centralized error handling

    Wraps an async function call with error handling, converting
    exceptions to ToolError with user-friendly messages.

    Args:
        operation: Description of the operation (e.g., "registering cat")
        func: Async function to execute

    Returns:
        The result of the function call

    Raises:
        ToolError: If an error occurs during execution

    Requirements 7.1, 7.2, 7.3, 7.4, 7.5: Centralized error handling

    Example:
        >>> result = await with_error_handling(
        ...     "registering cat", lambda: api_client.create_animal(data)
        ... )
    """
    try:
        return await func()
    except Exception as e:
        raise handle_api_error(e, operation) from e


def validate_positive_integer(value: int, field_name: str) -> None:
    """
    Validate that a value is a positive integer

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Raises:
        ToolError: If validation fails

    Requirements 7.2: Specific validation error details

    Example:
        >>> validate_positive_integer(42, "animal_id")  # OK
        >>> validate_positive_integer(-1, "animal_id")  # Raises ToolError
    """
    if not isinstance(value, int):
        raise ToolError(
            f"Validation error: {field_name} must be an integer. "
            f"Got: {type(value).__name__}"
        )

    if value <= 0:
        raise ToolError(
            f"Validation error: {field_name} must be a positive integer. Got: {value}"
        )


def validate_non_empty_string(value: str, field_name: str) -> None:
    """
    Validate that a string is not empty

    Args:
        value: Value to validate
        field_name: Name of the field for error messages

    Raises:
        ToolError: If validation fails

    Requirements 7.2: Specific validation error details

    Example:
        >>> validate_non_empty_string("test", "name")  # OK
        >>> validate_non_empty_string("", "name")  # Raises ToolError
    """
    if not isinstance(value, str):
        raise ToolError(
            f"Validation error: {field_name} must be a string. "
            f"Got: {type(value).__name__}"
        )

    if not value or not value.strip():
        raise ToolError(
            f"Validation error: {field_name} cannot be empty. "
            f"Please provide a valid value."
        )
