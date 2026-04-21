# writing.draft

**Trigger**: User wants to write a specific paper section, or outline is approved and ready to draft.

## Process

1. Read `paper/papers/outline.md` for structure and section plan.
2. Read source materials relevant to the target section:
   - Proofs and theorems from `proofs/`
   - Theory documents from `theory/`
   - Experiment results from `experiments/`
   - Related work notes and references
3. Draft the section:
   - Academic tone, precise language
   - All citations use `\cite{}` format with BibTeX keys
   - Full LaTeX formatting (equations, theorems, algorithms as needed)
   - Follow outline's page length targets
4. Save draft to `paper/papers/{section_name}.tex`.
5. Post-draft citation verification: run `scripts/citation_fetch.py` to check all `\cite{}` keys resolve and flag missing references.

## Suggested Next

- Draft complete -> `writing.review` for feedback before polishing.
