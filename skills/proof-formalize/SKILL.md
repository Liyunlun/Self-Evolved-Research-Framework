---
name: proof-formalize
description: Convert a validated proof into a polished LaTeX writeup with proper theorem/lemma/proof environments, consistent notation, and full justification, saved to outputs/{topic}/proofs/. Triggers on "make this LaTeX", "publication-ready proof", "write this up formally".
---

# proof-formalize

**Trigger**: User asks for LaTeX version, formal write-up, or "make this publication-ready".

**Process**:
1. Take the validated proof (post-critique/fix)
2. Generate complete LaTeX proof:
   - Proper theorem/lemma/proof environments
   - Consistent notation (aligned with paper conventions)
   - All steps explicitly justified
   - References to standard results cited properly
3. Save to `outputs/{topic}/proofs/{theorem_name}.tex`
4. Output both the LaTeX source and a readable preview

**Inputs**: Validated proof + notation conventions
**Outputs**: `outputs/{topic}/proofs/{theorem_name}.tex`
**Token**: ~3-10K
**Composition**: Formalized proof → natural input for `writing-draft` (paper section)
