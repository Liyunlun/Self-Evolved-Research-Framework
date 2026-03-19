# Meta Micro-Skills — Skill Evolution via TD-NL

> The framework evolves its own micro-skills through natural language reinforcement learning.
> Each micro-skill has a value estimate (Q^L). Feedback accumulates during sessions.
> At session.close, `evolve.suggest` aggregates feedback and proposes spec improvements.
> On user approval, `evolve.apply` edits the skill specs with version tracking and rollback.

## TD-NL Infrastructure

```
skills/td-nl/
  feedback-log.md          # Append-only session feedback (G2 entries)
  value-function.md        # V^L: global skill system assessment
  skill-values/            # Q^L per skill (created on first firing)
    _template.md           # Template for new skill value files
    {skill-name}.md        # Per-skill value (e.g., paper-read.md)
  history/                 # Spec version archive for rollback
    {skill}-v{N}.md        # Snapshot before edit
```

## G2: Inline Skill Assessment

**Trigger**: After EVERY micro-skill execution (automatic, silent).

This is the raw feedback signal. Appended to `skills/td-nl/feedback-log.md § Pending`.

**Process**:
1. After a micro-skill completes, assess its performance:
   - Did the skill trigger correctly? (right intent detected)
   - Was the output useful to the user? (did they use it, reject it, modify it?)
   - Was the token cost proportional to the value delivered?
2. Score as: `better` (exceeded expectations), `as_expected`, `worse` (missed or unhelpful)
3. Append to feedback-log.md:
   ```
   - [YYYY-MM-DD] skill:{skill_name} | outcome:{better|as_expected|worse} | delta:{+1|0|-1} | "{1-sentence evidence}"
   ```
4. If skill-values/{skill-name}.md doesn't exist yet, create from `_template.md`

**Token**: ~100-200 (just a log append)

**Important**: G2 is cheap and frequent. Do NOT skip it. The quality of evolution
depends entirely on honest, granular feedback. Even "as_expected" is valuable signal.

---

## evolve.suggest (G1 Aggregation + Proposal)

**Trigger**: Runs at `session.close`, after `memory.write` and `memory.consolidate`.

This is the aggregation and reasoning step. Processes all pending G2 feedback into
per-skill value updates and (optionally) proposes spec edits.

**Process**:

### Phase 1: Read Current State
1. Read `skills/td-nl/feedback-log.md § Pending Feedback`
2. If no pending feedback → terminate (nothing to update)
3. Read `skills/td-nl/value-function.md`
4. Read relevant `skills/td-nl/skill-values/*.md` for skills that fired

### Phase 2: Per-Skill Aggregation (G1)
5. For each skill with G2 entries this session:
   - Count: N_better, N_expected, N_worse
   - Compute `net_delta` = sum of all delta values
   - Synthesize `dominant_pattern` = 1-sentence summary of evidence
   - Confidence: high (6+ entries), medium (3-5), low (1-2)

### Phase 3: Per-Skill Value Update
6. For each skill with G1 output:
   a. Read current scores from skill-values/{skill}.md
   b. Learning rate by confidence: high=1.0, medium=0.5, low=0.25
   c. Update: `new_score = old_score + (net_delta × learning_rate)`, clamp to [1, 10]
   d. Update assessment fields (total_firings, success_rate, failure modes)
   e. Append session row to History table
   f. Write updated skill-values/{skill}.md

### Phase 4: System Value Update
7. Recompute V^L from per-skill values:
   - intent_routing_accuracy ← average of trigger_accuracy across fired skills
   - output_quality ← average of output_usefulness
   - token_efficiency ← average of token_efficiency
   - overall ← weighted average
8. Compare with previous prediction → update delta_direction
9. Write updated value-function.md

### Phase 5: Spec Edit Proposal (conditional)
10. Check trigger conditions:
    - Total |net_delta| across all skills >= 3, OR
    - Same improvement_direction for a skill in 3+ consecutive sessions
    - If neither met → skip, log "insufficient signal"
