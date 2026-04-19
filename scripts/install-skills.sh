#!/usr/bin/env bash
# install-skills.sh — Install bundled Claude Code skills into a .claude/skills directory
#
# Auto-discovers every directory containing a SKILL.md under the source tree
# (default: ./skills), and installs each one into a target skills directory
# (default: ./.claude/skills) as either a copy or a symlink.
#
# Directories without a SKILL.md (e.g. skills/_shared, skills/td-nl) are ignored:
# they are SER internal infrastructure, not Claude Code skills.
#
# Safe to run multiple times. Existing installs are skipped unless --force.
#
# ─────────────────────────────────────────────────────────────────────────────
# Usage:
#   bash scripts/install-skills.sh [options]
#
# Options:
#   -h, --help            Show this help and exit
#   -n, --dry-run         Print actions without modifying the filesystem
#   -f, --force           Overwrite existing skills at the target
#   -l, --link            Symlink instead of copying (ideal for development)
#   -s, --source DIR      Source directory to scan (default: ./skills)
#   -t, --target DIR      Target directory            (default: ./.claude/skills)
#       --user            Shortcut for --target ~/.claude/skills (global install)
#       --list            List discovered skills and exit (no installation)
#       --no-color        Disable ANSI color output
#
# Exit codes:
#   0  success (or nothing to do)
#   1  argument / usage error
#   2  source directory invalid
#   3  one or more skills failed to install
# ─────────────────────────────────────────────────────────────────────────────

set -euo pipefail

# --- Defaults ------------------------------------------------------------------
REPO_ROOT="$(cd "$(dirname "$0")/.." && pwd)"
SOURCE_DIR="${REPO_ROOT}/skills"
TARGET_DIR="${REPO_ROOT}/.claude/skills"
MODE="copy"          # copy | link
DRY_RUN=0
FORCE=0
LIST_ONLY=0
USE_COLOR=1

# --- Helpers -------------------------------------------------------------------
if [ -t 1 ]; then :; else USE_COLOR=0; fi

color() {
  # $1 = color name, $2... = message
  local c="$1"; shift
  if [ "$USE_COLOR" -eq 0 ]; then
    printf '%s' "$*"
    return
  fi
  case "$c" in
    red)    printf '\033[31m%s\033[0m' "$*" ;;
    green)  printf '\033[32m%s\033[0m' "$*" ;;
    yellow) printf '\033[33m%s\033[0m' "$*" ;;
    blue)   printf '\033[34m%s\033[0m' "$*" ;;
    dim)    printf '\033[2m%s\033[0m'  "$*" ;;
    *)      printf '%s' "$*" ;;
  esac
}

log_info()    { echo "$(color blue   '[*]') $*"; }
log_ok()      { echo "$(color green  '[+]') $*"; }
log_skip()    { echo "$(color dim    '[=]') $*"; }
log_warn()    { echo "$(color yellow '[!]') $*" >&2; }
log_error()   { echo "$(color red    '[x]') $*" >&2; }

usage() {
  sed -n '2,34p' "$0" | sed 's/^# \{0,1\}//'
  exit "${1:-0}"
}

# --- Arg parsing ---------------------------------------------------------------
while [ $# -gt 0 ]; do
  case "$1" in
    -h|--help)      usage 0 ;;
    -n|--dry-run)   DRY_RUN=1; shift ;;
    -f|--force)     FORCE=1; shift ;;
    -l|--link)      MODE="link"; shift ;;
    -s|--source)    [ $# -ge 2 ] || { log_error "--source requires an argument"; exit 1; }
                    SOURCE_DIR="$2"; shift 2 ;;
    -t|--target)    [ $# -ge 2 ] || { log_error "--target requires an argument"; exit 1; }
                    TARGET_DIR="$2"; shift 2 ;;
    --user)         TARGET_DIR="${HOME}/.claude/skills"; shift ;;
    --list)         LIST_ONLY=1; shift ;;
    --no-color)     USE_COLOR=0; shift ;;
    --)             shift; break ;;
    -*)             log_error "Unknown option: $1"; usage 1 ;;
    *)              log_error "Unexpected argument: $1"; usage 1 ;;
  esac
done

