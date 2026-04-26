---
name: evolve-suggest
description: On-demand audit and spec-edit proposer for the SER skill evolution cycle. Reads skills/td-nl/feedback-log.md § Pending Flags (written by skill-feedback during normal use), recomputes V^L from per-skill Q^L's, and — when the flag pattern meets the proposal threshold — drafts a single spec edit for the most-affected skill. Never auto-applies. Triggered by the user (e.g. "audit the skills", "propose any skill edits") or optionally invoked from session-close.
---

# evolve-suggest

**Trigger**: On demand. The user asks for an audit or for the framework to
propose skill improvements. May also be invoked from `session-close` if the
user opts into the optional evolution step.

**Shared context**: Read `skills/_shared/evolve-cycle.md` for the
infrastructure layout, the online vs. audit split, and rollback rules.

This skill no longer runs the per-firing learning loop — that lives in
`skill-feedback` (online, EWMA-with-anchor, signal-gated). `evolve-suggest`
now does three things only:

1. Recompute the global system value `V^L` from current per-skill `Q^L`'s.
2. Decide whether the accumulated `[FLAG-HARD]` / `[FLAG-SOFT]` /
   `[ROLLBACK-CANDIDATE]` lines justify a spec-edit proposal.
3. Draft at most **one** proposal and queue it for `evolve-apply`.

## Modes

- **Default**: full audit + propose-if-justified.
- **`--audit`** (or user says "just audit, don't propose"): steps 1–3 below
  only. No proposal drafted.
- **`--apply-proposal --json`**: legacy Python-backend invocation; same
  pipeline, machine-readable output. The TextGrad backward pass path that
  used to run here is removed — it only made sense for the deprecated batch
  G2→G1 pipeline.

## Phase 1 — Read state

1. Read `skills/td-nl/feedback-log.md`. Locate `§ Pending Flags`.
2. If empty → exit with "no pending flags; nothing to audit". Skip the rest.
3. Read `skills/td-nl/value-function.md` (current `V^L`).
4. Read `skills/td-nl/skill-values/{name}.md` for every skill named in the
   pending flags (and any skill referenced for V^L recomputation).

## Phase 2 — Recompute V^L (derived, not stored separately)

Per `_shared/evolve-cycle.md § V^L`:

```
V^L.overall = sum_{s in active_skills}  w(s) * Q^L_s.overall
            / sum_{s in active_skills}  w(s)

w(s) = exp(-days_since_last_firing(s) / 14)
active_skills = skills with at least one firing in the last 30 days
```

Component fields (`intent_routing_accuracy`, `output_quality`,
`token_efficiency`) are recomputed the same way from the corresponding
per-skill components. Update `delta_direction` with hysteresis (change only
when |Δ| ≥ 0.3 vs the previously written value). Write
`skills/td-nl/value-function.md`.

In `--audit` mode, **stop here** and emit a short report:

```
[AUDIT] V^L: {old} → {new} (Δ {±d.dd}, direction: {improving|stable|degrading})
        active skills: {N}
        pending flags:  HARD={a}  SOFT={b}  ROLLBACK={c}
        top movers:
          - {skill}: Q^L {q_old}→{q_new}
          - ...
```

## Phase 3 — Proposal trigger

Draft a proposal iff **either**:
- At least one `[FLAG-HARD]` line exists in pending flags, OR
- `[FLAG-SOFT]` for the same skill in the same direction (positive vs.
  negative) appears **3+ times in a row** in the flag list.

If neither holds → log `insufficient signal — no proposal` and proceed to
Phase 5.

If a `[ROLLBACK-CANDIDATE]` line exists, route to **Phase 4b** (rollback
proposal) instead of a forward edit. A rollback always wins over a forward
edit in the same session.

## Phase 4a — Forward proposal

Pick **one** skill: the one with the largest `|Q_new − Q_at_edit|` since its
last edit (or `|Q_new − Q_first_seen|` if it has never been edited).

Synthesize the proposal:

1. **Pattern**: 1–2 sentence summary of the flag evidence strings — what
   actually went wrong or right across firings. Quote at most one short
   evidence snippet.
2. **Suggested edit**: 1–3 sentences describing the prose change to apply
   to `skills/{skill-name}/SKILL.md`. Be specific about *where* in the spec
   the change goes (e.g., "in the 'Process' section, add a step before X").
   Do not paste a full rewritten file.
3. **Risk**: name what could regress, and the rollback path
   `skills/td-nl/history/{skill-name}-v{N}.md` that `evolve-apply` will
   create.

Append to `skills/td-nl/feedback-log.md § Pending Proposals`:

```
- [YYYY-MM-DD] [PROPOSE] skill:{name} Q^L:{old}→{new}
    Pattern: {pattern}
    Edit:    {suggested edit}
    Risk:    {risk + history path}
```

## Phase 4b — Rollback proposal

When a `[ROLLBACK-CANDIDATE]` exists for skill `S`:

1. Locate the most recent `[APPLIED]` entry for `S` in `§ Processed Flags`
   (or the historical applied log).
2. Read `skills/td-nl/history/{S}-v{N-1}.md` to confirm it exists.
3. Append:
   ```
   - [YYYY-MM-DD] [PROPOSE-ROLLBACK] skill:{S} v{N}→v{N-1}
       Reason: {rollback evidence — Q^L drop of {drop} within 5 firings}
       Restores: skills/td-nl/history/{S}-v{N-1}.md
   ```

## Phase 5 — Cleanup

- Move flags consumed by Phase 3/4 from `§ Pending Flags` to
  `§ Processed Flags` (annotated with the cycle date).
- Write a one-line cycle summary at the top of `§ Processed Flags`:
  ```
  - Cycle YYYY-MM-DD: {N} flags processed → V^L {old}→{new}, proposal: {forward|rollback|none}
  ```

## What this skill never does

- It does **not** modify any `SKILL.md` file directly. Spec edits are the
  job of `evolve-apply` after user approval.
- It does **not** write per-skill `Q^L` updates. Those happen online via
  `skill-feedback`.
- It does **not** require pending G2 blocks in the v3 5-phase format.
  That format is deprecated and migrated to flags.
- It does **not** run the TextGrad backward pass. That belonged to the
  batch DAG attribution and added cost without changing outcomes after the
  feedback signal moved online.

## Outputs

- Updated `skills/td-nl/value-function.md` (recomputed V^L)
- Optional one or two lines appended to `skills/td-nl/feedback-log.md`
  (proposal + cycle summary)

## Token cost

- `--audit`: ~1–2K (read flags, read skill-values, recompute, emit report)
- Default (with proposal drafting): ~2–3K
- Old v3 cost was ~2–4K + per-firing G2 blocks (~200-400 tokens × every
  firing) that mostly never got read. Net win is on the per-session
  amortised cost, not the per-invocation one.

## Composition

- **Upstream**: `skill-feedback` (writes the flags this skill consumes).
- **Downstream**: user reviews proposal → `evolve-apply` (forward edit or
  rollback).
- May be invoked at `session-close` when the user opts in. Not mandatory.
