# Skill Evolution Cycle — Shared Reference

> Shared reference for the evolution skills (`skill-feedback`, `evolve-suggest`,
> `evolve-apply`). Describes the value-function infrastructure, the online
> incremental Q-update path, the on-demand audit/proposal path, and the
> rollback mechanism.
>
> Not a skill itself (no `SKILL.md`). Skills that need this reference Read it
> on demand.

---

## Architecture (replaces the v3 batch G2→G1 pipeline)

The previous design said "every skill firing writes a 5-phase G2 block; at
session-close, G1 aggregates them and proposes spec edits." In practice G2
was rarely populated, G1 always reported 'no pending feedback', and evolution
never happened. The fix is **not** to enforce G2 harder — it is to remove the
self-assessment step entirely and only update values when there is a real
signal.

```
OLD (deprecated, do not implement):
  every firing → 5-phase G2 → session-close → G1 batch → TextGrad → proposal
                                                       ^ never reached

NEW (signal-gated online):
  firing with reward signal ──► skill-feedback ──► EWMA Q-update
                                       │            (+ optional FLAG line)
                                       │
  user types `audit` / session-close ──► evolve-suggest
                                            ├─ reads § Pending Flags
                                            ├─ recomputes V^L from Q^L's
                                            └─ drafts proposal (if hard signal)
                                                       │
                                            user approves
                                                       │
                                                       ▼
                                                evolve-apply
                                                (archive + edit)
```

Two-tier separation:

| Tier | Skill | Frequency | Token cost | Purpose |
|------|-------|-----------|------------|---------|
| Online | `skill-feedback` | Per-firing **with reward** (~3-8/session) | ~80-150 ea | Keep Q^L current |
| Audit  | `evolve-suggest` | On demand or at session-close | ~2-3K | Aggregate flags, draft spec proposal, recompute V^L |

`skill-feedback` is honest about being an EWMA-with-anchor. It is **not**
TD(0): there is no Markov state-transition between skill firings, no `V(s')`
to bootstrap from. Calling it TD(0) was a category error in the old design.

---

## Infrastructure

```
skills/td-nl/
  feedback-log.md          # § Pending Flags  +  § Processed Flags
  value-function.md        # V^L: derived from Q^L's (recomputed, not stored as ground truth)
  skill-values/            # Q^L per skill
    _template.md           # Template for new skill value files
    {skill-name}.md        # Per-skill Q^L
  history/                 # Spec version archive for rollback
    {skill}-v{N}.md        # Snapshot before edit
```

`feedback-log.md` is no longer a stream of G2 blocks. It is a list of flags
(`[FLAG-HARD]`, `[FLAG-SOFT]`, `[ROLLBACK-CANDIDATE]`, `[APPLIED]`,
`[ROLLBACK]`) that survive until `evolve-suggest` processes them.

---

## skill-feedback — Online Q-update (signal-gated)

Full spec lives in `skills/skill-feedback/SKILL.md`. Key invariants:

**Signal gate** — fire only when one of these is true:
1. Explicit user feedback in the messages following the firing.
2. Downstream skill consumed the output (or had to redo it).
3. Hard failure (no output, error, schema-invalid artifact).

Self-assessment is **not** a signal source. That was the failure mode of v3.

**Math (EWMA-with-anchor)**:
```
alpha = 1.0 (high) | 0.5 (medium) | 0.25 (low)   # confidence
Q_new = clip(Q_old + alpha * reward, 1, 10)
```
`reward ∈ {-2, -1, +1, +2}`. (`reward = 0` is the gate-rejected case; never reached.)

**Strength gate (controls flagging only — Q always updates)**:
- `|reward * alpha|` ≥ 2 (loosely: |delta| ≥ 2) → `[FLAG-HARD]`, eligible for proposal
- `|reward * alpha|` ≥ 1 → `[FLAG-SOFT]`, promotes to hard after 3 same-direction firings
- otherwise: silent update

---

## evolve-suggest — On-demand Audit & Proposal

No longer a mandatory session-close step. The user invokes it explicitly
(or `session-close` invokes it only if the user opts in).

Process:
1. Read `feedback-log.md § Pending Flags`. If empty → terminate.
2. Read `value-function.md` and per-skill `skill-values/*.md` for any skill
   that appears in the flag list.
