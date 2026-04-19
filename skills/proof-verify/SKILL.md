---
name: proof-verify
description: Verify a specific mathematical expression or derivation step symbolically, numerically, or dimensionally, and return CONFIRMED / REFUTED / INCONCLUSIVE. Triggers on "does this simplify to...", "check this formula", "verify this algebraic step", "is this identity correct?".
---

# proof-verify

**Trigger**: User asks to check a formula, verify an algebraic step, or "does this simplify to...".

**Process**:
1. Identify the mathematical expression(s) to verify
2. Approach verification:
   - Symbolic: attempt algebraic manipulation to confirm/deny
   - Numeric: test with concrete values (multiple random inputs)
   - Dimensional: check units/types consistency
3. Report:
   - CONFIRMED: step is correct (show verification)
   - REFUTED: step is wrong (show counterexample, suggest correction)
   - INCONCLUSIVE: can't determine (explain why, suggest alternative verification)
4. If Python/SymPy would help, suggest or run verification code

**Inputs**: Mathematical expression(s) or derivation step
**Outputs**: Verification report (inline)
**Token**: ~2-5K
**Composition**: If refuted → leads to `proof-fix`
