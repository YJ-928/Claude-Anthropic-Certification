"""
Tool Parser — Utilities for parsing and validating tool definitions and tool results.
"""

from __future__ import annotations

import json
from typing import Any


def extract_tool_calls(response) -> list[dict[str, Any]]:
    """Extract tool_use blocks from a Claude API response.

    Args:
        response: An anthropic Message object.

    Returns:
        A list of dicts with keys: id, name, input.
    """
    calls = []
    for block in response.content:
        if block.type == "tool_use":
            calls.append({
                "id": block.id,
                "name": block.name,
                "input": block.input,
            })
    return calls


def extract_text(response) -> str:
    """Extract concatenated text blocks from a Claude API response.

    Args:
        response: An anthropic Message object.

    Returns:
        Combined text from all text blocks.
    """
    parts = []
    for block in response.content:
        if block.type == "text":
            parts.append(block.text)
    return "\n".join(parts)


def build_tool_result(tool_use_id: str, content: str, is_error: bool = False) -> dict[str, Any]:
    """Build a tool_result message block for the API.

    Args:
        tool_use_id: The tool_use block ID from the response.
        content: The result string.
        is_error: Whether this result represents an error.

    Returns:
        A dict suitable for inclusion in the messages array.
    """
    result: dict[str, Any] = {
        "type": "tool_result",
        "tool_use_id": tool_use_id,
        "content": content,
    }
    if is_error:
        result["is_error"] = True
    return result


def validate_tool_schema(tool_definition: dict[str, Any]) -> list[str]:
    """Validate a tool definition against the expected schema.

    Args:
        tool_definition: A tool definition dict.

    Returns:
        A list of validation error messages (empty if valid).
    """
    errors = []

    if "name" not in tool_definition:
        errors.append("Missing required field: 'name'")
    elif not isinstance(tool_definition["name"], str):
        errors.append("'name' must be a string")

    if "description" not in tool_definition:
        errors.append("Missing required field: 'description'")

    if "input_schema" not in tool_definition:
        errors.append("Missing required field: 'input_schema'")
    else:
        schema = tool_definition["input_schema"]
        if not isinstance(schema, dict):
            errors.append("'input_schema' must be an object")
        elif schema.get("type") != "object":
            errors.append("'input_schema.type' must be 'object'")
        elif "properties" not in schema:
            errors.append("'input_schema.properties' is required")

    return errors


def format_tool_call_log(name: str, inputs: dict[str, Any], result: str, max_result_len: int = 300) -> str:
    """Format a tool call for human-readable logging.

    Args:
        name: Tool name.
        inputs: Tool input parameters.
        result: The tool execution result.
        max_result_len: Maximum characters of result to include.

    Returns:
        A formatted log string.
    """
    input_str = json.dumps(inputs, indent=2)
    truncated = result[:max_result_len] + "..." if len(result) > max_result_len else result
    return f"[Tool Call] {name}\n  Input: {input_str}\n  Result: {truncated}"
