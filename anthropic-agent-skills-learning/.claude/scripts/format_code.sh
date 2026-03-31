#!/bin/bash
# =============================================================================
# Script: format_code.sh
# Purpose: Format all source files in the workspace by language
# Called by: Manually, or by hooks/post_file_write.sh
#
# Usage:
#   .claude/scripts/format_code.sh           # format all files
#   .claude/scripts/format_code.sh src/      # format specific directory
# =============================================================================

set -uo pipefail

TARGET="${1:-.}"
LOG_FILE=".claude/logs/format_code.log"
mkdir -p .claude/logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] FORMAT | target=$TARGET" >> "$LOG_FILE"
echo ""
echo "=============================="
echo "  Formatting Code"
echo "  Target: $TARGET"
echo "=============================="
echo ""

# ---------------------------------------------------------------------------
# Python — black + isort
# ---------------------------------------------------------------------------
if command -v black &>/dev/null; then
  echo ">>> Python (black)"
  black "$TARGET" --line-length 100 --quiet 2>&1 | tee -a "$LOG_FILE"
  echo "  black: done"
else
  echo "  [SKIP] black not installed. Run: pip install black"
fi

if command -v isort &>/dev/null; then
  echo ">>> Python imports (isort)"
  isort "$TARGET" --profile black --quiet 2>&1 | tee -a "$LOG_FILE"
  echo "  isort: done"
else
  echo "  [SKIP] isort not installed. Run: pip install isort"
fi

echo ""

# ---------------------------------------------------------------------------
# JavaScript / TypeScript / JSON / Markdown — prettier
# ---------------------------------------------------------------------------
if command -v prettier &>/dev/null; then
  echo ">>> JS/TS/JSON/Markdown (prettier)"
  prettier --write "$TARGET/**/*.{js,ts,jsx,tsx,json,md}" \
    --ignore-unknown \
    --log-level warn 2>&1 | tee -a "$LOG_FILE"
  echo "  prettier: done"
else
  echo "  [SKIP] prettier not installed. Run: npm install -g prettier"
fi

echo ""

# ---------------------------------------------------------------------------
# Shell scripts — shfmt (if available)
# ---------------------------------------------------------------------------
if command -v shfmt &>/dev/null; then
  echo ">>> Shell scripts (shfmt)"
  find "$TARGET" -name "*.sh" -not -path "*/.git/*" -not -path "*/node_modules/*" \
    -exec shfmt -w -i 2 {} \;
  echo "  shfmt: done"
else
  echo "  [SKIP] shfmt not installed (optional)"
fi

echo ""
echo "=============================="
echo "  Formatting complete"
echo "=============================="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] FORMAT DONE" >> "$LOG_FILE"
exit 0
