#!/bin/bash
# =============================================================================
# Script: run_tests.sh
# Purpose: Unified test runner — detects project type and runs appropriate tests
# Called by: hooks/post_file_write.sh, Claude Code agents, or manually
#
# Usage:
#   .claude/scripts/run_tests.sh             # run all tests
#   .claude/scripts/run_tests.sh src/auth    # run tests for a specific module
# =============================================================================

set -euo pipefail

TARGET="${1:-}"
LOG_FILE=".claude/logs/run_tests.log"
mkdir -p .claude/logs

echo "[$(date '+%Y-%m-%d %H:%M:%S')] RUN_TESTS | target=${TARGET:-all}" >> "$LOG_FILE"
echo ""
echo "=============================="
echo "  Running Tests"
echo "  Target: ${TARGET:-all}"
echo "=============================="
echo ""

PASS=0
FAIL=0

# ---------------------------------------------------------------------------
# Python — pytest
# ---------------------------------------------------------------------------
run_python_tests() {
  if ! command -v pytest &>/dev/null; then
    echo "[SKIP] pytest not installed. Run: pip install pytest"
    return
  fi

  echo ">>> Python Tests (pytest)"
  if [[ -n "$TARGET" ]]; then
    pytest "$TARGET" -v --tb=short 2>&1 | tee -a "$LOG_FILE" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
  else
    pytest tests/ -v --tb=short 2>&1 | tee -a "$LOG_FILE" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
  fi
  echo ""
}

# ---------------------------------------------------------------------------
# JavaScript / TypeScript — npm test or jest
# ---------------------------------------------------------------------------
run_js_tests() {
  if [[ -f "package.json" ]]; then
    echo ">>> JavaScript/TypeScript Tests (npm test)"
    npm test --silent 2>&1 | tee -a "$LOG_FILE" && PASS=$((PASS+1)) || FAIL=$((FAIL+1))
    echo ""
  fi
}

# ---------------------------------------------------------------------------
# Shell scripts — shellcheck
# ---------------------------------------------------------------------------
run_shell_checks() {
  if command -v shellcheck &>/dev/null; then
    echo ">>> Shell Script Checks (shellcheck)"
    find . -name "*.sh" -not -path "*/.git/*" -not -path "*/node_modules/*" | while read -r script; do
      shellcheck "$script" && echo "  OK: $script" || echo "  WARN: $script"
    done 2>&1 | tee -a "$LOG_FILE"
    echo ""
  fi
}

# Detect and run applicable test suites
if [[ -f "requirements.txt" || -f "setup.py" || -f "pyproject.toml" || -d "tests" ]]; then
  run_python_tests
fi

if [[ -f "package.json" ]]; then
  run_js_tests
fi

run_shell_checks

# Summary
echo "=============================="
echo "  Results: $PASS passed, $FAIL failed"
echo "=============================="
echo "[$(date '+%Y-%m-%d %H:%M:%S')] RUN_TESTS DONE | pass=$PASS fail=$FAIL" >> "$LOG_FILE"

[[ "$FAIL" -eq 0 ]] && exit 0 || exit 1
