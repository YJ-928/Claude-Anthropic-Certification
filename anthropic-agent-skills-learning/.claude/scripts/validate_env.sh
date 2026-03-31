#!/bin/bash
# =============================================================================
# Script: validate_env.sh
# Purpose: Validate the workspace environment before a Claude Code session
# Called by: hooks/session_start.sh, or manually before starting work
#
# Checks:
#   - Required tools are installed
#   - Git repository is in good shape
#   - No sensitive files are accidentally exposed
#   - Python/Node versions meet minimums
#
# Exit codes:
#   0 = environment is valid
#   1 = critical error found (session should not proceed)
# =============================================================================

set -uo pipefail

LOG_FILE=".claude/logs/validate_env.log"
mkdir -p .claude/logs

ERRORS=0
WARNINGS=0

log() { echo "[$(date '+%Y-%m-%d %H:%M:%S')] $*" >> "$LOG_FILE"; }
ok()   { echo "  [OK]   $*"; log "OK: $*"; }
warn() { echo "  [WARN] $*"; log "WARN: $*"; WARNINGS=$((WARNINGS+1)); }
fail() { echo "  [FAIL] $*"; log "FAIL: $*"; ERRORS=$((ERRORS+1)); }

echo ""
echo "=============================="
echo "  Environment Validation"
echo "=============================="
echo ""
log "VALIDATE_ENV START"

# ---------------------------------------------------------------------------
# Section 1: Required tools
# ---------------------------------------------------------------------------
echo "--- Required Tools ---"

REQUIRED=("git" "bash")
for tool in "${REQUIRED[@]}"; do
  if command -v "$tool" &>/dev/null; then
    ok "$tool found: $(command -v "$tool")"
  else
    fail "$tool NOT FOUND — this is required"
  fi
done

echo ""

# ---------------------------------------------------------------------------
# Section 2: Recommended tools (warn, don't fail)
# ---------------------------------------------------------------------------
echo "--- Recommended Tools ---"

RECOMMENDED=("python3" "pip" "node" "npm" "black" "pytest" "prettier" "shellcheck" "jq")
for tool in "${RECOMMENDED[@]}"; do
  if command -v "$tool" &>/dev/null; then
    ok "$tool: available"
  else
    warn "$tool: not installed (recommended but not required)"
  fi
done

echo ""

# ---------------------------------------------------------------------------
# Section 3: Python version check (>= 3.9 recommended)
# ---------------------------------------------------------------------------
echo "--- Python Version ---"
if command -v python3 &>/dev/null; then
  PY_VERSION=$(python3 --version 2>&1 | awk '{print $2}')
  PY_MAJOR=$(echo "$PY_VERSION" | cut -d. -f1)
  PY_MINOR=$(echo "$PY_VERSION" | cut -d. -f2)

  if [[ "$PY_MAJOR" -ge 3 && "$PY_MINOR" -ge 9 ]]; then
    ok "Python $PY_VERSION (>= 3.9 requirement met)"
  else
    warn "Python $PY_VERSION — version 3.9+ is recommended"
  fi
else
  warn "Python 3 not found"
fi

echo ""

# ---------------------------------------------------------------------------
# Section 4: Git hygiene
# ---------------------------------------------------------------------------
echo "--- Git Status ---"
if git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "detached HEAD")
  ok "Git repository found, branch: $BRANCH"

  # Warn if on main/master with uncommitted changes
  if [[ "$BRANCH" == "main" || "$BRANCH" == "master" ]]; then
    DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
    if [[ "$DIRTY" -gt 0 ]]; then
      warn "On '$BRANCH' branch with $DIRTY uncommitted file(s) — consider a feature branch"
    fi
  fi
else
  warn "Not inside a git repository"
fi

echo ""

# ---------------------------------------------------------------------------
# Section 5: Secrets / sensitive file check
# ---------------------------------------------------------------------------
echo "--- Sensitive File Check ---"

SENSITIVE_PATTERNS=(".env" "*.pem" "*.key" "*.p12" "*.pfx" "id_rsa" "credentials.json")
FOUND_SENSITIVE=0

for pattern in "${SENSITIVE_PATTERNS[@]}"; do
  matches=$(find . -name "$pattern" -not -path "*/.git/*" -not -path "*/node_modules/*" 2>/dev/null)
  if [[ -n "$matches" ]]; then
    warn "Found sensitive file matching '$pattern': $matches"
    FOUND_SENSITIVE=1
  fi
done

if [[ "$FOUND_SENSITIVE" -eq 0 ]]; then
  ok "No sensitive files detected in workspace root"
fi

# Check .gitignore covers .env
if [[ -f ".gitignore" ]]; then
  if grep -q "\.env" .gitignore 2>/dev/null; then
    ok ".env is in .gitignore"
  else
    warn ".env is NOT in .gitignore — add it to prevent accidental commits"
  fi
fi

echo ""

# ---------------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------------
echo "=============================="
echo "  Validation Summary"
echo "  Errors:   $ERRORS"
echo "  Warnings: $WARNINGS"
echo "=============================="
echo ""
log "VALIDATE_ENV DONE | errors=$ERRORS warnings=$WARNINGS"

if [[ "$ERRORS" -gt 0 ]]; then
  echo "RESULT: FAILED — $ERRORS critical error(s) must be resolved."
  exit 1
else
  echo "RESULT: PASSED — environment is ready."
  exit 0
fi
