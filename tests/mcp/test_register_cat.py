"""
Tests for register_cat MCP Tool

This module tests the register_cat tool implementation, including
successful registration, validation errors, and error handling.

Context7 Reference: /pytest-dev/pytest (Trust Score: 9.5)
Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
Requirements: 1.1, 1.2, 1.3, 1.4

Note: These tests use pytest.importorskip to skip if fastmcp is not installed.
FastMCP is an optional dependency for MCP server functionality.
"""

from __future__ import annotations

from unittest.mock import AsyncMock, MagicMock

import pytest

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.tools.register_cat import register_tool

# Skip all tests if fastmcp is not installed
fastmcp = pytest.importorskip("fastmcp", reason="fastmcp not installed")
FastMCP = fastmcp.FastMCP
Client = fastmcp.Client
ToolError = fastmcp.exceptions.ToolError


@pytest.fixture
def mock_api_client() -> AsyncMock:
    """Create a mock API client for testing"""
    client = AsyncMock(spec=NecoKeeperAPIClient)
    client.config = MagicMock()
    client.config.api_url = "http://localhost:8000"
    return client


@pytest.fixture
def mcp_server(mock_api_client: AsyncMock) -> FastMCP:
    """Create a FastMCP server with register_cat tool registered"""
    mcp = FastMCP(name="TestServer")
    register_tool(mcp, mock_api_client)
    return mcp


class TestRegisterCatTool:
    """Test suite for register_cat tool"""

    @pytest.mark.asyncio
    async def test_register_cat_success(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test successful cat registration. Requirements: 1.1, 1.2, 1.3"""
        mock_api_client.create_animal.return_value = {
            "id": 42,
            "name": "たま",
            "pattern": "キジトラ",
            "tail_length": "長い",
            "age_months": 12,
            "gender": "male",
            "status": "保護中",
            "ear_cut": False,
        }

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "register_cat",
                {
                    "name": "たま",
                    "pattern": "キジトラ",
                    "tail_length": "長い",
                    "age_months": 12,
                    "gender": "male",
                },
            )
            assert result.data["id"] == 42
            assert result.data["name"] == "たま"

        mock_api_client.create_animal.assert_called_once()

    @pytest.mark.asyncio
    async def test_register_cat_with_optional_fields(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with optional fields. Requirements: 1.1, 1.2, 1.3"""
        mock_api_client.create_animal.return_value = {
            "id": 43,
            "name": "みけ",
            "pattern": "三毛",
            "collar": "赤い首輪",
            "ear_cut": True,
        }

        async with Client(mcp_server) as client:
            result = await client.call_tool(
                "register_cat",
                {
                    "name": "みけ",
                    "pattern": "三毛",
                    "tail_length": "短い",
                    "age_months": 6,
                    "gender": "female",
                    "collar": "赤い首輪",
                    "ear_cut": True,
                },
            )
            assert result.data["id"] == 43

        call_args = mock_api_client.create_animal.call_args[0][0]
        assert call_args["collar"] == "赤い首輪"
        assert call_args["ear_cut"] is True

    @pytest.mark.asyncio
    async def test_register_cat_invalid_gender(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with invalid gender. Requirements: 1.4, 7.2"""
        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "invalid",
                    },
                )
            assert "gender must be one of" in str(exc_info.value)

        mock_api_client.create_animal.assert_not_called()

    @pytest.mark.asyncio
    async def test_register_cat_authentication_error(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with authentication error. Requirements: 1.4, 7.3"""
        mock_api_client.create_animal.side_effect = PermissionError(
            "Invalid Automation API Key"
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "Authentication error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_cat_network_error(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with network error. Requirements: 1.4, 7.1"""
        mock_api_client.create_animal.side_effect = ConnectionError("Failed to connect")

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_cat_timeout_error(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with timeout error. Requirements: 1.4, 7.1"""
        mock_api_client.create_animal.side_effect = TimeoutError("Request timed out")

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_register_cat_validation_error(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with API validation error. Requirements: 1.4, 7.2"""
        mock_api_client.create_animal.side_effect = ValueError("Name is required")

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "Validation error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_cat_unexpected_error(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test cat registration with unexpected error. Requirements: 1.4, 7.4"""
        mock_api_client.create_animal.side_effect = RuntimeError("Unexpected error")

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_register_cat_missing_response_fields(
        self, mcp_server: FastMCP, mock_api_client: AsyncMock
    ) -> None:
        """Test when API response is missing required fields. Requirements: 1.3, 1.4"""
        mock_api_client.create_animal.return_value = {"pattern": "キジトラ"}

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool(
                    "register_cat",
                    {
                        "name": "たま",
                        "pattern": "キジトラ",
                        "tail_length": "長い",
                        "age_months": 12,
                        "gender": "male",
                    },
                )
            assert "missing required fields" in str(exc_info.value).lower()
