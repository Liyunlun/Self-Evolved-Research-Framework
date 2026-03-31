#!/usr/bin/env bash
# SER v6 — Tool Observation Hook
# Fires on PreToolUse and PostToolUse. Appends one JSONL line per invocation.
# Budget: must complete within 50ms. Silent failure — never block research workflow.
#
# Input: JSON on stdin from Claude Code hook system
# Output: appends to logs/observations/{session}.jsonl
# Env: CLAUDE_HOOK_PHASE=pre|post
#
# Additional behaviors:
#   A. Dirty flag — PostToolUse Write/Edit → touch .claude/.ser-dirty
#   B. Review reminder — PreToolUse non-read tool + dirty flag → warn if code files changed
#   C. Commit detection — PostToolUse Bash containing "git commit" → clear dirty flag

set -o pipefail

OBS_DIR="logs/observations"
[ -d "$OBS_DIR" ] || mkdir -p "$OBS_DIR" 2>/dev/null || exit 0

# Session file: one per day (rotated)
SESSION_FILE="$OBS_DIR/$(date +%Y-%m-%d).jsonl"

# Read hook input (JSON from stdin)
INPUT=$(cat 2>/dev/null) || exit 0
[ -z "$INPUT" ] && exit 0

PHASE="${CLAUDE_HOOK_PHASE:-unknown}"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")

# Extract tool name from hook input
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")

# Append observation (atomic via >> redirect; flock not needed for append)
printf '{"type":"tool","phase":"%s","tool":"%s","ts":"%s"}\n' "$PHASE" "$TOOL" "$TS" >> "$SESSION_FILE" 2>/dev/null

DIRTY_FLAG=".claude/.ser-dirty"

# --- A. Dirty flag: mark code as modified on Write/Edit ---
if [ "$PHASE" = "post" ] && { [ "$TOOL" = "Write" ] || [ "$TOOL" = "Edit" ]; }; then
  # Check if the written file is a code file (by extension)
  FILE_PATH=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('file_path', d.get('input',{}).get('file_path','')))" 2>/dev/null || echo "")
  if [ -n "$FILE_PATH" ]; then
    EXT="${FILE_PATH##*.}"
    case ".$EXT" in
      .py|.jl|.js|.ts|.sh|.yaml|.yml|.json|.toml|.cfg|.ini|.r|.R|.go|.rs|.c|.cpp|.h|.hpp|.java)
        touch "$DIRTY_FLAG" 2>/dev/null
        ;;
    esac
  fi
fi

# --- B. Review reminder: warn if uncommitted code changes exist ---
if [ "$PHASE" = "pre" ] && [ -f "$DIRTY_FLAG" ]; then
  # Only remind on tools that indicate task-switching (not read/edit/grep/glob)
  case "$TOOL" in
    Read|Edit|Write|Grep|Glob|Skill) ;;  # skip — still coding
    *)
      # Check if git tracks code changes
      if [ -d ".git" ]; then
        CODE_DIFF=$(git diff --name-only 2>/dev/null | grep -E '\.(py|jl|js|ts|sh|yaml)$' | head -1)
        if [ -n "$CODE_DIFF" ]; then
          echo "[SER] Uncommitted code changes detected. Run code.review → code.commit before proceeding."
        fi
      fi
      ;;
  esac
fi

# --- C. Commit detection: clear dirty flag after git commit ---
if [ "$PHASE" = "post" ] && [ "$TOOL" = "Bash" ]; then
  COMMAND=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('command', d.get('input',{}).get('command','')))" 2>/dev/null || echo "")
  if echo "$COMMAND" | grep -q "git commit" 2>/dev/null; then
    rm -f "$DIRTY_FLAG" 2>/dev/null
    printf '{"type":"code_commit","ts":"%s"}\n' "$TS" >> "$SESSION_FILE" 2>/dev/null
  fi
fi

exit 0
