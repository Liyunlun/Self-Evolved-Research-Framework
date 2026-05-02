# Style Standard — Kaiming He Academic Writing

Loaded by `peer-review-for-ddl` (and any other caller that explicitly opts in)
by appending to the run's `level_bar.md` at dispatch time. Every stage that
reads the level bar will see these rules and must apply them when scoring
clarity, presentation, and logic-flow findings.

The rules below are calibrated against the writing in ResNet (CVPR'16),
Mask R-CNN (ICCV'17), MoCo (CVPR'20), and MAE (CVPR'22): direct,
simple-sentence-first prose where every claim is paired with the table or
figure that proves it.

## Hard rules (R1–R8) — flag as `major`; escalate to `critical` at best_paper

### R1 — One core idea, named once, stated early
- The contribution is summarized in 1-3 sentences in the introduction.
- The method has a short, consistent short-name; the paper does not switch
  between synonyms across sections.
- Trigger: contribution scattered across multiple paragraphs, or the same
  method referred to by two or more different names.

### R2 — Topic-sentence-first paragraphs
- Each paragraph opens with a single declarative sentence stating its
  claim; the rest of the paragraph supplies evidence.
- Trigger: a paragraph whose first sentence is transition / setup / hedge,
  with the actual claim buried in the middle or end.

### R3 — Every quantitative claim points to a table or figure
- "X improves over Y by Z%" must cite Table N or Figure N inline.
- Trigger: numerical comparison appearing in prose with no inline pointer
  to the artifact that proves it.

### R4 — No hedging adjectives without earned evidence
- Forbidden unless the immediately following sentence supplies a numeric
  comparison or named reference: `novel`, `powerful`, `elegant`,
  `state-of-the-art`, `we believe`, `may be`, `arguably`.
- Trigger: any of those tokens followed only by more prose.

### R5 — One idea per sentence
- Compound sentences combining setup + claim + caveat are split.
- Trigger: a sentence with three or more commas chaining independent
  assertions.

### R6 — Comparisons are explicit
- "Ours vs. baseline" with the baseline named, the metric named, and the
  delta given numerically.
- Trigger: `outperforms prior work` / `competitive results` / `comparable
  to <category>` with no named baseline + metric + delta.

### R7 — Limitations are concrete and present
- A limitations / failure-modes section exists. It names at least one
  setting where the method underperforms or is invalid. It is not
  rhetorical (e.g. "a limitation is that future work could ...").
- Trigger: missing limitations section, or limitations that read as
  marketing for follow-up work.

### R8 — Order is consistent
- The method section follows the same order as the introduction's
  contribution list. The experiments section evaluates the contribution
  list in the same order.
- Trigger: contribution C2 in the intro is evaluated before C1 in the
  experiments, with no signposting that says so.

## Soft rules (R9–R11) — flag as `minor`

### R9 — Equation density is justified
- Each equation either (a) defines a quantity used later, or (b) is the
  subject of an explicit derivation step. Equations that restate prose in
  symbol form without adding precision are noise.

### R10 — Notation consistency
- Same symbol means the same thing across the whole paper. Subscripts,
  hats, and bars are introduced once and reused.

### R11 — Figure captions stand alone
- A reader who only reads captions can recover the paper's takeaways from
  figures. Captions name the metric, the comparison, and the conclusion.

## Severity escalation

`peer-review-for-ddl` pins venue level to `best_paper`, so R1–R8 violations
escalate one tier (`minor` → `major`, `major` → `critical`). Always-on for
that shortcut. Other callers that opt in must state explicitly whether the
escalation applies.

## Probe interaction

These rules are orthogonal to the seven taste-prior probes in
`shared/taste-priors.md`. A finding may cite both — for example, R6 plus
`benchmark_claim_match`. When both apply:

- Attach both tags in the `probe:` field of the finding.
- Pick the higher severity of the two for the finding's overall severity.
- Do NOT emit two separate findings for the same underlying issue.

## What this addendum does NOT do

- It does not replace `shared/base_instruction.md`'s severity scale.
- It does not change the schema in `shared/review_schema.md`.
- It does not turn off any existing must-check list at any stage.

It is purely additive: it tells stages what *additional* presentation /
logic-flow violations to flag, and how to grade them at best_paper.
