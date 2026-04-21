## counterexample

**Trigger**: User asks "is this true?", wants to verify a claim before investing in a proof, or suspects a statement might be false.

### Process
1. Identify the precise claim and all its assumptions
2. Systematically construct candidate counterexamples:
   - **Degenerate cases**: zero vectors, identity matrices, trivial graphs, constant functions
   - **Boundary cases**: dimension 1, n=2, extreme parameter values
   - **Pathological cases**: non-smooth functions, disconnected graphs, degenerate distributions
   - **Random instances**: small random examples to build intuition
3. For each candidate, check whether it satisfies all assumptions and violates the conclusion
4. If counterexample found:
   - Present the minimal counterexample (simplest case that breaks the claim)
   - Identify exactly which assumption is too weak
   - Propose strengthened assumptions that would exclude the counterexample
   - Check if the strengthened claim is now plausible
5. If no counterexample found:
   - State confidence level (low/medium/high) based on breadth of search
   - List the categories of cases checked
   - Note which cases came closest to failing (these inform proof difficulties)

### Suggested Next
- If counterexample found -> `theory.formalize` with corrected/strengthened statement
- If no counterexample and claim seems true -> `proof.critique` on any existing proof attempt
