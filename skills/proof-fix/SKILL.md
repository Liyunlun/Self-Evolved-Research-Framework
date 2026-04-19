---
name: proof-fix
description: Rewrite specific problematic proof steps identified by proof-critique (or the user) with correct reasoning, then re-check that the fix doesn't break downstream steps. Triggers when the user asks to fix a proof issue, "how do I fix this step?", or after a proof critique identifies errors.
---

# proof-fix

**Trigger**: User asks to fix proof issues identified by `proof-critique`, or asks "how do I fix this step?".

**Process**:
1. Focus on the specific issue(s) to fix
2. For each issue:
   - Rewrite the problematic step(s) with correct reasoning
   - Explain the fix and why the original was wrong
   - Verify the fix doesn't break downstream steps
3. Present the corrected proof segment in context
4. Re-check the overall proof flow with the fix applied

**Inputs**: Original proof + identified issues (from proof-critique or user)
**Outputs**: Corrected proof segment(s) with explanations
**Token**: ~3-8K
**Composition**: After fixing → may re-trigger `proof-critique` to verify, or proceed to `proof-formalize`
