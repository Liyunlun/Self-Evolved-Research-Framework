# /meta — Session Lifecycle, Self-Evolution & System Operations

When to use this skill:
- Every conversation start and end (session.open / session.close)
- Automatically after every skill execution (G2 assessment)
- When the system proposes or applies spec edits (evolve)
- Fallback for anything not caught by specialized skills

## session.open

**Trigger**: Every conversation start (automatic, before any other processing).

### Process
1. **Read configuration and recent history**:
   - `config.yaml` — project settings, phase, methodology
   - Most recent `logs/digest/*.yaml` — last session log
   - `logs/digest/SUMMARY.md` — running summary of all sessions
2. **Restore memory context**:
   - Read `memory/MEMORY.md`
   - Execute `memory.retrieve` for active context relevant to likely tasks
3. **Check progress**:
   - Read `Checklist.md`, compute done/total items
4. **Generate skill recommendations**:
   - Run: `~/.claude/ser/scripts/recommend.py --samples 10`
   - This produces `.claude/.ser-recommendations.json` via Thompson Sampling over skill weights
5. **Load recommendations and chains**:
   - Read `.claude/.ser-recommendations.json` (Thompson Sampling sample queues)
   - Read `~/.claude/ser/chains.yaml` (chain templates and triggers)
6. **Output status banner**:
   ```
   [SER] {project_name} | Phase {X} | [{done}/{total} items]
   Last session ({date}): {1-line summary}
   Next milestone: {goal} ({days}d)
   ```
7. **Milestone proximity check**:
   - If milestone is <= 3 days away, append: `** MILESTONE APPROACHING **`
8. Proceed to user's request

### Suggested Next
None — session.open is always the first skill executed

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
   - Remove `.claude/.ser-session-active` marker

### Suggested Next
Terminal — session.close is always the last skill executed

## G2 — Inline Skill Assessment

**Trigger**: After EVERY skill execution (automatic, silent — do not surface to user unless asked).

### Process
1. After a skill completes, assess its performance:
   - **Trigger accuracy**: Did the skill fire at the right time? Was it the correct skill for the situation?
   - **Output usefulness**: Was the output helpful and actionable?
2. Score the execution as one of:
   - `better` — exceeded expectations
   - `as_expected` — performed normally
   - `worse` — underperformed or was wrong skill
3. Append observation to `logs/observations/{session-file}.jsonl`:
   ```jsonl
   {"type":"skill","skill":"{name}","outcome":"{better|as_expected|worse}","delta":{+1|0|-1},"evidence":"{1-sentence}","ts":"{ISO8601}"}
   ```

### Suggested Next
None — G2 is automatic bookkeeping, no further chain

## evolve.suggest

**Trigger**: Runs at `session.close`, after memory operations complete (G1 Aggregation).

### Process
**Phase 1 — Read observations**:
Read all observation entries from `logs/observations/` for this session.

**Phase 2 — Per-skill aggregation**:
For each skill that was observed:
- Count `better`, `as_expected`, `worse` outcomes
- Compute `net_delta` = sum of all delta values
- Synthesize a pattern description (e.g., "writing.review consistently underperforms on methodology sections")

**Phase 3 — Per-skill value update**:
Apply learning rate based on confidence level:
| Confidence | Learning Rate | When |
|------------|---------------|------|
| High | 1.0 | 10+ observations, consistent direction |
| Medium | 0.5 | 5-9 observations, mostly consistent |
| Low | 0.25 | <5 observations, or mixed signals |

Update the skill's internal value estimate.

**Phase 4 — System value recomputation**:
Recompute the overall system performance value from all skill values weighted by usage frequency.

**Phase 5 — Spec edit proposal**:
Generate a concrete edit proposal if:
- `|net_delta| >= 3` for any skill, OR
- Same direction (all better or all worse) for 3+ consecutive sessions

The proposal includes: target skill, specific text to change, rationale, and expected impact.

**Phase 6 — Cleanup**:
- Move processed observation entries to archive
- Write cycle summary to `logs/evolution/`

### Suggested Next
- Proposal generated: present to user for approval, then `evolve.apply` on approval

## evolve.apply

**Trigger**: User approves a proposal from `evolve.suggest`.

### Process
**Phase 1 — Read pending proposals**:
Load all unapplied proposals from the most recent evolution cycle.

**Phase 2 — User approval**:
Present each proposal individually with:
- What will change
- Why (evidence from observations)
- Expected impact
User can approve, reject, or modify each proposal.

**Phase 3 — Apply edits**:
For each approved proposal:
1. Archive current spec: copy `.claude/skills/{group}/SKILL.md` to `.claude/skills/{group}/SKILL.md.bak.{timestamp}`
2. Apply the edit to the SKILL.md file
3. Update evolution records with the change

**Phase 4 — Rollback check**:
At the next session after applying edits:
- Monitor the modified skill's `output_usefulness` score
- If it drops >= 2 points compared to pre-edit baseline, auto-propose a rollback to the archived version

**Phase 5 — Evolution report**:
Summarize all applied changes, their rationale, and the rollback monitoring plan.

### Suggested Next
Terminal for the evolution cycle

## general.research

**Trigger**: Fallback — any user request not matched by a specialized skill.

### Process
1. Respond with full project context awareness:
   - Load `config.yaml` for project scope and methodology
   - Reference relevant `memory/` entries
   - Consider `logs/digest/` for recent session context
   - Check `papers/` for literature if relevant
2. If the response involves research artifacts (writing, proofs, experiments, ideas), suggest the appropriate specialized skill rather than handling it inline
3. Act as a context-aware general assistant — not a dumb fallback. Use all available project knowledge to give informed responses.

### Suggested Next
- May suggest specialized skills when the request touches their domain (e.g., "This looks like a proof task — want me to run `proof.sketch`?")
