# Scripts — Reference Guide

## What is a Script?

A **Script** is a reusable shell utility that lives in `.claude/scripts/`.
Scripts are **not auto-executed** by Claude Code — they are helper programs
that hooks, agents, or skills call when they need to do a job.

Think of scripts as the **implementation layer** and hooks as the **trigger layer**:

```
Hook fires (trigger)
    └──► calls Script (implementation)
              └──► does the actual work (format, test, validate)
```

You can also run scripts manually from the terminal at any time.

---

## Scripts vs Hooks — Key Difference

| | Hooks | Scripts |
|---|---|---|
| **Triggered by** | Claude Code lifecycle events automatically | Hooks, agents, or manual terminal calls |
| **Auto-executed** | Yes — fires on its own | No — must be called explicitly |
| **Purpose** | React to events, block actions | Do the actual work (format, test, check) |
| **Example** | `post_file_write.sh` detects a `.py` file | `format_code.sh` actually runs black/prettier |

---

## Scripts in This Workspace

### `run_tests.sh`
**Purpose:** Unified test runner that detects your project type and runs the right tests.

**What it does:**
- Detects Python project (`requirements.txt`, `setup.py`, `pyproject.toml`, `tests/`) → runs `pytest`
- Detects Node project (`package.json`) → runs `npm test`
- Always runs `shellcheck` on all `.sh` files
- Accepts an optional target path to run tests for a specific module only
- Logs results to `.claude/logs/run_tests.log`
- Exits `0` if all pass, `1` if any fail

```bash
# Run all tests
.claude/scripts/run_tests.sh

# Run tests for a specific module
.claude/scripts/run_tests.sh src/auth
```

### `format_code.sh`
**Purpose:** Format all source files in the workspace (or a specific directory).

**What it does:**
- Python → `black` (formatter, line length 100) + `isort` (import sorting)
- JS/TS/JSON/Markdown → `prettier`
- Shell scripts → `shfmt` (if installed)
- Accepts an optional path argument; defaults to current directory
- Logs to `.claude/logs/format_code.log`

```bash
# Format everything
.claude/scripts/format_code.sh

# Format only the src/ directory
.claude/scripts/format_code.sh src/
```

### `validate_env.sh`
**Purpose:** Pre-flight check — validates your environment before starting work.

**What it does:**
- Checks required tools (`git`, `bash`) — fails if missing
- Checks recommended tools (`python3`, `node`, `black`, `pytest`, etc.) — warns if missing
- Checks Python version (warns if < 3.9)
- Checks git branch and warns about uncommitted changes on `main`/`master`
- Scans for sensitive files (`.env`, `.pem`, `.key`, `id_rsa`) and checks `.gitignore`
- Prints a pass/fail summary with error and warning counts

```bash
# Run before starting a session
.claude/scripts/validate_env.sh

# Example output:
# [OK]   git found: /usr/bin/git
# [OK]   python3: available
# [WARN] prettier: not installed (recommended but not required)
# [OK]   .env is in .gitignore
# RESULT: PASSED — environment is ready.
```

---

## How to Create a New Script

### Step 1 — Create the file

```bash
touch .claude/scripts/your_script.sh
chmod +x .claude/scripts/your_script.sh
```

### Step 2 — Write it following the standard template

```bash
#!/bin/bash
# =============================================================================
# Script: your_script.sh
# Purpose: One line description of what this does
# Called by: [which hook or agent calls this]
#
# Usage:
#   .claude/scripts/your_script.sh              # default behaviour
#   .claude/scripts/your_script.sh <argument>   # with optional argument
# =============================================================================

set -euo pipefail

# Accept optional arguments with defaults
TARGET="${1:-.}"
LOG_FILE=".claude/logs/your_script.log"
mkdir -p .claude/logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] YOUR_SCRIPT START | target=$TARGET" >> "$LOG_FILE"
echo ""
echo "=============================="
echo "  Running Your Script"
echo "=============================="
echo ""

# --- Your logic here ---


echo ""
echo "=============================="
echo "  Done"
echo "=============================="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] YOUR_SCRIPT DONE" >> "$LOG_FILE"
exit 0
```

### Step 3 — Call it from a hook or agent

From a hook:
```bash
# Inside post_file_write.sh
if [[ "$FILE" == *.py ]]; then
  .claude/scripts/run_tests.sh "$FILE"
fi
```

From Claude directly (Claude can run it as a terminal command):
```
Run .claude/scripts/validate_env.sh
```

---

## Script Design Principles

| Principle | Why |
|---|---|
| **Accept arguments** | Makes the script reusable for both full-workspace and single-file use |
| **Always log** | Write to `.claude/logs/` so there is an audit trail |
| **Exit codes matter** | `0` = success, non-zero = failure. Hooks and agents check these |
| **Non-destructive by default** | Scripts should never delete or overwrite without being explicit |
| **Idempotent** | Running the same script twice should produce the same result |
| **Graceful tool checks** | Use `command -v tool` before calling it; skip with a warning if missing |

---

## Calling Scripts from Claude Code

You can ask Claude to run any script directly:

> "Run the test suite"  →  Claude runs `.claude/scripts/run_tests.sh`
> "Format all the code" →  Claude runs `.claude/scripts/format_code.sh`
> "Check my environment" → Claude runs `.claude/scripts/validate_env.sh`

Claude Code knows about these scripts because they are listed in `CLAUDE.md`
under "Key Commands".

---

## Logging Convention

All scripts write to `.claude/logs/`:

```
.claude/logs/
├── run_tests.log       ← test runner output
├── format_code.log     ← formatter output
└── validate_env.log    ← env validation results
```

Log format used throughout this workspace:
```
[2026-03-24 14:05:32] SCRIPT_NAME | key=value | key=value
```

---

## Common Mistakes to Avoid

| Mistake | Problem | Fix |
|---|---|---|
| No `chmod +x` | Script can't be executed | `chmod +x .claude/scripts/*.sh` |
| `set -e` only (no `set -u`) | Undefined variables silently expand to empty | Use `set -euo pipefail` |
| Hardcoding absolute paths | Breaks on other machines | Use `$PWD` or relative paths |
| No tool availability check | Script crashes if `black`/`prettier` not installed | Check with `command -v` first |
| Writing to stdout excessively | Clutters output | Log routine info to `.claude/logs/`, only print summaries to stdout |

---

## Quick Reference

```
Location:        .claude/scripts/
Auto-executed:   No — must be called by a hook, agent, or manually
Permissions:     Must be chmod +x to run
Arguments:       Use ${1:-default} pattern for optional args
Logging:         Always write to .claude/logs/<script_name>.log
Exit codes:      0 = success, 1 = failure
Called from:     Hooks (auto), agents (on-demand), Claude (via terminal), manually
```
