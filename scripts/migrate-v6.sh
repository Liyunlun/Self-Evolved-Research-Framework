#!/usr/bin/env bash
# SER v5 → v6 Migration Script
# Converts an existing SER v5 project to v6 architecture.
#
# Usage:
#   cd your-ser-v5-project/
#   bash /path/to/ser-v6/scripts/migrate-v6.sh
#
# Three-phase migration: Prepare → Switch → Verify+Rollback

set -euo pipefail

SER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
PROJECT_ROOT="$(pwd)"
HOME_ABS="$(eval echo ~)"
SER_GLOBAL="$HOME_ABS/.claude/ser"
TIMESTAMP="$(date +%s)"

echo "=== SER v5 → v6 Migration ==="
echo "Framework source: $SER_ROOT"
echo "Project:          $PROJECT_ROOT"
echo

# Pre-flight check: is this a SER v5 project?
if [ ! -d "$PROJECT_ROOT/skills/micro" ]; then
  echo "[!] No skills/micro/ directory found — is this a SER v5 project?"
  echo "    Run from the root of a SER v5 project."
  exit 1
fi

if [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
  echo "[!] No CLAUDE.md found"
  exit 1
fi

# ============================================================
# Phase A: Prepare (non-destructive)
# ============================================================

echo "--- Phase A: Prepare ---"

# A1. Backup global state
if [ -d "$SER_GLOBAL" ]; then
  BACKUP_DIR="$HOME_ABS/.claude/ser.backup.$TIMESTAMP"
  cp -r "$SER_GLOBAL" "$BACKUP_DIR"
  echo "[+] Backed up global state to $BACKUP_DIR"
else
  BACKUP_DIR=""
  echo "[=] No existing global state to backup"
fi

# A2. Stage global files in temp dir
STAGING_GLOBAL="/tmp/ser-v6-global-staging-$$"
mkdir -p "$STAGING_GLOBAL"/{hooks,scripts,td-nl}

# Copy from framework source's parent (where global files were installed)
if [ -d "$SER_ROOT/../.claude/ser" ]; then
  cp -r "$SER_ROOT/../.claude/ser/"* "$STAGING_GLOBAL/" 2>/dev/null || true
fi
echo "[+] Staged global files"

# A3. Stage project files in temp dir
STAGING_PROJECT="/tmp/ser-v6-project-staging-$$"
mkdir -p "$STAGING_PROJECT/.claude/skills"

# Copy grouped SKILL.md files
if [ -d "$SER_ROOT/.claude/skills" ]; then
  cp -r "$SER_ROOT/.claude/skills/"* "$STAGING_PROJECT/.claude/skills/" 2>/dev/null || true
fi

# Copy new CLAUDE.md
cp "$SER_ROOT/CLAUDE.md" "$STAGING_PROJECT/CLAUDE.md"

# Generate settings.json with absolute paths
cat > "$STAGING_PROJECT/.claude/settings.json" << SETEOF
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "command": "$SER_GLOBAL/hooks/session-guard.sh",
        "timeout": 3000
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "command": "CLAUDE_HOOK_PHASE=pre $SER_GLOBAL/hooks/observe.sh",
        "timeout": 5000
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "command": "CLAUDE_HOOK_PHASE=post $SER_GLOBAL/hooks/observe.sh",
        "timeout": 5000
      }
    ]
  }
}
SETEOF
echo "[+] Staged project files"

# A4. Pre-populate weights from existing TD-NL data (if available)
if [ -f "$PROJECT_ROOT/skills/td-nl/feedback-log.md" ]; then
  echo "[i] Found existing TD-NL feedback log — weights will start from uniform priors"
  echo "    (Future: parse historical G2 data to pre-populate weights)"
fi

echo

# ============================================================
# Phase B: Atomic Switch
# ============================================================

echo "--- Phase B: Atomic Switch ---"

# B1. Git backup branch (if git repo)
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  BACKUP_BRANCH="backup/pre-v6-migration-$TIMESTAMP"
  git stash --include-untracked -m "pre-v6 migration stash" 2>/dev/null || true
  git stash pop 2>/dev/null || true
  git add -A 2>/dev/null || true
  git commit -m "backup: pre-v6 migration snapshot" --allow-empty 2>/dev/null || true
  BACKUP_COMMIT=$(git rev-parse HEAD)
  echo "[+] Git backup commit: $BACKUP_COMMIT"
else
  BACKUP_COMMIT=""
  echo "[i] Not a git repo — skipping git backup"
fi

