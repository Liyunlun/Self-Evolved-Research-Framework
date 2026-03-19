# Session Micro-Skills

> Auto-triggered at conversation boundaries. Zero user action required.

## session.open

**Trigger**: Every conversation start (automatic, before any other processing)

**Process**:
1. Silently read: `config.yaml` (project status, milestone), last `logs/digest/*.yaml`, `logs/digest/SUMMARY.md`
2. Read: `memory/MEMORY.md` + execute `memory.retrieve` for active context
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

---

## session.close

**Trigger**: Conversation is ending (detected via: user says goodbye/done, or long session with substantial work completed)

**Process**:
1. Auto-summarize the current session from conversation history:
   - What was discussed/accomplished (1-3 bullet points)
   - Key decisions made
   - Files created/modified
   - Token estimate for session
2. Present summary and ask: "Save session log? [Y/edit]"
3. On confirmation, write to `logs/digest/YYYY-MM-DD.yaml`:
   ```yaml
   date: "YYYY-MM-DD"
   type: "session"
   auto_strategy: "conversation-summary"
   summary: "{auto-generated}"
   accomplishments:
     - "{item}"
   decisions: []
   files_changed: []
   token_estimate: N
   milestone_phase: "{current phase}"
   ```
4. Update `logs/digest/SUMMARY.md` index table with new entry

**Inputs**: Conversation history, config.yaml
**Outputs**: `logs/digest/YYYY-MM-DD.yaml`, updated SUMMARY.md
**Token**: ~2K
**Composition**:
- Chain to `memory.write` (capture unrecorded insights/decisions)
- Chain to `memory.consolidate` (check if consolidation needed)
- Chain to `evolve.suggest` (G1 aggregation + skill value updates + optional spec edit proposal)
- Chain to `checklist.update` — mark completed items from this session
- Terminal after all chains complete
