"""
MCP Server Main Module

This module implements the main MCP server that registers all tools and
handles communication with Claude via stdio transport.

Context7 Reference: /jlowin/fastmcp (Benchmark Score: 82.4)
Requirements: 4.1, 4.3, 4.4, 6.3, 7.1, 7.2, 7.3, 7.4, 7.5
"""

from __future__ import annotations

import logging
import sys

from fastmcp import FastMCP

from app.mcp.api_client import NecoKeeperAPIClient
from app.mcp.config import MCPConfig
from app.mcp.error_handler import configure_logging
from app.mcp.tools import (
    register_cat_tool,
    register_qr_card_tool,
    register_qr_tool,
    register_upload_tool,
)

logger = logging.getLogger(__name__)


class MCPServer:
    """
    Main MCP Server class

    This class initializes the FastMCP server, registers all tools,
    and manages the API client lifecycle.

    Attributes:
        config: MCP configuration instance
        api_client: NecoKeeper API client
        mcp: FastMCP server instance

    Example:
        >>> server = MCPServer()
        >>> server.run()  # Start the server with stdio transport
    """

    def __init__(self) -> None:
        """
        Initialize the MCP server

        Performs startup configuration validation and initializes
        the FastMCP instance with all registered tools.

        Raises:
            ValueError: If configuration is missing or invalid
        """
        # Configure logging first
        # Requirements 7.5: Add logging configuration
        try:
            self.config = MCPConfig()
            configure_logging(
                log_level=self.config.log_level, log_file=self.config.log_file
            )
        except ValueError as e:
            # If config fails, use basic logging
            configure_logging(log_level="INFO")
            logger.error(f"Configuration validation failed: {e}")
            raise

        logger.info("Initializing NecoKeeper MCP Server...")
        logger.info(f"Configuration loaded: {self.config}")

        # Initialize API client
        self.api_client = NecoKeeperAPIClient(self.config)
        logger.info(f"API client initialized for {self.config.api_url}")

        # Initialize FastMCP server
        # Context7: FastMCP(name=...) creates a new MCP server instance
        self.mcp = FastMCP(
            name="NecoKeeper MCP Server",
            instructions=(
                "NecoKeeper MCP Server provides tools for managing cat shelter data. "
                "Use register_cat to add new cats, generate_qr_card to create single QR card PDF (A6), "
                "generate_qr to create QR code grid PDF (A4, 2x5), and upload_cat_image to add profile images."
            ),
        )

        # Register all tools
        # Requirements 4.3: Register all three tools
        self._register_tools()

        logger.info("MCP Server initialization complete")

    def _register_tools(self) -> None:
        """
        Register all MCP tools

        Registers the four main tools with the FastMCP server:
        - register_cat: Register new cat profiles
        - generate_qr_card: Generate single QR card PDF (A6)
        - generate_qr: Generate QR code grid PDF (A4, 2x5)
        - upload_cat_image: Upload cat profile images

        Requirements 4.4: Return list of all registered tools with schemas
        """
        logger.info("Registering MCP tools...")

        # Register register_cat tool
        # Requirements 1.1: Expose register_cat tool
        register_cat_tool(self.mcp, self.api_client)
        logger.info("Registered tool: register_cat")

        # Register generate_qr_card tool
        # Requirements 2.1: Expose generate_qr_card tool
        register_qr_card_tool(self.mcp, self.api_client)
        logger.info("Registered tool: generate_qr_card")

        # Register generate_qr tool
        # Requirements 2.1: Expose generate_qr tool
        register_qr_tool(self.mcp, self.api_client)
        logger.info("Registered tool: generate_qr")

        # Register upload_cat_image tool
        # Requirements 3.1: Expose upload_cat_image tool
        register_upload_tool(self.mcp, self.api_client)
        logger.info("Registered tool: upload_cat_image")

        logger.info("All tools registered successfully")

    def run(self) -> None:
        """
        Start the MCP server with stdio transport

        Runs the FastMCP server using stdio transport for communication
        with Claude/Kiro. This is a blocking call that runs until the
        server is terminated.

        Requirements 4.1: Provide command to launch server
        Context7: mcp.run(transport="stdio") starts the server with stdio
        """
        logger.info("Starting MCP server with stdio transport...")

        try:
            # Context7: FastMCP.run() starts the server event loop
            # stdio transport communicates via stdin/stdout
            self.mcp.run(transport="stdio")
        except KeyboardInterrupt:
            logger.info("Server shutdown requested")
        except Exception as e:
            logger.error(f"Server error: {e}", exc_info=True)
            raise
        finally:
            logger.info("MCP server stopped")


def main() -> None:
    """
    Main entry point for the MCP server

    Creates and runs the MCP server instance. This function is called
    when the module is executed as a script.

    Requirements 4.1: python -m app.mcp.server launches the server
    """
    try:
        server = MCPServer()
        server.run()
    except ValueError as e:
        # Configuration validation errors
        logger.error(f"Failed to start server: {e}")
        sys.exit(1)
    except Exception as e:
        # Unexpected errors
        logger.error(f"Unexpected error: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()