# B2. Install global files
if [ -d "$STAGING_GLOBAL" ]; then
  # Merge into existing global dir (don't replace weights if they exist)
  mkdir -p "$SER_GLOBAL"
  cp -r "$STAGING_GLOBAL/hooks" "$SER_GLOBAL/" 2>/dev/null || true
  cp -r "$STAGING_GLOBAL/scripts" "$SER_GLOBAL/" 2>/dev/null || true
  cp -r "$STAGING_GLOBAL/td-nl" "$SER_GLOBAL/" 2>/dev/null || true
  [ ! -f "$SER_GLOBAL/chains.yaml" ] && cp "$STAGING_GLOBAL/chains.yaml" "$SER_GLOBAL/" 2>/dev/null || true
  [ ! -f "$SER_GLOBAL/weights.yaml" ] && cp "$STAGING_GLOBAL/weights.yaml" "$SER_GLOBAL/" 2>/dev/null || true
  [ ! -f "$SER_GLOBAL/config.yaml" ] && cp "$STAGING_GLOBAL/config.yaml" "$SER_GLOBAL/" 2>/dev/null || true
  chmod +x "$SER_GLOBAL/hooks/"*.sh "$SER_GLOBAL/scripts/"*.py 2>/dev/null || true
  echo "[+] Installed global files"
fi

# B3. Apply project changes
mkdir -p "$PROJECT_ROOT/.claude/skills"
cp -r "$STAGING_PROJECT/.claude/skills/"* "$PROJECT_ROOT/.claude/skills/"
cp "$STAGING_PROJECT/.claude/settings.json" "$PROJECT_ROOT/.claude/settings.json"
cp "$STAGING_PROJECT/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"

# Create observation directory (new in v6)
mkdir -p "$PROJECT_ROOT/logs/observations"

echo "[+] Applied project changes"

# Cleanup staging dirs
rm -rf "$STAGING_GLOBAL" "$STAGING_PROJECT"

echo

# ============================================================
# Phase C: Verify (rollback on failure)
# ============================================================

echo "--- Phase C: Verify ---"

PASS=0; FAIL=0
check() {
  if eval "$1"; then echo "  [ok] $2"; PASS=$((PASS+1))
  else echo "  [!!] $2"; FAIL=$((FAIL+1)); fi
}

check "[ -f '$SER_GLOBAL/chains.yaml' ]" "global chains.yaml"
check "[ -f '$SER_GLOBAL/weights.yaml' ]" "global weights.yaml"
check "[ -x '$SER_GLOBAL/hooks/session-guard.sh' ]" "session-guard.sh"
check "[ -x '$SER_GLOBAL/hooks/observe.sh' ]" "observe.sh"
check "[ -f '$SER_GLOBAL/scripts/recommend.py' ]" "recommend.py"
check "[ -f '$SER_GLOBAL/scripts/update_weights.py' ]" "update_weights.py"
check "[ -f '$PROJECT_ROOT/.claude/settings.json' ]" "project settings.json"
check "[ -d '$PROJECT_ROOT/.claude/skills/meta' ]" "meta skill"
check "[ -d '$PROJECT_ROOT/.claude/skills/review' ]" "review skill"
check "[ -d '$PROJECT_ROOT/logs/observations' ]" "observation directory"
check "[ -f '$PROJECT_ROOT/CLAUDE.md' ]" "CLAUDE.md (v6)"
check "grep -q 'v6' '$PROJECT_ROOT/CLAUDE.md' 2>/dev/null" "CLAUDE.md is v6"

SKILL_COUNT=$(ls -1d "$PROJECT_ROOT/.claude/skills/"*/SKILL.md 2>/dev/null | wc -l)
echo "  Skills: $SKILL_COUNT groups"

echo
echo "Verification: $PASS passed, $FAIL failed"

if [ "$FAIL" -gt 0 ]; then
  echo
  echo "[!] VERIFICATION FAILED — Rolling back..."

  # Rollback project
  if [ -n "$BACKUP_COMMIT" ]; then
    git checkout "$BACKUP_COMMIT" -- . 2>/dev/null || true
    echo "[+] Rolled back project files from git"
  fi

  # Rollback global
  if [ -n "$BACKUP_DIR" ] && [ -d "$BACKUP_DIR" ]; then
    rm -rf "$SER_GLOBAL"
    mv "$BACKUP_DIR" "$SER_GLOBAL"
    echo "[+] Rolled back global state from backup"
  fi

  echo "[!] Migration failed and rolled back. Check errors above."
  exit 1
fi

# Success — clean up backup info
echo
echo "=== Migration Complete ==="
echo "v5 → v6 migration successful."
echo
echo "What changed:"
echo "  - CLAUDE.md: replaced with v6 (~140 lines, streamlined)"
echo "  - .claude/skills/: $SKILL_COUNT grouped SKILL.md files (replaces skills/micro/)"
echo "  - .claude/settings.json: hooks with absolute paths"
echo "  - logs/observations/: new directory for JSONL observation data"
echo "  - Global ~/.claude/ser/: hooks, scripts, chains, weights"
echo
echo "What's preserved:"
echo "  - config.yaml, memory/, checklists/, logs/digest/"
echo "  - skills/micro/ (old specs kept for reference)"
echo "  - All project data and paper artifacts"
echo
if [ -n "$BACKUP_COMMIT" ]; then
  echo "Rollback: git checkout $BACKUP_COMMIT -- ."
fi
if [ -n "$BACKUP_DIR" ]; then
  echo "Global rollback: mv $BACKUP_DIR ~/.claude/ser/"
fi
