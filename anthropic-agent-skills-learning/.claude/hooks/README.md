# Hooks — Reference Guide

## What is a Hook?

A **Hook** is a shell script that Claude Code **automatically executes** at
specific points in its lifecycle — before or after certain events happen.

Hooks let you automate reactions to Claude's actions: format code after a file
is saved, block a dangerous command before it runs, log every tool call for
auditing, or set up the environment when a session starts.

You write the hook once. Claude Code fires it for you, every time, automatically.

---

## How Hooks Work — The Execution Model

```
Claude decides to run a tool (e.g. write a file)
         │
         ▼
pre_tool_call hook fires ──► exit 1? ──► BLOCK the action, show error
         │
     exit 0
         │
         ▼
   Tool executes (file is written)
         │
         ▼
post_tool_call hook fires ──► runs side effects (format, lint, log)
         │
         ▼
   Claude continues
```

**Pre-hooks** can BLOCK. Return exit code `1` to stop the action.
**Post-hooks** react. They can log, format, or trigger follow-up tasks.

---

## The Lifecycle Events (All Hook Types)

| Hook File Name | Fires When | Can Block? | Common Use |
|---|---|---|---|
| `session_start.sh` | Claude Code session opens | No | Validate env, print context, check tools |
| `pre_tool_call.sh` | Before ANY tool runs | **Yes** | Block dangerous commands, validate args |
| `post_tool_call.sh` | After ANY tool completes | No | Log all tool usage, audit trail |
| `pre_file_write.sh` | Before a file is saved | **Yes** | Lint check, reject invalid files |
| `post_file_write.sh` | After a file is saved | No | Auto-format, run tests, git add |
| `on_error.sh` | When Claude hits an error | No | Alert, log, rollback |
| `session_end.sh` | When the session closes | No | Clean up, commit log, summary |

---

## Hook Arguments

Claude Code passes information to each hook via positional arguments:

```bash
# pre_tool_call.sh
$1 = tool name         (e.g. "run_in_terminal", "replace_string_in_file")
$2 = tool arguments    (JSON string with all parameters)

# post_file_write.sh
$1 = absolute file path that was written

# session_start.sh
$1 = workspace path    (the root of the project)
```

Always check `${1:-}` with a default to avoid errors if args are missing.

---

## Exit Codes

| Exit Code | Meaning |
|---|---|
| `0` | Success — allow the action / hook ran fine |
| `1` | **BLOCK** (pre-hooks only) — stop the action, surface message to Claude |
| Any non-zero | Same as `1` for blocking hooks |

Post-hooks should always `exit 0` unless you intentionally want to surface an error.

---

## Hooks in This Workspace

### `pre_tool_call.sh`
**Purpose:** Security guard — runs before every tool call.

What it does:
- Blocks destructive shell patterns (`rm -rf /`, `dd if=/dev/zero`, fork bombs)
- Blocks writes to protected system paths (`/etc/`, `/sys/`, `/boot/`)
- Blocks force-push and `git reset --hard` without manual confirmation
- Logs every tool call to `.claude/logs/pre_tool_call.log`

```bash
# Called automatically. You can also test it manually:
.claude/hooks/pre_tool_call.sh run_in_terminal '{"command":"rm -rf /"}'
# → exits 1, prints BLOCKED message
```

### `post_file_write.sh`
**Purpose:** Code quality enforcer — runs after every file write.

What it does:
- Python files → runs `black` (formatter) and `flake8` (linter)
- JS/TS files → runs `prettier` (formatter) and `eslint` (linter)
- Shell files → runs `shellcheck`, sets executable bit
- Markdown files → runs `prettier` for prose wrap
- Logs all actions to `.claude/logs/post_file_write.log`

```bash
# Called automatically. You can also test it manually:
.claude/hooks/post_file_write.sh /path/to/file.py
```

### `session_start.sh`
**Purpose:** Welcome screen + environment check.

What it does:
- Prints git branch and uncommitted file count
- Shows availability of recommended tools with versions
- Reports whether a `.env` file is present
- Logs session start time to `.claude/logs/session_start.log`

```bash
# Called automatically at session open. Also useful to run manually:
.claude/hooks/session_start.sh
```

---

## How to Create a New Hook

### Step 1 — Create the script file

```bash
touch .claude/hooks/your_hook.sh
chmod +x .claude/hooks/your_hook.sh
```

### Step 2 — Write the script

```bash
#!/bin/bash
# Hook: your_hook.sh
# Fires: [when this fires]
# Purpose: [what this does]

set -euo pipefail

# Your logic here
TOOL_NAME="${1:-}"
echo "Hook fired for: $TOOL_NAME"

exit 0   # always exit 0 for non-blocking hooks
         # exit 1 to BLOCK (pre-hooks only)
```

### Step 3 — Register it

Hooks are registered in your Claude Code / VS Code configuration.
The hook name maps to the lifecycle event it should fire on.

```json
{
  "hooks": {
    "pre_tool_call": ".claude/hooks/pre_tool_call.sh",
    "post_file_write": ".claude/hooks/post_file_write.sh",
    "session_start": ".claude/hooks/session_start.sh"
  }
}
```

---

## Hook Anatomy — Best Practices

```bash
#!/bin/bash
# =======================================================
# Hook: name.sh
# Fires: [lifecycle event]
# Purpose: [one line]
# Arguments: $1 = ..., $2 = ...
# Exit: 0 = proceed, 1 = block (pre-hooks only)
# =======================================================

set -euo pipefail                        # fail fast on errors

# Always use defaults for arguments
TOOL_NAME="${1:-}"
TOOL_ARGS="${2:-}"

# Log to a file (don't print noise to stdout for post-hooks)
LOG_FILE=".claude/logs/hook_name.log"
mkdir -p .claude/logs
echo "[$(date '+%Y-%m-%d %H:%M:%S')] $TOOL_NAME" >> "$LOG_FILE"

# Your logic
if [[ "$TOOL_NAME" == "run_in_terminal" ]]; then
  # do something
  :
fi

exit 0
```

---

## Logging Convention

All hooks in this workspace write to `.claude/logs/`:

```
.claude/logs/
├── pre_tool_call.log      ← every tool call with tool name + args
├── post_file_write.log    ← every file write with formatter results
├── session_start.log      ← session timestamps
├── run_tests.log          ← test run output
└── validate_env.log       ← env check results
```

Never log secrets or credentials. Log tool names, file paths, timestamps, and outcomes only.

---

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---|---|---|
| Missing `exit 0` in post-hook | Hook exits with `1`, Claude sees an error | Always explicitly `exit 0` |
| `set -e` without defaults | Hook crashes on missing args | Use `${1:-}` pattern |
| Blocking in a post-hook | Post-hooks can't stop actions after the fact | Only block in pre-hooks |
| Printing too much stdout | Clutters Claude's output | Use a log file, not `echo` for routine messages |
| Hardcoding paths | Breaks on different machines | Use relative paths from workspace root |

---

## Quick Reference

```
Pre-hooks:    Run BEFORE a tool call. Can block (exit 1). Block = stop the action.
Post-hooks:   Run AFTER a tool call. Always non-blocking. Used for side effects.
Arguments:    $1 = tool name or file path, $2 = JSON args (where applicable)
Log location: .claude/logs/
Registration: Configured in VS Code / Claude Code settings
```
