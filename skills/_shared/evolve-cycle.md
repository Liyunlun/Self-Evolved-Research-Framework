# TD-NL Skill Evolution Cycle — Shared Reference

> Shared reference for the `evolve-*` skills. Describes the TD-NL infrastructure,
> the G2 (inline) → G1 (aggregated) feedback loop, and the rollback mechanism.
>
> Not a skill itself (no `SKILL.md`). Each `evolve-*/SKILL.md` reads this file
> for the cycle definition, file layout, and safety rules.

---

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

---

## G2 — Inline Skill Assessment

**When**: After EVERY micro-skill execution (automatic, silent).

G2 is the raw feedback signal. Appended to `skills/td-nl/feedback-log.md § Pending`.

**Process**:
1. After a micro-skill completes, assess its performance:
   - Did the skill trigger correctly? (right intent detected)
   - Was the output useful to the user? (did they use it, reject it, modify it?)
   - Was the token cost proportional to the value delivered?
2. Score as: `better` (exceeded expectations), `as_expected`, `worse` (missed or unhelpful)
3. Append to feedback-log.md:
   ```
   - [YYYY-MM-DD] skill:{skill-name} | outcome:{better|as_expected|worse} | delta:{+1|0|-1} | "{1-sentence evidence}"
   ```
4. If `skill-values/{skill-name}.md` doesn't exist yet, create from `_template.md`

**Token**: ~100-200 (just a log append)

**Important**: G2 is cheap and frequent. Do NOT skip it. The quality of evolution
depends entirely on honest, granular feedback. Even "as_expected" is valuable signal.

---

## G1 — Session-Close Aggregation

Runs inside `evolve-suggest` at `session-close`, after `memory-write` and
`memory-consolidate`. Aggregates pending G2 entries into per-skill value
updates and (optionally) proposes spec edits.

See `skills/evolve-suggest/SKILL.md` for the full 6-phase process (Read →
Aggregate → Update Values → Update V^L → Propose Edit → Cleanup).

Learning rate by confidence:
- high (6+ entries): 1.0
- medium (3-5 entries): 0.5
- low (1-2 entries): 0.25

Score update: `new_score = clamp(old_score + net_delta × learning_rate, 1, 10)`.

### Spec-edit trigger

A spec edit is proposed only when:
- Total `|net_delta|` across all skills ≥ 3, OR
- Same `improvement_direction` for a skill across 3+ consecutive sessions.

Otherwise `evolve-suggest` logs "insufficient signal" and skips proposal.

---

## evolve-apply Safety Rules

Applied by `evolve-apply` when the user approves a proposal:

1. **Archive before edit**: copy `skills/{skill-name}/SKILL.md` →
   `skills/td-nl/history/{skill-name}-v{N}.md` before any modification.
2. **One edit per session**: max 1 spec edit per session to prevent cascading
   changes obscuring cause-effect attribution.
3. **Post-edit tracking**: update `skill-values/{skill-name}.md`:
   - `last_spec_edit` → today's date
   - `edit_reason` → proposal summary
4. **Apply log entry** in `feedback-log.md`:
   ```
   - [YYYY-MM-DD] APPLIED: {skill-name} v{N-1}→v{N}: "{edit summary}"
   ```

---

## Rollback Mechanism

Safety net for bad edits. Checked by `evolve-suggest` at the next session-close:

- If `output_usefulness` dropped ≥ 2 points since the edit, auto-propose a rollback.
- Rollback = copy `skills/td-nl/history/{skill-name}-v{N-1}.md` back to
  `skills/{skill-name}/SKILL.md`.
- Log line:
  ```
  - [YYYY-MM-DD] ROLLBACK: {skill-name} v{N}→v{N-1}: "{reason}"
  ```
- Rollbacks count against the "one edit per session" cap (they're edits too).

---

## V^L — Global System Value

Stored in `skills/td-nl/value-function.md`. Recomputed at each `evolve-suggest`:

- `intent_routing_accuracy` ← average of `trigger_accuracy` across fired skills
- `output_quality` ← average of `output_usefulness`
- `token_efficiency` ← average of `token_efficiency`
- `overall` ← weighted average (weights configurable in `config.yaml`)

Compared with previous prediction to update `delta_direction` (improving / stable / degrading).