# Resolve to absolute paths (portable: no realpath required)
abspath() {
  local p="$1"
  case "$p" in
    /*) printf '%s' "$p" ;;
    *)  printf '%s/%s' "$(pwd)" "$p" ;;
  esac
}
SOURCE_DIR="$(abspath "$SOURCE_DIR")"
TARGET_DIR="$(abspath "$TARGET_DIR")"

# --- Validate source -----------------------------------------------------------
if [ ! -d "$SOURCE_DIR" ]; then
  log_error "Source directory not found: $SOURCE_DIR"
  exit 2
fi

# --- Discovery -----------------------------------------------------------------
# Find every directory that contains a SKILL.md. Store (name, abs_path) pairs.
# "name" is the leaf directory name — Claude Code indexes skills by that.
#
# We deliberately use `-print0` + null-delim read to be safe with unusual names.
discover_skills() {
  local roots=()
  # Sort for deterministic output.
  while IFS= read -r -d '' f; do
    roots+=("$f")
  done < <(find "$SOURCE_DIR" -type f -name 'SKILL.md' -print0 | sort -z)

  for skill_md in "${roots[@]}"; do
    local skill_dir name
    skill_dir="$(dirname "$skill_md")"
    name="$(basename "$skill_dir")"
    printf '%s\t%s\n' "$name" "$skill_dir"
  done
}

mapfile -t DISCOVERED < <(discover_skills)

if [ "${#DISCOVERED[@]}" -eq 0 ]; then
  log_warn "No SKILL.md files found under $SOURCE_DIR — nothing to install."
  exit 0
fi

# --- List mode -----------------------------------------------------------------
if [ "$LIST_ONLY" -eq 1 ]; then
  echo "Discovered ${#DISCOVERED[@]} skill(s) in $SOURCE_DIR:"
  echo
  printf '  %-32s  %s\n' "NAME" "PATH"
  printf '  %-32s  %s\n' "----" "----"
  for entry in "${DISCOVERED[@]}"; do
    IFS=$'\t' read -r name path <<<"$entry"
    # Display path relative to REPO_ROOT when possible
    rel="${path#$REPO_ROOT/}"
    printf '  %-32s  %s\n' "$name" "$rel"
  done
  exit 0
fi

# --- Detect duplicate leaf names (e.g. two skills both named "foo") ------------
dup_check() {
  local seen="" name path
  for entry in "${DISCOVERED[@]}"; do
    IFS=$'\t' read -r name path <<<"$entry"
    case " $seen " in
      *" $name "*)
        log_error "Duplicate skill name detected: '$name' — each skill directory must have a unique basename."
        log_error "Conflicting paths include: $path"
        return 1 ;;
    esac
    seen="$seen $name"
  done
}
dup_check || exit 3

# --- Install -------------------------------------------------------------------
log_info "Source : $SOURCE_DIR"
log_info "Target : $TARGET_DIR"
log_info "Mode   : $MODE$( [ "$DRY_RUN" -eq 1 ] && echo ' (dry-run)' )"
log_info "Force  : $( [ "$FORCE" -eq 1 ] && echo yes || echo no )"
echo

if [ "$DRY_RUN" -eq 0 ]; then
  mkdir -p "$TARGET_DIR"
fi

installed=0
updated=0
skipped=0
failed=0

install_one() {
  local name="$1" src="$2"
  local dst="${TARGET_DIR}/${name}"
  local action=""

  if [ -e "$dst" ] || [ -L "$dst" ]; then
    if [ "$FORCE" -eq 0 ]; then
      log_skip "$name (already installed — use --force to overwrite)"
      skipped=$((skipped + 1))
      return 0
    fi
    action="update"
  else
    action="install"
  fi

  if [ "$DRY_RUN" -eq 1 ]; then
    if [ "$MODE" = "link" ]; then
      log_ok "would $action (symlink): $name → $src"
    else
      log_ok "would $action (copy): $name ← $src"
    fi
    [ "$action" = "update" ] && updated=$((updated + 1)) || installed=$((installed + 1))
    return 0
  fi

  # Remove existing target when overwriting.
  if [ "$action" = "update" ]; then
    rm -rf "$dst"
  fi

  if [ "$MODE" = "link" ]; then
    # Use absolute symlink so the target is resilient to cwd changes.
    ln -s "$src" "$dst"
    log_ok "$action (symlink): $name"
  else
    # Prefer rsync if available for robust copy semantics; fall back to cp.
    if command -v rsync >/dev/null 2>&1; then
      rsync -a --delete "$src/" "$dst/"
    else
      cp -R "$src" "$dst"
    fi
    log_ok "$action (copy): $name"
  fi
  [ "$action" = "update" ] && updated=$((updated + 1)) || installed=$((installed + 1))
}

for entry in "${DISCOVERED[@]}"; do
  IFS=$'\t' read -r name path <<<"$entry"
  if ! install_one "$name" "$path"; then
    log_error "Failed to install: $name"
    failed=$((failed + 1))
  fi
done

echo
log_info "Summary: installed=${installed}  updated=${updated}  skipped=${skipped}  failed=${failed}"

if [ "$failed" -gt 0 ]; then
  exit 3
fi
exit 0
