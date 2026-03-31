"""
Coding Assistant — Orchestrates the tool use loop with Claude.
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic

from projects.claude_code_cli.tool_executor import ToolExecutor
from projects.claude_code_cli.context_manager import ContextManager

# Tool definitions for the Anthropic API
TOOLS = [
    {
        "name": "read_file",
        "description": "Read the contents of a file from disk.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file to read (relative to workspace).",
                }
            },
            "required": ["file_path"],
        },
    },
    {
        "name": "write_file",
        "description": "Write content to a file. Creates parent directories if needed.",
        "input_schema": {
            "type": "object",
            "properties": {
                "file_path": {
                    "type": "string",
                    "description": "Path to the file (relative to workspace).",
                },
                "content": {
                    "type": "string",
                    "description": "The content to write to the file.",
                },
            },
            "required": ["file_path", "content"],
        },
    },
    {
        "name": "list_directory",
        "description": "List the contents of a directory.",
        "input_schema": {
            "type": "object",
            "properties": {
                "path": {
                    "type": "string",
                    "description": "Directory path (relative to workspace). Defaults to '.'.",
                }
            },
            "required": [],
        },
    },
    {
        "name": "run_command",
        "description": "Execute a shell command in the workspace directory. Use for running tests, checking versions, etc.",
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
    },
    {
        "name": "search_files",
        "description": "Search for a text pattern across files in the workspace.",
        "input_schema": {
            "type": "object",
            "properties": {
                "pattern": {
                    "type": "string",
                    "description": "The text or regex pattern to search for.",
                },
                "path": {
                    "type": "string",
                    "description": "Directory to search in (relative to workspace). Defaults to '.'.",
                },
            },
            "required": ["pattern"],
        },
    },
]


class CodingAssistant:
    """A simplified coding assistant that uses Claude with tool execution."""

    def __init__(
        self,
        workspace: Path,
        model: str = "claude-sonnet-4-20250514",
        max_iterations: int = 15,
    ) -> None:
        self.client = anthropic.Anthropic()
        self.model = model
        self.max_iterations = max_iterations
        self.tool_executor = ToolExecutor(workspace=workspace)
        self.context_manager = ContextManager(workspace=workspace)
        self.messages: list[dict] = []

    def clear(self) -> None:
        """Clear conversation history."""
        self.messages.clear()

    def chat(self, user_message: str) -> str:
        """Process a user message and return the assistant's response."""
        self.messages.append({"role": "user", "content": user_message})

        system_prompt = self.context_manager.build_system_prompt()

        for iteration in range(self.max_iterations):
            response = self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=system_prompt,
                tools=TOOLS,
                messages=self.messages,
            )

            if response.stop_reason == "end_turn":
                # Extract text from the response
                text_blocks = [b.text for b in response.content if b.type == "text"]
                assistant_text = "\n".join(text_blocks)
                self.messages.append({"role": "assistant", "content": response.content})
                return assistant_text

            if response.stop_reason == "tool_use":
                self.messages.append({"role": "assistant", "content": response.content})

                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        print(f"  [tool] {block.name}({json.dumps(block.input, indent=2)})")
                        result = self.tool_executor.execute(block.name, block.input)
                        preview = result[:200] + "..." if len(result) > 200 else result
                        print(f"  [result] {preview}")
                        tool_results.append({
                            "type": "tool_result",
                            "tool_use_id": block.id,
                            "content": result,
                        })

                self.messages.append({"role": "user", "content": tool_results})

        return "I reached the maximum number of tool iterations. Please try a simpler request."
