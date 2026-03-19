#!/usr/bin/env bash
# SER Framework Setup Script
# Safe to run multiple times (idempotent).

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

echo "Setting up SER framework in: $REPO_ROOT"
echo

# --- 1. Config ---
if [ ! -f config.yaml ]; then
  cp config.template.yaml config.yaml
  echo "[+] Created config.yaml from template"
  echo "    Edit config.yaml with your project details."
else
  echo "[=] config.yaml already exists, skipping"
fi

# --- 2. Required directories ---
dirs=(
  memory/episodes
  memory/topics
  memory/procedures
  memory/td-nl
  logs/digest
  logs/progress
  papers
  background
  methodology/ideas
  experiments
  outputs
  resources/papers
  resources/repos
  docs
  skills/td-nl/history
  skills/td-nl/skill-values
  checklists/short-term
  checklists/mid-term
  checklists/long-term
)

for d in "${dirs[@]}"; do
  mkdir -p "$d"
done
echo "[+] Created all required directories"

# --- 3. .gitkeep for empty directories ---
gitkeep_dirs=(
  memory/episodes
  memory/topics
  memory/procedures
  memory/td-nl
  logs/progress
  papers
  background
  methodology/ideas
  experiments
  outputs
  resources/repos
  docs
  skills/td-nl/history
  checklists/short-term
  checklists/mid-term
  checklists/long-term
)

for d in "${gitkeep_dirs[@]}"; do
  if [ ! -f "$d/.gitkeep" ]; then
    touch "$d/.gitkeep"
  fi
done
echo "[+] Added .gitkeep files to empty directories"

# --- 4. Memory index ---
if [ ! -f memory/MEMORY.md ]; then
  cat > memory/MEMORY.md << 'MEMEOF'
# Memory Index

## Active Context
- Project initialized, no sessions yet

## Topic Index
(empty)

## Recent Episodes
(empty)

## Procedure Index
(empty)
MEMEOF
  echo "[+] Created memory/MEMORY.md"
else
  echo "[=] memory/MEMORY.md already exists, skipping"
fi

# --- 5. Session log summary ---
if [ ! -f logs/digest/SUMMARY.md ]; then
  cat > logs/digest/SUMMARY.md << 'SUMEOF'
# Session Log Summary

| Date | Type | Summary |
|------|------|---------|
SUMEOF
  echo "[+] Created logs/digest/SUMMARY.md"
else
  echo "[=] logs/digest/SUMMARY.md already exists, skipping"
fi

# --- 6. Checklist system ---

# Try to extract project name from config.yaml
PROJECT_NAME="My Project"
if [ -f config.yaml ]; then
  _name=$(grep -m1 '^  name:' config.yaml 2>/dev/null | sed 's/^  name: *"\?\([^"]*\)"\?/\1/' || true)
  if [ -n "$_name" ]; then
    PROJECT_NAME="$_name"
  fi
fi

if [ ! -f Checklist.md ]; then
  cat > Checklist.md << CLEOF
# $PROJECT_NAME — Project Checklist (L0)

## Short-Term
- [0/0] Short-term tasks → checklists/short-term.md

## Mid-Term
- [0/0] Mid-term tasks → checklists/mid-term.md

## Long-Term
- [0/0] Long-term tasks → checklists/long-term.md
CLEOF
  echo "[+] Created Checklist.md (L0 root)"
else
  echo "[=] Checklist.md already exists, skipping"
fi

if [ ! -f checklists/CLAUDE.md ]; then
  echo "# Checklist system — see skills/micro/checklist.md" > checklists/CLAUDE.md
  echo "[+] Created checklists/CLAUDE.md"
else
  echo "[=] checklists/CLAUDE.md already exists, skipping"
fi

for term in short-term mid-term long-term; do
  if [ ! -f "checklists/${term}.md" ]; then
    cat > "checklists/${term}.md" << TERMEOF
# ${term^} Checklist (L1)

<!-- Add items as: - [ ] Task description -->
<!-- Branch items link to L2: - [0/0] Category → checklists/${term}/category-slug.md -->
TERMEOF
    echo "[+] Created checklists/${term}.md"
  else
    echo "[=] checklists/${term}.md already exists, skipping"
  fi
done

echo
echo "Setup complete! Next steps:"
echo "  1. Edit config.yaml with your project details"
echo "  2. Run 'claude' to start your first session"
echo "  3. SER will auto-detect your intent — just talk naturally"
