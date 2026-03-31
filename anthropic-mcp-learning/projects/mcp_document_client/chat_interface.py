"""
Chat Interface

Manages multi-turn conversations with Claude using tools from MCP servers.
Implements the agentic loop: send to Claude → execute tools → loop until text response.
"""

import json
from typing import Literal

from anthropic import Anthropic
from anthropic.types import Message, ToolResultBlockParam
from mcp.types import CallToolResult, TextContent

from .client import MCPClient


class ChatInterface:
    """Manages conversations between the user, Claude, and MCP servers."""

    def __init__(
        self,
        anthropic_client: Anthropic,
        model: str,
        clients: dict[str, MCPClient],
    ):
        self.anthropic = anthropic_client
        self.model = model
        self.clients = clients
        self.messages: list[dict] = []

    # ─── Tool management ───────────────────────────────────

    async def get_all_tools(self) -> list[dict]:
        """Aggregate tool schemas from all connected MCP clients."""
        tools = []
        for client in self.clients.values():
            tool_models = await client.list_tools()
            tools.extend(
                {
                    "name": t.name,
                    "description": t.description,
                    "input_schema": t.inputSchema,
                }
                for t in tool_models
            )
        return tools

    async def _find_client_with_tool(self, tool_name: str) -> MCPClient | None:
        """Find the MCP client that provides a given tool."""
        for client in self.clients.values():
            tools = await client.list_tools()
            if any(t.name == tool_name for t in tools):
                return client
        return None

    # ─── Tool execution ────────────────────────────────────

    @staticmethod
    def _build_tool_result(
        tool_use_id: str,
        text: str,
        status: Literal["success", "error"],
    ) -> ToolResultBlockParam:
        """Build a tool result block for the Anthropic API."""
        return {
            "tool_use_id": tool_use_id,
            "type": "tool_result",
            "content": text,
            "is_error": status == "error",
        }

    async def _execute_tool_requests(
        self, message: Message
    ) -> list[ToolResultBlockParam]:
        """Execute all tool requests in a Claude response."""
        tool_requests = [
            block for block in message.content if block.type == "tool_use"
        ]
        results: list[ToolResultBlockParam] = []

        for request in tool_requests:
            client = await self._find_client_with_tool(request.name)

            if not client:
                results.append(
                    self._build_tool_result(
                        request.id,
                        f"Tool '{request.name}' not found on any server",
                        "error",
                    )
                )
                continue

            try:
                tool_output: CallToolResult | None = await client.call_tool(
                    request.name, request.input
                )
                content_list = []
                if tool_output:
                    content_list = [
                        item.text
                        for item in tool_output.content
                        if isinstance(item, TextContent)
                    ]
                content_json = json.dumps(content_list)
                is_error = tool_output.isError if tool_output else False
                results.append(
                    self._build_tool_result(
                        request.id,
                        content_json,
                        "error" if is_error else "success",
                    )
                )
            except Exception as e:
                error_msg = f"Error executing tool '{request.name}': {e}"
                print(f"  [Error] {error_msg}")
                results.append(
                    self._build_tool_result(
                        request.id,
                        json.dumps({"error": error_msg}),
                        "error",
                    )
                )

        return results

    # ─── Conversation ──────────────────────────────────────

    def _extract_text(self, message: Message) -> str:
        """Extract text content from a Claude response."""
        return "\n".join(
            block.text for block in message.content if block.type == "text"
        )

    async def run(self, user_message: str) -> str:
        """Run one turn of the agentic loop."""
        self.messages.append({"role": "user", "content": user_message})

        tools = await self.get_all_tools()

        while True:
            response = self.anthropic.messages.create(
                model=self.model,
                max_tokens=8000,
                messages=self.messages,
                tools=tools,
            )

            # Add assistant response to history
            self.messages.append(
                {"role": "assistant", "content": response.content}
            )

            if response.stop_reason == "tool_use":
                # Print any text Claude included before tool calls
                text = self._extract_text(response)
                if text.strip():
                    print(f"  {text}")

                # Execute tools and loop
                tool_results = await self._execute_tool_requests(response)
                self.messages.append({"role": "user", "content": tool_results})
            else:
                # Final text response
                return self._extract_text(response)
