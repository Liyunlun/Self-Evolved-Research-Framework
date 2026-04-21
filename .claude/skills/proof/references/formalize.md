# proof.formalize

**Trigger**: User wants a validated proof made publication-ready, or asks "make this publication-ready", "format for paper".

## Process

1. Take the validated proof (should have passed `proof.critique` or be known correct)
2. Generate complete LaTeX:
   - Proper `\begin{theorem}` / `\begin{proof}` environments
   - Consistent notation throughout (match the paper's notation conventions if known)
   - Every step fully justified with references to lemmas, definitions, or prior results
   - Appropriate use of `\label{}` and `\ref{}` for cross-referencing
   - Citations formatted with `\cite{}`
3. Ensure mathematical typography standards:
   - Displayed equations for important results (`equation` or `align` environments)
   - Inline math for short expressions
   - Proper use of `\qed` or `\qedhere`
   - Consistent font choices (blackboard bold for number sets, bold for vectors, etc.)
4. Save to `outputs/{topic}/proofs/{theorem_name}.tex`
   - Include a brief header comment noting the theorem name and date

## Suggested Next

- After formalizing -> `writing.draft` to incorporate the proof into a paper section
