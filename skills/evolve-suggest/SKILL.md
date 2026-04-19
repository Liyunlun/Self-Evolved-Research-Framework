---
name: evolve-suggest
description: At session-close, aggregate pending G2 feedback (from skills/td-nl/feedback-log.md) into per-skill value updates (Q^L) and the global V^L, then — when signal is strong enough — propose a concrete edit to a skill's SKILL.md. Never auto-applies; a proposal is queued for user approval via evolve-apply.
---

# evolve-suggest

**Trigger**: Runs at `session-close`, after `memory-write` and `memory-consolidate`.

**Shared context**: Before running this skill, Read `skills/_shared/evolve-cycle.md` for the G2/G1 loop, infrastructure layout, and rollback rules.

This is the aggregation and reasoning step. Processes all pending G2 feedback into
per-skill value updates and (optionally) proposes spec edits.

**Process**:

## Phase 1: Read Current State
1. Read `skills/td-nl/feedback-log.md § Pending Feedback`
2. If no pending feedback → terminate (nothing to update)
3. Read `skills/td-nl/value-function.md`
4. Read relevant `skills/td-nl/skill-values/*.md` for skills that fired

## Phase 2: Per-Skill Aggregation (G1)
5. For each skill with G2 entries this session:
   - Count: N_better, N_expected, N_worse
   - Compute `net_delta` = sum of all delta values
   - Synthesize `dominant_pattern` = 1-sentence summary of evidence
   - Confidence: high (6+ entries), medium (3-5), low (1-2)

## Phase 3: Per-Skill Value Update
6. For each skill with G1 output:
   a. Read current scores from `skill-values/{skill-name}.md`
   b. Learning rate by confidence: high=1.0, medium=0.5, low=0.25
   c. Update: `new_score = old_score + (net_delta × learning_rate)`, clamp to [1, 10]
   d. Update assessment fields (total_firings, success_rate, failure modes)
   e. Append session row to History table
   f. Write updated `skill-values/{skill-name}.md`

## Phase 4: System Value Update
7. Recompute V^L from per-skill values:
   - intent_routing_accuracy ← average of trigger_accuracy across fired skills
   - output_quality ← average of output_usefulness
   - token_efficiency ← average of token_efficiency
   - overall ← weighted average
8. Compare with previous prediction → update delta_direction
9. Write updated `value-function.md`

## Phase 5: Spec Edit Proposal (conditional)
10. Check trigger conditions:
    - Total |net_delta| across all skills >= 3, OR
    - Same improvement_direction for a skill in 3+ consecutive sessions
    - If neither met → skip, log "insufficient signal"
11. Identify target: the skill with highest |net_delta|
12. Read the current spec file (`skills/{skill-name}/SKILL.md`)
13. Generate specific edit proposal:
    ```
    [EVOLVE] {skill-name} (Q^L: {old} → {new})
    Problem: {what the feedback says is wrong}
    Proposed edit: {specific text change in the spec file}
    Evidence: {aggregated G1 pattern from N sessions}
    Expected impact: {what should improve}
    Risk: {what could break}
    ```
14. Append proposal to `skills/td-nl/feedback-log.md § Pending Proposals`
15. Do NOT auto-apply — present to user for approval

## Phase 6: Cleanup
16. Move processed G2 entries from Pending → Processed in feedback-log.md
17. Write cycle summary:
    ```
    - Cycle YYYY-MM-DD: {N} entries across {M} skills
      - {skill-name}: net_delta={N}, pattern="{summary}"
      - Spec proposal: {yes: "{description}" | none: "{reason}"}
    ```

**Outputs**: Updated skill-values, updated value-function, optional spec edit proposal
**Token**: ~2-4K
**Composition**: If proposal generated → present to user → `evolve-apply` on approval
