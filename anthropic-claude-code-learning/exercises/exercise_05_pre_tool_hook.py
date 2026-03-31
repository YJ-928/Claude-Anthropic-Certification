"""
Exercise 05 — Pre-Tool-Use Hook

Demonstrates a pre-tool-use hook that blocks access to .env files.
This simulates the hook that Claude Code runs before executing read/grep tools.

The hook:
1. Receives tool call data as JSON (simulated here)
2. Checks if the file path contains ".env"
3. Returns exit code 0 (allow) or 2 (block)

Usage:
    python exercise_05_pre_tool_hook.py
"""

from __future__ import annotations

import json
import sys
from dataclasses import dataclass
from typing import Any


@dataclass
class HookResult:
    """Result of a hook execution."""
    exit_code: int  # 0 = allow, 2 = block
    stderr_message: str = ""

    @property
    def allowed(self) -> bool:
        return self.exit_code == 0


# --- Configurable Hook ---

BLOCKED_PATTERNS = [".env", ".secret", "credentials", "private_key", "id_rsa"]
ALLOWED_EXCEPTIONS = [".env.example", ".env.template"]


def pre_hook_block_sensitive_files(tool_call_json: str) -> HookResult:
    """
    Pre-tool-use hook that blocks access to sensitive files.

    This is the Python equivalent of what you'd write in a Node.js hook script.
    In real Claude Code, this receives JSON via stdin and exits with a code.
    """
    try:
        tool_call = json.loads(tool_call_json)
    except json.JSONDecodeError:
        # Fail-open: if we can't parse, allow the call
        return HookResult(exit_code=0)

    tool_name = tool_call.get("tool_name", "")
    tool_input = tool_call.get("tool_input", {})

    # Extract file path (different tools use different keys)
    file_path: str = tool_input.get("file_path", "") or tool_input.get("path", "")

    if not file_path:
        return HookResult(exit_code=0)

    # Check for allowed exceptions first
    for exception in ALLOWED_EXCEPTIONS:
        if file_path.endswith(exception):
            return HookResult(exit_code=0)

    # Check for blocked patterns
    for pattern in BLOCKED_PATTERNS:
        if pattern in file_path.lower():
            return HookResult(
                exit_code=2,
                stderr_message=(
                    f'BLOCKED: Access to "{file_path}" denied by security hook. '
                    f'Matches sensitive pattern: "{pattern}". '
                    f"This file may contain credentials and must not be read."
                ),
            )

    return HookResult(exit_code=0)


# --- Test Suite ---

def run_tests() -> None:
    """Run test cases for the pre-tool hook."""
    test_cases: list[tuple[dict[str, Any], bool, str]] = [
        # (tool_call_data, expected_allowed, description)
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/.env"}},
            False,
            "Block: .env file",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/.env.local"}},
            False,
            "Block: .env.local file",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/.env.example"}},
            True,
            "Allow: .env.example (exception)",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/src/app.py"}},
            True,
            "Allow: regular Python file",
        ),
        (
            {"tool_name": "grep", "tool_input": {"path": "/project/.env", "pattern": "KEY"}},
            False,
            "Block: grep on .env",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/credentials.json"}},
            False,
            "Block: credentials file",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/home/user/.ssh/id_rsa"}},
            False,
            "Block: SSH private key",
        ),
        (
            {"tool_name": "read", "tool_input": {"file_path": "/project/README.md"}},
            True,
            "Allow: README file",
        ),
        (
            {"tool_name": "bash", "tool_input": {"command": "ls -la"}},
            True,
            "Allow: no file path in bash",
        ),
    ]

    print(f"Running {len(test_cases)} test cases:\n")

    passed = 0
    for tool_call_data, expected_allowed, description in test_cases:
        tool_json = json.dumps(tool_call_data)
        result = pre_hook_block_sensitive_files(tool_json)

        status = "PASS" if result.allowed == expected_allowed else "FAIL"
        icon = "✅" if status == "PASS" else "❌"
        state = "ALLOW" if result.allowed else "BLOCK"

        print(f"  {icon} {status} | {description}")
        print(f"       {state}: {result.stderr_message or 'Allowed.'}")

        if status == "PASS":
            passed += 1

    print(f"\n{passed}/{len(test_cases)} tests passed.")


# --- Standalone Hook Mode ---

def standalone_hook_mode() -> None:
    """Run as a standalone hook script (reads JSON from stdin)."""
    input_data = sys.stdin.read()
    result = pre_hook_block_sensitive_files(input_data)

    if result.stderr_message:
        print(result.stderr_message, file=sys.stderr)

    sys.exit(result.exit_code)


# --- Main ---

def main() -> None:
    # If stdin is not a terminal, run as a real hook
    if not sys.stdin.isatty():
        standalone_hook_mode()
        return

    # Otherwise, run the test suite
    print("=" * 60)
    print("Exercise 05 — Pre-Tool-Use Hook")
    print("=" * 60)
    print()
    run_tests()

    print("\n" + "=" * 60)
    print("To use as a real hook, pipe JSON to stdin:")
    print('  echo \'{"tool_name":"read","tool_input":{"file_path":".env"}}\' | python exercise_05_pre_tool_hook.py')
    print("  echo $?  # Check exit code: 0=allow, 2=block")


if __name__ == "__main__":
    main()
