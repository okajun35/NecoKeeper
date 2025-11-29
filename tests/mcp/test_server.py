"""
Tests for MCP Server

This module tests the main MCP server initialization, tool registration,
and configuration validation.

Requirements: 4.1, 4.3, 4.4, 4.5
"""

from __future__ import annotations

from unittest.mock import patch

import pytest

from app.mcp.server import MCPServer


class TestMCPServer:
    """Test suite for MCPServer class"""

    def test_server_initialization_success(self, monkeypatch):
        """
        Test successful server initialization with valid configuration

        Requirements 4.1, 4.3: Server initializes and registers tools
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Initialize server
        server = MCPServer()

        # Verify server attributes
        assert server.config is not None
        assert server.api_client is not None
        assert server.mcp is not None
        assert server.mcp.name == "NecoKeeper MCP Server"

    def test_server_initialization_missing_api_key(self, monkeypatch):
        """
        Test server initialization fails with missing API key

        Requirements 4.5: Fail fast with clear error messages
        """
        # Set up environment without API key
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        # Verify initialization fails
        with pytest.raises(ValueError) as exc_info:
            MCPServer()

        assert "AUTOMATION_API_KEY is required" in str(exc_info.value)

    def test_server_initialization_short_api_key(self, monkeypatch):
        """
        Test server initialization fails with short API key

        Requirements 4.5: Validate API key length
        """
        # Set up environment with short API key
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "short")

        # Verify initialization fails
        with pytest.raises(ValueError) as exc_info:
            MCPServer()

        assert "must be at least 32 characters" in str(exc_info.value)

    def test_tools_registered(self, monkeypatch):
        """
        Test that all three tools are registered

        Requirements 4.3, 4.4: Register all three tools

        Note: We verify tool registration by checking that the registration
        functions are called during server initialization. The actual tool
        list is only accessible via the MCP client protocol.
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Mock the tool registration functions to verify they're called
        with (
            patch("app.mcp.server.register_cat_tool") as mock_register_cat,
            patch("app.mcp.server.register_qr_tool") as mock_register_qr,
            patch("app.mcp.server.register_upload_tool") as mock_register_upload,
        ):
            # Initialize server
            server = MCPServer()

            # Verify all three registration functions were called
            mock_register_cat.assert_called_once()
            mock_register_qr.assert_called_once()
            mock_register_upload.assert_called_once()

            # Verify they were called with the correct arguments
            assert mock_register_cat.call_args[0][0] == server.mcp
            assert mock_register_cat.call_args[0][1] == server.api_client

    def test_server_run_with_stdio_transport(self, monkeypatch):
        """
        Test server run method uses stdio transport

        Requirements 4.1: Configure stdio transport
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Initialize server
        server = MCPServer()

        # Mock the mcp.run method
        with patch.object(server.mcp, "run") as mock_run:
            # Call run
            server.run()

            # Verify run was called with stdio transport
            mock_run.assert_called_once_with(transport="stdio")

    def test_server_run_handles_keyboard_interrupt(self, monkeypatch):
        """
        Test server handles KeyboardInterrupt gracefully
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Initialize server
        server = MCPServer()

        # Mock the mcp.run method to raise KeyboardInterrupt
        with patch.object(server.mcp, "run", side_effect=KeyboardInterrupt):
            # Should not raise exception
            server.run()

    def test_server_run_handles_exception(self, monkeypatch):
        """
        Test server handles unexpected exceptions
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Initialize server
        server = MCPServer()

        # Mock the mcp.run method to raise exception
        with (
            patch.object(server.mcp, "run", side_effect=RuntimeError("Test error")),
            pytest.raises(RuntimeError, match="Test error"),
        ):
            # Should raise the exception
            server.run()

    def test_main_function_success(self, monkeypatch):
        """
        Test main function with valid configuration
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Import main function
        from app.mcp.server import main

        # Mock MCPServer.run to avoid blocking
        with patch("app.mcp.server.MCPServer.run"):
            # Should not raise exception
            main()

    def test_main_function_config_error(self, monkeypatch):
        """
        Test main function exits with code 1 on configuration error
        """
        # Set up invalid environment (missing API key)
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.delenv("AUTOMATION_API_KEY", raising=False)

        # Import main function
        from app.mcp.server import main

        # Should exit with code 1
        with pytest.raises(SystemExit) as exc_info:
            main()

        assert exc_info.value.code == 1

    def test_main_function_unexpected_error(self, monkeypatch):
        """
        Test main function exits with code 1 on unexpected error
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Import main function
        from app.mcp.server import main

        # Mock MCPServer to raise unexpected error
        with patch("app.mcp.server.MCPServer", side_effect=RuntimeError("Test error")):
            # Should exit with code 1
            with pytest.raises(SystemExit) as exc_info:
                main()

            assert exc_info.value.code == 1

    def test_server_instructions(self, monkeypatch):
        """
        Test server has instructions for Claude
        """
        # Set up valid environment
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
        monkeypatch.setenv("AUTOMATION_API_KEY", "a" * 32)

        # Initialize server
        server = MCPServer()

        # Verify instructions are set
        assert server.mcp.instructions is not None
        assert "NecoKeeper MCP Server" in server.mcp.instructions
        assert "register_cat" in server.mcp.instructions
        assert "generate_qr" in server.mcp.instructions
        assert "upload_cat_image" in server.mcp.instructions
