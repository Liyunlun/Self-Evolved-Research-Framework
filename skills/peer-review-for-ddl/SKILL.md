---
name: peer-review-for-ddl
description: Deadline-mode shortcut for the multi-reviewer peer-review pipeline. Pins venue level to best_paper, dispatches 3 reviewers, and overlays Kaiming He's academic writing style as a hard standard for logic, word choice, and presentation. Asks the user once for their research background, derives 3 calibrated reviewer personas from it, builds a strict best-paper × Kaiming-He × mandatory-taste-priors level bar, then hands off to the `peer-review` orchestrator. Triggers on "peer-review-for-ddl <paper>", "ddl review", "deadline-mode peer review", "submit tomorrow review this", "best-paper review with Kaiming He style", "投稿前严审", "提交前审稿".
---

# peer-review-for-ddl (deadline-mode shortcut)

A thin wrapper around the `peer-review` orchestrator preset for "I'm
submitting to a top venue tomorrow — be brutal." Pins venue level to
`best_paper`, dispatches 3 reviewers, requires recommendations, and overlays
Kaiming-He-style logic + word-choice rules on top of the best-paper bar.

## Hard-wired presets

| Field                | Value                                                   |
|----------------------|---------------------------------------------------------|
| `level`              | `best_paper`                                            |
| `reviewers`          | `3`                                                     |
| `rec`                | `yes`                                                   |
| `level_bar_override` | `outputs/peer-review/<paper_id>/level_bar.md` (built by Step 3 below) |
| Taste priors         | All applicable probes mandatory; headline-claim hits auto-`critical` |

These are non-negotiable for this shortcut. If the user wants a softer
setting, route them to plain `peer-review`.

## Inputs

- A paper, given as: arXiv URL / local PDF path / local markdown path.
- (Asked exactly once) The user's primary research background — used to
  calibrate the 3 reviewer personas.

## Step 0 — Resolve paper input + paper_id

Same as `peer-review` Step 1: derive `paper_id` as a lowercased alphanumeric
slug from the arXiv identifier or PDF filename. Create the run directory:

```
outputs/peer-review/<paper_id>/
```

If the directory already exists with a complete `run_config.yaml` from a
prior shortcut invocation, ask the user `Reuse existing run? [y/N]`. On `n`,
append a timestamp suffix to `paper_id` so the prior run is not overwritten.

## Step 1 — Ask for the user's research background (single question)

Use `AskUserQuestion` with one open-text field:

> What is your primary research area? Used to derive 3 calibrated reviewer
> personas. Examples: "continual reinforcement learning, JAX", "efficient
> LLM inference", "algebraic topology in topological data analysis".

Save the response as `user_background` (one short string). Do NOT ask any
follow-up clarifiers in this step — Step 2 surfaces the derived personas
for review and edit.

## Step 2 — Derive 3 reviewer personas from `user_background`

Construct the three personas mechanically:

1. **R1 — In-domain expert.**
   `"Senior researcher in <user_background>; applies the field's standard
    methodological bar and is unforgiving about claims that overlap known
    work in the area."`

2. **R2 — Adjacent expert.**
   Pick one immediately neighboring subfield (e.g. continual RL → meta-RL
   or representation learning; LLM inference → systems / compilers). Format:
   `"Researcher in <neighbor>; tests whether the claims generalize beyond
    <user_background> and whether the framing imports concepts from
    <neighbor> faithfully."`

3. **R3 — Cross-disciplinary skeptic.**
   `"Researcher in a methodologically different field with strong empirical
    taste; probes whether the paper's evidence would convince a
    non-specialist and whether the method's stated novelty survives
    translation to plain language."`

Show all three to the user via `AskUserQuestion` with options:

- `Use as-is` (default)
- `Edit personas` (accept replacement free-text for any of the three)
- `Re-derive` (ask one clarifier on `user_background` then retry Step 2)

## Step 3 — Build `level_bar.md` (best_paper + Kaiming-He overlay + taste-prior pin)

Construct `outputs/peer-review/<paper_id>/level_bar.md` by concatenating, in
this order:

1. The default `best_paper.bar` block from `peer-review/shared/review_level.yaml`.
2. A heading `## Writing-style standard (Kaiming He)` followed by the full
   contents of `peer-review/shared/style_kaiming_he.md`.
