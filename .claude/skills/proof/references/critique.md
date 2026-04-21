# proof.critique

**Trigger**: User presents a proof draft, asks "is this proof correct?", or submits a proof attempt for review.

## Process

1. Read the proof carefully, tracking each logical step:
   - What is being assumed vs. what is being derived
   - Whether each implication actually follows
   - Whether quantifiers are handled correctly (order, scope)
2. Classify issues found into severity levels:
   - **Fatal**: logical gaps (step doesn't follow), circular reasoning, wrong direction of implication, incorrect theorem application
   - **Major**: missing edge cases (boundary, degenerate), unstated assumptions that are non-trivial, unjustified steps that might be true but aren't proven
   - **Minor**: stylistic issues, redundant steps, non-standard notation, sub-optimal organization
3. For each issue:
   - Quote the exact problematic step or passage
   - Explain why it is incorrect or insufficient
   - Suggest a specific fix or indicate if the gap is fillable
4. Give an overall verdict:
   - **Sound**: proof is correct, at most minor issues
   - **Fixable**: has major issues but the overall approach works; list what needs repair
   - **Fundamentally flawed**: approach cannot work; explain why and suggest alternatives

## Suggested Next

- If fatal or major issues found -> `proof.fix`
- If proof is sound and ready for polishing -> `proof.formalize`
