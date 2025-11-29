"""
NecoKeeper MCP Server

This package implements a Model Context Protocol (MCP) server that enables
Claude (running on AWS Kiro) to interact with NecoKeeper through structured
tool calls.

The MCP server provides tools for:
- Registering cat profiles
- Generating QR code PDFs
- Uploading cat images

Context7 Reference: /jlowin/fastmcp - FastMCP framework for building MCP servers
"""

from __future__ import annotations

from app.mcp.config import MCPConfig

__all__ = ["MCPConfig"]
