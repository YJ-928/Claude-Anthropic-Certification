"""
Exercise 04 — Custom Command Simulation

Demonstrates how Claude Code custom commands work by simulating the
/audit and /generate-tests command patterns.

Usage:
    python exercise_04_custom_command.py audit
    python exercise_04_custom_command.py generate-tests src/app.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()

# --- Command Definitions ---
# In real Claude Code, these would be .claude/commands/*.md files

COMMANDS: dict[str, str] = {
    "audit": """\
Review all dependencies in this project for:

1. Known security vulnerabilities
2. Outdated versions with available updates
3. Unused dependencies that can be removed
4. License compatibility issues

For each issue found, provide:
- Severity (critical/high/medium/low)
- Current version vs recommended version
- Remediation steps

Output a summary table at the end.
""",
    "generate-tests": """\
Generate comprehensive tests for the file: $ARGUMENTS

Include:
1. Unit tests for all public functions
2. Edge cases (empty input, null values, boundary conditions)
3. Error handling tests
4. Use pytest with descriptive test names
5. Add docstrings explaining what each test verifies

Follow best practices for Python testing.
""",
    "review": """\
Perform a thorough code review of $ARGUMENTS:

1. **Correctness**: Logic errors, off-by-one, null handling
2. **Security**: Input validation, injection risks, auth checks
3. **Performance**: N+1 queries, unnecessary allocations
4. **Style**: Naming, structure, consistency

Format findings as:
- 🔴 Critical — must fix
- 🟡 Warning — should fix
- 🔵 Suggestion — nice to have
""",
}


def load_command(name: str) -> str | None:
    """Load a command template by name."""
    return COMMANDS.get(name)


def execute_command(name: str, arguments: str = "") -> str:
    """Execute a custom command with optional arguments."""
    template = load_command(name)
    if template is None:
        return f"Unknown command: /{name}\nAvailable: {', '.join(f'/{c}' for c in COMMANDS)}"

    # Replace $ARGUMENTS placeholder
    prompt = template.replace("$ARGUMENTS", arguments)

    # Add project context
    project_dir = Path(__file__).parent.parent
    requirements = project_dir / "requirements.txt"
    context = ""
    if requirements.exists():
        context = f"\n\nProject requirements.txt:\n{requirements.read_text()}"

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=4096,
        system="You are a coding assistant executing a custom command." + context,
        messages=[{"role": "user", "content": prompt}],
    )

    return response.content[0].text


# --- Main ---

def main() -> None:
    print("=" * 60)
    print("Exercise 04 — Custom Command Simulation")
    print("=" * 60)

    if len(sys.argv) < 2:
        print("\nUsage:")
        print("  python exercise_04_custom_command.py <command> [arguments]")
        print(f"\nAvailable commands: {', '.join(f'/{c}' for c in COMMANDS)}")
        sys.exit(1)

    command_name = sys.argv[1]
    arguments = " ".join(sys.argv[2:]) if len(sys.argv) > 2 else ""

    print(f"\nRunning: /{command_name} {arguments}")
    print("-" * 40)

    result = execute_command(command_name, arguments)
    print(result)


if __name__ == "__main__":
    main()
