"""
upload_cat_image MCP Tool

This module provides the upload_cat_image tool for the MCP server, allowing
Claude to upload profile images for registered cats.

Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
Requirements: 3.1, 3.2, 3.3, 3.4, 3.5, 6.3, 7.1, 7.2, 7.3, 7.4
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.error_handler import (
    handle_api_error,
    validate_non_empty_string,
    validate_positive_integer,
)

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, api_client: NecoKeeperAPIClient) -> None:
    """
    Register the upload_cat_image tool with the MCP server.

    This function registers the tool using the FastMCP decorator pattern,
    binding it to the provided API client for making authenticated requests.

    Args:
        mcp: FastMCP server instance
        api_client: NecoKeeper API client for making authenticated requests

    Context7: FastMCP tool registration using @mcp.tool decorator
    """

    @mcp.tool  # type: ignore[misc]
    async def upload_cat_image(
        animal_id: Annotated[int, Field(description="猫ID", gt=0)],
        image_path: Annotated[str, Field(description="ローカル画像ファイルパス")],
    ) -> dict[str, Any]:
        """
        猫プロフィール画像をアップロード

        指定された猫のプロフィール画像をローカルファイルシステムから読み込み、
        NecoKeeperにアップロードします。

        Args:
            animal_id: 猫のID（必須、正の整数）
            image_path: ローカル画像ファイルのパス（必須）

        Returns:
            dict: アップロード結果
                - image_url (str): アップロードされた画像のURL
                - animal_id (int): 猫のID

        Raises:
            ToolError: アップロードに失敗した場合

        Example:
            >>> result = await upload_cat_image(
            ...     animal_id=42, image_path="/path/to/cat.jpg"
            ... )
            >>> print(result["image_url"])
            http://localhost:8000/media/animals/42/image.jpg
        """
        try:
            # Validate inputs using centralized validation
            # Requirements 7.2: Specific validation error details
            validate_positive_integer(animal_id, "animal_id")
            validate_non_empty_string(image_path, "image_path")

            logger.info(f"Uploading image for animal_id={animal_id} from {image_path}")

            # Read image file from local filesystem
            # Requirements 3.2: Read image file from local filesystem
            image_file = Path(image_path)

            # Check if file exists
            # Requirements 3.5: Handle file not found errors
            if not image_file.exists():
                raise ToolError(
                    f"File error: Image file not found at '{image_path}'. "
                    "Please verify the file path is correct."
                )

            # Check if it's a file (not a directory)
            if not image_file.is_file():
                raise ToolError(
                    f"File error: '{image_path}' is not a file. "
                    "Please provide a path to an image file."
                )

            # Validate file extension
            # Requirements 3.5: Handle invalid file errors
            valid_extensions = {".jpg", ".jpeg", ".png", ".gif", ".webp"}
            if image_file.suffix.lower() not in valid_extensions:
                raise ToolError(
                    f"Validation error: Invalid image file type '{image_file.suffix}'. "
                    f"Supported formats: {', '.join(valid_extensions)}"
                )

            # Read file content
            try:
                image_data = image_file.read_bytes()
            except PermissionError as e:
                raise ToolError(
                    f"File error: Permission denied reading '{image_path}'. "
                    "Please check file permissions."
                ) from e
            except OSError as e:
                raise ToolError(
                    f"File error: Could not read '{image_path}'. {e}"
                ) from e

            # Validate file size (max 10MB)
            max_size = 10 * 1024 * 1024  # 10MB
            if len(image_data) > max_size:
                raise ToolError(
                    f"Validation error: Image file too large ({len(image_data)} bytes). "
                    f"Maximum size is {max_size} bytes (10MB)."
                )

            # Validate file is not empty
            if len(image_data) == 0:
                raise ToolError(
                    f"Validation error: Image file is empty at '{image_path}'."
                )

            logger.info(
                f"Read {len(image_data)} bytes from {image_path}, "
                f"uploading to animal_id={animal_id}"
            )

            # Upload via API
            # Requirements 3.3: Call /api/automation/animals/{animal_id}/images
            response = await api_client.upload_image(
                animal_id=animal_id,
                image_data=image_data,
                filename=image_file.name,
            )

            # Extract image URL from response
            # Requirements 3.4: Return image_url or image_id
            image_url = response.get("image_url") or response.get("url")
            image_id = response.get("image_id") or response.get("id")

            if not image_url and not image_id:
                raise ToolError(
                    "API error: Response missing image_url or image_id. "
                    "Upload may have failed."
                )

            result: dict[str, Any] = {
                "animal_id": animal_id,
            }

            if image_url:
                result["image_url"] = image_url
            if image_id:
                result["image_id"] = image_id

            logger.info(
                f"Successfully uploaded image for animal_id={animal_id}: "
                f"image_url={image_url}, image_id={image_id}"
            )

            return result

        except ToolError:
            # Re-raise ToolError as-is
            raise

        except Exception as e:
            # Use centralized error handling
            # Requirements 6.3, 7.1, 7.2, 7.3, 7.4: Centralized error handling
            raise handle_api_error(e, "uploading image") from e
