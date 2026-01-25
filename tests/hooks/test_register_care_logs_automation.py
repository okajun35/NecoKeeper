"""
Tests for register_care_logs.py Hook with Automation API

Requirements:
- 8.1: Use /api/automation/care-logs endpoint
- 8.2: Include X-Automation-Key header
- 8.3: Read from AUTOMATION_API_KEY environment variable
- 8.4: Log error and display user-friendly message on authentication failure
- 8.5: Display setup instructions if API Key is not set
"""

from __future__ import annotations

import json
from unittest.mock import Mock, patch

import pytest

from scripts.hooks.register_care_logs import (
    AuthenticationError,
    RegistrationError,
    RegistrationSummary,
    get_api_config,
    load_json_file,
    register_care_log,
    register_care_logs_batch,
    verify_api_key,
)


class TestGetApiConfig:
    """Test API configuration loading"""

    def test_get_api_config_with_valid_key(self, monkeypatch):
        """Test loading API config with valid API Key"""
        # Given
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://test.example.com")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key-12345")

        # When
        config = get_api_config()

        # Then
        assert config["base_url"] == "http://test.example.com"
        assert config["api_key"] == "test-api-key-12345"

    def test_get_api_config_default_url(self, monkeypatch):
        """Test default API URL when not set"""
        # Given
        monkeypatch.delenv("NECOKEEPER_API_URL", raising=False)
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-api-key")

        # When
        config = get_api_config()

        # Then
        assert config["base_url"] == "http://localhost:8000"

    def test_get_api_config_missing_api_key(self, monkeypatch):
        """Test error when API Key is not set (Requirement 8.5)"""
        # Given
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            get_api_config()

        # Verify error message contains setup instructions
        error_msg = str(exc_info.value)
        assert "AUTOMATION_API_KEY" in error_msg
        assert "Setup Instructions" in error_msg
        assert "secrets.token_urlsafe(32)" in error_msg
        assert "ENABLE_AUTOMATION_API=true" in error_msg

    def test_get_api_config_strips_trailing_slash(self, monkeypatch):
        """Test that trailing slash is removed from base URL"""
        # Given
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://test.example.com/")
        monkeypatch.setenv("AUTOMATION_API_KEY", "test-key")

        # When
        config = get_api_config()

        # Then
        assert config["base_url"] == "http://test.example.com"


class TestVerifyApiKey:
    """Test API Key verification"""

    def test_verify_api_key_logs_success(self, caplog):
        """Test that API Key verification logs success"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "test-key"

        # When
        verify_api_key(base_url, api_key)

        # Then
        assert "Verifying Automation API Key" in caplog.text
        assert "API Key configured" in caplog.text


class TestRegisterCareLog:
    """Test single care log registration via Automation API"""

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_success(self, mock_post):
        """Test successful care log registration (Requirement 8.1, 8.2)"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "test-api-key-12345"
        care_log_data = {
            "animal_id": 1,
            "log_date": "2025-11-24",
            "time_slot": "morning",
            "appetite": 1.0,
            "energy": 5,
        }

        mock_response = Mock()
        mock_response.status_code = 201
        mock_response.json.return_value = {"id": 123, **care_log_data}
        mock_post.return_value = mock_response

        # When
        result = register_care_log(base_url, api_key, care_log_data)

        # Then
        assert result["id"] == 123
        assert result["animal_id"] == 1

        # Verify correct endpoint was called (Requirement 8.1)
        mock_post.assert_called_once()
        call_args = mock_post.call_args
        assert call_args[0][0] == "http://localhost:8000/api/automation/care-logs"

        # Verify X-Automation-Key header was sent (Requirement 8.2)
        headers = call_args[1]["headers"]
        assert headers["X-Automation-Key"] == "test-api-key-12345"
        assert headers["Content-Type"] == "application/json"

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_401_unauthorized(self, mock_post):
        """Test 401 Unauthorized error (Requirement 8.4)"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "invalid-key"
        care_log_data = {"animal_id": 1}

        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.json.return_value = {
            "detail": "X-Automation-Key header is required"
        }
        mock_post.return_value = mock_response

        # When/Then
        with pytest.raises(AuthenticationError) as exc_info:
            register_care_log(base_url, api_key, care_log_data)

        error_msg = str(exc_info.value)
        assert "Authentication failed" in error_msg
        assert "AUTOMATION_API_KEY" in error_msg

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_403_forbidden(self, mock_post):
        """Test 403 Forbidden error (Requirement 8.4)"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "invalid-key"
        care_log_data = {"animal_id": 1}

        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.json.return_value = {"detail": "Invalid Automation API Key"}
        mock_post.return_value = mock_response

        # When/Then
        with pytest.raises(AuthenticationError) as exc_info:
            register_care_log(base_url, api_key, care_log_data)

        error_msg = str(exc_info.value)
        assert "Authentication failed" in error_msg
        assert "API Key is invalid" in error_msg

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_503_service_unavailable(self, mock_post):
        """Test 503 Service Unavailable error (Requirement 8.4)"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "test-key"
        care_log_data = {"animal_id": 1}

        mock_response = Mock()
        mock_response.status_code = 503
        mock_response.json.return_value = {"detail": "Automation API is disabled"}
        mock_post.return_value = mock_response

        # When/Then
        with pytest.raises(AuthenticationError) as exc_info:
            register_care_log(base_url, api_key, care_log_data)

        error_msg = str(exc_info.value)
        assert "Service unavailable" in error_msg
        assert "ENABLE_AUTOMATION_API=true" in error_msg

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_400_bad_request(self, mock_post):
        """Test 400 Bad Request error"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "test-key"
        care_log_data = {"invalid": "data"}

        mock_response = Mock()
        mock_response.status_code = 400
        mock_response.json.return_value = {"detail": "Invalid data"}
        mock_post.return_value = mock_response

        # When/Then
        with pytest.raises(RegistrationError) as exc_info:
            register_care_log(base_url, api_key, care_log_data)

        assert "Registration failed" in str(exc_info.value)
        assert "400" in str(exc_info.value)

    @patch("scripts.hooks.register_care_logs.requests.post")
    def test_register_care_log_network_error(self, mock_post):
        """Test network error handling"""
        # Given
        base_url = "http://localhost:8000"
        api_key = "test-key"
        care_log_data = {"animal_id": 1}

        import requests

        mock_post.side_effect = requests.exceptions.RequestException(
            "Connection refused"
        )

        # When/Then
        with pytest.raises(RegistrationError) as exc_info:
            register_care_log(base_url, api_key, care_log_data)

        assert "Network error" in str(exc_info.value)


