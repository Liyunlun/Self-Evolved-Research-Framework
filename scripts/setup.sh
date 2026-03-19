#!/usr/bin/env bash
# SER Framework Setup Script (dev)
# Safe to run multiple times (idempotent).
# Supports: fresh install and --update mode.

set -euo pipefail

REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$REPO_ROOT"

UPDATE_MODE=false
if [[ "${1:-}" == "--update" ]]; then
  UPDATE_MODE=true
  echo "Running in UPDATE mode — will refresh framework files, preserve project data"
  echo
fi

echo "Setting up SER framework in: $REPO_ROOT"
echo

# --- 1. Experiment mode selection (first install only) ---
if [[ "$UPDATE_MODE" == false ]]; then
  EXPERIMENT_MODE="local"
  read -p "Use MetaScheduler for experiment management? [y/N] " USE_MS
  if [[ "$USE_MS" =~ ^[Yy]$ ]]; then
    EXPERIMENT_MODE="metascheduler"
    read -p "MetaScheduler chat_id: " MS_CHAT_ID
    echo "[+] MetaScheduler mode selected (chat_id: $MS_CHAT_ID)"
  else
    echo "[+] Local mode selected (direct GPU access)"
  fi
  echo
fi

# --- 2. Assemble experiment.md ---
if [[ "$UPDATE_MODE" == false ]]; then
  if [[ "$EXPERIMENT_MODE" == "metascheduler" ]]; then
    cat skills/micro/experiment.base.md skills/micro/experiment.ms.md \
      > skills/micro/experiment.md
    echo "[+] Assembled experiment.md (MetaScheduler mode)"
  else
    cat skills/micro/experiment.base.md skills/micro/experiment.local.md \
      > skills/micro/experiment.md
    echo "[+] Assembled experiment.md (Local mode)"
  fi
else
  if [[ -f skills/micro/experiment.md ]]; then
    echo "[=] experiment.md preserved (update mode — install mode unchanged)"
  else
    echo "[!] WARNING: experiment.md missing. Re-run without --update to select mode."
  fi
fi

# --- 3. Config ---
if [[ "$UPDATE_MODE" == false ]]; then
  if [ ! -f config.yaml ]; then
    cp config.template.yaml config.yaml

    # If MetaScheduler mode, uncomment and fill metascheduler section
    if [[ "${EXPERIMENT_MODE:-local}" == "metascheduler" ]]; then
      cat >> config.yaml << MSEOF

# MetaScheduler integration (auto-configured by setup.sh)
metascheduler:
  chat_id: "$MS_CHAT_ID"
  default_gpu_type: "RTX4090"
  default_gpu_count: 1
  default_conda_env: "research"
MSEOF
      echo "[+] Created config.yaml with MetaScheduler settings"
    else
      echo "[+] Created config.yaml from template"
    fi
    echo "    Edit config.yaml with your project details."
  else
    echo "[=] config.yaml already exists, skipping"
  fi
else
  echo "[=] config.yaml preserved (update mode)"
fi

# --- 4. Required directories ---
dirs=(
  memory/episodes
  memory/topics
  memory/procedures
  memory/td-nl
  logs/digest
  logs/progress
  logs/experiments
  papers
  paper/proofs
  paper/figures
  paper/figures/scripts
  paper/papers
  paper/reviews
  background
  methodology/ideas
  experiments
  outputs
  outputs/visuals
  outputs/paper
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

# --- 5. .gitkeep for empty directories ---
gitkeep_dirs=(
  memory/episodes
  memory/topics
  memory/procedures
  memory/td-nl
  logs/progress
  logs/experiments
  papers
  paper/proofs
  paper/figures
  paper/figures/scripts
  paper/papers
  paper/reviews
  background
  methodology/ideas
  experiments
  outputs
  outputs/visuals
  outputs/paper
  resources/repos
  docs
  skills/td-nl/history
  skills/td-nl/skill-values
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

# --- 6. Memory index (preserve in update mode) ---
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

# --- 7. Session log summary (preserve in update mode) ---
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

# --- 8. Checklist system (preserve in update mode) ---

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
if [[ "$UPDATE_MODE" == true ]]; then
  echo
  echo "UPDATE mode: Framework files refreshed. Project data preserved."
  echo "  - config.yaml: unchanged"
  echo "  - memory/: unchanged"
  echo "  - skills/td-nl/: unchanged"
  echo "  - experiment.md: unchanged (install mode preserved)"
fi
