#!/usr/bin/env bash
# SER v6 Framework Setup Script
# Safe to run multiple times (idempotent).
# Supports: fresh install and --update mode.
#
# Usage:
#   cd your-project/
#   bash /path/to/ser-v6/scripts/setup-v6.sh            # fresh install
#   bash /path/to/ser-v6/scripts/setup-v6.sh --update    # update framework files

set -euo pipefail

SER_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SER_TEMPLATES="$SER_ROOT/templates/global"
PROJECT_ROOT="$(pwd)"
HOME_ABS="$(eval echo ~)"
SER_GLOBAL="$HOME_ABS/.claude/ser"

UPDATE_MODE=false
if [[ "${1:-}" == "--update" ]]; then
  UPDATE_MODE=true
  echo "Running in UPDATE mode — will refresh framework files, preserve project data"
  echo
fi

echo "=== SER v6 Setup ==="
echo "Framework source: $SER_ROOT"
echo "Project target:   $PROJECT_ROOT"
echo "Global dir:       $SER_GLOBAL"
echo

# ============================================================
# PART A: Global infrastructure (once, if not exists)
# ============================================================

echo "--- Part A: Global infrastructure ---"

mkdir -p "$SER_GLOBAL"/{hooks,scripts,td-nl}

# A1. Install hook scripts
if [ ! -f "$SER_GLOBAL/hooks/session-guard.sh" ]; then
  cat > "$SER_GLOBAL/hooks/session-guard.sh" << 'HOOKEOF'
#!/usr/bin/env bash
MARKER=".claude/.ser-session-active"
if [ ! -f "$MARKER" ]; then
    touch "$MARKER"
    echo "[SER] Execute session.open before responding. Read .claude/skills/meta/SKILL.md."
fi
HOOKEOF
  echo "[+] Created session-guard.sh"
else
  echo "[=] session-guard.sh already exists"
fi

if [ ! -f "$SER_GLOBAL/hooks/observe.sh" ]; then
  cat > "$SER_GLOBAL/hooks/observe.sh" << 'OBSEOF'
#!/usr/bin/env bash
set -o pipefail
OBS_DIR="logs/observations"
[ -d "$OBS_DIR" ] || mkdir -p "$OBS_DIR" 2>/dev/null || exit 0
SESSION_FILE="$OBS_DIR/$(date +%Y-%m-%d).jsonl"
INPUT=$(cat 2>/dev/null) || exit 0
[ -z "$INPUT" ] && exit 0
PHASE="${CLAUDE_HOOK_PHASE:-unknown}"
TS=$(date -u +%Y-%m-%dT%H:%M:%SZ 2>/dev/null || echo "unknown")
TOOL=$(echo "$INPUT" | python3 -c "import sys,json; d=json.load(sys.stdin); print(d.get('tool_name','unknown'))" 2>/dev/null || echo "unknown")
printf '{"type":"tool","phase":"%s","tool":"%s","ts":"%s"}\n' "$PHASE" "$TOOL" "$TS" >> "$SESSION_FILE" 2>/dev/null
exit 0
OBSEOF
  echo "[+] Created observe.sh"
else
  echo "[=] observe.sh already exists"
fi
chmod +x "$SER_GLOBAL/hooks/"*.sh

# A2. Install Python scripts
for script in recommend.py update_weights.py; do
  if [ -f "$SER_GLOBAL/scripts/$script" ]; then
    if [[ "$UPDATE_MODE" == true ]]; then
      cp "$SER_TEMPLATES/scripts/$script" "$SER_GLOBAL/scripts/$script" 2>/dev/null || true
      echo "[~] Updated $script"
    else
      echo "[=] $script already exists"
    fi
  else
    cp "$SER_TEMPLATES/scripts/$script" "$SER_GLOBAL/scripts/$script" 2>/dev/null || true
    echo "[+] Installed $script"
  fi
done
chmod +x "$SER_GLOBAL/scripts/"*.py 2>/dev/null || true

# A3. Generate chains.yaml, weights.yaml, config.yaml if not exist
for f in chains.yaml weights.yaml config.yaml; do
  if [ ! -f "$SER_GLOBAL/$f" ]; then
    cp "$SER_TEMPLATES/$f" "$SER_GLOBAL/$f" 2>/dev/null || true
    echo "[+] Created $f"
  else
    echo "[=] $f already exists"
  fi
done

# A4. TD-NL README
if [ ! -f "$SER_GLOBAL/td-nl/README.md" ]; then
  cp "$SER_TEMPLATES/td-nl/README.md" "$SER_GLOBAL/td-nl/README.md" 2>/dev/null || true
  echo "[+] Created td-nl/README.md"