class TestRegisterCareLogsBatch:
    """Test batch registration via Automation API"""

    @patch("scripts.hooks.register_care_logs.register_care_log")
    @patch("scripts.hooks.register_care_logs.verify_api_key")
    def test_batch_registration_all_success(self, mock_verify, mock_register, caplog):
        """Test successful batch registration"""
        # Given
        care_logs = [
            {"animal_id": 1, "log_date": "2025-11-24", "time_slot": "morning"},
            {"animal_id": 2, "log_date": "2025-11-24", "time_slot": "afternoon"},
        ]
        api_base_url = "http://localhost:8000"
        api_key = "test-key"

        mock_register.side_effect = [
            {"id": 1, "animal_id": 1},
            {"id": 2, "animal_id": 2},
        ]

        # When
        result = register_care_logs_batch(care_logs, api_base_url, api_key)

        # Then
        assert result["status"] == "success"
        assert result["summary"]["total_records"] == 2
        assert result["summary"]["successful"] == 2
        assert result["summary"]["failed"] == 0
        assert len(result["errors"]) == 0

        # Verify API Key was used
        assert "Using Automation API with API Key authentication" in caplog.text

    @patch("scripts.hooks.register_care_logs.register_care_log")
    @patch("scripts.hooks.register_care_logs.verify_api_key")
    def test_batch_registration_partial_success(self, mock_verify, mock_register):
        """Test batch registration with some failures"""
        # Given
        care_logs = [
            {"animal_id": 1, "log_date": "2025-11-24", "time_slot": "morning"},
            {"animal_id": 999, "log_date": "2025-11-24", "time_slot": "afternoon"},
            {"animal_id": 3, "log_date": "2025-11-24", "time_slot": "evening"},
        ]
        api_base_url = "http://localhost:8000"
        api_key = "test-key"

        mock_register.side_effect = [
            {"id": 1, "animal_id": 1},
            RegistrationError("Animal not found"),
            {"id": 3, "animal_id": 3},
        ]

        # When
        result = register_care_logs_batch(care_logs, api_base_url, api_key)

        # Then
        assert result["status"] == "partial_success"
        assert result["summary"]["total_records"] == 3
        assert result["summary"]["successful"] == 2
        assert result["summary"]["failed"] == 1
        assert len(result["errors"]) == 1
        assert result["errors"][0]["animal_id"] == 999

    @patch("scripts.hooks.register_care_logs.register_care_log")
    @patch("scripts.hooks.register_care_logs.verify_api_key")
    def test_batch_registration_authentication_failure_stops_processing(
        self, mock_verify, mock_register, caplog
    ):
        """Test that authentication failure stops processing remaining records"""
        # Given
        care_logs = [
            {"animal_id": 1, "log_date": "2025-11-24", "time_slot": "morning"},
            {"animal_id": 2, "log_date": "2025-11-24", "time_slot": "afternoon"},
            {"animal_id": 3, "log_date": "2025-11-24", "time_slot": "evening"},
        ]
        api_base_url = "http://localhost:8000"
        api_key = "invalid-key"

        # First record succeeds, second fails with auth error
        mock_register.side_effect = [
            {"id": 1, "animal_id": 1},
            AuthenticationError("Invalid API Key"),
        ]

        # When
        result = register_care_logs_batch(care_logs, api_base_url, api_key)

        # Then
        # Status is partial_success because at least one record succeeded
        assert result["status"] == "partial_success"
        assert result["summary"]["total_records"] == 3
        assert result["summary"]["successful"] == 1
        assert result["summary"]["failed"] == 2

        # Verify remaining records were marked as failed
        assert len(result["errors"]) == 2
        assert result["errors"][0]["animal_id"] == 2
        assert result["errors"][0]["error_type"] == "authentication_error"
        assert result["errors"][1]["animal_id"] == 3
        assert result["errors"][1]["error_type"] == "authentication_error"
        assert (
            "Skipped due to authentication failure"
            in result["errors"][1]["error_message"]
        )

        # Verify error message in logs
        assert "Authentication failed" in caplog.text
        assert "AUTOMATION_API_KEY" in caplog.text

    @patch("scripts.hooks.register_care_logs.verify_api_key")
    def test_batch_registration_verification_failure(self, mock_verify, caplog):
        """Test that verification failure marks all records as failed"""
        # Given
        care_logs = [
            {"animal_id": 1, "log_date": "2025-11-24", "time_slot": "morning"},
        ]
        api_base_url = "http://localhost:8000"
        api_key = "invalid-key"

        mock_verify.side_effect = AuthenticationError("API Key verification failed")

        # When
        result = register_care_logs_batch(care_logs, api_base_url, api_key)

        # Then
        assert result["status"] == "failed"
        assert result["summary"]["successful"] == 0
        assert result["summary"]["failed"] == 1
        assert "API Key verification failed" in caplog.text


