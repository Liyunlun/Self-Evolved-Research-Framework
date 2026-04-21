# proof.verify

**Trigger**: User wants to check a specific formula, verify an algebraic manipulation, or asks "does this simplify to...?", "is this identity correct?".

## Process

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

## Suggested Next

- If a step is refuted -> `proof.fix` to correct the proof that used this step
