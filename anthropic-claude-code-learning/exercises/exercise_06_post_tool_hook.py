"""
Exercise 06 — Post-Tool-Use Hook

Demonstrates a post-tool-use hook that runs checks after Claude edits files.
Examples: auto-formatting, type checking, running tests.

Post-hooks:
- Run AFTER the tool executes
- Cannot block (the action already happened)
- Provide feedback to Claude via stderr

Usage:
    python exercise_06_post_tool_hook.py
"""

from __future__ import annotations

import json
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Any


@dataclass
class PostHookResult:
    """Result of a post-tool-use hook."""
    feedback: str = ""
    actions_taken: list[str] = field(default_factory=list)


# --- Post-Hook Implementations ---

def post_hook_python_format(tool_call: dict[str, Any]) -> PostHookResult:
    """Run black formatter after Python file edits."""
    file_path: str = tool_call.get("tool_input", {}).get("file_path", "")

    if not file_path.endswith(".py"):
        return PostHookResult()

    # In a real hook, this would actually run black
    # result = subprocess.run(["black", file_path], capture_output=True, text=True)
    return PostHookResult(
        feedback=f"Formatted {file_path} with black.",
        actions_taken=[f"black {file_path}"],
    )


def post_hook_type_check(tool_call: dict[str, Any]) -> PostHookResult:
    """Run type checker after TypeScript file edits."""
    file_path: str = tool_call.get("tool_input", {}).get("file_path", "")

    if not file_path.endswith((".ts", ".tsx")):
        return PostHookResult()

    # Simulate type check result
    # In real hook: result = subprocess.run(["npx", "tsc", "--no-emit"], ...)
    return PostHookResult(
        feedback=f"Type check passed for {file_path}.",
        actions_taken=["npx tsc --no-emit"],
    )


def post_hook_run_tests(tool_call: dict[str, Any]) -> PostHookResult:
    """Run relevant tests after file edits."""
    file_path: str = tool_call.get("tool_input", {}).get("file_path", "")

    if not file_path.endswith(".py"):
        return PostHookResult()

    # Determine test file
    if file_path.startswith("src/"):
        test_file = file_path.replace("src/", "tests/test_", 1)
    else:
        test_file = f"tests/test_{file_path.split('/')[-1]}"

    return PostHookResult(
        feedback=f"Tests should be run: pytest {test_file}",
        actions_taken=[f"pytest {test_file} -v"],
    )


def post_hook_line_count(tool_call: dict[str, Any]) -> PostHookResult:
    """Count lines in the edited file."""
    file_path: str = tool_call.get("tool_input", {}).get("file_path", "")
    content: str = tool_call.get("tool_input", {}).get("content", "")

    if content:
        line_count = content.count("\n") + 1
        return PostHookResult(
            feedback=f"{file_path}: {line_count} lines written.",
        )

    return PostHookResult()


# --- Hook Pipeline ---

@dataclass
class PostHookPipeline:
    """Pipeline of post-tool-use hooks."""
    hooks: list[tuple[str, Any]] = field(default_factory=list)

    def add(self, matcher: str, hook_fn: Any) -> None:
        self.hooks.append((matcher, hook_fn))

    def _matches(self, matcher: str, tool_name: str) -> bool:
        return any(m.strip() == tool_name for m in matcher.split("|"))

    def run(self, tool_call: dict[str, Any]) -> list[PostHookResult]:
        """Run all matching hooks for a tool call."""
        tool_name = tool_call.get("tool_name", "")
        results = []

        for matcher, hook_fn in self.hooks:
            if self._matches(matcher, tool_name):
                result = hook_fn(tool_call)
                if result.feedback:
                    results.append(result)

        return results


# --- Test Suite ---

def run_tests() -> None:
    """Test the post-hook pipeline."""
    pipeline = PostHookPipeline()
    pipeline.add("write|edit", post_hook_python_format)
    pipeline.add("write|edit", post_hook_type_check)
    pipeline.add("write|edit", post_hook_run_tests)
    pipeline.add("write", post_hook_line_count)

    test_cases = [
        {
            "tool_name": "write",
            "tool_input": {
                "file_path": "src/utils.py",
                "content": "def add(a, b):\n    return a + b\n",
            },
        },
        {
            "tool_name": "edit",
            "tool_input": {
                "file_path": "src/components/App.tsx",
            },
        },
        {
            "tool_name": "write",
            "tool_input": {
                "file_path": "README.md",
                "content": "# Project\n\nDescription here.\n",
            },
        },
        {
            "tool_name": "read",
            "tool_input": {
                "file_path": "src/app.py",
            },
        },
    ]

    for tool_call in test_cases:
        tool_name = tool_call["tool_name"]
        file_path = tool_call["tool_input"].get("file_path", "")
        print(f"\n{'=' * 50}")
        print(f"Tool: {tool_name}({file_path})")
        print("-" * 50)

        results = pipeline.run(tool_call)

        if results:
            for r in results:
                print(f"  📝 {r.feedback}")
                for action in r.actions_taken:
                    print(f"     → {action}")
        else:
            print("  (no post-hooks triggered)")


# --- Standalone Hook Mode ---

def standalone_hook_mode() -> None:
    """Run as a standalone post-hook (reads JSON from stdin)."""
    input_data = sys.stdin.read()
    tool_call = json.loads(input_data)

    results = [
        post_hook_python_format(tool_call),
        post_hook_run_tests(tool_call),
    ]

    for r in results:
        if r.feedback:
            print(r.feedback, file=sys.stderr)

    sys.exit(0)  # Post-hooks always exit 0


# --- Main ---

def main() -> None:
    if not sys.stdin.isatty():
        standalone_hook_mode()
        return

    print("=" * 60)
    print("Exercise 06 — Post-Tool-Use Hook")
    print("=" * 60)
    run_tests()

    print("\n\nTo use as a real hook, pipe JSON to stdin:")
    print('  echo \'{"tool_name":"write","tool_input":{"file_path":"app.py","content":"..."}}\' '
          "| python exercise_06_post_tool_hook.py")


if __name__ == "__main__":
    main()
