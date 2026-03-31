"""
Context Utilities — Helpers for loading and merging Claude.md context files.
"""

from __future__ import annotations

from pathlib import Path


CONTEXT_LEVELS = ("machine", "project", "local")


def find_claude_md_files(workspace: Path) -> dict[str, Path]:
    """Find Claude.md files at all three context levels.

    Levels:
        machine — ~/.claude/Claude.md
        project — <workspace>/Claude.md
        local   — <workspace>/.claude/Claude.md

    Args:
        workspace: Path to the project workspace.

    Returns:
        A dict mapping level names to existing file paths.
    """
    candidates = {
        "machine": Path.home() / ".claude" / "Claude.md",
        "project": workspace / "Claude.md",
        "local": workspace / ".claude" / "Claude.md",
    }
    return {level: path for level, path in candidates.items() if path.exists()}


def load_contexts(workspace: Path) -> dict[str, str]:
    """Load content from all available Claude.md files.

    Args:
        workspace: Path to the project workspace.

    Returns:
        A dict mapping level names to file contents.
    """
    files = find_claude_md_files(workspace)
    return {level: path.read_text() for level, path in files.items()}


def merge_contexts(contexts: dict[str, str], separator: str = "\n\n---\n\n") -> str:
    """Merge context from all levels (machine → project → local).

    Later levels override / append to earlier ones.

    Args:
        contexts: A dict of level → content.
        separator: String used between context blocks.

    Returns:
        Combined context string.
    """
    parts = []
    for level in CONTEXT_LEVELS:
        content = contexts.get(level, "").strip()
        if content:
            parts.append(f"[{level.upper()}]\n{content}")
    return separator.join(parts)


def generate_claude_md(
    project_name: str,
    language: str = "Python",
    conventions: list[str] | None = None,
    extra: str = "",
) -> str:
    """Generate a Claude.md template for a project.

    Args:
        project_name: Name of the project.
        language: Primary programming language.
        conventions: List of coding conventions to follow.
        extra: Additional instructions to append.

    Returns:
        The Claude.md content string.
    """
    lines = [
        f"# {project_name}",
        "",
        f"Primary language: {language}",
        "",
    ]

    if conventions:
        lines.append("## Conventions")
        for c in conventions:
            lines.append(f"- {c}")
        lines.append("")

    lines.extend([
        "## Guidelines",
        "- Write clean, well-documented code.",
        "- Follow existing project patterns.",
        "- Add tests for new functionality.",
        f"- Use {language} best practices.",
        "",
    ])

    if extra:
        lines.extend(["## Additional", extra, ""])

    return "\n".join(lines)
