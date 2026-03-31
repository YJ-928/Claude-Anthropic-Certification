"""
Exercise 07 — Claude Code SDK Query

Demonstrates using the Claude Code SDK pattern — sending programmatic
queries with controlled permissions. Uses the Anthropic API directly
to simulate SDK behavior.

Usage:
    python exercise_07_sdk_query.py
"""

from __future__ import annotations

import json
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()


class ClaudeCodeSDKSimulator:
    """
    Simulates the Claude Code SDK interface.

    In a real setup, this would call `claude --print` via subprocess.
    Here we use the Anthropic API directly to demonstrate the pattern.
    """

    def __init__(self, project_dir: str = ".") -> None:
        self.project_dir = Path(project_dir)
        self.client = anthropic.Anthropic()
        self.default_model = "claude-sonnet-4-20250514"

    def query(
        self,
        prompt: str,
        allowed_tools: list[str] | None = None,
        max_tokens: int = 2048,
    ) -> str:
        """Send a query to the SDK (simulated)."""
        system = "You are a Claude Code assistant analyzing a codebase."

        if allowed_tools:
            perms = ", ".join(allowed_tools)
            system += f"\nYou have access to these tools: {perms}"
        else:
            system += "\nYou have read-only access. No file modifications allowed."

        response = self.client.messages.create(
            model=self.default_model,
            max_tokens=max_tokens,
            system=system,
            messages=[{"role": "user", "content": prompt}],
        )

        return response.content[0].text

    def review(self, code: str, filename: str = "unknown.py") -> str:
        """Review code for issues (read-only)."""
        return self.query(
            f"Review this code from `{filename}` for bugs, security issues, "
            f"and style problems. Provide severity ratings.\n\n"
            f"```python\n{code}\n```"
        )

    def suggest_refactoring(self, code: str, filename: str = "unknown.py") -> str:
        """Suggest refactoring improvements (read-only)."""
        return self.query(
            f"Analyze this code from `{filename}` and suggest refactoring "
            f"improvements. Focus on readability and maintainability.\n\n"
            f"```python\n{code}\n```"
        )

    def generate_tests(self, code: str, filename: str = "unknown.py") -> str:
        """Generate tests for the given code."""
        return self.query(
            f"Generate comprehensive pytest tests for this code from `{filename}`.\n\n"
            f"```python\n{code}\n```\n\n"
            "Include edge cases and error handling tests.",
            allowed_tools=["read", "write"],
        )

    def explain(self, code: str) -> str:
        """Explain what code does."""
        return self.query(
            f"Explain what this code does in 2-3 concise paragraphs:\n\n"
            f"```python\n{code}\n```"
        )


# --- Pipeline Example ---

def code_quality_pipeline(sdk: ClaudeCodeSDKSimulator, code_samples: dict[str, str]) -> None:
    """Run a code quality pipeline on multiple code samples."""
    print("\n" + "=" * 60)
    print("CODE QUALITY PIPELINE")
    print("=" * 60)

    for filename, code in code_samples.items():
        print(f"\n{'─' * 50}")
        print(f"File: {filename}")
        print(f"{'─' * 50}")

        # Step 1: Review
        print("\n📋 Code Review:")
        review = sdk.review(code, filename)
        print(review)

        # Step 2: Refactoring suggestions
        print("\n🔧 Refactoring Suggestions:")
        refactoring = sdk.suggest_refactoring(code, filename)
        print(refactoring)

        print()


# --- Main ---

def main() -> None:
    print("=" * 60)
    print("Exercise 07 — Claude Code SDK Query")
    print("=" * 60)

    sdk = ClaudeCodeSDKSimulator()

    # Sample code to analyze
    sample_code = {
        "auth.py": '''\
import sqlite3

def get_user(username):
    conn = sqlite3.connect("users.db")
    query = f"SELECT * FROM users WHERE username = '{username}'"
    cursor = conn.cursor()
    cursor.execute(query)
    return cursor.fetchone()

def check_password(username, password):
    user = get_user(username)
    if user and user[2] == password:
        return True
    return False
''',
        "utils.py": '''\
def parse_config(data):
    return eval(data)

def process_items(items):
    result = []
    for i in range(len(items)):
        if items[i] != None:
            result.append(items[i])
    return result
''',
    }

    # Run the pipeline
    code_quality_pipeline(sdk, sample_code)

    # Demo: Generate tests for one sample
    print("=" * 60)
    print("GENERATING TESTS")
    print("=" * 60)
    print("\nGenerating tests for utils.py...")
    tests = sdk.generate_tests(sample_code["utils.py"], "utils.py")
    print(tests)


if __name__ == "__main__":
    main()
