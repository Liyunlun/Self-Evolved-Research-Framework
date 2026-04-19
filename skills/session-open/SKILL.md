---
name: session-open
description: Runs silently at the start of every conversation. Reads config.yaml, the most recent session log, memory/MEMORY.md, and Checklist.md, then prints a one-screen SER status banner (project, phase, item counts, V^L, last session, next milestone). Fires before any other processing — triggered by conversation start, not by user words.
---

# session-open

**Trigger**: Every conversation start (automatic, before any other processing).

**Process**:
1. Silently read: `config.yaml` (project status, milestone), last `logs/digest/*.yaml`, `logs/digest/SUMMARY.md`
2. Read: `memory/MEMORY.md` + execute `memory-retrieve` for active context
3. Read: `skills/td-nl/value-function.md` (current V^L)
4. Read: `Checklist.md` (project progress root — compute done/total item counts)
5. Output status banner:
   ```
   [SER] {project_name} | Phase {X} | [{done}/{total} items] | V^L={overall}/10
   Last session ({date}): {1-line summary from last log}
   Next milestone: {milestone_goal} ({days_remaining}d)
   ```
6. If milestone <= 3 days away, append: `** MILESTONE APPROACHING **`
7. Proceed immediately to user's request — no questions asked

**Inputs**: config.yaml, last digest log, SUMMARY.md, Checklist.md
**Outputs**: Status banner (inline, not saved)
**Token**: ~1K
**Composition**: None (always first)

**Strategy auto-selection**:
- If many untracked git changes detected: note in banner `({N} untracked changes)`
- If last session was >7 days ago: add `(long gap — consider /review for catch-up)`
