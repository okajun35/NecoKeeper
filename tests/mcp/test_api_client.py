"""
Tests for NecoKeeper API Client

Context7 Reference: /encode/httpx (Benchmark Score: 91.8)
"""

from __future__ import annotations

import secrets
from typing import Any
from unittest.mock import AsyncMock, patch

import httpx
import pytest

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.config import MCPConfig


@pytest.fixture
def valid_api_key() -> str:
    """Generate a valid API key for testing."""
    return secrets.token_urlsafe(32)


@pytest.fixture
def mock_config(monkeypatch: Any, valid_api_key: str) -> MCPConfig:
    """Create a mock configuration for testing."""
    monkeypatch.setenv("AUTOMATION_API_KEY", valid_api_key)
    monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")
    return MCPConfig()


class TestNecoKeeperAPIClient:
    """Test suite for NecoKeeperAPIClient class."""

    @pytest.mark.asyncio
    async def test_client_initialization(self, mock_config: MCPConfig) -> None:
        """Test that API client initializes correctly."""
        async with NecoKeeperAPIClient(mock_config) as client:
            assert client.config == mock_config
            assert client.client.base_url == "http://localhost:8000"
            assert "X-Automation-Key" in client.client.headers

    @pytest.mark.asyncio
    async def test_client_context_manager(self, mock_config: MCPConfig) -> None:
        """Test that API client works as async context manager."""
        async with NecoKeeperAPIClient(mock_config) as client:
            assert client.client is not None
        assert client.client.is_closed

    @pytest.mark.asyncio
    async def test_create_animal_success(self, mock_config: MCPConfig) -> None:
        """Test successful animal creation via API."""
        animal_data = {"name": "Tama", "sex": "メス", "age": "2歳", "status": "保護中"}
        expected_response = {
            "animal_id": 42,
            "name": "Tama",
            "public_url": "http://localhost:8000/public/care?animal_id=42",
        }

        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            200, json=expected_response, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                result = await client.create_animal(animal_data)

        assert result == expected_response
        assert result["animal_id"] == 42

    @pytest.mark.asyncio
    async def test_create_animal_authentication_error(
        self, mock_config: MCPConfig
    ) -> None:
        """Test that 401 authentication errors are handled correctly."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            401, json={"detail": "Invalid API key"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(PermissionError, match="Authentication failed"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_create_animal_validation_error(self, mock_config: MCPConfig) -> None:
        """Test that 400 validation errors are handled correctly."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            400, json={"detail": "Name is required"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(ValueError, match="Validation error"):
                    await client.create_animal({})

    @pytest.mark.asyncio
    async def test_create_animal_not_found_error(self, mock_config: MCPConfig) -> None:
        """Test that 404 not found errors are handled correctly."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            404, json={"detail": "Not found"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(FileNotFoundError, match="Resource not found"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_create_animal_server_error(self, mock_config: MCPConfig) -> None:
        """Test that 500 server errors are handled correctly."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            500, json={"detail": "Internal error"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(RuntimeError, match="Server error"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_create_animal_rate_limit_error(self, mock_config: MCPConfig) -> None:
        """Test that 429 rate limit errors are handled correctly."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals"
        )
        mock_response = httpx.Response(
            429, json={"detail": "Too many requests"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(RuntimeError, match="Rate limit exceeded"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_create_animal_connection_error(self, mock_config: MCPConfig) -> None:
        """Test that connection errors are handled correctly."""
        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client,
                "post",
                new=AsyncMock(side_effect=httpx.ConnectError("Connection refused")),
            ):
                with pytest.raises(ConnectionError, match="Failed to connect"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_create_animal_timeout_error(self, mock_config: MCPConfig) -> None:
        """Test that timeout errors are handled correctly."""
        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client,
                "post",
                new=AsyncMock(side_effect=httpx.TimeoutException("Timeout")),
            ):
                with pytest.raises(TimeoutError, match="timed out"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_generate_qr_pdf_success(self, mock_config: MCPConfig) -> None:
        """Test successful QR PDF generation via API."""
        pdf_content = b"%PDF-1.4\nfake pdf content"
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/pdf/qr-card-grid"
        )
        mock_response = httpx.Response(200, content=pdf_content, request=mock_request)

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                result = await client.generate_qr_pdf([42])

        assert result == pdf_content

    @pytest.mark.asyncio
    async def test_generate_qr_pdf_authentication_error(
        self, mock_config: MCPConfig
    ) -> None:
        """Test that QR PDF generation handles authentication errors."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/pdf/qr-card-grid"
        )
        mock_response = httpx.Response(
            401, json={"detail": "Invalid API key"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(PermissionError, match="Authentication failed"):
                    await client.generate_qr_pdf([42])

    @pytest.mark.asyncio
    async def test_upload_image_success(self, mock_config: MCPConfig) -> None:
        """Test successful image upload via API."""
        image_data = b"fake image data"
        expected_response = {
            "image_id": 123,
            "image_url": "http://localhost:8000/media/animals/42/image.jpg",
        }
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals/42/images"
        )
        mock_response = httpx.Response(
            200, json=expected_response, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                result = await client.upload_image(42, image_data, "test.jpg")

        assert result == expected_response

    @pytest.mark.asyncio
    async def test_upload_image_authentication_error(
        self, mock_config: MCPConfig
    ) -> None:
        """Test that image upload handles authentication errors."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals/42/images"
        )
        mock_response = httpx.Response(
            401, json={"detail": "Invalid API key"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(PermissionError, match="Authentication failed"):
                    await client.upload_image(42, b"fake data")

    @pytest.mark.asyncio
    async def test_upload_image_not_found_error(self, mock_config: MCPConfig) -> None:
        """Test that image upload handles animal not found errors."""
        mock_request = httpx.Request(
            "POST", "http://localhost:8000/api/automation/animals/999/images"
        )
        mock_response = httpx.Response(
            404, json={"detail": "Animal not found"}, request=mock_request
        )

        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client, "post", new=AsyncMock(return_value=mock_response)
            ):
                with pytest.raises(FileNotFoundError, match="Resource not found"):
                    await client.upload_image(999, b"fake data")

    @pytest.mark.asyncio
    async def test_network_error_handling(self, mock_config: MCPConfig) -> None:
        """Test that network errors are handled correctly."""
        async with NecoKeeperAPIClient(mock_config) as client:
            with patch.object(
                client.client,
                "post",
                new=AsyncMock(side_effect=httpx.NetworkError("Network unreachable")),
            ):
                with pytest.raises(ConnectionError, match="Network error"):
                    await client.create_animal({"name": "Test"})

    @pytest.mark.asyncio
    async def test_client_without_config(self, monkeypatch: Any) -> None:
        """Test that client can create its own config if none provided."""
        api_key = secrets.token_urlsafe(32)
        monkeypatch.setenv("AUTOMATION_API_KEY", api_key)
        monkeypatch.setenv("NECOKEEPER_API_URL", "http://localhost:8000")

        async with NecoKeeperAPIClient() as client:
            assert client.config is not None
            assert client.config.api_key == api_key

    @pytest.mark.asyncio
    async def test_client_close_method(self, mock_config: MCPConfig) -> None:
        """Test that client close method works correctly."""
        client = NecoKeeperAPIClient(mock_config)
        assert not client.client.is_closed
        await client.close()
        assert client.client.is_closed
