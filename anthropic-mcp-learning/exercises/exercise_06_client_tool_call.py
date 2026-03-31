"""
Exercise 06 — Client Tool Call

Demonstrates:
- Creating an MCP client
- Connecting to an MCP server
- Listing available tools
- Calling a tool and reading the result
- Reading resources

Run:
    python exercises/exercise_06_client_tool_call.py

Note: This requires the document server to be available.
      It will start the server automatically via stdio.
"""

import sys
import asyncio
import json
import os
from typing import Optional, Any
from contextlib import AsyncExitStack
from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
from pydantic import AnyUrl


class MCPClient:
    """MCP Client wrapper for connecting to an MCP server."""

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

    async def list_tools(self) -> list[types.Tool]:
        """Get all tools available on the MCP server."""
        result = await self.session.list_tools()
        return result.tools

    async def call_tool(
        self, tool_name: str, tool_input: dict
    ) -> types.CallToolResult | None:
        """Execute a tool on the MCP server."""
        return await self.session.call_tool(tool_name, tool_input)

    async def read_resource(self, uri: str) -> Any:
        """Read a resource and parse based on MIME type."""
        result = await self.session.read_resource(AnyUrl(uri))
        resource = result.contents[0]
        if isinstance(resource, types.TextResourceContents):
            if resource.mimeType == "application/json":
                return json.loads(resource.text)
            return resource.text

    async def list_prompts(self) -> list[types.Prompt]:
        """Get all prompts from the MCP server."""
        result = await self.session.list_prompts()
        return result.prompts

    async def get_prompt(self, prompt_name: str, args: dict[str, str]):
        """Fetch a populated prompt template."""
        result = await self.session.get_prompt(prompt_name, args)
        return result.messages

    async def cleanup(self):
        await self._exit_stack.aclose()
        self._session = None

    async def __aenter__(self):
        await self.connect()
        return self

    async def __aexit__(self, *exc):
        await self.cleanup()


# ─── Main demonstration ───────────────────────────────────


async def main():
    # Determine server script path
    script_dir = os.path.dirname(os.path.abspath(__file__))
    server_script = os.path.join(
        script_dir, "..", "projects", "mcp_document_server", "server.py"
    )

    print("=" * 60)
    print("MCP Client Tool Call Exercise")
    print("=" * 60)
    print()

    async with MCPClient(command="python", args=[server_script]) as client:
        # 1. List available tools
        print("1. Available Tools:")
        print("-" * 40)
        tools = await client.list_tools()
        for tool in tools:
            print(f"   {tool.name}: {tool.description}")
        print()

        # 2. Call the read_doc_contents tool
        print("2. Calling read_doc_contents('report.pdf'):")
        print("-" * 40)
        result = await client.call_tool(
            "read_doc_contents", {"doc_id": "report.pdf"}
        )
        if result:
            for item in result.content:
                if isinstance(item, types.TextContent):
                    print(f"   Result: {item.text}")
        print()

        # 3. Read a resource
        print("3. Reading resource docs://documents:")
        print("-" * 40)
        doc_list = await client.read_resource("docs://documents")
        print(f"   Documents: {doc_list}")
        print()

        # 4. Read a specific document via resource
        print("4. Reading resource docs://documents/plan.md:")
        print("-" * 40)
        doc_content = await client.read_resource("docs://documents/plan.md")
        print(f"   Content: {doc_content}")
        print()

        # 5. List available prompts
        print("5. Available Prompts:")
        print("-" * 40)
        prompts = await client.list_prompts()
        for prompt in prompts:
            print(f"   /{prompt.name}: {prompt.description}")
        print()

        # 6. Call the edit_document tool
        print("6. Calling edit_document:")
        print("-" * 40)
        result = await client.call_tool(
            "edit_document",
            {
                "doc_id": "report.pdf",
                "old_str": "20m",
                "new_str": "20-meter",
            },
        )
        if result:
            for item in result.content:
                if isinstance(item, types.TextContent):
                    print(f"   Result: {item.text}")

        # Verify the edit
        result = await client.call_tool(
            "read_doc_contents", {"doc_id": "report.pdf"}
        )
        if result:
            for item in result.content:
                if isinstance(item, types.TextContent):
                    print(f"   Updated content: {item.text}")
        print()

    print("=" * 60)
    print("Exercise complete!")
    print("=" * 60)


if __name__ == "__main__":
    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
    asyncio.run(main())
