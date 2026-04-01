# Session Micro-Skills

> Auto-triggered at conversation boundaries. Zero user action required.

## session.open

**Trigger**: Every conversation start (automatic, before any other processing)

**Process**:
1. Silently read: `config.yaml`, latest `logs/digest/*.yaml`, `Checklist.md` (compute done/total)
2. Read: `memory/MEMORY.md`
3. Run: `~/.claude/ser/scripts/recommend.py --samples 10` (read output for chain suggestion)
4. Output status banner:
   ```
   [SER] {project_name} | Phase {X} | [{done}/{total} items]
   Last session ({date}): {1-line summary from last log}
   ```
5. Proceed immediately to user's request → Skill Execution Loop

**Inputs**: config.yaml, last digest log, Checklist.md
**Outputs**: Status banner (inline, not saved)
**Token**: ~1K
**Composition**: None (always first)

---

## session.close

**Trigger**: Conversation is ending (detected via: user says goodbye/done, or long session with substantial work completed)

**Process**:
1. Auto-summarize the current session from conversation history:
   - What was discussed/accomplished (1-3 bullet points)
   - Key decisions made
   - Files created/modified
2. Record skill observations — for each skill used this session, append to `logs/observations/YYYY-MM-DD.jsonl`:
   ```jsonl
   {"type":"skill","skill":"{name}","chain":"{chain|null}","outcome":"{better|as_expected|worse}","ts":"{ISO8601}"}
   ```
3. Present summary and ask: "Save session log? [Y/edit]"
4. On confirmation, write to `logs/digest/YYYY-MM-DD.yaml`:
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
5. Update `logs/digest/SUMMARY.md` index table with new entry

**Inputs**: Conversation history, config.yaml
**Outputs**: `logs/digest/YYYY-MM-DD.yaml`, updated SUMMARY.md
**Token**: ~2K
**Composition**:
- Chain to `memory.write` (capture unrecorded insights/decisions)
- Chain to `memory.consolidate` (check if consolidation needed)
- Chain to `evolve.suggest` (G1 aggregation + skill value updates + optional spec edit proposal)
- Chain to `checklist.update` — mark completed items from this session
- Terminal after all chains complete
