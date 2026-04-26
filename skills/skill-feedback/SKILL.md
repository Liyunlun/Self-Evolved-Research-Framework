---
name: skill-feedback
description: Online incremental Q-update for SER skills. Runs after a SER skill firing whenever a usable reward signal is present. Updates skills/td-nl/skill-values/{name}.md with an EWMA-with-anchor pull and, on hard signals (|delta| >= 1.0), appends a flagged entry that evolve-suggest later turns into a spec-edit proposal. Replaces the dead "G2 every firing → G1 batch" pipeline with an honest signal-gated update.
---

# skill-feedback

**Trigger**: Right after a SER micro-skill firing, **only when a usable reward signal exists**. Zero-signal firings cost zero tokens (skip).

**Shared context**: Read `skills/_shared/evolve-cycle.md` for the value-function layout, history archive, and rollback rules.

This is an **online incremental Q-update**. It is *not* TD(0) — there is no Markov state transition between skill firings. The math is honest EWMA-with-anchor: the per-skill value `Q^L` is pulled toward `Q^L + reward`, scaled by a confidence-dependent step size.

## When to fire (signal gate)

Fire `skill-feedback` for the just-completed skill if **any** of the following holds:

1. **Explicit user feedback** — the user, in the messages between the firing and now, told you the output was useful, useless, wrong, redundant, slow, etc. Includes corrections ("no, do it this way") and confirmations ("yes, that's right").
2. **Downstream consumption** — a subsequent skill in this session referenced the output (read its file, used its result, chained from it). Successful consumption is a positive signal; an immediate retry/rewrite is negative.
3. **Hard failure** — the skill emitted no output, errored, hit a tool denial, or produced a schema-invalid artifact.

If none of the three apply, **do not fire**. Self-assessed "I think this was fine" is not a reward signal — it was the failure mode of the dead G2 pipeline.

## Inputs

- `skill_name`: the skill that just fired (e.g., `paper-read`)
- `reward`: integer in {-2, -1, 0, +1, +2}
  - +2 user explicitly said the output was excellent / unblocked them
  - +1 user accepted output without correction, or downstream consumed it
  -  0 do not fire (gate already excluded this case)
  - -1 user corrected approach, or downstream had to retry
  - -2 hard failure or user explicitly rejected the output
- `confidence`: high | medium | low
  - high: explicit user statement
  - medium: clear downstream evidence
  - low: indirect / inferred
- `evidence`: one short sentence — what observable triggered this (cite the user message or downstream file)

## Math (EWMA-with-anchor)

```
Q_old   = read `overall` from skills/td-nl/skill-values/{skill_name}.md
                (create from _template.md if missing)
alpha   = 1.0 if confidence == high
        | 0.5 if confidence == medium
        | 0.25 if confidence == low
delta   = reward                       # the only learning signal
Q_new   = clip(Q_old + alpha * delta, 1, 10)
```

No bootstrapped `V(s')`, no fake γ. The "anchor" is the current `Q_old`; the "pull" is `alpha * reward`. This is incremental averaging with adjustable step size.

## Strength gate (controls *flagging*, not the update)

| |delta| | strength | Q^L update | Flag |
|---------|----------|------------|------|
| ≥ 2     | hard     | yes        | append `[FLAG-HARD]` line to feedback-log → eligible for proposal |
| 1       | soft     | yes        | append `[FLAG-SOFT]` line; promotes to hard if 3 same-direction firings in a row |
| 0       | drop     | (gate already filtered) | — |

`hard` flags are *candidates*, not commands. Single outliers should not trigger spec edits; `evolve-suggest` (now on-demand) decides whether to turn a flag into a proposal after looking at the surrounding flags.

## Process

1. Verify the gate (one of the three signal types above). If gate fails → exit, write nothing.
2. Read `skills/td-nl/skill-values/{skill_name}.md`. If missing, copy `_template.md` to that path with the skill name filled in.
3. Compute `Q_new` per the formula above. Clip to [1, 10].
4. Update the file:
   - `overall:` → `Q_new` (1 decimal)
   - Append a row to the `Session History` table:
     `| YYYY-MM-DD | {context-tag} | {outcome} | {±delta} | "{evidence}" |`
   - `total_firings` += 1
5. If `strength == hard` or `strength == soft`, append a one-line entry to `skills/td-nl/feedback-log.md § Pending Flags`:
   ```
   - [YYYY-MM-DD] [FLAG-{HARD|SOFT}] skill:{name} Q:{old}→{new} delta:{±r} conf:{c} ev:"{evidence}"
   ```
6. **Auto-rollback check** (only if the skill's `last_spec_edit` is within the last 5 firings of this skill): if `Q^L` has dropped by ≥ 1.5 since `last_spec_edit`, append:
   ```
   - [YYYY-MM-DD] [ROLLBACK-CANDIDATE] skill:{name} Q since edit: {Q_at_edit}→{Q_new} (Δ={drop})
   ```
   to `§ Pending Flags`. `evolve-suggest` will route this to `evolve-apply --rollback` next time the user runs it.

## What this skill does NOT do

- It does **not** auto-edit `SKILL.md`. Spec edits require `evolve-suggest` (proposal) → user approval → `evolve-apply`.
- It does **not** recompute `V^L`. That happens on demand via `evolve-suggest --audit` or at session-close if the user invokes it.
- It does **not** run a TextGrad backward pass. That belonged to the batch pipeline.
- It does **not** fire on every skill execution. Zero-signal firings are skipped.

## Token cost

- ~80–150 tokens per fire (read one file, append one row, optionally one feedback-log line). Zero tokens when the signal gate rejects.
- Per session: typically 3–8 fires, not 30+.

## Outputs

- Updated `skills/td-nl/skill-values/{skill_name}.md`
- Optional one-line append to `skills/td-nl/feedback-log.md § Pending Flags`

## Composition

- **Upstream**: any SER skill firing. Caller passes (`reward`, `confidence`, `evidence`) explicitly — no self-assessment.
- **Downstream**: `evolve-suggest` (when the user asks for an audit, or at session-close if invoked) reads the `§ Pending Flags` section to decide whether to draft a proposal.

## Tests

- Reward = 0 path → no file write (gate works).
- Reward = +1, low conf → Q_new = Q_old + 0.25, clipped to [1, 10].
- Reward = -2, high conf → Q_new = Q_old - 2, clipped, FLAG-HARD line written.
- Q_old = 9.5, reward = +2, high conf → Q_new = 10 (clip).
- Rollback path: simulate edit, then 3 consecutive -1s, verify ROLLBACK-CANDIDATE line appears.
