## session.close

**Trigger**: Conversation ending — user says goodbye/done, or a long session with substantial work has been completed.

### Process
1. **Auto-summarize session**:
   - 1-3 key points of what was accomplished
   - Decisions made and their rationale
   - Files changed (created, modified, deleted)
   - Record all user text input from the session
2. **Confirm with user**:
   - Present the summary
   - Ask: "Save session log? [Y/edit]"
3. **Persist session log**:
   - Write to `logs/digest/YYYY-MM-DD.yaml`
   - Update `logs/digest/SUMMARY.md` with one-line entry
4. **Memory operations**:
   - Execute `memory.write` for any unwritten insights from the session
   - Execute `memory.consolidate` if thresholds are met
5. **Evolution cycle**:
   - Execute `evolve.suggest` (G1 aggregation over this session's observations)
6. **Update skill weights**:
   - Run: `~/.claude/ser/scripts/update_weights.py`
   - This updates `~/.claude/ser/weights.yaml` from observations in `logs/observations/`
7. **Clean up**:
   - Remove `.ser/session-active` marker via `rm -f .ser/session-active`

### Suggested Next
Terminal — session.close is always the last skill executed
