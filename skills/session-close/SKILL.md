---
name: session-close
description: Wraps up a conversation. Auto-summarizes the session, asks the user to save a digest log, writes logs/digest/YYYY-MM-DD.yaml, updates SUMMARY.md, then chains into memory-write, memory-consolidate, and checklist-update. Optionally invokes evolve-suggest for skill audit/proposal when the user asks for it. Triggers on end-of-conversation signals (user says goodbye/done, or a long session with substantial work completed).
---

# session-close

**Trigger**: Conversation is ending (detected via: user says goodbye/done, or long session with substantial work completed).

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
5. Skill evolution is **not** run automatically at session-close. Per-firing
   `Q^L` updates already happened online via `skill-feedback` whenever a real
   reward signal was present. Offer once: "Run skill audit? [y/N]" — if yes,
   chain to `evolve-suggest`; otherwise terminate. Defaulting off keeps
   session-close cheap and avoids the dead-batch failure mode of the v3
   pipeline (running aggregation when there is nothing to aggregate).

**Inputs**: Conversation history, config.yaml
**Outputs**: `logs/digest/YYYY-MM-DD.yaml`, updated SUMMARY.md
**Token**: ~2K (plus ~2-3K only if the user opts into `evolve-suggest`)
**Composition**:
- Chain to `memory-write` (capture unrecorded insights/decisions)
- Chain to `memory-consolidate` (check if consolidation needed)
- Chain to `checklist-update` — mark completed items from this session
- Optional: chain to `evolve-suggest` only if the user accepted the audit prompt
- Terminal after all chains complete