3. A heading `## Taste-prior pinning` followed by this literal paragraph:

   > Taste-prior probes are mandatory for this run. All applicable probes
   > from `shared/taste-priors.md` (mechanism_attribution,
   > hidden_assumption_audit, benchmark_claim_match, efficiency_vs_claim,
   > terminology_audit, decorative_theorem) MUST be evaluated by the stage
   > that owns them. A probe that fires on a headline claim is
   > automatically `critical` for this run. `vote_moving_weakness` is
   > applied during self-critique as usual.

Do NOT show this concatenated bar to the user for further editing — the
shortcut's contract is that the bar is fixed. (If the user wants to edit
the bar, they should use plain `peer-review`.)

## Step 4 — Write `run_config.yaml`

Write `outputs/peer-review/<paper_id>/run_config.yaml` exactly:

```yaml
level: best_paper
reviewers: 3
recommendation: yes
reviewer_backgrounds:
  - "<R1 persona text from Step 2>"
  - "<R2 persona text from Step 2>"
  - "<R3 persona text from Step 2>"
user_background: "<verbatim response from Step 1>"
shortcut: peer-review-for-ddl
```

Also write `outputs/peer-review/<paper_id>/shortcut.yaml` with the same
`shortcut: peer-review-for-ddl` tag (used by downstream tooling and by
test_skills_static to identify shortcut-produced runs):

```yaml
shortcut: peer-review-for-ddl
created_by: peer-review-for-ddl
preset:
  level: best_paper
  reviewers: 3
  rec: yes
  style: kaiming_he
  taste_priors: mandatory
```

## Step 5 — Hand off to the `peer-review` orchestrator

Invoke `Skill(peer-review)` with all overrides supplied inline so the
orchestrator's interactive Step 0 is fully bypassed (see "Orchestrator
contract" below):

```
peer-review <paper_input> level=best_paper reviewers=3 rec=yes \
  level_bar_override=outputs/peer-review/<paper_id>/level_bar.md \
  paper_id=<paper_id>
```

The orchestrator should detect the existing `run_config.yaml` and
`level_bar.md` at the target path and skip Step 0 prompts, then proceed to
multi-reviewer dispatch (Step 2 of `peer-review`). Output: 3 ×
`reviewer_<i>/06_final.md` + 3 × `reviewer_<i>/07_qa.md` + `sac_summary.md`.

## Orchestrator contract

This shortcut depends on `peer-review/SKILL.md` Step 0 honoring this rule:

> If `run_config.yaml` and `level_bar.md` both already exist at
> `outputs/peer-review/<paper_id>/`, AND `run_config.yaml` contains every
> required field (`level`, `reviewers`, `recommendation`, plus
> `reviewer_backgrounds` of length `reviewers` when `reviewers > 1`), THEN
> skip Step 0 prompts entirely and use the existing files verbatim.

If a future change to the orchestrator removes that rule, the shortcut
still works, but the user will be re-prompted for level / reviewers / rec
— they should answer with the values written above.

## Output layout

Same as `peer-review` multi-reviewer mode (3 reviewers + sac_summary), plus
two extra identifying artifacts:

```
outputs/peer-review/<paper_id>/
  run_config.yaml         # written by this skill (Step 4)
  level_bar.md            # written by this skill (Step 3)
  shortcut.yaml           # tag identifying this shortcut (Step 4)
  00_preprocess/...
  reviewer_1/01_story.md ... reviewer_1/06_final.md  reviewer_1/07_qa.md
  reviewer_2/...
  reviewer_3/...
  sac_summary.md
```

## When NOT to use this skill

- Submitting to a workshop or as a poster (use `peer-review` with
  `level=poster`).
- Wanting an encouraging or balanced review (this shortcut is designed to
  be punitive on logic and word choice — use plain `peer-review` for tone
  control).
- Mid-draft ideation feedback before any results are in (use
  `writing-review` instead — that's a writing pass, not a venue review).

## Related skills

- `peer-review` — the orchestrator this shortcut delegates to.
- `peer-review-{story, presentation, evaluations, correctness, significance,
  critique, qa, sac}` — invoked transitively via the orchestrator.
- `writing-review` — softer "is this draft submission-ready" pass.

## Tests

Inherits the test suite of `peer-review` (`tests/run_all_tests.sh` at that
skill's root). No new fixtures are required: the shortcut produces the
same artifact shapes as plain multi-reviewer mode plus two identifying
files (`shortcut.yaml` and a fixed-content `level_bar.md`). The static
lint at `peer-review/tests/test_skills_static.py` should pick up this
SKILL.md as a sibling skill via standard discovery.
