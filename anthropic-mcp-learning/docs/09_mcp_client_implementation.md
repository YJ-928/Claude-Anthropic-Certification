# 09 — MCP Client Implementation

## Overview

This document covers building a full MCP client that connects to an MCP server, discovers its capabilities, and provides an interface for your application to use them.

---

## Client Class Architecture

```python
import json
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    """Wrapper around MCP ClientSession for lifecycle management."""

    def __init__(self, command: str, args: list[str], env: Optional[dict] = None):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        """Establish connection to the MCP server."""
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
            env=self._env,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

    @property
    def session(self) -> ClientSession:
        if self._session is None:
            raise ConnectionError("Not connected. Call connect() first.")
        return self._session
```

---

## Core Client Methods

### List Tools

```python
async def list_tools(self) -> list[types.Tool]:
    """Get all tools available on the connected MCP server."""
    result = await self.session.list_tools()
    return result.tools
```

### Call Tool

```python
async def call_tool(self, tool_name: str, tool_input: dict) -> types.CallToolResult | None:
    """Execute a tool on the MCP server."""
    return await self.session.call_tool(tool_name, tool_input)
```

### List Prompts

```python
async def list_prompts(self) -> list[types.Prompt]:
    """Get all prompts defined by the MCP server."""
    result = await self.session.list_prompts()
    return result.prompts
```

### Get Prompt

```python
async def get_prompt(self, prompt_name: str, args: dict[str, str]):
    """Fetch a populated prompt template."""
    result = await self.session.get_prompt(prompt_name, args)
    return result.messages
```

### Read Resource

```python
async def read_resource(self, uri: str) -> Any:
    """Read a resource and parse based on MIME type."""
    result = await self.session.read_resource(AnyUrl(uri))
    resource = result.contents[0]

    if isinstance(resource, types.TextResourceContents):
        if resource.mimeType == "application/json":
            return json.loads(resource.text)
        return resource.text
```

---

## Lifecycle Management

### Context Manager Pattern

```python
async def cleanup(self):
    """Close the connection and release resources."""
    await self._exit_stack.aclose()
    self._session = None

async def __aenter__(self):
    await self.connect()
    return self

async def __aexit__(self, exc_type, exc_val, exc_tb):
    await self.cleanup()
```

### Usage

```python
async with MCPClient(command="python", args=["server.py"]) as client:
    tools = await client.list_tools()
    for tool in tools:
        print(f"Tool: {tool.name} — {tool.description}")
```

---

## Tool Schema Conversion

To send MCP tools to the Anthropic API, convert the schema format:

```python
async def get_anthropic_tools(client: MCPClient) -> list[dict]:
    """Convert MCP tool schemas to Anthropic API format."""
    tools = await client.list_tools()
    return [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema,
        }
        for t in tools
    ]
```

---

## Multiple Client Aggregation

When connecting to multiple MCP servers:

```python
async def get_all_tools(clients: dict[str, MCPClient]) -> list[dict]:
    """Aggregate tools from all connected MCP clients."""
    tools = []
    for client in clients.values():
        tool_models = await client.list_tools()
        tools += [
            {
                "name": t.name,
                "description": t.description,
                "input_schema": t.inputSchema,
            }
            for t in tool_models
        ]
    return tools
```

---

## Testing the Client

```python
async def main():
    async with MCPClient(command="python", args=["server.py"]) as client:
        # Test tool listing
        tools = await client.list_tools()
        print(f"Available tools: {[t.name for t in tools]}")

        # Test tool execution
        result = await client.call_tool("read_doc_contents", {"doc_id": "report.pdf"})
        print(f"Result: {result}")

        # Test resource reading
        doc_ids = await client.read_resource("docs://documents")
        print(f"Documents: {doc_ids}")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())
```

---

## Best Practices

1. **Always use context managers** — ensures cleanup even on exceptions
2. **Convert tool schemas** for the Anthropic API format before sending to Claude
3. **Handle `ConnectionError`** — server may not be running
4. **Parse MIME types** — use `application/json` for structured data
5. **Use `AnyUrl`** from pydantic for resource URIs

---

## Exercises

1. Implement a client that connects and prints all available tools, resources, and prompts
2. Write a function that finds which client has a specific tool (for multi-server setups)
3. Add retry logic for failed connections
