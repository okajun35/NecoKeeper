"""
NecoKeeper API Client for MCP Server

This module provides an HTTP client for interacting with the NecoKeeper Automation API
using httpx.AsyncClient with X-Automation-Key header authentication.

Context7 Reference: /encode/httpx (Benchmark Score: 91.8)
"""

from __future__ import annotations

from typing import Any

import httpx

from app.mcp.config import MCPConfig


class NecoKeeperAPIClient:
    """
    Async HTTP client for NecoKeeper Automation API

    Handles authentication via X-Automation-Key header and provides
    error handling for network, authentication, and API errors.

    Example:
        >>> config = MCPConfig()
        >>> async with NecoKeeperAPIClient(config) as client:
        ...     animal = await client.create_animal({"name": "Tama", "sex": "メス"})
    """

    def __init__(self, config: MCPConfig | None = None):
        """
        Initialize the API client

        Args:
            config: MCP configuration instance. If None, creates a new one.

        Raises:
            ValueError: If AUTOMATION_API_KEY is missing or invalid
        """
        self.config = config or MCPConfig()

        # Create httpx AsyncClient with authentication header
        # Context7: AsyncClient manages connection pooling and supports headers
        # Note: Don't set Content-Type here as it needs to vary by request
        # (application/json for JSON, multipart/form-data for file uploads)
        headers: dict[str, str] = {
            "X-Automation-Key": self.config.api_key,
        }
        self.client = httpx.AsyncClient(
            base_url=self.config.api_url,
            headers=headers,
            timeout=30.0,
        )

    async def __aenter__(self) -> NecoKeeperAPIClient:
        """Context manager entry"""
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: object,
    ) -> None:
        """Context manager exit - close the client"""
        await self.close()

    async def close(self) -> None:
        """Close the HTTP client connection"""
        await self.client.aclose()

    async def create_animal(self, animal_data: dict[str, Any]) -> dict[str, Any]:
        """
        Create a new animal profile

        Args:
            animal_data: Animal profile data (name, sex, age_months, status, etc.)

        Returns:
            dict: Created animal data with id, name, and public_url

        Raises:
            httpx.HTTPStatusError: For HTTP 4xx/5xx responses
            httpx.ConnectError: For connection failures
            httpx.TimeoutException: For request timeouts
            httpx.NetworkError: For network-level errors

        Example:
            >>> animal_data = {
            ...     "name": "Tama",
            ...     "sex": "メス",
            ...     "age_months": 24,
            ...     "age_is_estimated": False,
            ...     "status": "保護中",
            ... }
            >>> result = await client.create_animal(animal_data)
            >>> print(result["animal_id"])
        """
        try:
            response = await self.client.post(
                "/api/automation/animals", json=animal_data
            )
            # Context7: raise_for_status() raises HTTPStatusError for 4xx/5xx
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result

        except httpx.HTTPStatusError as exc:
            # Context7: HTTPStatusError includes .request and .response attributes
            self._handle_http_status_error(exc)
            raise

        except httpx.ConnectError as exc:
            # Context7: ConnectError for failed connection establishment
            raise ConnectionError(
                f"Failed to connect to NecoKeeper API at {self.config.api_url}. "
                f"Please ensure the server is running."
            ) from exc

        except httpx.ConnectTimeout as exc:
            # Context7: ConnectTimeout for connection timeout
            raise TimeoutError(
                "Connection to NecoKeeper API timed out. "
                "Please check your network connection."
            ) from exc

        except httpx.ReadTimeout as exc:
            # Context7: ReadTimeout for read operation timeout
            raise TimeoutError(
                "Request to NecoKeeper API timed out while reading response. "
                "The server may be overloaded."
            ) from exc

        except httpx.TimeoutException as exc:
            # Context7: TimeoutException is the base class for all timeouts
            raise TimeoutError(f"Request to NecoKeeper API timed out: {exc}") from exc

        except httpx.NetworkError as exc:
            # Context7: NetworkError for network-level errors
            raise ConnectionError(
                f"Network error while communicating with NecoKeeper API: {exc}"
            ) from exc

    async def generate_qr_card_pdf(self, animal_id: int) -> bytes:
        """
        Generate single QR card PDF for an animal (A6 size)

        Args:
            animal_id: Animal ID to generate QR card for

        Returns:
            bytes: PDF file content

        Raises:
            httpx.HTTPStatusError: For HTTP 4xx/5xx responses
            httpx.ConnectError: For connection failures
            httpx.TimeoutException: For request timeouts
            httpx.NetworkError: For network-level errors
        """
        try:
            response = await self.client.post(
                "/api/automation/pdf/qr-card", json={"animal_id": animal_id}
            )
            response.raise_for_status()
            content: bytes = response.content
            return content

        except httpx.HTTPStatusError as exc:
            self._handle_http_status_error(exc)
            raise

        except httpx.ConnectError as exc:
            raise ConnectionError(
                f"Failed to connect to NecoKeeper API at {self.config.api_url}. "
                f"Please ensure the server is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to NecoKeeper API timed out: {exc}") from exc

        except httpx.NetworkError as exc:
            raise ConnectionError(
                f"Network error while communicating with NecoKeeper API: {exc}"
            ) from exc

    async def generate_qr_pdf(self, animal_ids: list[int]) -> bytes:
        """
        Generate QR code grid PDF for multiple animals (A4 size, 2x5 layout)

        Args:
            animal_ids: List of animal IDs to include in the PDF

        Returns:
            bytes: PDF file content

        Raises:
            httpx.HTTPStatusError: For HTTP 4xx/5xx responses
            httpx.ConnectError: For connection failures
            httpx.TimeoutException: For request timeouts
            httpx.NetworkError: For network-level errors
        """
        try:
            response = await self.client.post(
                "/api/automation/pdf/qr-card-grid", json={"animal_ids": animal_ids}
            )
            response.raise_for_status()
            content: bytes = response.content
            return content

        except httpx.HTTPStatusError as exc:
            self._handle_http_status_error(exc)
            raise

        except httpx.ConnectError as exc:
            raise ConnectionError(
                f"Failed to connect to NecoKeeper API at {self.config.api_url}. "
                f"Please ensure the server is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to NecoKeeper API timed out: {exc}") from exc

        except httpx.NetworkError as exc:
            raise ConnectionError(
                f"Network error while communicating with NecoKeeper API: {exc}"
            ) from exc

    async def upload_image(
        self, animal_id: int, image_data: bytes, filename: str = "image.jpg"
    ) -> dict[str, Any]:
        """
        Upload an image for an animal

        Args:
            animal_id: Animal ID to upload image for
            image_data: Image file content as bytes
            filename: Original filename (default: "image.jpg")

        Returns:
            dict: Upload result with image_url or image_id

        Raises:
            httpx.HTTPStatusError: For HTTP 4xx/5xx responses
            httpx.ConnectError: For connection failures
            httpx.TimeoutException: For request timeouts
            httpx.NetworkError: For network-level errors
        """
        try:
            # Determine content type from filename extension
            content_type = "image/jpeg"  # default
            if filename.lower().endswith(".png"):
                content_type = "image/png"
            elif filename.lower().endswith(".webp"):
                content_type = "image/webp"
            elif filename.lower().endswith((".jpg", ".jpeg")):
                content_type = "image/jpeg"
            elif filename.lower().endswith(".gif"):
                content_type = "image/gif"

            files = {"file": (filename, image_data, content_type)}
            response = await self.client.post(
                f"/api/automation/animals/{animal_id}/images", files=files
            )
            response.raise_for_status()
            result: dict[str, Any] = response.json()
            return result

        except httpx.HTTPStatusError as exc:
            self._handle_http_status_error(exc)
            raise

        except httpx.ConnectError as exc:
            raise ConnectionError(
                f"Failed to connect to NecoKeeper API at {self.config.api_url}. "
                f"Please ensure the server is running."
            ) from exc

        except httpx.TimeoutException as exc:
            raise TimeoutError(f"Request to NecoKeeper API timed out: {exc}") from exc

        except httpx.NetworkError as exc:
            raise ConnectionError(
                f"Network error while communicating with NecoKeeper API: {exc}"
            ) from exc

    def _handle_http_status_error(self, exc: httpx.HTTPStatusError) -> None:
        """
        Handle HTTP status errors with descriptive messages

        Context7: HTTPStatusError includes .request and .response attributes
        for detailed error information

        Args:
            exc: The HTTP status error exception

        Raises:
            PermissionError: For 401/403 authentication/authorization errors
            ValueError: For 400 validation errors
            FileNotFoundError: For 404 not found errors
            RuntimeError: For 500+ server errors
        """
        status_code = exc.response.status_code
        url = exc.request.url

        # Try to extract error detail from response
        try:
            error_detail = exc.response.json().get("detail", exc.response.text)
        except Exception:
            error_detail = exc.response.text

        if status_code == 401:
            raise PermissionError(
                f"Authentication failed: Invalid or missing Automation API Key. "
                f"Please check AUTOMATION_API_KEY environment variable. "
                f"URL: {url}"
            ) from exc

        elif status_code == 403:
            raise PermissionError(
                f"Authorization failed: Insufficient permissions. "
                f"URL: {url}, Detail: {error_detail}"
            ) from exc

        elif status_code == 400:
            raise ValueError(f"Validation error: {error_detail}. URL: {url}") from exc

        elif status_code == 404:
            raise FileNotFoundError(
                f"Resource not found: {error_detail}. URL: {url}"
            ) from exc

        elif status_code == 429:
            raise RuntimeError(
                f"Rate limit exceeded. Please try again later. URL: {url}"
            ) from exc

        elif status_code >= 500:
            raise RuntimeError(
                f"Server error ({status_code}): {error_detail}. URL: {url}"
            ) from exc

        else:
            raise RuntimeError(
                f"HTTP error ({status_code}): {error_detail}. URL: {url}"
            ) from exc
