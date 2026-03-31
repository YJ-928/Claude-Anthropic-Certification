# 12 — Claude Code SDK

## Overview

The Claude Code SDK is a programmatic interface for Claude Code, available as CLI, TypeScript, and Python libraries. It contains the **same tools** as the terminal version and enables integration into larger pipelines and workflows.

---

## Why Use the SDK?

| Use Case | Description |
|----------|-------------|
| Automation pipelines | Add Claude intelligence to CI/CD and build scripts |
| Helper commands | Build project-specific tooling on top of Claude Code |
| Hooks | Use Claude as a reviewer inside hook scripts |
| Batch processing | Process multiple files or tasks programmatically |
| Custom integrations | Embed Claude Code in your own applications |

---

## Installation

### Python SDK

```bash
pip install anthropic
```

### CLI

Claude Code SDK is accessed via the `claude` CLI with the `--print` or programmatic flags.

---

## Default Permissions

The SDK defaults to **read-only** permissions:

| Allowed by Default | Requires Opt-in |
|-------------------|-----------------|
| Read files | Write files |
| List directories | Edit files |
| Grep/search | Run commands |

To enable write permissions, explicitly list allowed tools.

---

## Python SDK Usage

### Basic Query (Read-Only)

```python
import subprocess
import json


def claude_query(prompt: str, project_dir: str = ".") -> str:
    """Send a read-only query to Claude Code SDK."""
    result = subprocess.run(
        [
            "claude",
            "--print",
            "--output-format", "json",
            prompt,
        ],
        capture_output=True,
        text=True,
        cwd=project_dir,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude Code error: {result.stderr}")

    response = json.loads(result.stdout)
    return response.get("result", result.stdout)
```

### Query with Write Permissions

```python
def claude_query_with_tools(
    prompt: str,
    allowed_tools: list[str] | None = None,
    project_dir: str = ".",
) -> str:
    """Send a query to Claude Code with specific tool permissions."""
    cmd = ["claude", "--print", "--output-format", "json"]

    if allowed_tools:
        for tool in allowed_tools:
            cmd.extend(["--allowedTools", tool])

    cmd.append(prompt)

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True,
        cwd=project_dir,
    )

    if result.returncode != 0:
        raise RuntimeError(f"Claude Code error: {result.stderr}")

    return result.stdout
```

### Example: Code Review Pipeline

```python
def review_file(file_path: str) -> str:
    """Use Claude Code SDK to review a file."""
    return claude_query(
        f"Review {file_path} for bugs, security issues, and style problems. "
        "Provide a summary with severity ratings.",
        project_dir=".",
    )


def generate_tests(file_path: str) -> str:
    """Use Claude Code SDK to generate tests for a file."""
    return claude_query_with_tools(
        f"Generate pytest tests for {file_path}. Write them to the tests/ directory.",
        allowed_tools=["read", "write", "edit"],
        project_dir=".",
    )


def suggest_refactoring(file_path: str) -> str:
    """Use Claude Code SDK to suggest refactoring."""
    return claude_query(
        f"Analyze {file_path} and suggest refactoring improvements. "
        "Focus on readability, maintainability, and SOLID principles.",
        project_dir=".",
    )
```

---

## Pipeline Example

```python
import json
from pathlib import Path


def code_quality_pipeline(directory: str) -> dict:
    """Run a full code quality pipeline using Claude Code SDK."""
    results = {}

    # Find all Python files
    py_files = list(Path(directory).rglob("*.py"))

    for py_file in py_files:
        file_path = str(py_file)
        print(f"Reviewing: {file_path}")

        review = claude_query(
            f"Review {file_path} for: "
            "1) Bugs and logic errors "
            "2) Security vulnerabilities "
            "3) Performance issues "
            "4) Style and readability "
            "Respond in JSON with keys: bugs, security, performance, style",
            project_dir=directory,
        )

        results[file_path] = review

    return results


def main() -> None:
    results = code_quality_pipeline("src/")
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
```

---

## SDK in Hooks

The SDK can be used inside hooks for advanced checks:

```javascript
// Post-tool-use hook that uses Claude to check for duplicate code
const { execSync } = require("child_process");

let input = "";
process.stdin.on("data", (chunk) => { input += chunk; });

process.stdin.on("end", () => {
  const toolCall = JSON.parse(input);
  const filePath = toolCall.tool_input?.file_path || "";

  // Only check files in the queries directory
  if (!filePath.includes("queries/")) {
    process.exit(0);
  }

  try {
    const result = execSync(
      `claude --print "Check if the code in ${filePath} duplicates ` +
      `any existing functionality in the queries/ directory. ` +
      `Respond with DUPLICATE or UNIQUE."`,
      { encoding: "utf-8" }
    );

    if (result.includes("DUPLICATE")) {
      console.error(`Duplicate code detected in ${filePath}. Reuse existing code.`);
      process.exit(2);
    }
  } catch (err) {
    // Don't block on SDK errors
  }

  process.exit(0);
});
```

---

## Architecture

```
┌─────────────────────────────────────────┐
│           Your Application               │
│                                         │
│   ┌──────────────────────────────────┐  │
│   │  subprocess.run("claude", ...)   │  │
│   └──────────────┬───────────────────┘  │
│                  ↓                      │
│   ┌──────────────────────────────────┐  │
│   │  Claude Code SDK                 │  │
│   │  ├─ Same tools as terminal       │  │
│   │  ├─ Default: read-only           │  │
│   │  └─ Configurable permissions     │  │
│   └──────────────┬───────────────────┘  │
│                  ↓                      │
│   ┌──────────────────────────────────┐  │
│   │  Claude API                      │  │
│   └──────────────────────────────────┘  │
└─────────────────────────────────────────┘
```

---

## Best Practices

1. **Default to read-only** — Only add write permissions when explicitly needed
2. **Use in pipelines** — SDK shines for batch operations and automated workflows
3. **Handle errors** — Always check return codes and handle SDK failures gracefully
4. **Scope permissions** — List specific tools rather than granting blanket access
5. **Use for reviews** — SDK is excellent for automated code review in CI/CD

---

## Exercises

1. Write a script that uses Claude Code SDK to review all Python files in a directory
2. Create a pipeline that generates documentation for each module
3. Build a hook that uses SDK to detect duplicate code in a specific directory
4. Compare the output of a read-only query vs one with write permissions
