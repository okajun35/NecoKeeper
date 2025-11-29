"""
MCP Server Configuration Module

This module handles configuration validation for the MCP server,
ensuring all required environment variables are present and valid.

Context7 Reference: /jlowin/fastmcp - Environment variable configuration patterns
"""

from __future__ import annotations

import os


class MCPConfig:
    """
    MCP Server configuration with environment variable validation.

    This class reads and validates configuration from environment variables,
    ensuring the MCP server has all required settings before startup.

    Attributes:
        api_url: Base URL for the NecoKeeper API
        api_key: Automation API key for authentication
        log_level: Logging level (INFO, DEBUG, WARNING, ERROR)
        log_file: Path to log file

    Raises:
        ValueError: If required configuration is missing or invalid
    """

    def __init__(self) -> None:
        """
        Initialize configuration from environment variables.

        Reads configuration from environment and validates required fields.
        """
        self.api_url: str = os.getenv("NECOKEEPER_API_URL", "http://localhost:8000")
        api_key_raw: str | None = os.getenv("AUTOMATION_API_KEY")
        self.log_level: str = os.getenv("MCP_LOG_LEVEL", "INFO")
        self.log_file: str = os.getenv("MCP_LOG_FILE", "logs/mcp-server.log")

        self._validate(api_key_raw)
        # After validation, api_key is guaranteed to be str
        self.api_key: str = api_key_raw  # type: ignore[assignment]

    def _validate(self, api_key_raw: str | None) -> None:
        """
        Validate required configuration.

        Ensures all required environment variables are present and valid.

        Args:
            api_key_raw: Raw API key from environment (may be None)

        Raises:
            ValueError: If required configuration is missing or invalid
        """
        if not self.api_url:
            raise ValueError(
                "NECOKEEPER_API_URL is required. "
                "Set it to your NecoKeeper API base URL (e.g., http://localhost:8000)"
            )

        if not api_key_raw:
            raise ValueError(
                "AUTOMATION_API_KEY is required. "
                'Generate one with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

        # Validate API key length (should be at least 32 characters for security)
        if len(api_key_raw) < 32:
            raise ValueError(
                "AUTOMATION_API_KEY must be at least 32 characters for security. "
                'Generate a secure key with: python -c "import secrets; print(secrets.token_urlsafe(32))"'
            )

        # Validate log level
        valid_log_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        if self.log_level.upper() not in valid_log_levels:
            raise ValueError(
                f"MCP_LOG_LEVEL must be one of {valid_log_levels}. Got: {self.log_level}"
            )

    def __repr__(self) -> str:
        """
        Return string representation of configuration.

        Returns:
            String representation with masked API key
        """
        masked_key = f"{self.api_key[:8]}..." if self.api_key else "None"
        return (
            f"MCPConfig(api_url={self.api_url!r}, "
            f"api_key={masked_key!r}, "
            f"log_level={self.log_level!r}, "
            f"log_file={self.log_file!r})"
        )
