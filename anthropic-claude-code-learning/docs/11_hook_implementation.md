# 11 — Hook Implementation

## End-to-End: Building an `.env` Protection Hook

This guide walks through implementing a complete pre-tool-use hook that prevents Claude from reading `.env` files.

---

## Step 1: Configuration

Create or update `.claude/settings.local.json`:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "read|grep",
        "hooks": [
          {
            "type": "command",
            "command": "node ./hooks/read_hook.js"
          }
        ]
      }
    ]
  }
}
```

### Configuration Breakdown

| Field | Value | Description |
|-------|-------|-------------|
| `PreToolUse` | — | Hook runs before tool execution |
| `matcher` | `"read\|grep"` | Triggers on `read` and `grep` tools (both can access file contents) |
| `command` | `"node ./hooks/read_hook.js"` | Script to execute |

---

## Step 2: Hook Script

Create `hooks/read_hook.js`:

```javascript
#!/usr/bin/env node

/**
 * Pre-tool-use hook that blocks access to .env files.
 *
 * Receives tool call data as JSON via stdin.
 * Exit 0 = allow, Exit 2 = block.
 */

let input = "";

process.stdin.on("data", (chunk) => {
  input += chunk;
});

process.stdin.on("end", () => {
  try {
    const toolCall = JSON.parse(input);

    // Extract file path from tool input
    // Different tools use different parameter names
    const filePath =
      toolCall.tool_input?.file_path ||
      toolCall.tool_input?.path ||
      "";

    // Check if the file path references a .env file
    if (filePath.includes(".env")) {
      console.error(
        `BLOCKED: Access to "${filePath}" denied by security hook. ` +
        `.env files contain sensitive credentials and must not be read.`
      );
      process.exit(2);
    }

    // Allow all other file access
    process.exit(0);
  } catch (err) {
    // If JSON parsing fails, allow the operation
    // (fail-open for non-critical hooks)
    console.error(`Hook error: ${err.message}`);
    process.exit(0);
  }
});
```

---

## Step 3: Understanding the JSON Payload

When Claude calls a tool, the hook receives this JSON via stdin:

```json
{
  "session_id": "sess_abc123def456",
  "tool_name": "read",
  "tool_input": {
    "file_path": "/project/.env"
  }
}
```

For `grep`, the structure differs slightly:

```json
{
  "session_id": "sess_abc123def456",
  "tool_name": "grep",
  "tool_input": {
    "pattern": "API_KEY",
    "path": "/project/.env"
  }
}
```

This is why the hook checks both `file_path` and `path`.

---

## Step 4: Testing

1. **Restart Claude Code** (required after hook changes)
2. Ask Claude to read the `.env` file:

```
> Read the .env file and show me the contents
```

Expected behavior:
- Hook intercepts the `read` tool call
- Detects `.env` in the file path
- Exits with code 2
- Claude receives: "BLOCKED: Access to .env denied by security hook..."
- Claude responds: "I can't access .env files due to security restrictions."

3. Test with grep:

```
> Search for API_KEY in the project files
```

If Claude tries to grep `.env`, the hook blocks that too.

---

## Step 5: Extending the Hook

### Block Multiple Sensitive Patterns

```javascript
const BLOCKED_PATTERNS = [
  ".env",
  ".secret",
  "credentials",
  "private_key",
  "id_rsa",
];

const isBlocked = BLOCKED_PATTERNS.some((pattern) =>
  filePath.toLowerCase().includes(pattern)
);

if (isBlocked) {
  console.error(`BLOCKED: Access to "${filePath}" denied. Matches sensitive file pattern.`);
  process.exit(2);
}
```

### Allow Specific `.env` Files

```javascript
const ALLOWED_ENV_FILES = [".env.example", ".env.template"];

if (filePath.includes(".env")) {
  const isAllowed = ALLOWED_ENV_FILES.some((f) => filePath.endsWith(f));
  if (!isAllowed) {
    console.error(`BLOCKED: Access to "${filePath}" denied.`);
    process.exit(2);
  }
}
```

---

## Python Alternative

The same hook can be implemented in Python:

```python
#!/usr/bin/env python3
"""Pre-tool-use hook to block .env file access."""

import json
import sys


def main() -> None:
    data = json.load(sys.stdin)
    file_path = data.get("tool_input", {}).get("file_path", "")
    file_path = file_path or data.get("tool_input", {}).get("path", "")

    if ".env" in file_path:
        print(
            f'BLOCKED: Access to "{file_path}" denied by security hook.',
            file=sys.stderr,
        )
        sys.exit(2)

    sys.exit(0)


if __name__ == "__main__":
    main()
```

Configuration for Python:

```json
{
  "hooks": {
    "PreToolUse": [
      {
        "matcher": "read|grep",
        "hooks": [
          {
            "type": "command",
            "command": "python3 ./hooks/read_hook.py"
          }
        ]
      }
    ]
  }
}
```

---

## Architecture Diagram

```
Claude decides: read(".env")
       ↓
┌──────────────────────────────┐
│ Pre-tool-use Hook Pipeline   │
│                              │
│ 1. Match tool: read ✓       │
│ 2. Pipe JSON to hook stdin   │
│ 3. Hook parses JSON          │
│ 4. Hook checks file_path    │
│ 5. ".env" found → exit(2)   │
│ 6. stderr → Claude feedback  │
└──────────────────────────────┘
       ↓
Claude: "I cannot access .env files."
```

---

## Key Takeaways

1. **stdin** delivers tool call data as JSON
2. **stdout** is ignored; **stderr** is sent to Claude as feedback
3. **Exit code 0** allows the tool; **exit code 2** blocks it
4. Always check multiple path fields (`file_path`, `path`) for compatibility
5. **Restart Claude Code** after any hook changes

---

## Exercises

1. Implement the `.env` protection hook and test it
2. Extend the hook to block access to any file matching `*.secret.*`
3. Add logging to the hook that writes blocked attempts to a log file
4. Create a post-tool-use hook that logs all successful file reads to an audit file
