"""
SDK Demo — Simple query example using the Claude Code SDK.

The Claude Code SDK wraps the `claude` CLI, allowing programmatic
interaction with Claude from Python scripts.

Usage:
    python projects/sdk_demo/query_example.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path


def claude_query(
    prompt: str,
    *,
    model: str | None = None,
    allowed_tools: list[str] | None = None,
    max_turns: int = 1,
    output_format: str = "text",
) -> str:
    """Send a single query to Claude Code CLI (--print mode).

    Args:
        prompt: The user prompt.
        model: Optional model override.
        allowed_tools: Explicit list of tools to enable.
        max_turns: Maximum agentic turns (default 1 for single-shot).
        output_format: 'text' or 'json'.

    Returns:
        Claude's response as a string.
    """
    cmd = ["claude", "--print"]

    if model:
        cmd.extend(["--model", model])

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    if max_turns > 1:
        cmd.extend(["--max-turns", str(max_turns)])

    if output_format == "json":
        cmd.extend(["--output-format", "json"])

    cmd.extend(["--", prompt])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path.cwd()),
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed (exit {result.returncode}): {result.stderr}")

    return result.stdout.strip()


def main() -> None:
    # Example 1: Simple question (read-only, no tools)
    print("=" * 60)
    print("Example 1: Simple query (no tools)")
    print("=" * 60)
    try:
        answer = claude_query("What is a Python decorator? Explain in 2 sentences.")
        print(answer)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error (is `claude` installed?): {e}")

    print()

    # Example 2: Query with file reading
    print("=" * 60)
    print("Example 2: Query with read_file tool")
    print("=" * 60)
    try:
        answer = claude_query(
            "Read requirements.txt and list the dependencies.",
            allowed_tools=["read_file"],
            max_turns=3,
        )
        print(answer)
    except (RuntimeError, FileNotFoundError) as e:
        print(f"Error: {e}")

    print()

    # Example 3: JSON output format
    print("=" * 60)
    print("Example 3: JSON output")
    print("=" * 60)
    try:
        raw = claude_query(
            "Return a JSON object with keys 'language' and 'version' for Python.",
            output_format="json",
        )
        parsed = json.loads(raw)
        print(json.dumps(parsed, indent=2))
    except (RuntimeError, FileNotFoundError, json.JSONDecodeError) as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main()
