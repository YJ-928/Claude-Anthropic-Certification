"""
MCP Document Client

Wrapper around MCP ClientSession for connecting to MCP servers.
Manages connection lifecycle and provides a clean interface for
listing tools, calling tools, reading resources, and getting prompts.
"""

import sys
import asyncio
import json
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    """MCP Client with lifecycle management for connecting to MCP servers."""

    def __init__(
        self,
        command: str,
        args: list[str],
        env: Optional[dict] = None,
    ):
        self._command = command
        self._args = args
        self._env = env
        self._session: Optional[ClientSession] = None
        self._exit_stack: AsyncExitStack = AsyncExitStack()

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
        """Get the active client session. Raises if not connected."""
        if self._session is None:
            raise ConnectionError(
                "Client session not initialized. Call connect() first."
            )
        return self._session

    # ─── Tools ─────────────────────────────────────────────

    async def list_tools(self) -> list[types.Tool]:
        """Get all tools available on the connected MCP server."""
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Execute a tool on the MCP server."""
        return await self.session.call_tool(tool_name, tool_input)

    # ─── Resources ─────────────────────────────────────────

    async def read_resource(self, uri: str) -> Any:
        """Read a resource and parse based on MIME type."""
        result = await self.session.read_resource(AnyUrl(uri))
        resource = result.contents[0]

        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text

    # ─── Prompts ───────────────────────────────────────────

    async def list_prompts(self) -> list[types.Prompt]:
        """Get all prompts defined by the MCP server."""
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(
        self, prompt_name: str, args: dict[str, str]
    ) -> list[types.PromptMessage]:
        """Fetch a populated prompt template by name."""
        result = await self.session.get_prompt(prompt_name, args)
        return result.messages

    # ─── Lifecycle ─────────────────────────────────────────

    async def cleanup(self):
        """Close the connection and release resources."""
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.cleanup()


# ─── Testing harness ───────────────────────────────────────

async def main():
    """Test the client by connecting to the document server."""
    import os

    server_path = os.path.join(
        os.path.dirname(os.path.abspath(__file__)),
        "..",
        "mcp_document_server",
        "server.py",
    )

    async with MCPClient(command="python", args=[server_path]) as client:
        # List tools
        tools = await client.list_tools()
        print("Available tools:")
        for tool in tools:
            print(f"  - {tool.name}: {tool.description}")
        print()

        # List resources
        doc_ids = await client.read_resource("docs://documents")
        print(f"Available documents: {doc_ids}")
        print()

        # Read a document
        content = await client.read_resource("docs://documents/report.pdf")
        print(f"report.pdf content: {content}")
        print()

        # List prompts
        prompts = await client.list_prompts()
        print("Available prompts:")
        for prompt in prompts:
            print(f"  - /{prompt.name}: {prompt.description}")


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
