---
name: evolve-suggest
description: At session-close, aggregate pending G2 feedback (from skills/td-nl/feedback-log.md) into per-skill value updates (Q^L) and the global V^L, then — when the TD error is strong enough — propose a concrete edit to a skill's SKILL.md. Runs a TextGrad-based backward pass with a TD(0) layer on top. Never auto-applies; a proposal is queued for user approval via evolve-apply.
---

# evolve-suggest

**Trigger**: Runs at `session-close`, after `memory-write` and `memory-consolidate`.

**Shared context**: Before running this skill, Read `skills/_shared/evolve-cycle.md` for the G2/G1 loop, DAG schema, TD(0) layer, infrastructure layout, and rollback rules.

This is the aggregation and reasoning step. It runs a TextGrad-style backward
pass over the per-session DAG of skill firings, scales the resulting textual
gradients by a TD(0) error, and (optionally) proposes spec edits.

**Preferred path — run the Python backend**:

```bash
python scripts/evolve_textgrad.py --apply-proposal --json
```

The backend (`skills/td-nl/textgrad_backend/`) performs all of Phases 1-6
below automatically and writes the cycle summary + optional PROPOSAL entry
back into `skills/td-nl/feedback-log.md`. Use `--dry-run` first if you want
a preview without mutating the log.

**Fallback path — execute the phases manually** (use when Python is not
available in the environment, or when you want to audit a specific step):

## Phase 1: Read Current State
1. Read `skills/td-nl/feedback-log.md § Pending Feedback`
2. If no pending feedback → terminate (nothing to update)
3. Read `skills/td-nl/value-function.md`
4. Read relevant `skills/td-nl/skill-values/*.md` for skills that fired

## Phase 2: DAG Reconstruction + Per-Skill Aggregation (G1)
5. Parse each pending G2 entry (schema v2: includes `session`, `node`,
   `upstream`). Group by session → per-session DAG of firings.
6. For each skill in each session:
   - Count: N_better, N_expected, N_worse
   - Compute `net_delta` = sum of all delta values
   - Synthesize `dominant_pattern` = 1-sentence summary of evidence
   - Confidence: high (6+ entries), medium (3-5), low (1-2)

## Phase 3: TD(0) Scoring + Per-Skill Value Update
7. For each skill with G1 output:
   a. Read current `overall` from `skill-values/{skill-name}.md` as V(s)
   b. Bootstrap V(s') = clip(V(s) + 0.5 · r_clipped, 1, 10)
   c. Compute TD error: `td = r + γ·V(s') - V(s)` with γ=0.9
   d. Strength: `hard` (|td| ≥ 1.0), `soft` (≥ 0.25), `drop` (< 0.25)
   e. Learning rate by confidence: high=1.0, medium=0.5, low=0.25
   f. Update: `new_score = clamp(old_score + lr · td, 1, 10)`
   g. Append session row to History table; write updated file.

## Phase 4: System Value Update
8. Recompute V^L from per-skill values:
   - intent_routing_accuracy ← average of trigger_accuracy across fired skills
   - output_quality ← average of output_usefulness
   - token_efficiency ← average of token_efficiency
   - overall ← weighted average
9. Compare with previous prediction → update delta_direction
10. Write updated `value-function.md`

## Phase 5: TextGrad Backward + Spec Edit Proposal (conditional)
11. Build a textgrad computation graph mirroring the DAG:
    - Each skill spec (SKILL.md) becomes a `requires_grad` Variable
    - Each firing node becomes an output Variable; its predecessors are its
      skill-spec Variable plus its upstream firing-nodes
    - Attach a `TextLoss` at the synthetic head aggregating all leaves
12. Call `loss.backward(critique)` where `critique` folds in the per-skill
    TD errors, strengths, and a short evidence digest
13. Run `TextualGradientDescent.step()` but only over skills with
    `strength == hard`. This enforces the one-edit-per-session safety cap
    (the proposal writer further narrows to the single highest |td| skill).
14. Check trigger conditions:
    - Any skill with `strength == hard`, OR
    - Same improvement_direction for a skill in 3+ consecutive sessions
    - If neither met → skip, log "insufficient signal"
15. Generate proposal:
    ```
    [EVOLVE] {skill-name} (Q^L: {old} → {new}, td: {±d.dd})
    Problem: {aggregated evidence}
    Gradient: {textual gradient from backward()}
    Diff: {candidate SKILL.md after TGD.step}
    Evidence: {aggregated G1 pattern}
    Risk: {what could break; history snapshot path}
    ```
16. Append proposal to `skills/td-nl/feedback-log.md § Pending Proposals`
17. Do NOT auto-apply — present to user for approval via `evolve-apply`.

## Phase 6: Cleanup
18. Move processed G2 entries from `## Pending Feedback` to `## Processed Feedback`
19. Write cycle summary (per-session):
    ```
    - Cycle YYYY-MM-DD [session:{sid}]: {N} entries across {M} skills (V^L old→new)
      - {skill-name}: net_delta=N, td_error=±d.dd, strength=hard|soft|drop
      - Spec proposal: {yes|none}
    ```

**Outputs**: Updated skill-values, updated value-function, optional spec edit proposal
**Token**: ~2-4K (the Python backend is essentially token-free; phases 1-6 manual fallback costs ~2-4K)
**Composition**: If proposal generated → present to user → `evolve-apply` on approval
