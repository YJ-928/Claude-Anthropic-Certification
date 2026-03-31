#!/bin/bash
# =============================================================================
# Hook: session_start.sh
# Fires: At the START of every Claude Code session in this workspace
# Purpose: Validate environment, print session context, check prerequisites
#
# This hook runs once per session. It is non-blocking (always exits 0)
# but prints warnings if the environment is missing recommended tools.
# =============================================================================

set -uo pipefail

LOG_FILE=".claude/logs/session_start.log"
mkdir -p .claude/logs

echo ""
echo "======================================================"
echo "  Claude Code Session Started"
echo "  Workspace: Claude Anthropic Certification"
echo "  Date: $(date '+%Y-%m-%d %H:%M:%S')"
echo "======================================================"
echo ""

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION START" >> "$LOG_FILE"

# ---------------------------------------------------------------------------
# Check: Git status
# ---------------------------------------------------------------------------
if command -v git &>/dev/null && git rev-parse --is-inside-work-tree &>/dev/null 2>&1; then
  BRANCH=$(git branch --show-current 2>/dev/null || echo "unknown")
  DIRTY=$(git status --porcelain 2>/dev/null | wc -l | tr -d ' ')
  echo "Git branch   : $BRANCH"
  echo "Uncommitted  : $DIRTY file(s) modified"
  echo "[$(date '+%Y-%m-%d %H:%M:%S')] git branch=$BRANCH dirty=$DIRTY" >> "$LOG_FILE"
else
  echo "Git          : not a git repository (or git not installed)"
fi

echo ""

# ---------------------------------------------------------------------------
# Check: Recommended tools
# ---------------------------------------------------------------------------
echo "Tool availability:"

TOOLS=("python3" "node" "npm" "black" "flake8" "prettier" "eslint" "shellcheck" "jq")

for tool in "${TOOLS[@]}"; do
  if command -v "$tool" &>/dev/null; then
    VERSION=$("$tool" --version 2>/dev/null | head -1 || echo "installed")
    printf "  %-12s : OK  (%s)\n" "$tool" "$VERSION"
  else
    printf "  %-12s : MISSING (optional)\n" "$tool"
  fi
done

echo ""

# ---------------------------------------------------------------------------
# Check: .env file presence (do NOT print its contents)
# ---------------------------------------------------------------------------
if [[ -f ".env" ]]; then
  echo "Environment  : .env file found"
else
  echo "Environment  : No .env file (create one if API keys are needed)"
fi

# ---------------------------------------------------------------------------
# Check: .claude/logs directory
# ---------------------------------------------------------------------------
echo "Logs         : .claude/logs/ (pre_tool_call.log, post_file_write.log)"
echo ""

echo "Session context loaded. Ready."
echo "======================================================"
echo ""

echo "[$(date '+%Y-%m-%d %H:%M:%S')] SESSION START COMPLETE" >> "$LOG_FILE"
exit 0
