#!/bin/bash
# =============================================================================
# Hook: post_file_write.sh
# Fires: AFTER Claude Code writes or modifies a file
# Purpose: Auto-format code, run linters, trigger tests on changed files
#
# Arguments passed by Claude Code:
#   $1 = absolute path of the file that was written
#
# This hook always exits 0 (non-blocking). Errors are logged but do not
# prevent Claude from continuing.
# =============================================================================

set -uo pipefail

FILE="${1:-}"
LOG_FILE=".claude/logs/post_file_write.log"
mkdir -p .claude/logs

if [[ -z "$FILE" ]]; then
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] POST_WRITE | No file path provided" >> "$LOG_FILE"
  exit 0
fi

echo "[$(date '+%Y-%m-%d %H:%M:%S')] POST_WRITE | file=$FILE" >> "$LOG_FILE"

# ---------------------------------------------------------------------------
# Python files → auto-format with black, lint with flake8
# ---------------------------------------------------------------------------
if [[ "$FILE" == *.py ]]; then
  echo "  -> Python file detected: $FILE" >> "$LOG_FILE"

  if command -v black &>/dev/null; then
    black "$FILE" --quiet 2>> "$LOG_FILE" && \
      echo "  -> black: formatted OK" >> "$LOG_FILE" || \
      echo "  -> black: formatting failed (non-fatal)" >> "$LOG_FILE"
  fi

  if command -v flake8 &>/dev/null; then
    flake8 "$FILE" --max-line-length=100 2>> "$LOG_FILE" && \
      echo "  -> flake8: no issues" >> "$LOG_FILE" || \
      echo "  -> flake8: lint warnings found (non-fatal)" >> "$LOG_FILE"
  fi
fi

# ---------------------------------------------------------------------------
# JavaScript / TypeScript → auto-format with prettier, lint with eslint
# ---------------------------------------------------------------------------
if [[ "$FILE" == *.js || "$FILE" == *.ts || "$FILE" == *.jsx || "$FILE" == *.tsx ]]; then
  echo "  -> JS/TS file detected: $FILE" >> "$LOG_FILE"

  if command -v prettier &>/dev/null; then
    prettier --write "$FILE" 2>> "$LOG_FILE" && \
      echo "  -> prettier: formatted OK" >> "$LOG_FILE" || \
      echo "  -> prettier: formatting failed (non-fatal)" >> "$LOG_FILE"
  fi

  if command -v eslint &>/dev/null; then
    eslint "$FILE" --fix --quiet 2>> "$LOG_FILE" && \
      echo "  -> eslint: no issues" >> "$LOG_FILE" || \
      echo "  -> eslint: lint warnings found (non-fatal)" >> "$LOG_FILE"
  fi
fi

# ---------------------------------------------------------------------------
# Shell scripts → validate with shellcheck
# ---------------------------------------------------------------------------
if [[ "$FILE" == *.sh ]]; then
  echo "  -> Shell script detected: $FILE" >> "$LOG_FILE"
  chmod +x "$FILE"

  if command -v shellcheck &>/dev/null; then
    shellcheck "$FILE" 2>> "$LOG_FILE" && \
      echo "  -> shellcheck: OK" >> "$LOG_FILE" || \
      echo "  -> shellcheck: warnings found (non-fatal)" >> "$LOG_FILE"
  fi
fi

# ---------------------------------------------------------------------------
# Markdown files → format with prettier if available
# ---------------------------------------------------------------------------
if [[ "$FILE" == *.md ]]; then
  if command -v prettier &>/dev/null; then
    prettier --write "$FILE" --prose-wrap always 2>> "$LOG_FILE" || true
  fi
fi

exit 0
