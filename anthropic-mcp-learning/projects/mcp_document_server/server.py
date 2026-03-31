"""
MCP Document Server

A complete MCP server exposing tools, resources, and prompts for
managing an in-memory document store.

Run directly:
    python projects/mcp_document_server/server.py

Test with inspector:
    mcp dev projects/mcp_document_server/server.py
"""

import sys
import os

# Add project root to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from mcp.server.fastmcp import FastMCP

mcp = FastMCP("DocumentMCP", log_level="ERROR")

# Register all server primitives
from tools import register_tools
from resources import register_resources
from prompts import register_prompts

register_tools(mcp)
register_resources(mcp)
register_prompts(mcp)

if __name__ == "__main__":
    mcp.run(transport="stdio")
