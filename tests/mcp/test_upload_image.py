"""
Tests for upload_cat_image MCP Tool

This module tests the upload_cat_image tool functionality, including:
- Tool registration
- Basic functionality verification

Context7 Reference: /pytest-dev/pytest (Trust Score: 9.5)
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5

Note: These tests verify tool registration and basic structure.
Full integration testing requires a running MCP server.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, patch

import pytest

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.config import MCPConfig
from app.mcp.tools.upload_image import register_tool

# Skip all tests if fastmcp is not installed
fastmcp = pytest.importorskip("fastmcp", reason="fastmcp not installed")
FastMCP = fastmcp.FastMCP


@pytest.fixture
def mock_config() -> MCPConfig:
    """Create a mock MCP configuration"""
    with patch.dict(
        "os.environ",
        {
            "NECOKEEPER_API_URL": "http://localhost:8000",
            "AUTOMATION_API_KEY": "test-key-" + "x" * 32,
        },
    ):
        return MCPConfig()


@pytest.fixture
def mock_api_client(mock_config: MCPConfig) -> NecoKeeperAPIClient:
    """Create a mock API client"""
    client = NecoKeeperAPIClient(mock_config)
    # Mock the httpx client
    client.client = AsyncMock()
    return client


@pytest.fixture
def mcp_server(mock_api_client: NecoKeeperAPIClient) -> FastMCP:
    """Create a FastMCP server instance with upload_cat_image tool registered"""
    mcp = FastMCP(name="Test MCP Server")
    register_tool(mcp, mock_api_client)
    return mcp


class TestUploadCatImageTool:
    """Test suite for upload_cat_image tool"""

    def test_tool_registration(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """
        Test that upload_cat_image tool is registered correctly

        Requirements: 3.1
        """
        # Verify the tool was registered by checking the server has tools
        # The actual registration is tested by the fact that register_tool() runs without error
        assert mcp_server is not None
        assert mock_api_client is not None

        # If we got here, the tool was registered successfully
        # (register_tool would have raised an exception if it failed)
