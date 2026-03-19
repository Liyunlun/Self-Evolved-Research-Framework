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

echo
echo "Setup complete! Next steps:"
echo "  1. Edit config.yaml with your project details"
echo "  2. Run 'claude' to start your first session"
echo "  3. SER will auto-detect your intent — just talk naturally"
