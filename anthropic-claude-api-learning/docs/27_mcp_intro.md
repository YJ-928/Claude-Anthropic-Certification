# 27 — Model Context Protocol (MCP)

## Overview

MCP is an open protocol that standardises how AI models connect to external tools and data sources — similar to USB-C for AI integrations.

```
Claude (MCP Client)
      │
      │  MCP Protocol (JSON-RPC)
      │
MCP Server
      │
      ├── tools/     (functions Claude can call)
      ├── resources/ (data Claude can read)
      └── prompts/   (pre-built prompt templates)
```

## Key Concepts
- **MCP Server**: exposes tools, resources, prompts over stdio or HTTP
- **MCP Client**: the AI app that connects to servers (Claude Desktop, custom apps)
- **Transport**: stdio (local) or HTTP+SSE (remote)

## FastMCP Example

```python
from fastmcp import FastMCP

mcp = FastMCP("My Server")

@mcp.tool()
def get_weather(city: str) -> str:
    """Returns current weather for a city."""
    return f"Sunny, 22°C in {city}"

if __name__ == "__main__":
    mcp.run()
```

## Best Practices
- Use FastMCP for Python servers — it handles the protocol boilerplate
- Keep tools focused: one tool per action
- Return descriptive strings, not raw data structures

## Exercise
Build an MCP server with three tools: `list_files(dir)`, `read_file(path)`, `write_file(path, content)`. Connect it to a Claude client.
