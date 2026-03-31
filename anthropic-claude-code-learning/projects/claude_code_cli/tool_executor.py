"""
Tool Executor — Executes tool calls from Claude.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


class ToolExecutor:
    """Executes tool calls within a workspace directory."""

    # Commands that are never allowed
    BLOCKED_COMMANDS = ["rm -rf /", "sudo rm", "mkfs", "dd if=/dev", "> /dev/"]

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def execute(self, tool_name: str, tool_input: dict[str, Any]) -> str:
        """Dispatch a tool call to the appropriate handler."""
        handlers = {
            "read_file": self._read_file,
            "write_file": self._write_file,
            "list_directory": self._list_directory,
            "run_command": self._run_command,
            "search_files": self._search_files,
        }

        handler = handlers.get(tool_name)
        if handler is None:
            return f"Error: Unknown tool '{tool_name}'."

        try:
            return handler(tool_input)
        except Exception as e:
            return f"Error executing {tool_name}: {e}"

    def _resolve_path(self, rel_path: str) -> Path:
        """Resolve a relative path within the workspace. Prevent traversal."""
        resolved = (self.workspace / rel_path).resolve()
        if not str(resolved).startswith(str(self.workspace)):
            raise ValueError(f"Path traversal blocked: {rel_path}")
        return resolved

    def _read_file(self, params: dict[str, Any]) -> str:
        """Read a file from the workspace."""
        path = self._resolve_path(params["file_path"])
        if not path.exists():
            return f"Error: File not found: {params['file_path']}"
        if not path.is_file():
            return f"Error: Not a file: {params['file_path']}"
        return path.read_text()

    def _write_file(self, params: dict[str, Any]) -> str:
        """Write content to a file in the workspace."""
        path = self._resolve_path(params["file_path"])
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(params["content"])
        return f"File written: {params['file_path']}"

    def _list_directory(self, params: dict[str, Any]) -> str:
        """List contents of a directory."""
        rel_path = params.get("path", ".")
        path = self._resolve_path(rel_path)
        if not path.is_dir():
            return f"Error: Not a directory: {rel_path}"

        entries = sorted(path.iterdir())
        lines = []
        for entry in entries:
            name = entry.name
            if entry.is_dir():
                name += "/"
            lines.append(name)
        return "\n".join(lines) if lines else "(empty directory)"

    def _run_command(self, params: dict[str, Any]) -> str:
        """Execute a shell command in the workspace."""
        command = params["command"]

        # Security check
        for blocked in self.BLOCKED_COMMANDS:
            if blocked in command:
                return f"Error: Command blocked for safety: '{blocked}'"

        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                cwd=str(self.workspace),
                timeout=30,
            )
            output = result.stdout
            if result.returncode != 0:
                output += f"\nExit code: {result.returncode}\nSTDERR:\n{result.stderr}"
            return output or "(no output)"
        except subprocess.TimeoutExpired:
            return "Error: Command timed out after 30 seconds."

    def _search_files(self, params: dict[str, Any]) -> str:
        """Search for a pattern in files."""
        pattern = params["pattern"]
        search_path = self._resolve_path(params.get("path", "."))

        try:
            result = subprocess.run(
                ["grep", "-rn", "--include=*.py", "--include=*.md",
                 "--include=*.json", "--include=*.txt", "--include=*.yaml",
                 "--include=*.yml", "--include=*.toml", "--include=*.js",
                 "--include=*.ts", pattern, str(search_path)],
                capture_output=True,
                text=True,
                timeout=15,
            )
            return result.stdout or "No matches found."
        except subprocess.TimeoutExpired:
            return "Error: Search timed out."
