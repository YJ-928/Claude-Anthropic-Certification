"""
Exercise 01 — Tool: Read File

Simulates Claude requesting a file read operation.
Demonstrates the core tool use pattern: define tool → receive call → execute → return result.

Usage:
    python exercise_01_tool_read_file.py
"""

from __future__ import annotations

import json
import os
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

# --- Tool Definition ---

READ_FILE_TOOL = {
    "name": "read_file",
    "description": "Read the contents of a file from disk.",
    "input_schema": {
        "type": "object",
        "properties": {
            "file_path": {
                "type": "string",
                "description": "The path to the file to read.",
            }
        },
        "required": ["file_path"],
    },
}


# --- Tool Executor ---

def execute_read_file(file_path: str) -> str:
    """Execute the read_file tool."""
    path = Path(file_path)
    if not path.exists():
        return f"Error: File not found: {path}"
    if not path.is_file():
        return f"Error: Not a file: {path}"
    return path.read_text()


# --- Tool Use Loop ---

def run_tool_loop(user_request: str) -> str:
    """Single-tool loop: Claude can request file reads."""
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": user_request}]

    for _ in range(5):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system="You are a coding assistant. Use the read_file tool when you need to see file contents.",
            tools=[READ_FILE_TOOL],
            messages=messages,
        )

        print(f"[stop_reason={response.stop_reason}]")

        if response.stop_reason == "end_turn":
            return "\n".join(b.text for b in response.content if b.type == "text")

        # Handle tool calls
        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                print(f"  Tool call: {block.name}({json.dumps(block.input)})")
                result = execute_read_file(block.input["file_path"])
                print(f"  Result preview: {result[:100]}...")
                tool_results.append({
                    "type": "tool_result",
                    "tool_use_id": block.id,
                    "content": result,
                })

        messages.append({"role": "user", "content": tool_results})

    return "Max iterations reached."


# --- Main ---

def main() -> None:
    print("=" * 60)
    print("Exercise 01 — Read File Tool")
    print("=" * 60)

    # Read the requirements.txt file from the repo
    target = str(Path(__file__).parent.parent / "requirements.txt")
    request = f"Read the file at {target} and tell me what dependencies this project uses."

    print(f"\nUser: {request}\n")
    result = run_tool_loop(request)
    print(f"\nAssistant:\n{result}")


if __name__ == "__main__":
    main()
