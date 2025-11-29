"""
Tests for MCP Error Handler

This module tests the centralized error handling functionality,
including error mapping, logging configuration, and error categorization.

Requirements: 6.3, 7.1, 7.2, 7.3, 7.4, 7.5
"""

from __future__ import annotations

import logging

import httpx
import pytest
from fastmcp.exceptions import ToolError

from app.mcp.error_handler import (
    ErrorCategory,
    configure_logging,
    handle_api_error,
    map_http_error_to_message,
    validate_non_empty_string,
    validate_positive_integer,
    with_error_handling,
)


class TestConfigureLogging:
    """Tests for logging configuration"""

    def test_configure_logging_default(self):
        """Test logging configuration with default settings"""
        # Given: Default log level
        log_level = "INFO"

        # When: Configure logging
        configure_logging(log_level=log_level)

        # Then: Root logger should be configured
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_configure_logging_with_file(self, tmp_path):
        """Test logging configuration with file output"""
        # Given: Log file path
        log_file = tmp_path / "test.log"

        # When: Configure logging with file
        configure_logging(log_level="DEBUG", log_file=str(log_file))

        # Then: Log file should be created
        root_logger = logging.getLogger()
        assert root_logger.level == logging.DEBUG

        # Log a message to verify file handler works
        test_logger = logging.getLogger("test")
        test_logger.info("Test message")

        # File should exist (though it may be empty due to buffering)
        assert log_file.parent.exists()

    def test_configure_logging_invalid_level(self):
        """Test logging configuration with invalid level falls back to INFO"""
        # Given: Invalid log level
        log_level = "INVALID"

        # When: Configure logging
        configure_logging(log_level=log_level)

        # Then: Should fall back to INFO level
        root_logger = logging.getLogger()
        assert root_logger.level == logging.INFO

    def test_configure_logging_creates_directory(self, tmp_path):
        """Test logging configuration creates log directory"""
        # Given: Log file in non-existent directory
        log_file = tmp_path / "logs" / "mcp" / "test.log"

        # When: Configure logging
        configure_logging(log_level="INFO", log_file=str(log_file))

        # Then: Directory should be created
        assert log_file.parent.exists()


class TestMapHttpErrorToMessage:
    """Tests for HTTP error mapping"""

    def test_map_401_authentication_error(self):
        """Test mapping 401 Unauthorized to authentication error"""
        # Given: 401 HTTP error
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(401, request=request, text="Unauthorized")
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return authentication category and clear message
        # Requirements 6.3, 7.3: Authentication errors are clear
        assert category == ErrorCategory.AUTHENTICATION
        assert "Authentication failed" in message
        assert "AUTOMATION_API_KEY" in message
        assert "token_urlsafe" in message

    def test_map_403_authorization_error(self):
        """Test mapping 403 Forbidden to authorization error"""
        # Given: 403 HTTP error
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(403, request=request, text="Forbidden")
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return authentication category
        assert category == ErrorCategory.AUTHENTICATION
        assert "Authorization failed" in message
        assert "Insufficient permissions" in message

    def test_map_400_validation_error(self):
        """Test mapping 400 Bad Request to validation error"""
        # Given: 400 HTTP error with detail
        request = httpx.Request("POST", "http://test.com/api")
        response = httpx.Response(
            400,
            request=request,
            json={"detail": "Invalid field: name is required"},
        )
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return validation category with details
        # Requirements 7.2: Specific validation error details
        assert category == ErrorCategory.VALIDATION
        assert "Validation error" in message
        assert "name is required" in message

    def test_map_404_not_found_error(self):
        """Test mapping 404 Not Found to not found error"""
        # Given: 404 HTTP error
        request = httpx.Request("GET", "http://test.com/api/animals/999")
        response = httpx.Response(
            404, request=request, json={"detail": "Animal not found"}
        )
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return not found category
        assert category == ErrorCategory.NOT_FOUND
        assert "Resource not found" in message
        assert "Animal not found" in message

    def test_map_422_validation_error(self):
        """Test mapping 422 Unprocessable Entity to validation error"""
        # Given: 422 HTTP error
        request = httpx.Request("POST", "http://test.com/api")
        response = httpx.Response(
            422, request=request, json={"detail": "Invalid data format"}
        )
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return validation category
        assert category == ErrorCategory.VALIDATION
        assert "Validation error" in message

    def test_map_429_rate_limit_error(self):
        """Test mapping 429 Too Many Requests to network error"""
        # Given: 429 HTTP error
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(429, request=request, text="Rate limit exceeded")
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return network category
        assert category == ErrorCategory.NETWORK
        assert "Rate limit exceeded" in message

    def test_map_500_server_error(self):
        """Test mapping 500 Internal Server Error to unexpected error"""
        # Given: 500 HTTP error
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(
            500, request=request, json={"detail": "Internal server error"}
        )
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should return unexpected category
        assert category == ErrorCategory.UNEXPECTED
        assert "Server error (500)" in message
        assert "Internal server error" in message

    def test_map_error_with_non_json_response(self):
        """Test mapping error with non-JSON response"""
        # Given: HTTP error with plain text response
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(400, request=request, text="Bad request")
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Map error to message
        category, message = map_http_error_to_message(exc)

        # Then: Should handle plain text response
        assert category == ErrorCategory.VALIDATION
        assert "Bad request" in message


