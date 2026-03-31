# 09 — Hooks Introduction

## What Are Hooks?

Hooks are custom commands that run **before** or **after** Claude executes a tool. They let you intercept, inspect, and control tool calls — adding automated checks, blocking dangerous operations, or performing follow-up actions.

---

## Hook Types

```
┌──────────────────────────────────────────────────────┐
│              Claude Tool Execution Flow                │
│                                                      │
│  Tool Call Initiated                                 │
│       ↓                                              │
│  ┌────────────────────────┐                          │
│  │  Pre-tool-use Hook     │                          │
│  │  ├─ exit 0 → allow     │                          │
│  │  └─ exit 2 → BLOCK     │                          │
│  └────────────┬───────────┘                          │
│               ↓                                      │
│  ┌────────────────────────┐                          │
│  │  Tool Executes         │ (only if pre-hook allows)│
│  └────────────┬───────────┘                          │
│               ↓                                      │
│  ┌────────────────────────┐                          │
│  │  Post-tool-use Hook    │                          │
│  │  → feedback / actions  │                          │
│  │  (cannot block)        │                          │
│  └────────────────────────┘                          │
└──────────────────────────────────────────────────────┘
```

### Pre-tool-use Hooks

- Run **before** tool execution
- Can **inspect** the tool call (name, parameters)
- Can **block** the tool call (exit code 2)
- Can send an **error message** back to Claude via stderr

### Post-tool-use Hooks

- Run **after** tool execution
- Cannot block (tool already ran)
- Can perform follow-up actions (formatting, testing, linting)
- Can provide feedback to Claude

---

## Configuration

Hooks are defined in Claude's settings files:

- **Global**: `~/.claude/settings.json`
- **Project (shared)**: `.claude/settings.json`
- **Project (personal)**: `.claude/settings.local.json`

Or use the interactive command:

```bash
/hooks
```

### Configuration Structure

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
    ],
    "PostToolUse": [
      {
        "matcher": "write|edit",
        "hooks": [
          {
            "type": "command",
            "command": "npx prettier --write $FILE_PATH"
          }
        ]
      }
    ]
  }
}
```

---

## Exit Codes

| Code | Meaning | Pre-hook | Post-hook |
|------|---------|----------|-----------|
| `0` | Allow / success | Tool proceeds | — |
| `2` | Block | Tool is **blocked** | — (ignored) |
| Other | Error | Treated as allow | — |

When a pre-hook exits with code `2`, the stderr output is sent to Claude as a feedback message explaining why the tool was blocked.

---

## Hook Data Flow

```
Claude requests tool call
       ↓
Hook receives JSON via stdin:
{
  "session_id": "abc123",
  "tool_name": "read",
  "tool_input": {
    "file_path": "/project/.env"
  }
}
       ↓
Hook script processes data
       ↓
Hook exits with code 0 (allow) or 2 (block)
       ↓
If blocked: stderr message sent to Claude
```

---

## Common Use Cases

| Use Case | Hook Type | Description |
|----------|-----------|-------------|
| Block `.env` access | Pre-tool | Prevent reading sensitive files |
| Auto-format on save | Post-tool | Run prettier/black after writes |
| Type checking | Post-tool | Run `tsc --no-emit` after edits |
| Test runner | Post-tool | Run tests after code changes |
| Duplicate detection | Post-tool | Check for duplicate code patterns |
| Audit logging | Pre-tool | Log all tool calls for review |

---

## Best Practices

1. **Start with pre-hooks** for security (blocking sensitive file access)
2. **Use post-hooks** for quality (formatting, testing, linting)
3. **Keep hooks fast** — They run on every matching tool call
4. **Restart Claude Code** after changing hook configuration
5. **Use the matcher** to limit which tools trigger the hook

---

## Exercises

1. Describe a pre-tool-use hook that blocks write access to `migrations/` directory
2. Design a post-tool-use hook that runs `pytest` after any file edit
3. List three security-focused hooks that would protect a production project
