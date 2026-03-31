"""
Git Helpers — Utilities for working with Git in the context of Claude Code.
"""

from __future__ import annotations

import subprocess
from pathlib import Path
from typing import Any


def run_git(args: list[str], cwd: str | Path | None = None) -> str:
    """Run a git command and return stdout.

    Args:
        args: Git subcommand and arguments (e.g. ["status", "--short"]).
        cwd: Working directory (defaults to current directory).

    Returns:
        The stdout of the git command.

    Raises:
        RuntimeError: If git returns a non-zero exit code.
    """
    cmd = ["git"] + args
    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=str(cwd) if cwd else None,
    )
    if result.returncode != 0:
        raise RuntimeError(f"git {' '.join(args)} failed:\n{result.stderr}")
    return result.stdout.strip()


def get_changed_files(cwd: str | Path | None = None) -> list[str]:
    """Get a list of changed (unstaged + staged) files.

    Args:
        cwd: Repository path.

    Returns:
        List of file paths that have been modified.
    """
    output = run_git(["status", "--short", "--porcelain"], cwd=cwd)
    files = []
    for line in output.splitlines():
        # Format: "XY filename" or "XY filename -> renamed"
        if line.strip():
            parts = line[3:].split(" -> ")
            files.append(parts[-1])
    return files


def get_diff(staged: bool = False, cwd: str | Path | None = None) -> str:
    """Get the current diff.

    Args:
        staged: Whether to show only staged changes.
        cwd: Repository path.

    Returns:
        The diff output.
    """
    args = ["diff"]
    if staged:
        args.append("--cached")
    return run_git(args, cwd=cwd)


def get_current_branch(cwd: str | Path | None = None) -> str:
    """Get the name of the current branch.

    Args:
        cwd: Repository path.

    Returns:
        The current branch name.
    """
    return run_git(["branch", "--show-current"], cwd=cwd)


def get_recent_commits(count: int = 10, cwd: str | Path | None = None) -> list[dict[str, str]]:
    """Get recent commit summaries.

    Args:
        count: Number of commits to return.
        cwd: Repository path.

    Returns:
        List of dicts with 'hash', 'author', 'date', 'message' keys.
    """
    output = run_git(
        ["log", f"-{count}", "--pretty=format:%H|%an|%ad|%s", "--date=short"],
        cwd=cwd,
    )
    commits = []
    for line in output.splitlines():
        parts = line.split("|", 3)
        if len(parts) == 4:
            commits.append({
                "hash": parts[0],
                "author": parts[1],
                "date": parts[2],
                "message": parts[3],
            })
    return commits


def generate_commit_message_prompt(diff: str) -> str:
    """Generate a prompt for Claude to create a commit message.

    Args:
        diff: The git diff string.

    Returns:
        A prompt string suitable for sending to Claude.
    """
    return (
        "Based on the following git diff, generate a concise and descriptive "
        "commit message following Conventional Commits format "
        "(e.g., feat:, fix:, refactor:, docs:, test:).\n\n"
        "Rules:\n"
        "- Subject line max 72 characters\n"
        "- Use imperative mood ('add' not 'added')\n"
        "- Include a body only if the change is complex\n\n"
        f"Diff:\n```\n{diff}\n```"
    )
