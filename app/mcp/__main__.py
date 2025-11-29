"""
MCP Server Entry Point

This module provides the entry point for running the MCP server as a module.
Usage: python -m app.mcp

The server will:
1. Load and validate configuration from environment variables
2. Initialize the FastMCP server instance
3. Register all available tools
4. Start the server with stdio transport

Context7 Reference: /jlowin/fastmcp - Server initialization and configuration
Requirements: 4.1
"""

from __future__ import annotations

from app.mcp.server import main

if __name__ == "__main__":
    main()
