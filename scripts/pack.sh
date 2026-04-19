#!/usr/bin/env bash
# Pack SER framework as a clean template for new projects.
# Produces ser-v{VERSION}.tar.gz in the repo root.
#
# Usage:
#   bash scripts/pack.sh              # auto-detect version from git tag or use "dev"
#   bash scripts/pack.sh 5.1          # explicit version

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

# --- Version ---
if [ $# -ge 1 ]; then
  VERSION="$1"
else
  VERSION=$(git describe --tags --abbrev=0 2>/dev/null | sed 's/^v//' || echo "dev")
fi

PACK_NAME="ser-v${VERSION}"
STAGING_DIR=$(mktemp -d)
DEST="${STAGING_DIR}/${PACK_NAME}"

cleanup() { rm -rf "$STAGING_DIR"; }
trap cleanup EXIT

echo "Packing SER framework v${VERSION}..."

# --- Export clean git tree (respects .gitignore, excludes untracked) ---
mkdir -p "$DEST"
git archive HEAD | tar -x -C "$DEST"

# --- Remove project-specific content (keep structure) ---

# Config: keep only template
rm -f "$DEST/config.yaml"

# Logs: clear session content but keep structure
rm -f "$DEST/logs/digest/"*.yaml
cat > "$DEST/logs/digest/SUMMARY.md" << 'EOF'
# Session Log Summary

| Date | Type | Summary |
|------|------|---------|
EOF

# Memory: reset to blank
rm -rf "$DEST/memory/episodes/"* "$DEST/memory/topics/"* "$DEST/memory/procedures/"*
cat > "$DEST/memory/MEMORY.md" << 'EOF'
# Memory Index

## Active Context
- Project initialized, no sessions yet

## Topic Index
(empty)

## Recent Episodes
(empty)

## Procedure Index
(empty)
EOF

# Checklists: reset to template state
cat > "$DEST/Checklist.md" << 'EOF'
# {Project Name} — Master Checklist

> Single source of truth for project progress. Read at every session.open.
> Checklists track status; actual artifacts live in `outputs/`.

Updated: YYYY-MM-DD | Status: [0/3 phases]

## Short-term [0/0] → checklists/short-term.md
No items yet. Use `checklist.create` to add tasks.

## Mid-term [0/0] → checklists/mid-term.md
No items yet.

## Long-term [0/0] → checklists/long-term.md
No items yet.
EOF

for term in short-term mid-term long-term; do
  cat > "$DEST/checklists/${term}.md" << TERMEOF
# ${term} Checklist (L1)

<!-- Add items as: - [ ] Task description -->
<!-- Branch items link to L2: - [0/0] Category → checklists/${term}/category-slug.md -->
TERMEOF
  rm -f "$DEST/checklists/${term}/"*.md 2>/dev/null || true
done

# TD-NL evolution: reset feedback and values
: > "$DEST/skills/td-nl/feedback-log.md"
rm -f "$DEST/skills/td-nl/skill-values/"*.md 2>/dev/null || true
rm -f "$DEST/skills/td-nl/history/"* 2>/dev/null || true

# Clear project outputs and resources (keep dirs via .gitkeep)
find "$DEST/outputs" "$DEST/experiments" "$DEST/background" \
     "$DEST/methodology" "$DEST/docs" "$DEST/resources/papers" \
     -type f ! -name '.gitkeep' ! -name 'CLAUDE.md' ! -name 'README.md' \
     -delete 2>/dev/null || true

# Ensure .gitkeep files exist in empty dirs
for d in memory/episodes memory/topics memory/procedures memory/td-nl \
         logs/progress background methodology/ideas experiments \
         outputs resources/repos docs skills/td-nl/history \
         checklists/short-term checklists/mid-term checklists/long-term; do
  mkdir -p "$DEST/$d"
  touch "$DEST/$d/.gitkeep"
done

# --- Remove pack artifacts and dev-only files ---
rm -f "$DEST/.claude/.ser-session-active"
rm -rf "$DEST/.claude/worktrees"

# --- Create archive ---
ARCHIVE="${REPO_ROOT}/${PACK_NAME}.tar.gz"
tar -czf "$ARCHIVE" -C "$STAGING_DIR" "$PACK_NAME"

# File count and size
FILE_COUNT=$(tar -tzf "$ARCHIVE" | wc -l)
SIZE=$(du -h "$ARCHIVE" | cut -f1)

echo ""
echo "Created: ${PACK_NAME}.tar.gz (${SIZE}, ${FILE_COUNT} files)"
echo ""
echo "To use in a new project:"
echo "  tar xzf ${PACK_NAME}.tar.gz"
echo "  cd ${PACK_NAME}"
echo "  bash scripts/setup.sh"
