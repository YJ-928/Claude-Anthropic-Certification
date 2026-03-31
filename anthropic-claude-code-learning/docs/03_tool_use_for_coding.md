# 03 — Tool Use for Coding

## How Claude Performs Actions

Claude is a language model — it produces text. To interact with the real world (read files, write code, run tests), it relies on a **tool use system** where the host application executes actions on Claude's behalf.

---

## The Tool Use Loop

```
┌──────────────────────────────────────────────────────┐
│  1. User sends request                               │
│     "Fix the bug in utils.py"                        │
├──────────────────────────────────────────────────────┤
│  2. Claude decides which tool to call                │
│     → read(file_path="utils.py")                     │
├──────────────────────────────────────────────────────┤
│  3. Application executes the tool                    │
│     → reads utils.py from disk                       │
├──────────────────────────────────────────────────────┤
│  4. Result returned to Claude                        │
│     → file contents as text                          │
├──────────────────────────────────────────────────────┤
│  5. Claude analyzes and decides next action           │
│     → edit(file_path="utils.py", changes=...)        │
├──────────────────────────────────────────────────────┤
│  6. Application executes the edit                    │
├──────────────────────────────────────────────────────┤
│  7. Claude produces final response                   │
│     "Fixed the off-by-one error on line 42."         │
└──────────────────────────────────────────────────────┘
```

---

## Core Tools in Claude Code

### `read` — Read File

Reads the contents of a file from disk.

```json
{
  "tool_name": "read",
  "input": {
    "file_path": "/project/src/utils.py"
  }
}
```

### `write` — Write File

Creates or overwrites a file.

```json
{
  "tool_name": "write",
  "input": {
    "file_path": "/project/src/new_module.py",
    "content": "def hello():\n    return 'world'\n"
  }
}
```

### `edit` — Edit File

Makes targeted edits to an existing file.

```json
{
  "tool_name": "edit",
  "input": {
    "file_path": "/project/src/utils.py",
    "old_string": "value = x + 1",
    "new_string": "value = x + 2"
  }
}
```

### `bash` — Run Command

Executes a shell command and captures output.

```json
{
  "tool_name": "bash",
  "input": {
    "command": "pytest tests/ -v"
  }
}
```

### `grep` — Search Code

Searches file contents with regex patterns.

```json
{
  "tool_name": "grep",
  "input": {
    "pattern": "def authenticate",
    "path": "/project/src/"
  }
}
```

### `glob` — Find Files

Finds files matching a glob pattern.

```json
{
  "tool_name": "glob",
  "input": {
    "pattern": "**/*.py"
  }
}
```

---

## Tool Call Data Structure

Every tool call from Claude follows this JSON structure:

```json
{
  "type": "tool_use",
  "id": "toolu_abc123",
  "name": "read",
  "input": {
    "file_path": "/project/src/utils.py"
  }
}
```

The application returns a tool result:

```json
{
  "type": "tool_result",
  "tool_use_id": "toolu_abc123",
  "content": "def process(data):\n    return data.strip()\n"
}
```

---

## Implementing a Tool Executor in Python

```python
import subprocess
from pathlib import Path
from typing import Any


def execute_tool(tool_name: str, tool_input: dict[str, Any]) -> str:
    """Execute a tool call and return the result as text."""
    match tool_name:
        case "read":
            path = Path(tool_input["file_path"])
            if not path.exists():
                return f"Error: File not found: {path}"
            return path.read_text()

        case "write":
            path = Path(tool_input["file_path"])
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(tool_input["content"])
            return f"File written: {path}"

        case "bash":
            result = subprocess.run(
                tool_input["command"],
                shell=True,
                capture_output=True,
                text=True,
                timeout=30,
            )
            output = result.stdout
            if result.returncode != 0:
                output += f"\nSTDERR:\n{result.stderr}"
            return output

        case "grep":
            result = subprocess.run(
                ["grep", "-rn", tool_input["pattern"], tool_input["path"]],
                capture_output=True,
                text=True,
            )
            return result.stdout or "No matches found."

        case _:
            return f"Unknown tool: {tool_name}"
```

---

## Tool Chaining Example

Claude often chains multiple tools for a single task:

```
Task: "Add a new endpoint to the Flask app and test it"

Tool chain:
1. grep("@app.route", "src/")        → Find existing routes
2. read("src/app.py")                → Read the application file
3. edit("src/app.py", ...)           → Add new route
4. read("tests/test_app.py")         → Read existing tests
5. edit("tests/test_app.py", ...)    → Add test for new route
6. bash("pytest tests/test_app.py")  → Run tests
```

---

## Security Considerations

- Claude Code searches code directly rather than indexing and sending to external servers
- Tool permissions can be controlled via settings
- Hooks can intercept and block sensitive tool calls
- The SDK defaults to read-only permissions

---

## Best Practices

1. **Log tool calls** — Keep a record of what tools Claude invokes for debugging
2. **Set timeouts** — Always use timeouts for command execution tools
3. **Validate paths** — Prevent path traversal attacks in file operations
4. **Limit scope** — Restrict tools to the project directory

---

## Exercises

1. Implement the `edit` tool that replaces a specific string in a file
2. Write a tool executor that logs every tool invocation to a JSON file
3. Create a mock tool system for testing without real file system access
