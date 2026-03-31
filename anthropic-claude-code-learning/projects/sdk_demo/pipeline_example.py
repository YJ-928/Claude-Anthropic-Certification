"""
SDK Demo — Pipeline example using the Claude Code SDK.

Demonstrates chaining multiple Claude Code calls into an automation
pipeline: review → refactor → generate tests.

Usage:
    python projects/sdk_demo/pipeline_example.py <file_path>
"""

from __future__ import annotations

import subprocess
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class PipelineResult:
    """Result from one stage of the pipeline."""

    stage: str
    output: str
    success: bool


def claude_query(prompt: str, *, allowed_tools: list[str] | None = None, max_turns: int = 3) -> str:
    """Execute a Claude Code query."""
    cmd = ["claude", "--print"]

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    cmd.extend(["--max-turns", str(max_turns)])
    cmd.extend(["--", prompt])

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        timeout=120,
        cwd=str(Path.cwd()),
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude CLI failed: {result.stderr}")

    return result.stdout.strip()


def code_review_pipeline(file_path: str) -> list[PipelineResult]:
    """Run a code review pipeline on the given file.

    Stage 1: Code Review — Read the file and provide feedback.
    Stage 2: Suggest Refactoring — Based on the review, suggest improvements.
    Stage 3: Generate Tests — Generate unit tests for the file.
    """
    results: list[PipelineResult] = []

    # Stage 1: Review
    print(f"\n{'='*60}")
    print("Stage 1: Code Review")
    print(f"{'='*60}")
    try:
        review = claude_query(
            f"Read the file '{file_path}' and provide a code review. "
            "Focus on bugs, style, and potential improvements. Be concise.",
            allowed_tools=["read_file"],
        )
        results.append(PipelineResult("review", review, True))
        print(review)
    except (RuntimeError, FileNotFoundError) as e:
        results.append(PipelineResult("review", str(e), False))
        print(f"Error: {e}")
        return results

    # Stage 2: Refactoring suggestions
    print(f"\n{'='*60}")
    print("Stage 2: Refactoring Suggestions")
    print(f"{'='*60}")
    try:
        refactor = claude_query(
            f"Read '{file_path}'. Based on this review:\n\n{review}\n\n"
            "Suggest specific refactoring changes with code examples. "
            "Do NOT modify the file — only show what you would change.",
            allowed_tools=["read_file"],
        )
        results.append(PipelineResult("refactor", refactor, True))
        print(refactor)
    except (RuntimeError, FileNotFoundError) as e:
        results.append(PipelineResult("refactor", str(e), False))
        print(f"Error: {e}")

    # Stage 3: Generate tests
    print(f"\n{'='*60}")
    print("Stage 3: Generate Tests")
    print(f"{'='*60}")
    try:
        tests = claude_query(
            f"Read '{file_path}' and generate pytest unit tests for it. "
            "Cover happy path, edge cases, and error handling.",
            allowed_tools=["read_file"],
        )
        results.append(PipelineResult("tests", tests, True))
        print(tests)
    except (RuntimeError, FileNotFoundError) as e:
        results.append(PipelineResult("tests", str(e), False))
        print(f"Error: {e}")

    return results


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: python pipeline_example.py <file_path>")
        print("Example: python pipeline_example.py utils/tool_parser.py")
        sys.exit(1)

    target_file = sys.argv[1]

    if not Path(target_file).exists():
        print(f"Error: File '{target_file}' not found.")
        sys.exit(1)

    print(f"Running code review pipeline on: {target_file}")
    results = code_review_pipeline(target_file)

    # Summary
    print(f"\n{'='*60}")
    print("Pipeline Summary")
    print(f"{'='*60}")
    for r in results:
        status = "PASS" if r.success else "FAIL"
        print(f"  [{status}] {r.stage}")


if __name__ == "__main__":
    main()