class TestLoadJsonFile:
    """Test JSON file loading"""

    def test_load_json_file_success(self, tmp_path):
        """Test loading valid JSON file"""
        # Given
        json_file = tmp_path / "test.json"
        test_data = [
            {"animal_id": 1, "log_date": "2025-11-24"},
            {"animal_id": 2, "log_date": "2025-11-25"},
        ]
        json_file.write_text(json.dumps(test_data), encoding="utf-8")

        # When
        result = load_json_file(str(json_file))

        # Then
        assert len(result) == 2
        assert result[0]["animal_id"] == 1

    def test_load_json_file_not_found(self):
        """Test error when file does not exist"""
        # When/Then
        with pytest.raises(FileNotFoundError):
            load_json_file("nonexistent.json")

    def test_load_json_file_invalid_json(self, tmp_path):
        """Test error when JSON is invalid"""
        # Given
        json_file = tmp_path / "invalid.json"
        json_file.write_text("{ invalid json }", encoding="utf-8")

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            load_json_file(str(json_file))

        assert "Invalid JSON format" in str(exc_info.value)

    def test_load_json_file_not_array(self, tmp_path):
        """Test error when JSON is not an array"""
        # Given
        json_file = tmp_path / "object.json"
        json_file.write_text('{"key": "value"}', encoding="utf-8")

        # When/Then
        with pytest.raises(ValueError) as exc_info:
            load_json_file(str(json_file))

        assert "must be an array" in str(exc_info.value)


class TestRegistrationSummary:
    """Test RegistrationSummary class"""

    def test_summary_all_success(self):
        """Test summary with all successful registrations"""
        # Given
        summary = RegistrationSummary()
        summary.total_records = 3

        # When
        summary.add_success()
        summary.add_success()
        summary.add_success()

        # Then
        result = summary.to_dict()
        assert result["status"] == "success"
        assert result["summary"]["successful"] == 3
        assert result["summary"]["failed"] == 0

    def test_summary_partial_success(self):
        """Test summary with partial success"""
        # Given
        summary = RegistrationSummary()
        summary.total_records = 3

        # When
        summary.add_success()
        summary.add_failure(
            record_index=1,
            record={"animal_id": 2},
            error_message="Error",
            error_type="test_error",
        )
        summary.add_success()

        # Then
        result = summary.to_dict()
        assert result["status"] == "partial_success"
        assert result["summary"]["successful"] == 2
        assert result["summary"]["failed"] == 1

    def test_summary_all_failed(self):
        """Test summary with all failed registrations"""
        # Given
        summary = RegistrationSummary()
        summary.total_records = 2

        # When
        summary.add_failure(
            record_index=0, record={"animal_id": 1}, error_message="Error 1"
        )
        summary.add_failure(
            record_index=1, record={"animal_id": 2}, error_message="Error 2"
        )

        # Then
        result = summary.to_dict()
        assert result["status"] == "failed"
        assert result["summary"]["successful"] == 0
        assert result["summary"]["failed"] == 2
