#!/usr/bin/env bash
# SER v6 — Session Guard Hook
# Fires on UserPromptSubmit. Ensures session.open runs on first message.
# Also checks for uncommitted code changes from previous sessions.
MARKER=".ser/session-active"
if [ ! -f "$MARKER" ]; then
    mkdir -p "$(dirname "$MARKER")" 2>/dev/null
    touch "$MARKER"
    echo "[SER] Execute session.open before responding. Read .claude/skills/meta/SKILL.md."

    # Check for uncommitted code changes from previous session
    if [ -d ".git" ] && [ -f "config.yaml" ]; then
        CODE_DIFF=$(git diff --name-only 2>/dev/null | grep -E '\.(py|jl|js|ts|sh|yaml)$' | head -1)
        STAGED_DIFF=$(git diff --cached --name-only 2>/dev/null | grep -E '\.(py|jl|js|ts|sh|yaml)$' | head -1)
        if [ -n "$CODE_DIFF" ] || [ -n "$STAGED_DIFF" ]; then
            echo "[SER] Uncommitted code changes from previous session. Run code.review → code.commit early."
        fi
    fi
fi
