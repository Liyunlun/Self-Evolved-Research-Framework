#!/usr/bin/env bash
# SER v6 — State Backup Script
# Backs up checklist + memory state to an orphan 'ser-state' branch via git worktree.
# Main working directory is completely unaffected.
#
# Usage: ser-state-backup.sh /path/to/project
# Cron:  0 4 * * * /path/to/ser-state-backup.sh /path/to/project
#
# What gets backed up:
#   - Checklist.md (L0)
#   - checklists/ (L1 + L2)
#   - memory/MEMORY.md + memory/topics/ + memory/procedures/
#
# What is NOT backed up (ephemeral):
#   - memory/episodes/ (7-day TTL, not worth persisting)
#   - logs/ (observation data, regenerated each session)

set -euo pipefail

PROJECT_ROOT="${1:-.}"
PROJECT_ROOT=$(cd "$PROJECT_ROOT" && pwd)

WORKTREE_DIR="$PROJECT_ROOT/.ser-state-worktree"
BRANCH="ser-state"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ)

# Ensure we're in a git repo
if [ ! -d "$PROJECT_ROOT/.git" ]; then
  echo "[ser-state-backup] Not a git repo: $PROJECT_ROOT"
  exit 1
fi

cd "$PROJECT_ROOT"

# Clean up any leftover worktree from a previous failed run
if [ -d "$WORKTREE_DIR" ]; then
  git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"
fi

# Create orphan branch if it doesn't exist
if ! git rev-parse --verify "$BRANCH" >/dev/null 2>&1; then
  # Create orphan branch with an empty initial commit
  git worktree add --detach "$WORKTREE_DIR" 2>/dev/null
  cd "$WORKTREE_DIR"
  git checkout --orphan "$BRANCH"
  git rm -rf . 2>/dev/null || true
  echo "# SER State Backup" > README.md
  echo "Automated backup of checklist and memory state." >> README.md
  git add README.md
  git commit -m "chore: initialize ser-state branch"
  cd "$PROJECT_ROOT"
  git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"
fi

# Create worktree for the ser-state branch
git worktree add "$WORKTREE_DIR" "$BRANCH" 2>/dev/null

# Copy state files
copy_if_exists() {
  local src="$PROJECT_ROOT/$1"
  local dst="$WORKTREE_DIR/$1"
  if [ -e "$src" ]; then
    mkdir -p "$(dirname "$dst")"
    cp -r "$src" "$dst"
  fi
}

copy_if_exists "Checklist.md"
copy_if_exists "checklists"
copy_if_exists "memory/MEMORY.md"
copy_if_exists "memory/topics"
copy_if_exists "memory/procedures"

# Commit if there are changes
cd "$WORKTREE_DIR"
git add -A
if git diff --cached --quiet; then
  echo "[ser-state-backup] No changes to backup"
else
  git commit -m "backup: state snapshot $TS"
  echo "[ser-state-backup] Backed up state at $TS"
fi

# Clean up worktree
cd "$PROJECT_ROOT"
git worktree remove "$WORKTREE_DIR" --force 2>/dev/null || rm -rf "$WORKTREE_DIR"

exit 0
