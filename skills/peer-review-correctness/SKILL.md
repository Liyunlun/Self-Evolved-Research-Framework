---
name: peer-review-correctness
description: Stage 4 of the peer-review pipeline. Verifies mathematical and algorithmic correctness — equations, proofs, algorithms, and consistency between figure/table numbers and text claims. Uses a code interpreter to dim-check equations and re-derive key steps. Invoked by the `peer-review` orchestrator; standalone triggers include "check the math", "verify the proof", "are the equations dimensionally correct".
---

# peer-review-correctness

Fourth stage of the AAAI-26 AI peer-review pipeline. **Uses Bash as code interpreter.**

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- Previous stage outputs: `01_story.md`, `02_presentation.md`, `03_evaluations.md`
- `shared/base_instruction.md`, `shared/review_schema.md`

## Must-check list
1. **equation_dimensional_consistency** — Every equation, do LHS and RHS shapes/units match?
2. **proof_step_validity** — Each step justified? Any hand-wave presented as derivation?
3. **algorithm_matches_description** — Pseudocode in Alg N matches the prose description?
4. **figure_axis_labels_match_claims** — If text says "Fig 3 shows X decreases with Y", axes must be X and Y.
5. **table_numbers_consistent_across_text_and_table** — Number cited in prose must match the cell in the table.

## Process
1. Pull all numbered equations from the markdown. For each, parse LHS and RHS; note declared dimensions/shapes from surrounding prose.
2. Use Bash + Python sympy (if available) to symbolically verify 1–3 key equations. Log what you checked.
3. For each claim-verification pair ("as shown in Table 2, method X gets 87.3"), cross-reference the actual table cell.
4. Flag any proof step that lacks justification as `[major]`.

## Tools
- **Bash** — sympy or numpy for dimension/value checks.
- Read + Grep.

## Output
`outputs/peer-review/<paper_id>/04_correctness.md` — per schema. Include in `model_notes` how many equations/proofs you symbolically checked.

## Failure modes to avoid
- Do NOT re-prove correct results — only flag problems.
- Do NOT flag dimensionality when the paper uses conventional shorthand (scalar vs 1-vector).

## Tests
`tests/test_correctness.sh` — fixture contains an equation with mismatched dims: `y = W x + b` where `y ∈ R^3`, `W ∈ R^{2×4}`, `x ∈ R^4`. Output must contain `[critical]` flagging dimension mismatch.