fi

echo

# ============================================================
# PART B: Per-project setup
# ============================================================

echo "--- Part B: Project setup ---"

# B1. Create directories
dirs=(
  .claude src
  memory/episodes memory/topics memory/procedures
  logs/digest logs/observations logs/progress logs/experiments
  paper/proofs paper/theory paper/figures paper/figures/scripts paper/papers paper/reviews
  background methodology/ideas experiments
  outputs outputs/visuals outputs/paper outputs/short_term outputs/mid_term outputs/long_term
  resources/papers resources/repos resources/docs
  checklists/short-term checklists/mid-term checklists/long-term
)
for d in "${dirs[@]}"; do
  mkdir -p "$PROJECT_ROOT/$d"
done
# .gitkeep for empty dirs
for d in "${dirs[@]}"; do
  target="$PROJECT_ROOT/$d"
  if [ -d "$target" ] && [ -z "$(ls -A "$target" 2>/dev/null)" ]; then
    touch "$target/.gitkeep"
  fi
done
echo "[+] Project directories ready"

# B2. Copy grouped SKILL.md files (always refresh)
if [ -d "$SER_ROOT/.claude/skills" ]; then
  for skill_dir in "$SER_ROOT/.claude/skills/"*/; do
    skill_name="$(basename "$skill_dir")"
    mkdir -p "$PROJECT_ROOT/.claude/skills/$skill_name"
    cp "$skill_dir/SKILL.md" "$PROJECT_ROOT/.claude/skills/$skill_name/SKILL.md" 2>/dev/null || true
  done
  SKILL_COUNT=$(ls -1d "$PROJECT_ROOT/.claude/skills/"*/SKILL.md 2>/dev/null | wc -l)
  echo "[+] Installed $SKILL_COUNT grouped SKILL.md files"
fi

# B3. CLAUDE.md
if [[ "$UPDATE_MODE" == false ]] || [ ! -f "$PROJECT_ROOT/CLAUDE.md" ]; then
  cp "$SER_ROOT/CLAUDE.md" "$PROJECT_ROOT/CLAUDE.md"
  echo "[+] Installed CLAUDE.md (v6)"
else
  echo "[=] CLAUDE.md preserved (update mode)"
fi

# B4. .claude/settings.json with absolute paths (always regenerate)
# Canonical hook format: nested hooks[] array with type field (required for SDK compatibility)
cat > "$PROJECT_ROOT/.claude/settings.json" << SETEOF
{
  "hooks": {
    "UserPromptSubmit": [
      {
        "matcher": "",
        "hooks": [
          {
            "type": "command",
            "command": "$SER_GLOBAL/hooks/session-guard.sh",
            "timeout": 3
          }
        ]
      }
    ],
    "PreToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "CLAUDE_HOOK_PHASE=pre $SER_GLOBAL/hooks/observe.sh",
            "timeout": 5
          }
        ]
      }
    ],
    "PostToolUse": [
      {
        "matcher": "*",
        "hooks": [
          {
            "type": "command",
            "command": "CLAUDE_HOOK_PHASE=post $SER_GLOBAL/hooks/observe.sh",
            "timeout": 5
          }
        ]
      }
    ]
  }
}
SETEOF
echo "[+] Created .claude/settings.json (paths: $SER_GLOBAL)"

# B5. Config template
if [ ! -f "$PROJECT_ROOT/config.yaml" ]; then
  if [ -f "$SER_ROOT/config.template.yaml" ]; then
    cp "$SER_ROOT/config.template.yaml" "$PROJECT_ROOT/config.yaml"
    echo "[+] Created config.yaml — edit with your project details"
  fi
else
  echo "[=] config.yaml preserved"
fi

# B6. Memory index
if [ ! -f "$PROJECT_ROOT/memory/MEMORY.md" ]; then
  cat > "$PROJECT_ROOT/memory/MEMORY.md" << 'MEMEOF'
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
  echo "[=] memory/MEMORY.md preserved"
fi

# B7. Session log summary
if [ ! -f "$PROJECT_ROOT/logs/digest/SUMMARY.md" ]; then
  cat > "$PROJECT_ROOT/logs/digest/SUMMARY.md" << 'SUMEOF'
# Session Log Summary

| Date | Type | Summary |
|------|------|---------|
SUMEOF
  echo "[+] Created logs/digest/SUMMARY.md"
else
  echo "[=] logs/digest/SUMMARY.md preserved"
fi

