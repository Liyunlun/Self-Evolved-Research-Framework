# writing.outline

**Trigger**: User wants to plan paper structure, start a new paper, or reorganize an existing draft.

## Process

1. Read existing outputs -- check `paper/papers/`, `experiments/`, `proofs/`, `SUMMARY.md` for available material.
2. Propose outline with:
   - Sections with target page lengths
   - Key content per section (main arguments, theorems, results to include)
   - Figure and table plan (what goes where, data source for each)
   - Gaps -- missing experiments, proofs, or analysis needed before writing
3. Generate a Claims-Evidence Matrix: rows = paper claims, columns = evidence type (theorem, experiment, ablation, baseline comparison), cells = status (done/partial/missing).
4. Save outline to `paper/papers/outline.md`.

## Suggested Next

- Outline approved -> `writing.draft` to begin section-by-section writing.
