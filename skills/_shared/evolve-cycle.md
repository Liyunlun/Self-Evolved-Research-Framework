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

## G2 — Inline Skill Assessment (5-phase TD reflection)

**When**: After EVERY micro-skill execution (automatic, silent).

G2 is the raw feedback signal. Appended to `skills/td-nl/feedback-log.md § Pending Feedback`.
Schema **v3** (preferred) walks through a short 5-phase TD reflection; schemas
v2/v1 remain accepted for brevity or legacy lines.

**Process (v3, 5 phases)**:

1. **P1 ANALYSIS** — Describe the firing state:
   - Key features of the input / situation
   - V^L coverage: does the global value function cover this scenario? flag gaps
   - Watch-outs: any prior failure mode this skill has exhibited in similar contexts?
2. **P2 VALUE PREDICTION** — Before the effect of this firing is known:
   - V (1-10): your self-estimate of the skill's Q^L in this context
   - confidence: high | medium | low
   - reason: 1-sentence why you chose this V
3. **P3 TD REFLECTION** — Only meaningful when there is a previous firing in the chain:
   - delta = reward_prev + γ·V(current) - V(previous)   (γ defaults 0.9)
   - interp: why the surprise is positive / negative
   - Omit this line on root firings (`upstream:-`).
4. **P4 STRATEGY** — Based on P3:
   - action ∈ {refine, keep, reset}
   - note: one concrete adjustment you will apply in THIS firing
5. **P5 RESULT** — After the firing has happened:
   - outcome: better | as_expected | worse
   - reward: +1 | 0 | -1
   - ev: 1-sentence post-hoc evidence (the textual gradient seed)

**Canonical v3 block**:
```
- [YYYY-MM-DD] session:{sid} node:{nid} upstream:{csv|-} skill:{name}
    P1_analysis: "..."
    P2_predict:  V=6, conf=med, reason="..."
    P3_td:       delta=-1.2, interp="..."          # omit on root firings
    P4_strategy: refine, note="..."
    P5_result:   outcome=worse, reward=-1, ev="..."
```

**Short-form v2 (still accepted when no TD reasoning needed)**:
```
- [YYYY-MM-DD] session:{sid} node:{nid} upstream:{csv|-} skill:{name} | outcome:{o} | delta:{d} | "{evidence}"
```

Legacy v1 (no session/node/upstream) is also accepted; the parser treats
such lines as isolated root firings in a synthetic `legacy` session.

**DAG conventions**:
- `session` is a short id that survives the session (e.g. `s1`, or a hash)
- `node` is a per-session unique id (e.g. `n1`, `n2`, ...)
- `upstream` lists node ids whose outputs this firing consumed; use `-` for
  root firings (e.g. `session-open`, `session-close`)

If `skill-values/{skill-name}.md` doesn't exist yet, create from `_template.md`.

**Token**: ~200-400 for v3 blocks; ~100-200 for v2 lines.

**Important**: G2 is cheap and frequent. Do NOT skip it. The quality of
evolution depends on honest, granular feedback. Even `as_expected` is valuable
signal. Prefer v3 when the firing is non-trivial (proof steps, paper reads,
design decisions); v2 is fine for routine firings (`memory-write`,
`progress-capture`).

---

## G1 — Session-Close Aggregation

Runs inside `evolve-suggest` at `session-close`, after `memory-write` and
`memory-consolidate`. Aggregates pending G2 entries into per-skill value
updates and (optionally) proposes spec edits.

See `skills/evolve-suggest/SKILL.md` for the full 6-phase process (Read →
Aggregate → TD(0) Scoring → Update V^L → TextGrad Backward + Propose → Cleanup).

### TD(0) layer on top of TextGrad

G1 no longer updates Q^L by the raw sum of G2 deltas. Instead:

1. V(s') estimate:
   - If v3 blocks supplied `P2_predict.V`, use the mean of those self-reports.
   - Else bootstrap: V(s') = clip(V(s) + 0.5 · r_clipped, 1, 10) where
     r_clipped = clip(net_delta · learning_rate, -2, 2).
2. TD error: `td = r + γ · V(s') - V(s)` with γ = 0.9 by default.
3. If v3 blocks also supplied `P3_td.delta` (inline per-firing TD), blend 50/50
   with the batch td so session-close and per-firing views stay consistent.
4. `new_score = clamp(old_score + learning_rate · td, 1, 10)`.

Strength thresholds gate downstream behavior:
- `hard`  (|td| ≥ 1.0): textual gradient kept, enters TGD.step, eligible for proposal
- `soft`  (|td| ≥ 0.25): value is updated, gradient kept but no proposal
                          unless the direction holds for 3 consecutive sessions
- `drop`  (|td| < 0.25): gradient is discarded; value update still applied

Learning rate by confidence:
- If v3 blocks supplied `P2_predict.conf`, take the majority vote.
- Else fall back to entry-count bins:
  - high (6+ entries): 1.0
  - medium (3-5 entries): 0.5
  - low (1-2 entries): 0.25

### TextGrad backward over the session DAG

For every session the backend reconstructs the DAG from `node`/`upstream`
fields, wraps each SKILL.md as a `requires_grad` Variable, wraps every firing
as an output Variable whose predecessors are `[spec_var] + upstream_firing_vars`,
then attaches a `TextLoss` at a synthetic head and runs one `loss.backward(...)`
call. Textual gradients therefore flow backward through the chain so an upstream
skill can be credited/blamed for a downstream failure. `TextualGradientDescent.step()`
is then called over the subset of specs with `strength == hard`.

If the `textgrad` package is not installed, a small shim implements just
enough of the `Variable` / `TextLoss` / `TextualGradientDescent` API to keep
the pipeline runnable; the shim emits deterministic placeholder gradients
instead of LLM-generated ones, so CI and smoke tests stay offline.

### Spec-edit trigger

A spec edit is proposed only when:
- At least one skill reached `strength == hard` in this session, OR
- Same `improvement_direction` for a skill across 3+ consecutive sessions.

Otherwise `evolve-suggest` logs "insufficient signal" and skips proposal.
When multiple skills qualify, only the one with the largest |td| gets a
proposal this session (enforcing one-edit-per-session).

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
