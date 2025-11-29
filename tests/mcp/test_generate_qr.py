"""
Tests for generate_qr MCP Tool

Context7 Reference: /pytest-dev/pytest (Trust Score: 9.5)
Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
"""

from __future__ import annotations

import shutil
from pathlib import Path
from unittest.mock import AsyncMock, patch

import pytest
from fastmcp import Client, FastMCP
from fastmcp.exceptions import ToolError

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.config import MCPConfig
from app.mcp.tools.generate_qr import register_tool


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
    client.client = AsyncMock()
    return client


@pytest.fixture
def mcp_server(mock_api_client: NecoKeeperAPIClient) -> FastMCP:
    """Create a FastMCP server instance with generate_qr tool registered"""
    mcp = FastMCP(name="Test MCP Server")
    register_tool(mcp, mock_api_client)
    return mcp


@pytest.fixture(autouse=True)
def cleanup_tmp_dir():
    """Clean up tmp/qr directory after each test"""
    yield
    tmp_dir = Path("tmp/qr")
    if tmp_dir.exists():
        shutil.rmtree(tmp_dir)


class TestGenerateQRTool:
    """Test suite for generate_qr tool"""

    @pytest.mark.asyncio
    async def test_generate_qr_success(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test successful QR PDF generation. Requirements: 2.1, 2.2, 2.3, 2.4"""
        fake_pdf_content = b"%PDF-1.4\nfake pdf content"
        mock_api_client.generate_qr_pdf = AsyncMock(return_value=fake_pdf_content)

        async with Client(mcp_server) as client:
            result = await client.call_tool("generate_qr", {"animal_id": 42})
            assert result.data["animal_id"] == 42
            pdf_path = Path(result.data["pdf_path"])
            assert pdf_path.exists()
            assert pdf_path.name == "qr_42.pdf"

    @pytest.mark.asyncio
    async def test_generate_qr_creates_directory(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test that generate_qr creates tmp/qr directory. Requirements: 2.5"""
        tmp_dir = Path("tmp/qr")
        if tmp_dir.exists():
            shutil.rmtree(tmp_dir)

        fake_pdf_content = b"%PDF-1.4\nfake pdf content"
        mock_api_client.generate_qr_pdf = AsyncMock(return_value=fake_pdf_content)

        async with Client(mcp_server) as client:
            await client.call_tool("generate_qr", {"animal_id": 1})
            assert tmp_dir.exists()

    @pytest.mark.asyncio
    async def test_generate_qr_naming_convention(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test PDF naming convention qr_{animal_id}.pdf. Requirements: 2.3"""
        fake_pdf_content = b"%PDF-1.4\nfake pdf content"
        mock_api_client.generate_qr_pdf = AsyncMock(return_value=fake_pdf_content)

        async with Client(mcp_server) as client:
            result = await client.call_tool("generate_qr", {"animal_id": 42})
            pdf_path = Path(result.data["pdf_path"])
            assert pdf_path.name == "qr_42.pdf"

    @pytest.mark.asyncio
    async def test_generate_qr_authentication_error(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test authentication error handling. Requirements: 7.3"""
        mock_api_client.generate_qr_pdf = AsyncMock(
            side_effect=PermissionError("Invalid API key")
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("generate_qr", {"animal_id": 42})
            assert "Authentication error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_qr_animal_not_found(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test animal not found error handling. Requirements: 7.2"""
        mock_api_client.generate_qr_pdf = AsyncMock(
            side_effect=FileNotFoundError("Animal with ID 999 not found")
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("generate_qr", {"animal_id": 999})
            assert "not found" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_qr_network_error(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test network error handling. Requirements: 7.1"""
        mock_api_client.generate_qr_pdf = AsyncMock(
            side_effect=ConnectionError("Connection refused")
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("generate_qr", {"animal_id": 42})
            assert "Network error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_qr_timeout_error(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test timeout error handling. Requirements: 7.1"""
        mock_api_client.generate_qr_pdf = AsyncMock(
            side_effect=TimeoutError("Request timed out")
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("generate_qr", {"animal_id": 42})
            assert "timed out" in str(exc_info.value).lower()

    @pytest.mark.asyncio
    async def test_generate_qr_file_system_error(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test file system error handling. Requirements: 7.4"""
        fake_pdf_content = b"%PDF-1.4\nfake pdf content"
        mock_api_client.generate_qr_pdf = AsyncMock(return_value=fake_pdf_content)

        with patch(
            "pathlib.Path.write_bytes", side_effect=OSError("Permission denied")
        ):
            async with Client(mcp_server) as client:
                with pytest.raises(ToolError) as exc_info:
                    await client.call_tool("generate_qr", {"animal_id": 42})
                assert "File system error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_qr_unexpected_error(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test unexpected error handling. Requirements: 7.4"""
        mock_api_client.generate_qr_pdf = AsyncMock(
            side_effect=RuntimeError("Unexpected error")
        )

        async with Client(mcp_server) as client:
            with pytest.raises(ToolError) as exc_info:
                await client.call_tool("generate_qr", {"animal_id": 42})
            assert "Unexpected error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_generate_qr_invalid_animal_id(self, mcp_server: FastMCP):
        """Test validation of animal_id parameter. Requirements: 2.1"""
        async with Client(mcp_server) as client:
            with pytest.raises((ToolError, ValueError, TypeError)):
                await client.call_tool("generate_qr", {"animal_id": 0})

    @pytest.mark.asyncio
    async def test_generate_qr_overwrites_existing_file(
        self, mcp_server: FastMCP, mock_api_client: NecoKeeperAPIClient
    ):
        """Test that generate_qr overwrites existing PDF file"""
        tmp_dir = Path("tmp/qr")
        tmp_dir.mkdir(parents=True, exist_ok=True)
        existing_file = tmp_dir / "qr_42.pdf"
        existing_file.write_bytes(b"old content")

        new_pdf_content = b"%PDF-1.4\nnew pdf content"
        mock_api_client.generate_qr_pdf = AsyncMock(return_value=new_pdf_content)

        async with Client(mcp_server) as client:
            result = await client.call_tool("generate_qr", {"animal_id": 42})
            pdf_path = Path(result.data["pdf_path"])
            assert pdf_path.read_bytes() == new_pdf_content
