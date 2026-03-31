"""
Exercise 03 — Create a Claude.md File

Demonstrates programmatically generating a Claude.md project context file
by analyzing a project directory. This simulates the `/init` command.

Usage:
    python exercise_03_create_claude_md.py [project_dir]
"""

from __future__ import annotations

import sys
from pathlib import Path

import anthropic
from dotenv import load_dotenv

load_dotenv()


def scan_project(project_dir: Path) -> dict:
    """Scan a project directory and collect metadata."""
    info: dict = {
        "files": [],
        "directories": [],
        "config_files": {},
        "total_files": 0,
    }

    config_names = {
        "requirements.txt", "pyproject.toml", "setup.py", "setup.cfg",
        "package.json", "Cargo.toml", "go.mod", "Makefile",
        "Dockerfile", ".gitignore", "README.md",
    }

    for path in sorted(project_dir.rglob("*")):
        # Skip hidden dirs and common noise
        parts = path.relative_to(project_dir).parts
        if any(p.startswith(".") or p in {"__pycache__", "node_modules", ".venv", "venv"} for p in parts):
            continue

        if path.is_file():
            rel = str(path.relative_to(project_dir))
            info["files"].append(rel)
            info["total_files"] += 1

            if path.name in config_names:
                try:
                    content = path.read_text(errors="replace")[:2000]
                    info["config_files"][rel] = content
                except OSError:
                    pass
        elif path.is_dir():
            info["directories"].append(str(path.relative_to(project_dir)))

    return info


def generate_claude_md(project_dir: Path) -> str:
    """Generate a Claude.md file for the given project."""
    info = scan_project(project_dir)

    # Build a summary for Claude to analyze
    summary_parts = [
        f"Project directory: {project_dir.name}",
        f"Total files: {info['total_files']}",
        f"\nDirectories:\n" + "\n".join(f"  {d}/" for d in info["directories"][:30]),
        f"\nFiles (first 50):\n" + "\n".join(f"  {f}" for f in info["files"][:50]),
    ]

    for config_path, content in info["config_files"].items():
        summary_parts.append(f"\n--- {config_path} ---\n{content}")

    project_summary = "\n".join(summary_parts)

    client = anthropic.Anthropic()
    response = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2048,
        messages=[{
            "role": "user",
            "content": (
                "Based on this project analysis, generate a Claude.md file. "
                "Include: project name, description, tech stack, directory structure, "
                "key files, coding conventions, and common commands.\n\n"
                f"{project_summary}\n\n"
                "Output ONLY the markdown content for the Claude.md file."
            ),
        }],
    )

    return response.content[0].text


def main() -> None:
    print("=" * 60)
    print("Exercise 03 — Create Claude.md")
    print("=" * 60)

    # Use provided dir or current repo
    if len(sys.argv) > 1:
        project_dir = Path(sys.argv[1])
    else:
        project_dir = Path(__file__).parent.parent

    if not project_dir.is_dir():
        print(f"Error: {project_dir} is not a directory.")
        sys.exit(1)

    print(f"\nAnalyzing: {project_dir}")
    print("Generating Claude.md...\n")

    content = generate_claude_md(project_dir)

    output_path = project_dir / "Claude.md"
    print(f"Generated Claude.md content:\n")
    print(content)

    # Ask before writing
    answer = input(f"\nWrite to {output_path}? [y/N] ").strip().lower()
    if answer == "y":
        output_path.write_text(content)
        print(f"Written to {output_path}")
    else:
        print("Skipped writing.")


if __name__ == "__main__":
    main()