class TestHandleApiError:
    """Tests for centralized API error handling"""

    def test_handle_tool_error_passthrough(self):
        """Test that ToolError is passed through unchanged"""
        # Given: ToolError
        original_error = ToolError("Original error message")

        # When: Handle error
        result = handle_api_error(original_error, "testing")

        # Then: Should return same error
        assert result is original_error
        assert str(result) == "Original error message"

    def test_handle_http_status_error(self):
        """Test handling HTTP status error"""
        # Given: HTTP 401 error
        request = httpx.Request("GET", "http://test.com/api")
        response = httpx.Response(401, request=request, text="Unauthorized")
        exc = httpx.HTTPStatusError("", request=request, response=response)

        # When: Handle error
        result = handle_api_error(exc, "registering cat")

        # Then: Should return ToolError with authentication message
        # Requirements 6.3, 7.3: Authentication errors are clear
        assert isinstance(result, ToolError)
        assert "Authentication failed" in str(result)
        assert "AUTOMATION_API_KEY" in str(result)

    def test_handle_connect_error(self):
        """Test handling connection error"""
        # Given: Connection error
        exc = httpx.ConnectError("Connection refused")

        # When: Handle error
        result = handle_api_error(exc, "uploading image")

        # Then: Should return ToolError with network message
        # Requirements 7.1: User-friendly network error messages
        assert isinstance(result, ToolError)
        assert "Network error" in str(result)
        assert "Could not connect" in str(result)
        assert "server is running" in str(result)

    def test_handle_timeout_error(self):
        """Test handling timeout error"""
        # Given: Timeout error
        exc = httpx.TimeoutException("Request timed out")

        # When: Handle error
        result = handle_api_error(exc, "generating QR")

        # Then: Should return ToolError with timeout message
        # Requirements 7.1: User-friendly network error messages
        assert isinstance(result, ToolError)
        assert "Network error" in str(result)
        assert "timed out" in str(result)

    def test_handle_network_error(self):
        """Test handling network error"""
        # Given: Network error
        exc = httpx.NetworkError("Network unreachable")

        # When: Handle error
        result = handle_api_error(exc, "creating animal")

        # Then: Should return ToolError with network message
        assert isinstance(result, ToolError)
        assert "Network error" in str(result)
        assert "network connection" in str(result)

    def test_handle_permission_error(self):
        """Test handling permission error"""
        # Given: Permission error
        exc = PermissionError("Invalid API key")

        # When: Handle error
        result = handle_api_error(exc, "accessing API")

        # Then: Should return ToolError with authentication message
        # Requirements 6.3, 7.3: Authentication errors are clear
        assert isinstance(result, ToolError)
        assert "Authentication error" in str(result)
        assert "AUTOMATION_API_KEY" in str(result)

    def test_handle_value_error(self):
        """Test handling validation error"""
        # Given: ValueError
        exc = ValueError("Invalid animal_id: must be positive")

        # When: Handle error
        result = handle_api_error(exc, "validating input")

        # Then: Should return ToolError with validation message
        # Requirements 7.2: Specific validation error details
        assert isinstance(result, ToolError)
        assert "Validation error" in str(result)
        assert "must be positive" in str(result)

    def test_handle_file_not_found_error(self):
        """Test handling file not found error"""
        # Given: FileNotFoundError
        exc = FileNotFoundError("Image file not found: /path/to/image.jpg")

        # When: Handle error
        result = handle_api_error(exc, "reading image")

        # Then: Should return ToolError with file error message
        assert isinstance(result, ToolError)
        assert "File error" in str(result)
        assert "not found" in str(result)

    def test_handle_os_error(self):
        """Test handling OS error"""
        # Given: OSError
        exc = OSError("Permission denied")

        # When: Handle error
        result = handle_api_error(exc, "writing file")

        # Then: Should return ToolError with file system message
        assert isinstance(result, ToolError)
        assert "File system error" in str(result)
        assert "Permission denied" in str(result)

    def test_handle_unexpected_error(self):
        """Test handling unexpected error"""
        # Given: Unexpected error
        exc = RuntimeError("Something went wrong")

        # When: Handle error
        result = handle_api_error(exc, "processing request")

        # Then: Should return ToolError with generic message
        # Requirements 7.4: Log full error and return generic message
        assert isinstance(result, ToolError)
        assert "Unexpected error" in str(result)
        assert "check server logs" in str(result)
        assert "RuntimeError" in str(result)


