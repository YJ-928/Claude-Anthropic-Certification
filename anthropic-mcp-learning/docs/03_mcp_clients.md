# 03 — MCP Clients

## What is an MCP Client?

An MCP Client is a **communication interface** between your application server and an MCP server. It provides access to the server's tools, resources, and prompts through a standardized protocol.

The client does **not** execute tools itself — it facilitates communication between your application and the MCP server that actually runs the tools.

---

## Transport Agnostic

The client/server can communicate via multiple protocols:

- **stdin/stdout** — Most common for local development (both on same machine)
- **HTTP/SSE** — For remote servers
- **WebSockets** — For real-time bidirectional communication

---

## Key Client Operations

| Method | Purpose |
|--------|---------|
| `connect()` | Establish connection to MCP server |
| `list_tools()` | Get available tools from server |
| `call_tool(name, input)` | Execute a tool on the server |
| `list_resources()` | Get available resources |
| `read_resource(uri)` | Fetch a resource by URI |
| `list_prompts()` | Get available prompt templates |
| `get_prompt(name, args)` | Fetch a populated prompt |
| `cleanup()` | Close the connection |

---

## Client Session Lifecycle

```python
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from contextlib import AsyncExitStack

# 1. Define server connection parameters
server_params = StdioServerParameters(
    command="python",
    args=["mcp_server.py"],
)

# 2. Create transport
exit_stack = AsyncExitStack()
stdio_transport = await exit_stack.enter_async_context(
    stdio_client(server_params)
)
read_stream, write_stream = stdio_transport

# 3. Create and initialize session
session = await exit_stack.enter_async_context(
    ClientSession(read_stream, write_stream)
)
await session.initialize()

# 4. Use the session
tools = await session.list_tools()
result = await session.call_tool("read_doc_contents", {"doc_id": "report.pdf"})

# 5. Cleanup
await exit_stack.aclose()
```

---

## Typical Communication Flow

```
1. User sends query to application
2. Application asks MCP Client for tools
   └─► Client sends list_tools request to MCP Server
   ◄── Server responds with tool list
3. Application sends query + tool schemas to Claude
4. Claude requests tool execution
5. Application asks MCP Client to run tool
   └─► Client sends call_tool request to MCP Server
   ◄── Server executes tool and returns result
6. Application sends tool result back to Claude
7. Claude formulates final response
8. Application returns response to user
```

---

## Wrapper Pattern

In practice, wrap the `ClientSession` in a larger class for better resource management:

```python
class MCPClient:
    def __init__(self, command: str, args: list[str]):
        self._command = command
        self._args = args
        self._session: ClientSession | None = None
        self._exit_stack = AsyncExitStack()

    async def connect(self):
        server_params = StdioServerParameters(
            command=self._command,
            args=self._args,
        )
        stdio_transport = await self._exit_stack.enter_async_context(
            stdio_client(server_params)
        )
        read_stream, write_stream = stdio_transport
        self._session = await self._exit_stack.enter_async_context(
            ClientSession(read_stream, write_stream)
        )
        await self._session.initialize()

    async def list_tools(self):
        result = await self._session.list_tools()
        return result.tools

    async def call_tool(self, tool_name: str, tool_input: dict):
        return await self._session.call_tool(tool_name, tool_input)

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *exc):
        await self.cleanup()
```

---

## Best Practices

1. **Always clean up** — Use `async with` or explicit cleanup to close sessions
2. **Wrap in a class** — Don't use `ClientSession` directly; wrap it for lifecycle management
3. **One client per server** — Each MCP server connection gets its own client instance
4. **Handle connection errors** — Servers may not be available; fail gracefully

---

## Exercises

1. Implement a minimal MCP client that connects to a server and lists available tools
2. Extend the client to call a tool and print the result
3. Add error handling for when the MCP server is not running
