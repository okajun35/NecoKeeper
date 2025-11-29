"""
Tests for MCP Server Configuration

This module tests the MCPConfig class to ensure proper validation
of environment variables and configuration settings.
"""

from __future__ import annotations

import secrets
from typing import Any

import pytest

from app.mcp.config import MCPConfig


class TestMCPConfig:
    """Test suite for MCPConfig class."""

    def test_config_requires_automation_api_key(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig raises ValueError when AUTOMATION_API_KEY is missing.

        Validates: Requirements 4.5, 6.2, 6.5
        """
        # Remove AUTOMATION_API_KEY if it exists
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        with pytest.raises(ValueError, match="AUTOMATION_API_KEY is required"):
            MCPConfig()

    def test_config_validates_api_key_length(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig validates API key length (minimum 32 characters).

        Validates: Requirements 6.4
        """
        # Set a short API key
        monkeypatch.setenv("AUTOMATION_API_KEY", "short-key")

        with pytest.raises(
            ValueError, match="AUTOMATION_API_KEY must be at least 32 characters"
        ):
            MCPConfig()

    def test_config_with_valid_api_key(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig successfully initializes with valid API key.

        Validates: Requirements 4.2, 6.2
        """
        # Generate a valid API key
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")

        config = MCPConfig()

        assert config.api_key == api_key
        assert config.api_url == "http://localhost:8000"
        assert config.log_level == "INFO"
        assert config.log_file == "logs/mcp-server.log"

    def test_config_uses_default_values(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig uses default values for optional settings.

        Validates: Requirements 4.2
        """
        # Set only required environment variables
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)

        config = MCPConfig()

        # Check default values
        assert config.api_url == "http://localhost:8000"
        assert config.log_level == "INFO"
        assert config.log_file == "logs/mcp-server.log"

    def test_config_respects_custom_values(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig respects custom environment variable values.

        Validates: Requirements 4.2
        """
        # Set custom environment variables
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)
        monkeypatch.setenv("NECOKEEPER_API_URL", "https://api.example.com")
        monkeypatch.setenv("MCP_LOG_LEVEL", "DEBUG")
        monkeypatch.setenv("MCP_LOG_FILE", "/var/log/mcp.log")

        config = MCPConfig()

        assert config.api_url == "https://api.example.com"
        assert config.log_level == "DEBUG"
        assert config.log_file == "/var/log/mcp.log"

    def test_config_validates_log_level(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig validates log level values.

        Validates: Requirements 4.2
        """
        # Set invalid log level
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)
        monkeypatch.setenv("MCP_LOG_LEVEL", "INVALID")

        with pytest.raises(ValueError, match="MCP_LOG_LEVEL must be one of"):
            MCPConfig()

    def test_config_repr_masks_api_key(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig.__repr__ masks the API key for security.

        Validates: Security best practices
        """
        # Set environment variables
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)

        config = MCPConfig()
        repr_str = repr(config)

        # Check that API key is masked
        assert api_key not in repr_str
        assert "..." in repr_str
        assert api_key[:8] in repr_str

    def test_config_validates_api_url_required(self, monkeypatch: Any) -> None:
        """
        Test that MCPConfig validates NECOKEEPER_API_URL is not empty.

        Validates: Requirements 4.2
        """
        # Set empty API URL
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)
        monkeypatch.setenv("NECOKEEPER_API_URL", "")

        with pytest.raises(ValueError, match="NECOKEEPER_API_URL is required"):
            MCPConfig()
