# /proof — Proof Critique, Writing, Fixing, and Verification

When to use this skill:
- User presents a proof and wants it checked for correctness
- User needs to write a proof for a theorem or lemma from scratch
- User has a proof with identified issues that need fixing
- User wants a proof formatted for publication in LaTeX
- User wants to verify a specific formula, algebraic step, or simplification
- Keywords: "is this proof correct?", "写证明", "prove this", "证明这个定理", "fix the proof", "make this publication-ready", "does this simplify to"

## critique

**Trigger**: User presents a proof draft, asks "is this proof correct?", or submits a proof attempt for review.

### Process
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

### Suggested Next
- If fatal or major issues found -> `proof.fix`
- If proof is sound and ready for polishing -> `proof.formalize`

## write

**Trigger**: User asks to write a proof from scratch. Common phrases: "写证明", "prove this", "证明这个定理", "write a proof of".

### Process
1. Analyze the proposition:
   - Extract the precise statement to be proved
   - Identify the type: universal, existential, equivalence, bound, construction
   - List all premises and what tools/results are available
2. Select proof strategy:
   - **Direct**: assume premises, derive conclusion through a chain of implications
   - **Contradiction**: assume negation of conclusion, derive a contradiction
   - **Induction**: identify base case, inductive step, and what the induction variable is
   - **Construction**: explicitly build the object claimed to exist
   - **Contrapositive**: prove the equivalent contrapositive statement
   - Choose based on the structure of the claim; state why the chosen strategy fits
3. Build the proof step-by-step:
   - Each step must have an explicit justification (by assumption, by Lemma X, by definition of Y)
   - Introduce variables before using them
   - Handle all quantifier scoping correctly
   - Address edge cases (n=0, empty set, degenerate configurations)
   - No circular reasoning (never use the conclusion in a step)
4. Verify logical completeness:
   - Read through the completed proof to check flow
   - Confirm all variables are introduced before use
   - Confirm no circular reasoning
   - Confirm edge cases are addressed
   - Check that the final line actually establishes the desired conclusion
5. Output in LaTeX format with proper theorem/proof environments
6. Save to `paper/proofs/` or `outputs/{topic}/proofs/`

### Suggested Next
- After writing -> `proof.critique` to verify the proof is correct

## fix

**Trigger**: A proof has identified issues (from `proof.critique` or user's own analysis) that need to be repaired.

### Process
1. Focus on the specific issues identified:
   - Read the critique or issue description
   - Locate the exact steps in the proof that are problematic
2. For each issue, rewrite the problematic step(s):
   - Provide correct reasoning with full justification
   - If the original approach at that step cannot work, propose an alternative
   - Explain what was wrong and why the fix is correct
3. Verify the fix doesn't break downstream steps:
   - Check that later steps that depended on the problematic step still follow
   - If the fix changes the structure, trace implications through the rest of the proof
4. Present the corrected segment in context:
   - Show the surrounding steps so the fix is clearly situated
   - Mark what changed
5. Re-check overall flow of the proof after all fixes are applied

### Suggested Next
- After fixing -> `proof.critique` to verify the repaired proof
- If proof is now sound and needs formatting -> `proof.formalize`

## formalize

**Trigger**: User wants a validated proof made publication-ready, or asks "make this publication-ready", "format for paper".

### Process
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

### Suggested Next
- After formalizing -> `writing.draft` to incorporate the proof into a paper section

## verify

**Trigger**: User wants to check a specific formula, verify an algebraic manipulation, or asks "does this simplify to...?", "is this identity correct?".

### Process
1. Identify the expressions to be verified:
   - The starting expression
   - The claimed result or simplification
   - Any intermediate steps provided
2. Verify through multiple approaches:
   - **Symbolic**: carry out the algebra step-by-step, showing each manipulation
   - **Numerical**: substitute specific values (at least 3 distinct test points) and check both sides agree
   - **Dimensional / structural**: verify that types, dimensions, and units are consistent on both sides
3. Report result:
   - **CONFIRMED**: all checks pass, step-by-step derivation provided
   - **REFUTED**: found a discrepancy; show the exact step where it fails and the correct result
   - **INCONCLUSIVE**: symbolic verification is intractable; report numerical evidence and confidence
4. If the expression is complex, suggest using SymPy for independent computer algebra verification and provide the code snippet

### Suggested Next
- If a step is refuted -> `proof.fix` to correct the proof that used this step
