# proof.fix

**Trigger**: A proof has identified issues (from `proof.critique` or user's own analysis) that need to be repaired.

## Process

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

## Suggested Next

- After fixing -> `proof.critique` to verify the repaired proof
- If proof is now sound and needs formatting -> `proof.formalize`
