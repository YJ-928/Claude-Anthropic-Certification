"""
Conversation Runner

Provides a standalone agentic loop that can be used independently of
the full Conversation class — useful for scripted / programmatic usage.
"""

import json
from anthropic import Anthropic
from anthropic.types import ToolResultBlockParam
from mcp.types import TextContent

from projects.mcp_document_client.client import MCPClient


async def agentic_loop(
    anthropic_client: Anthropic,
    model: str,
    client: MCPClient,
    user_message: str,
    message_history: list[dict] | None = None,
    system_prompt: str | None = None,
) -> str:
    """
    Run a single agentic conversation turn.

    Sends user_message to Claude along with tool schemas from the MCP client.
    If Claude requests tools, they are executed and the loop continues until
    Claude returns a final text response.

    Args:
        anthropic_client: Initialized Anthropic SDK client.
        model: Claude model name.
        client: Connected MCPClient instance.
        user_message: The user's input.
        message_history: Optional prior messages. If None, starts fresh.
        system_prompt: Optional system prompt for Claude.

    Returns:
        The final text response from Claude.
    """
    messages = message_history if message_history is not None else []
    messages.append({"role": "user", "content": user_message})

    # Build tool schemas
    tool_models = await client.list_tools()
    tools = [
        {
            "name": t.name,
            "description": t.description,
            "input_schema": t.inputSchema,
        }
        for t in tool_models
    ]

    # agentic loop
    while True:
        kwargs = {
            "model": model,
            "max_tokens": 8000,
            "messages": messages,
            "tools": tools,
        }
        if system_prompt:
            kwargs["system"] = system_prompt

        response = anthropic_client.messages.create(**kwargs)
        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason != "tool_use":
            return "\n".join(
                block.text for block in response.content if block.type == "text"
            )

        # Execute tool calls
        tool_results: list[ToolResultBlockParam] = []
        for block in response.content:
            if block.type != "tool_use":
                continue
            try:
                result = await client.call_tool(block.name, block.input)
                content = []
                if result:
                    content = [
                        item.text
                        for item in result.content
                        if isinstance(item, TextContent)
                    ]
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps(content),
                        "is_error": result.isError if result else False,
                    }
                )
            except Exception as e:
                tool_results.append(
                    {
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": json.dumps({"error": str(e)}),
                        "is_error": True,
                    }
                )

        messages.append({"role": "user", "content": tool_results})
