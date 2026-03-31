"""
Exercise 02 — Tool: Run Command

Simulates Claude executing shell commands via a run_command tool.
Demonstrates command execution with timeout and error handling.

Usage:
    python exercise_02_run_command_tool.py
"""

from __future__ import annotations

import json
import subprocess

import anthropic
from dotenv import load_dotenv

load_dotenv()

# --- Tool Definition ---

RUN_COMMAND_TOOL = {
    "name": "run_command",
    "description": "Execute a shell command and return stdout/stderr. Use for running tests, checking versions, or listing files.",
    "input_schema": {
        "type": "object",
        "properties": {
            "command": {
                "type": "string",
                "description": "The shell command to execute.",
            }
        },
        "required": ["command"],
    },
}

# Commands that are never allowed (security)
BLOCKED_COMMANDS = ["rm -rf", "sudo", "mkfs", "dd if=", "> /dev/"]


# --- Tool Executor ---

def execute_run_command(command: str) -> str:
    """Execute a shell command with safety checks."""
    # Security: block dangerous commands
    for blocked in BLOCKED_COMMANDS:
        if blocked in command:
            return f"Error: Command blocked for safety: '{blocked}' is not allowed."

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=30,
        )
        output = result.stdout
        if result.returncode != 0:
            output += f"\nExit code: {result.returncode}\nSTDERR:\n{result.stderr}"
        return output or "(no output)"
    except subprocess.TimeoutExpired:
        return "Error: Command timed out after 30 seconds."


# --- Tool Use Loop ---

def run_tool_loop(user_request: str) -> str:
    """Tool loop with run_command support."""
    client = anthropic.Anthropic()
    messages: list[dict] = [{"role": "user", "content": user_request}]

    for _ in range(5):
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2048,
            system=(
                "You are a coding assistant. Use the run_command tool to execute "
                "shell commands when needed. Only run safe, read-only commands."
            ),
            tools=[RUN_COMMAND_TOOL],
            messages=messages,
        )

        print(f"[stop_reason={response.stop_reason}]")

        if response.stop_reason == "end_turn":
            return "\n".join(b.text for b in response.content if b.type == "text")

        messages.append({"role": "assistant", "content": response.content})
        tool_results = []

        for block in response.content:
            if block.type == "tool_use":
                print(f"  Tool call: {block.name}({json.dumps(block.input)})")
                result = execute_run_command(block.input["command"])
                print(f"  Output: {result[:200]}")
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
    print("Exercise 02 — Run Command Tool")
    print("=" * 60)

    request = "What Python version is installed? Also show the current directory contents."
    print(f"\nUser: {request}\n")

    result = run_tool_loop(request)
    print(f"\nAssistant:\n{result}")


if __name__ == "__main__":
    main()
