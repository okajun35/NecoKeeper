"""
generate_qr MCP Tool

This module provides the generate_qr tool for the MCP server, allowing
Claude to generate QR code PDFs for registered cats.

Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
Requirements: 2.1, 2.2, 2.3, 2.4, 2.5, 6.3, 7.1, 7.2, 7.3, 7.4
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Annotated, Any

from fastmcp import FastMCP
from fastmcp.exceptions import ToolError
from pydantic import Field

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.error_handler import handle_api_error, validate_positive_integer

logger = logging.getLogger(__name__)


def register_tool(mcp: FastMCP, api_client: NecoKeeperAPIClient) -> None:
    """
    Register the generate_qr tool with the MCP server.

    This function registers the tool using the FastMCP decorator pattern,
    binding it to the provided API client for making authenticated requests.

    Args:
        mcp: FastMCP server instance
        api_client: NecoKeeper API client for making authenticated requests

    Context7: FastMCP tool registration using @mcp.tool decorator
    """

    @mcp.tool  # type: ignore[misc]
    async def generate_qr(
        animal_id: Annotated[int, Field(description="猫ID", gt=0)],
    ) -> dict[str, Any]:
        """
        QR付きPDFを生成

        指定された猫のQRコード付きPDFを生成し、ローカルファイルシステムに保存します。
        PDFは tmp/qr/qr_{animal_id}.pdf に保存されます。

        Args:
            animal_id: 猫のID（必須、正の整数）

        Returns:
            dict: 生成結果
                - pdf_path (str): 保存されたPDFファイルのローカルパス
                - animal_id (int): 猫のID

        Raises:
            ToolError: PDF生成に失敗した場合

        Example:
            >>> result = await generate_qr(animal_id=42)
            >>> print(result["pdf_path"])
            tmp/qr/qr_42.pdf
        """
        try:
            # Validate animal_id using centralized validation
            # Requirements 7.2: Specific validation error details
            validate_positive_integer(animal_id, "animal_id")

            logger.info(f"Generating QR PDF for animal_id={animal_id}")

            # Call NecoKeeper API to generate PDF
            # Requirements 2.2: Call /api/automation/pdf/qr-card-grid endpoint
            pdf_content = await api_client.generate_qr_pdf([animal_id])

            # Create directory if it doesn't exist
            # Requirements 2.5: Create tmp/qr/ directory automatically
            output_dir = Path("tmp/qr")
            output_dir.mkdir(parents=True, exist_ok=True)

            # Save PDF to file
            # Requirements 2.3: Save to tmp/qr/qr_{animal_id}.pdf
            pdf_path = output_dir / f"qr_{animal_id}.pdf"
            pdf_path.write_bytes(pdf_content)

            logger.info(f"Successfully saved QR PDF to {pdf_path}")

            # Requirements 2.4: Return local file path
            result = {
                "pdf_path": str(pdf_path),
                "animal_id": animal_id,
            }

            return result

        except ToolError:
            # Re-raise ToolError as-is
            raise

        except Exception as e:
            # Use centralized error handling
            # Requirements 6.3, 7.1, 7.2, 7.3, 7.4: Centralized error handling
            raise handle_api_error(e, "generating QR PDF") from e
