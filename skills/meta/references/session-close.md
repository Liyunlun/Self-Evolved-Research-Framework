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
   - **CRITICAL for learning**: `skills_used` must list ALL skills invoked during the session (not just one).
     Each entry MUST use a canonical `chain` ID from `~/.claude/ser/chains.yaml`:
     `literature_survey`, `idea_pipeline`, `proof_cycle`, `paper_writing`,
     `experiment_loop`, `code_review_commit`, `code_plan_execute`.
     Leave `chain` empty if the skill was ad-hoc (not part of a chain).
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
