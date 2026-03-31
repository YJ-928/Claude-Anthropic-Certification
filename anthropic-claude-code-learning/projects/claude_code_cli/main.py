"""
Claude Code CLI — Simplified Coding Assistant

A simplified coding assistant that demonstrates the core Claude Code architecture:
User request → LLM decides tool → tool executor runs action → LLM returns result.

Usage:
    python -m projects.claude_code_cli.main
    # or
    python projects/claude_code_cli/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Allow running from repo root
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from dotenv import load_dotenv

from projects.claude_code_cli.assistant import CodingAssistant

load_dotenv()


def main() -> None:
    print("╔══════════════════════════════════════╗")
    print("║      Claude Code CLI (Simplified)    ║")
    print("║  Type 'quit' or 'exit' to stop.      ║")
    print("║  Type 'clear' to reset conversation.  ║")
    print("╚══════════════════════════════════════╝")

    workspace = Path.cwd()
    assistant = CodingAssistant(workspace=workspace)

    print(f"\nWorkspace: {workspace}\n")

    while True:
        try:
            user_input = input("You > ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\nGoodbye!")
            break

        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit"):
            print("Goodbye!")
            break
        if user_input.lower() == "clear":
            assistant.clear()
            print("Conversation cleared.\n")
            continue

        print()
        response = assistant.chat(user_input)
        print(f"Assistant > {response}\n")


if __name__ == "__main__":
    main()
