"""MCP (Model Context Protocol) package for T-Developer v2.

This package provides safe tool access for AI agents through the MCP protocol.
"""

from packages.mcp.client import MCPClient
from packages.mcp.server.main import MCPServer, ToolType

__version__ = "2.0.0"
__all__ = ["MCPClient", "MCPServer", "ToolType"]
