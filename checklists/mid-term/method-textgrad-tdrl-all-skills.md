# Method: TextGrad backend working with TDRL framework for all skills

Parent: checklists/mid-term.md § Methods | Created: 2026-04-20
Status: [5/13]

## Goal

Make the TextGrad backend the default engine behind the TD-NL skill-evolution
layer, so that every one of the 42 SER skills (plus external) accumulates
Q^L estimates and receives spec-edit proposals driven by a single TextGrad
trace + TD(0) scoring pipeline.

## Checklist

### Foundations (already in place from 2026-04-20 commit ae4b157)

- [x] Formal problem statement — textgrad trace + TD(0) over G2 v3 entries, DAG-backward credit, max|td| hard-gate → single-proposal-per-session  <!-- design in skills/_shared/evolve-cycle.md -->
- [x] Algorithm design / pseudocode — v3 5-phase G2 (analysis / predict / td / strategy / result), DAG backward, strength gates (hard ≥1.0 / soft ≥0.25 / drop <0.25)  <!-- locked in session 2026-04-20 -->
- [x] Implementation (core package) — `skills/td-nl/textgrad_backend/` (variables, trace, td_layer, backward, propose) + CLI `scripts/evolve_textgrad.py`

### Backend hardening

- [x] Real-data validation — ran `scripts/evolve_textgrad.py --dry-run` on live log; snapshot + golden-file regression test added | artifact: `skills/td-nl/textgrad_backend/fixtures/live_feedback_log_2026-04-20.{input.md,json}` + `test_live_fixture_regression` in `test_smoke.py`  <!-- 2026-04-20: s8 → V^L 5.0→6.567, 3 hard candidates, max|td|=general-research (+2.3) -->
- [x] Claude Code CLI as LLM engine — adapter + factory + shim TGD integration; `ClaudeCodeCLIEngine` shells out to `claude -p --model <m> --disable-slash-commands --output-format text` (OAuth auth, no separate key) | artifact: `skills/td-nl/textgrad_backend/engines/{__init__.py,claude_code.py}`, CLI flags `--no-engine` / `--engine-model` / `--engine-timeout` on `scripts/evolve_textgrad.py`, `test_engine_wiring` in `test_smoke.py` (fake-engine + failure-fallback)  <!-- 2026-04-20 -->
- [ ] Unit tests — extend `skills/td-nl/textgrad_backend/test_smoke.py` beyond 4 smoke cases: cover v1/v2/v3 mixed logs, empty log, shim vs real-textgrad parity  <!-- partial 2026-04-20: live-fixture regression + engine wiring added; still need mixed/empty/parity cases -->
- [ ] Fixture refresh policy — document when to regenerate fixtures vs investigate regressions (currently only in `fixtures/README.md`)
- [ ] Engine auth isolation — document that engine runs from `/tmp` with `--disable-slash-commands` (no SER recursion); decide on `--bare` vs OAuth tradeoff for unattended session-close runs
- [ ] Offline shim parity check — assert shim path produces a proposal of the same skill_target as real textgrad when API key is absent

### Per-skill rollout

- [ ] Seed `skills/td-nl/skill-values/` files for all 42 SER skills using `_template.md` on first firing (currently created lazily, one at a time)
- [ ] Verify `propose.py` picks a skill from the full 42-skill set (not only those with prior history) when td strength is tied
- [ ] Cover external skills — confirm `external/fey-r` and any future submodule skills are included in the Q^L registry

### Integration with evolve-suggest

- [ ] `evolve-suggest/SKILL.md`: make TextGrad backend the default path (current doc describes both bin-based and TextGrad — collapse to TextGrad-first with legacy-bin fallback)
- [ ] `evolve-apply/SKILL.md`: accept `--apply-proposal` output format from `evolve_textgrad.py` end-to-end (archive → edit → log)
- [ ] End-to-end dry run: collect ≥3 sessions of G2 entries, run `evolve_textgrad.py --apply-proposal` once, verify version archive + rollback work

### Documentation & close-out

- [ ] Update `skills/td-nl/README` (or create one) with TextGrad-first flow + commands
- [ ] Add walkthrough section to `skills/_shared/evolve-cycle.md` referencing the 2026-04-20 walkthrough PDF and the new default

## Design Decisions

| Decision | Options | Chosen | Rationale | Date |
|----------|---------|--------|-----------|------|
| Backend architecture | A: keep bin-based only / B: only P1 analysis upgrade / C: trace-ification (DAG credit) | C | Enables proper credit assignment across phases and aligns with TextGrad idioms | 2026-04-20 |
| V(s') source | bootstrap / P2 mean / P3.delta | P2 mean (fallback bootstrap) | v3 blocks already carry P2 value; keeps inline + batch views consistent | 2026-04-20 |
| Inline vs batch TD | inline-only / batch-only / 50-50 blend | 50-50 blend | Preserves per-firing signal without losing session-close aggregate | 2026-04-20 |
| One-edit-per-session | always one / always multi / hard-gate one | hard-gate one (max\|td\|) | Keeps spec-evolution conservative and auditable | 2026-04-20 |
| Offline story | require API / shim fallback | shim fallback | CI and airgapped sessions must still run the pipeline | 2026-04-20 |
| LLM engine for shim TGD | none / OpenAI / Anthropic SDK / Claude Code CLI | Claude Code CLI | Reuses user's existing Claude Code OAuth auth, no separate key, keeps the "one tool" UX | 2026-04-20 |
| Default engine model | opus / sonnet / haiku | haiku | Gradient generation is short-form text; haiku is 10× cheaper/faster with negligible quality loss for evolve notes | 2026-04-20 |
| Engine isolation | inherit cwd / run from /tmp / --bare | run from /tmp + --disable-slash-commands | Avoid loading SER CLAUDE.md recursively; keep OAuth auth working (--bare requires API key) | 2026-04-20 |

## Notes

Tracked in this L2 because the work spans multiple weeks and touches
`skills/td-nl/`, `skills/evolve-*/`, `scripts/`, and every
`skills/*/SKILL.md` entry point. First milestone is
"backend hardening + real-data validation complete" — everything after
that is rollout-shaped.
