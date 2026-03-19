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
    echo "[+] MetaScheduler mode selected"
  else
    echo "[+] Local mode selected (direct GPU access)"
  fi
  echo
fi

# --- 2. Assemble experiment.md (binary install — source files removed after) ---
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
  # Remove source files after assembly (binary install)
  rm -f skills/micro/experiment.base.md skills/micro/experiment.local.md skills/micro/experiment.ms.md
  echo "[+] Removed experiment source files (assembled binary)"
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
      cat >> config.yaml << 'MSEOF'

# MetaScheduler integration (auto-configured by setup.sh)
metascheduler:
  bot_name: "manager"
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
  logs/digest
  logs/progress
  logs/experiments
  paper/proofs
  paper/theory
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
for d in "${dirs[@]}"; do
  if [ ! -f "$d/.gitkeep" ]; then
    touch "$d/.gitkeep"
  fi
done
echo "[+] Added .gitkeep files to empty directories"

# --- 6. TD-NL infrastructure files ---
if [ ! -f skills/td-nl/value-function.md ]; then
  cat > skills/td-nl/value-function.md << 'VFEOF'
# V^L — System-Level Value Function

> Tracks overall SER skill system effectiveness. Updated by `evolve.suggest` at session.close.

## Current Value

**V^L = 5.0 / 10** (initial default)

## History

| Session | V^L | Delta | Notes |
|---------|-----|-------|-------|
| (init)  | 5.0 | —     | System initialized |

## Per-Category Summary

| Category | Avg Q^L | Skills | Notes |
|----------|---------|--------|-------|
| Session  | 5.0     | session.open, session.close | — |
| Paper    | 5.0     | paper.read, paper.compare, paper.index, lit.search | — |
| Theory   | 5.0     | theory.formalize, theory.decompose, theory.search, theory.counterexample, theory.generalize | — |
| Proof    | 5.0     | proof.critique, proof.fix, proof.formalize, proof.verify, proof.write | — |
| Writing  | 5.0     | writing.outline, writing.draft, writing.review, writing.polish, paper.figure, paper.compile | — |
| Planning | 5.0     | plan.suggest, plan.milestone, progress.capture, status.report, decision.analyze | — |
| Experiment | 5.0   | experiment.plan, experiment.analyze, experiment.run, experiment.monitor, math.dse | — |
| Idea     | 5.0     | idea.discover, idea.verify, idea.refine | — |
| Visual   | 5.0     | pixel.create, paper.illustrate | — |
| Checklist| 5.0     | checklist.create, checklist.verify, checklist.update, checklist.status | — |
| Research | 5.0     | research.explore, design.converge | — |
| Memory   | 5.0     | memory.write, memory.retrieve, memory.consolidate, memory.forget | — |
| Meta     | 5.0     | evolve.suggest, evolve.apply, general.research | — |
| Integrate| 5.0     | project.integrate | — |
VFEOF
  echo "[+] Created skills/td-nl/value-function.md (V^L=5.0)"
else
  echo "[=] skills/td-nl/value-function.md already exists, skipping"
fi

if [ ! -f skills/td-nl/feedback-log.md ]; then
  cat > skills/td-nl/feedback-log.md << 'FLEOF'
# TD-NL Feedback Log

> G2 entries appended after every micro-skill firing.
> Processed by `evolve.suggest` at session.close (G1 aggregation).

## Pending Feedback

<!-- G2 entries appended here during session -->

## Processed Feedback

<!-- Moved here after G1 aggregation at session.close -->

## Pending Proposals

<!-- Spec edit proposals from evolve.suggest, awaiting user approval -->
FLEOF
  echo "[+] Created skills/td-nl/feedback-log.md"
else
  echo "[=] skills/td-nl/feedback-log.md already exists, skipping"
fi

if [ ! -f skills/td-nl/skill-values/_template.md ]; then
  cat > skills/td-nl/skill-values/_template.md << 'TMPLEOF'
# Q^L — {skill-name}

> Per-skill value estimate. Created on first firing, updated by G1 aggregation.

## Current Value

**Q^L = 5.0 / 10** (initial default)

## Assessment History

| Session | Q^L | Delta | G2 Summary |
|---------|-----|-------|------------|

## Strengths

- (none yet)

## Improvement Areas

- (none yet)

## Spec Edit History

| Date | Edit | V^L Impact |
|------|------|------------|
TMPLEOF
  echo "[+] Created skills/td-nl/skill-values/_template.md"
else
  echo "[=] skills/td-nl/skill-values/_template.md already exists, skipping"
fi

# --- 7. Memory index (preserve in update mode) ---
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

# --- 8. Session log summary (preserve in update mode) ---
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

# --- 9. Methodology stub ---
if [ ! -f methodology/approach.md ]; then
  cat > methodology/approach.md << 'APPEOF'
# Research Approach

> Current research direction and methodology. Updated as the project evolves.
> Referenced by: idea.discover, experiment.plan, writing.outline, paper.illustrate

## Research Direction

<!-- Describe your high-level research direction here -->

## Current Methodology

<!-- Describe your current approach / algorithm / framework -->

## Key Assumptions

<!-- List assumptions your approach relies on -->

## Open Questions

<!-- Questions that need to be answered -->
APPEOF
  echo "[+] Created methodology/approach.md"
else
  echo "[=] methodology/approach.md already exists, skipping"
fi

# --- 10. Checklist system (preserve in update mode) ---

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

<!-- Branch items link to L2: - [0/0] Category → checklists/${term}/category-slug.md -->

## Ideas

## Methods

## Experiments

## Paper-Audit

## Review-Loop

## Paper-Writing

## Research-Pipeline
TERMEOF
    echo "[+] Created checklists/${term}.md (with 7 category headers)"
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
