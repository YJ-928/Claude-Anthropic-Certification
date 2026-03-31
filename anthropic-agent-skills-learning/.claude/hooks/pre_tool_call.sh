#!/bin/bash
# =============================================================================
# Hook: pre_tool_call.sh
# Fires: BEFORE any tool is executed by Claude Code
# Purpose: Validate and block potentially dangerous operations
#
# Arguments passed by Claude Code:
#   $1 = tool name (e.g. "run_in_terminal", "replace_string_in_file")
#   $2 = serialized tool arguments (JSON string)
#
# Exit codes:
#   0 = allow the tool call to proceed
#   1 = BLOCK the tool call (Claude will see an error and stop)
# =============================================================================

set -euo pipefail

TOOL_NAME="${1:-}"
TOOL_ARGS="${2:-}"

LOG_FILE=".claude/logs/pre_tool_call.log"
mkdir -p .claude/logs
echo "[$(date '+%Y-%m-%d %H:%M:%S')] PRE  | tool=$TOOL_NAME | args=$TOOL_ARGS" >> "$LOG_FILE"

# ---------------------------------------------------------------------------
# Rule 1: Block destructive shell commands
# ---------------------------------------------------------------------------
if [[ "$TOOL_NAME" == "run_in_terminal" ]]; then
  DANGEROUS_PATTERNS=(
    "rm -rf /"
    "rm -rf ~"
    "rm -rf \$HOME"
    "dd if=/dev/zero"
    "mkfs"
    "> /dev/sda"
    "chmod -R 777 /"
    "fork bomb"
    ":(){ :|:& };:"
  )

  for pattern in "${DANGEROUS_PATTERNS[@]}"; do
    if echo "$TOOL_ARGS" | grep -qF "$pattern"; then
      echo "BLOCKED: Dangerous command pattern detected: '$pattern'" >&2
      exit 1
    fi
  done
fi

# ---------------------------------------------------------------------------
# Rule 2: Block writes to critical system paths
# ---------------------------------------------------------------------------
if [[ "$TOOL_NAME" == "replace_string_in_file" || "$TOOL_NAME" == "create_file" ]]; then
  PROTECTED_PATHS=(
    "/etc/"
    "/sys/"
    "/proc/"
    "/boot/"
    "/usr/bin/"
    "/usr/sbin/"
  )

  for path in "${PROTECTED_PATHS[@]}"; do
    if echo "$TOOL_ARGS" | grep -q "$path"; then
      echo "BLOCKED: Write to protected system path '$path' is not allowed." >&2
      exit 1
    fi
  done
fi

# ---------------------------------------------------------------------------
# Rule 3: Block git force-push and hard reset without confirmation
# ---------------------------------------------------------------------------
if [[ "$TOOL_NAME" == "run_in_terminal" ]]; then
  if echo "$TOOL_ARGS" | grep -qE 'git push.*--force|git reset --hard'; then
    echo "BLOCKED: Destructive git operation requires explicit user confirmation." >&2
    echo "Run the command manually in the terminal if you are sure." >&2
    exit 1
  fi
fi

# All checks passed — allow the tool call
exit 0
