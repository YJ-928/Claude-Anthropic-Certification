"""
MCP Helper Utilities

Shared functions for working with MCP tools, resources, and prompts.
"""

from mcp.types import Tool, TextContent, CallToolResult


def tools_to_anthropic_schema(tools: list[Tool]) -> list[dict]:
    """
    Convert a list of MCP Tool objects into the Anthropic API tool schema format.

    Args:
        tools: List of MCP Tool objects (from client.list_tools()).

    Returns:
        A list of dicts with 'name', 'description', and 'input_schema' keys.
    """
    return [
        {
            "name": tool.name,
            "description": tool.description or "",
            "input_schema": tool.inputSchema,
        }
        for tool in tools
    ]


def extract_text_from_result(result: CallToolResult | None) -> str:
    """
    Extract text from a CallToolResult.

    Returns joined text from all TextContent blocks.
    """
    if not result or not result.content:
        return ""
    texts = [item.text for item in result.content if isinstance(item, TextContent)]
    return "\n".join(texts)


async def aggregate_tools(*clients) -> list[dict]:
    """
    Aggregate tool schemas from multiple MCPClient instances.

    Args:
        *clients: MCPClient instances (must be connected).

    Returns:
        Combined tool schemas in Anthropic format.
    """
    all_tools = []
    for client in clients:
        tool_models = await client.list_tools()
        all_tools.extend(tools_to_anthropic_schema(tool_models))
    return all_tools


async def route_tool_call(tool_name: str, tool_input: dict, *clients):
    """
    Route a tool call to the correct MCPClient.

    Searches each client for the named tool and calls it on the first match.

    Args:
        tool_name: Name of the tool to call.
        tool_input: Arguments to pass to the tool.
        *clients: MCPClient instances to search.

    Returns:
        The CallToolResult, or None if no client has the tool.
    """
    for client in clients:
        tools = await client.list_tools()
        if any(t.name == tool_name for t in tools):
            return await client.call_tool(tool_name, tool_input)
    return None
