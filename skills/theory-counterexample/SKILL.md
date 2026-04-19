---
name: theory-counterexample
description: Try to disprove a mathematical claim by constructing degenerate, boundary, or pathological counterexamples, and report whether the claim survives. Triggers on "is this true?", "verify this claim", or when the user proposes a conjecture before attempting to prove it.
---

# theory-counterexample

**Trigger**: User wants to verify a claim, asks "is this true?", or proposes a conjecture.

**Process**:
1. Identify the claim and its assumptions
2. Attempt to construct counterexamples:
   - Degenerate cases (n=1, empty set, identity)
   - Boundary cases (extremes of parameter ranges)
   - Known pathological examples in the domain
3. If counterexample found:
   - Present minimal counterexample
   - Identify which assumption it violates
   - Suggest strengthened assumptions
4. If no counterexample found:
   - State confidence level
   - Note which cases were checked
   - Suggest this supports (but doesn't prove) the claim

**Inputs**: Mathematical claim + assumptions
**Outputs**: Counterexample report (inline, saved to `outputs/{topic}/counterexamples/` if significant)
**Token**: ~2-5K
**Composition**:
- Counterexample found → may trigger `theory-formalize` with corrected statement
- No counterexample → strengthens case for `proof-critique` or direct proof
