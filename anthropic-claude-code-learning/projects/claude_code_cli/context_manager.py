"""
Context Manager — Manages system prompt and Claude.md context for the assistant.
"""

from __future__ import annotations

from pathlib import Path


class ContextManager:
    """Loads and merges context from Claude.md files."""

    def __init__(self, workspace: Path) -> None:
        self.workspace = workspace.resolve()

    def load_claude_md(self) -> dict[str, str]:
        """Load Claude.md files from all three levels."""
        contexts: dict[str, str] = {}

        # Machine level
        machine = Path.home() / ".claude" / "Claude.md"
        if machine.exists():
            contexts["machine"] = machine.read_text()

        # Project level
        project = self.workspace / "Claude.md"
        if project.exists():
            contexts["project"] = project.read_text()

        # Local level
        local = self.workspace / ".claude" / "Claude.md"
        if local.exists():
            contexts["local"] = local.read_text()

        return contexts

    def merge_contexts(self, contexts: dict[str, str]) -> str:
        """Merge context from all levels into a combined context block."""
        parts = []
        for level in ("machine", "project", "local"):
            content = contexts.get(level, "").strip()
            if content:
                parts.append(f"--- {level.upper()} CONTEXT ---\n{content}")
        return "\n\n".join(parts)

    def build_system_prompt(self) -> str:
        """Build the complete system prompt with context."""
        base_prompt = (
            "You are a coding assistant with access to file and command tools. "
            f"The workspace directory is: {self.workspace}\n"
            "Use the available tools to help the user with coding tasks. "
            "Always read files before modifying them. "
            "Explain what you're doing as you work."
        )

        contexts = self.load_claude_md()
        if contexts:
            context_block = self.merge_contexts(contexts)
            base_prompt += f"\n\n{context_block}"

        return base_prompt