# B8. Methodology stub
if [ ! -f "$PROJECT_ROOT/methodology/approach.md" ]; then
  cat > "$PROJECT_ROOT/methodology/approach.md" << 'APPEOF'
# Research Approach

## Research Direction
<!-- Describe your high-level research direction here -->

## Current Methodology
<!-- Describe your current approach -->

## Key Assumptions

## Open Questions
APPEOF
  echo "[+] Created methodology/approach.md"
else
  echo "[=] methodology/approach.md preserved"
fi

# B9. Checklist system
PROJECT_NAME="My Project"
if [ -f "$PROJECT_ROOT/config.yaml" ]; then
  _name=$(grep -m1 '^\s*name:' "$PROJECT_ROOT/config.yaml" 2>/dev/null | sed 's/.*name: *"\?\([^"]*\)"\?/\1/' || true)
  [ -n "$_name" ] && PROJECT_NAME="$_name"
fi

if [ ! -f "$PROJECT_ROOT/Checklist.md" ]; then
  cat > "$PROJECT_ROOT/Checklist.md" << CLEOF
# $PROJECT_NAME — Project Checklist (L0)

## Short-Term
- [0/0] Short-term tasks → checklists/short-term.md

## Mid-Term
- [0/0] Mid-term tasks → checklists/mid-term.md

## Long-Term
- [0/0] Long-term tasks → checklists/long-term.md
CLEOF
  echo "[+] Created Checklist.md"
fi

for term in short-term mid-term long-term; do
  if [ ! -f "$PROJECT_ROOT/checklists/${term}.md" ]; then
    cat > "$PROJECT_ROOT/checklists/${term}.md" << TERMEOF
# ${term} Checklist (L1)

## Ideas

## Methods

## Experiments

## Paper-Audit

## Review-Loop

## Paper-Writing

## Research-Pipeline
TERMEOF
    echo "[+] Created checklists/${term}.md"
  fi
done

# --- B10: .gitignore template ---
GITIGNORE="$PROJECT_ROOT/.gitignore"
if [ ! -f "$GITIGNORE" ]; then
  cat > "$GITIGNORE" << 'GIEOF'
# Claude Code (regenerated by setup, never track)
.claude/

# Logs & observations
logs/

# Ephemeral memory
memory/episodes/

# Worktrees
.worktrees/
.ser-state-worktree/

# Python
__pycache__/
*.pyc
.venv/

# Environment & IDE
.env
.vscode/
.idea/

# Large files
*.pt
*.pth
*.ckpt
*.safetensors
wandb/
GIEOF
  echo "[+] Created .gitignore"
else
  echo "[~] .gitignore already exists, skipping"
fi

# --- B11: git init ---
if [ ! -d "$PROJECT_ROOT/.git" ]; then
  git -C "$PROJECT_ROOT" init
  git -C "$PROJECT_ROOT" add .gitignore
  git -C "$PROJECT_ROOT" commit -m "chore: initialize SER v6 project"
  echo "[+] Initialized git repository"
else
  echo "[~] Git repository already exists, skipping"
fi

echo

# ============================================================
# PART C: Verification
# ============================================================

echo "--- Part C: Verification ---"

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
check "[ -d '$PROJECT_ROOT/logs/observations' ]" "observation dir"
check "[ -f '$PROJECT_ROOT/CLAUDE.md' ]" "CLAUDE.md (v6)"
check "[ -d '$PROJECT_ROOT/.git' ]" "git repository"
check "[ -f '$PROJECT_ROOT/.gitignore' ]" ".gitignore"

SKILL_COUNT=$(ls -1d "$PROJECT_ROOT/.claude/skills/"*/SKILL.md 2>/dev/null | wc -l)
echo "  Skills: $SKILL_COUNT groups"
echo
echo "Verification: $PASS passed, $FAIL failed"

if [ "$FAIL" -gt 0 ]; then
  echo "[!] Some checks failed"
  exit 1
fi

echo
echo "=== SER v6 Setup Complete ==="
echo "Next steps:"
echo "  1. Edit config.yaml with your project details"
echo "  2. Run 'claude' to start your first session"
echo "  3. SER will auto-detect your intent — just talk naturally"

# --- B12: Copy subdirectory README.md documentation ---
for subdir in background logs methodology outputs memory resources scripts checklists; do
  src_readme="$SER_ROOT/$subdir/README.md"
  dst_readme="$PROJECT_ROOT/$subdir/README.md"
  if [ -f "$src_readme" ] && [ ! -f "$dst_readme" ]; then
    cp "$src_readme" "$dst_readme"
    echo "[+] Created $subdir/README.md"
  fi
done