11. Identify target: the skill with highest |net_delta|
12. Read the current spec file (`skills/micro/{skill}.md`)
13. Generate specific edit proposal:
    ```
    [EVOLVE] {skill_name} (Q^L: {old} → {new})
    Problem: {what the feedback says is wrong}
    Proposed edit: {specific text change in the spec file}
    Evidence: {aggregated G1 pattern from N sessions}
    Expected impact: {what should improve}
    Risk: {what could break}
    ```
14. Append proposal to `skills/td-nl/feedback-log.md § Pending Proposals`
15. Do NOT auto-apply — present to user for approval

### Phase 6: Cleanup
16. Move processed G2 entries from Pending → Processed in feedback-log.md
17. Write cycle summary:
    ```
    - Cycle YYYY-MM-DD: {N} entries across {M} skills
      - {skill}: net_delta={N}, pattern="{summary}"
      - Spec proposal: {yes: "{description}" | none: "{reason}"}
    ```

**Outputs**: Updated skill-values, updated value-function, optional spec edit proposal
**Token**: ~2-4K
**Composition**: If proposal generated → present to user → `evolve.apply` on approval

---

## evolve.apply

**Trigger**: User approves a proposal from `evolve.suggest`, or explicitly asks to
improve the framework ("apply those improvements", "evolve the skills").

**Process**:

### Phase 1: Read Proposals
1. Read pending proposals from `skills/td-nl/feedback-log.md § Pending Proposals`
2. If called with a specific proposal, use that; otherwise present all pending
3. For each proposal, show: skill, problem, proposed edit, evidence, risk

### Phase 2: User Approval
4. Present proposals and get explicit approval per proposal
5. User can: approve, reject, or modify each proposal

### Phase 3: Apply Edits (for each approved proposal)
6. Archive current spec: copy `skills/micro/{skill}.md` → `skills/td-nl/history/{skill}-v{N}.md`
7. Apply the edit to `skills/micro/{skill}.md`
8. Update the skill-values/{skill}.md:
   - Set `last_spec_edit` to today's date
   - Set `edit_reason` to the proposal summary
9. Log to feedback-log.md:
   ```
   - [YYYY-MM-DD] APPLIED: {skill} v{N-1}→v{N}: "{edit summary}"
   ```

### Phase 4: Rollback Check (next session)
10. At the next `evolve.suggest`, compare pre-edit and post-edit performance:
    - If output_usefulness dropped >= 2 points → auto-propose rollback
    - Rollback: restore from `skills/td-nl/history/{skill}-v{N-1}.md`
    - Log: `[YYYY-MM-DD] ROLLBACK: {skill} v{N}→v{N-1}: "{reason}"`

### Phase 5: Evolution Report
11. Generate report:
    ```yaml
    date: "YYYY-MM-DD"
    skills_modified: ["{skill}"]
    proposals_approved: N
    proposals_rejected: N
    details:
      - skill: "{name}"
        change: "{description}"
        evidence_sessions: N
        pre_edit_score: X
    ```
12. Append to config.yaml `evolution_history`
13. Update CLAUDE.md if behavioral routing changed (rare)

**Outputs**: Modified skill specs + version archive + evolution log
**Token**: ~2-5K
**Composition**: Terminal for the evolution cycle

---

## Rollback Mechanism

Safety net for bad edits:
- Every spec edit is archived in `skills/td-nl/history/`
- If post-edit performance drops >= 2 points on output_usefulness, `evolve.suggest`
  auto-proposes a rollback at next session.close
- Rollback restores the archived version and logs the revert
- Max 1 spec edit per session (prevents cascading changes)

---

## general.research

**Trigger**: Fallback — anything not caught by other micro-skills.

**Process**:
1. Respond to user's request with full project context awareness
2. Leverage knowledge of:
   - Current project state (config.yaml)
   - Research direction (methodology/)
   - Recent progress (logs/)
   - Paper reading history (papers/)
3. If the response involves research artifacts, suggest the appropriate specialized micro-skill
4. This is NOT a dumb fallback — it's a context-aware general assistant

**Inputs**: User's request + project context
**Outputs**: Context-aware response
**Token**: varies
**Composition**: May suggest specialized micro-skills when relevant