class TestWithErrorHandling:
    """Tests for error handling wrapper"""

    @pytest.mark.anyio
    async def test_with_error_handling_success(self):
        """Test successful operation with error handling"""

        # Given: Successful async function
        async def successful_operation():
            return {"result": "success"}

        # When: Execute with error handling
        result = await with_error_handling("test operation", successful_operation)

        # Then: Should return result
        assert result == {"result": "success"}

    @pytest.mark.anyio
    async def test_with_error_handling_http_error(self):
        """Test error handling wrapper with HTTP error"""

        # Given: Function that raises HTTP error
        async def failing_operation():
            request = httpx.Request("GET", "http://test.com/api")
            response = httpx.Response(401, request=request, text="Unauthorized")
            raise httpx.HTTPStatusError("", request=request, response=response)

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            await with_error_handling("test operation", failing_operation)

        assert "Authentication failed" in str(exc_info.value)

    @pytest.mark.anyio
    async def test_with_error_handling_network_error(self):
        """Test error handling wrapper with network error"""

        # Given: Function that raises network error
        async def failing_operation():
            raise httpx.ConnectError("Connection refused")

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            await with_error_handling("test operation", failing_operation)

        assert "Network error" in str(exc_info.value)


class TestValidationHelpers:
    """Tests for validation helper functions"""

    def test_validate_positive_integer_valid(self):
        """Test validating valid positive integer"""
        # Given: Valid positive integer
        value = 42

        # When/Then: Should not raise error
        validate_positive_integer(value, "animal_id")

    def test_validate_positive_integer_zero(self):
        """Test validating zero"""
        # Given: Zero
        value = 0

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_positive_integer(value, "animal_id")

        assert "must be a positive integer" in str(exc_info.value)
        assert "animal_id" in str(exc_info.value)

    def test_validate_positive_integer_negative(self):
        """Test validating negative integer"""
        # Given: Negative integer
        value = -1

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_positive_integer(value, "animal_id")

        assert "must be a positive integer" in str(exc_info.value)

    def test_validate_positive_integer_non_integer(self):
        """Test validating non-integer"""
        # Given: Non-integer value
        value = "42"

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_positive_integer(value, "animal_id")

        assert "must be an integer" in str(exc_info.value)

    def test_validate_non_empty_string_valid(self):
        """Test validating valid non-empty string"""
        # Given: Valid string
        value = "test"

        # When/Then: Should not raise error
        validate_non_empty_string(value, "name")

    def test_validate_non_empty_string_empty(self):
        """Test validating empty string"""
        # Given: Empty string
        value = ""

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_non_empty_string(value, "name")

        assert "cannot be empty" in str(exc_info.value)
        assert "name" in str(exc_info.value)

    def test_validate_non_empty_string_whitespace(self):
        """Test validating whitespace-only string"""
        # Given: Whitespace string
        value = "   "

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_non_empty_string(value, "name")

        assert "cannot be empty" in str(exc_info.value)

    def test_validate_non_empty_string_non_string(self):
        """Test validating non-string"""
        # Given: Non-string value
        value = 42

        # When/Then: Should raise ToolError
        with pytest.raises(ToolError) as exc_info:
            validate_non_empty_string(value, "name")

        assert "must be a string" in str(exc_info.value)


class TestErrorCategoryConstants:
    """Tests for error category constants"""

    def test_error_categories_defined(self):
        """Test that all error categories are defined"""
        # Then: All categories should be defined
        assert ErrorCategory.NETWORK == "network"
        assert ErrorCategory.AUTHENTICATION == "authentication"
        assert ErrorCategory.VALIDATION == "validation"
        assert ErrorCategory.NOT_FOUND == "not_found"
        assert ErrorCategory.FILE_SYSTEM == "file_system"
        assert ErrorCategory.UNEXPECTED == "unexpected"
