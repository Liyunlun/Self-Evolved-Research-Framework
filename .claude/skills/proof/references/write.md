# proof.write

**Trigger**: User asks to write a proof from scratch. Common phrases: "prove this", "write a proof of".

## Process

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

## Suggested Next

- After writing -> `proof.critique` to verify the proof is correct