3. **Recompute V^L** as a derived quantity (no separate update path):
   ```
   V^L.overall = recency-weighted mean of Q^L.overall across all skills with
                 at least one firing in the last 30 days
   ```
4. **Decide whether to propose** a spec edit. Propose iff:
   - At least one `[FLAG-HARD]` exists in pending flags, OR
   - `[FLAG-SOFT]` for the same skill in the same direction appears 3+ times
     consecutively in the flag list.
5. **Pick one skill** (the one with the largest |Q_new − Q_old| since its
   last edit). Draft a proposal:
   ```
   [PROPOSE] {skill-name} (Q^L: {old} → {new})
     Pattern: {synthesized from the flag evidence strings}
     Suggested edit: {1-3 sentence prose change to SKILL.md}
     Risk: {what could break; history snapshot path skills/td-nl/history/{name}-v{N}.md}
   ```
6. Append the proposal to `feedback-log.md § Pending Proposals`.
7. Move processed flags from `§ Pending Flags` to `§ Processed Flags`.
8. Do **not** auto-apply. The user runs `evolve-apply` to commit.

**Audit mode** (`evolve-suggest --audit`): does steps 1–3 only; reports the
flag distribution and current V^L without drafting a proposal.

---

## evolve-apply Safety Rules

Applied by `evolve-apply` when the user approves a proposal:

1. **Archive before edit**: copy `skills/{skill-name}/SKILL.md` →
   `skills/td-nl/history/{skill-name}-v{N}.md` before any modification.
2. **One edit per session**: max 1 spec edit per session to keep
   cause-effect attribution clean.
3. **Stamp the skill-values file**:
   - `last_spec_edit` → today's date
   - `edit_reason` → proposal summary
   - `Q_at_edit` → record current Q^L (used by the rollback gate)
4. **Append `[APPLIED]`** to feedback-log:
   ```
   - [YYYY-MM-DD] [APPLIED] skill:{name} v{N-1}→v{N} "{edit summary}"
   ```

---

## Rollback Mechanism (defined, not decorative)

The old doc said "check rollback conditions" without specifying them. The new
gate is explicit:

**Trigger**: within 5 firings after `last_spec_edit`, if `Q^L` has dropped
by ≥ 1.5 from `Q_at_edit`, `skill-feedback` writes a `[ROLLBACK-CANDIDATE]`
flag.

**Action**: next `evolve-suggest` run sees the rollback candidate and stages
an `evolve-apply --rollback` proposal. On user approval:
- Copy `skills/td-nl/history/{skill-name}-v{N-1}.md` back to
  `skills/{skill-name}/SKILL.md`
- Append:
  ```
  - [YYYY-MM-DD] [ROLLBACK] skill:{name} v{N}→v{N-1} reason:"Q^L drop of {drop} within 5 firings"
  ```
- Rollbacks **count** against the one-edit-per-session cap.

---

## V^L — Global System Value (derived)

Stored in `skills/td-nl/value-function.md` for display, but recomputed by
`evolve-suggest` rather than maintained by a separate update path:

```
V^L.overall = sum_{s in active_skills}  w(s) * Q^L_s.overall
            / sum_{s in active_skills}  w(s)

where w(s) = exp(-days_since_last_firing(s) / 14)   # 14-day half-life
      active_skills = skills with at least one firing in the last 30 days
```

Component scores (`intent_routing_accuracy`, `output_quality`,
`token_efficiency`) are computed analogously from the per-skill `Q^L`
component fields.

`delta_direction` (`improving` / `stable` / `degrading`) is set by comparing
the current `V^L.overall` to the value last written, with hysteresis: change
only when |new − old| ≥ 0.3.

---

## Migration notes (from v3 batch pipeline)

- The v3 5-phase G2 block format is **deprecated**. Existing G2 entries in
  `feedback-log.md § Pending Feedback` can stay as-is — `evolve-suggest`
  reads the new `§ Pending Flags` section instead. A one-shot migration
  script (optional) can collapse old G2 blocks into flags by `outcome`.
- The `textgrad_backend/` directory and the TextGrad backward-pass code
  path are no longer load-bearing. Keep the directory for now in case
  someone wants to revisit batch attribution; mark it deprecated in its
  README.
- `evolve-suggest --apply-proposal --json` (Python backend invocation) is
  retained but now operates on `§ Pending Flags` only.
