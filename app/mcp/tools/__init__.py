"""
MCP Tools Package

This package contains the tool implementations for the MCP server.
Each tool is defined in a separate module for clarity and maintainability.

Available tools:
- register_cat: Register a new cat profile (implemented)
- generate_qr_card: Generate single QR card PDF for a cat (implemented)
- generate_qr: Generate QR code grid PDF for multiple cats (implemented)
- upload_cat_image: Upload a profile image for a cat (implemented)

Context7 Reference: /jlowin/fastmcp - Tool registration patterns
"""

from __future__ import annotations

from app.mcp.tools.generate_qr import register_tool as register_qr_tool
from app.mcp.tools.generate_qr_card import register_tool as register_qr_card_tool
from app.mcp.tools.register_cat import register_tool as register_cat_tool
from app.mcp.tools.upload_image import register_tool as register_upload_tool

__all__ = [
    "register_cat_tool",
    "register_qr_card_tool",
    "register_qr_tool",
    "register_upload_tool",
]
