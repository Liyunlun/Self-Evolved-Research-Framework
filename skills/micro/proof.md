# Proof Micro-Skills

> Triggered by proof text or proof-related requests.

## proof.critique

**Trigger**: User presents a proof draft, asks "is this proof correct?", or shares proof text

**Process**:
1. Read the proof carefully, tracking each logical step
2. Check for:
   - **Fatal**: Logical gaps, circular reasoning, unjustified claims, wrong direction of implication
   - **Major**: Missing edge cases, unstated assumptions, unclear notation
   - **Minor**: Style issues, redundant steps, non-standard notation
3. For each issue:
   - Quote the exact problematic step
   - Explain why it's wrong/unclear
   - Suggest a fix or alternative approach
4. Give overall verdict: Sound / Fixable / Fundamentally flawed
5. If sound, note strengths (elegant steps, good use of technique)

**Inputs**: Proof text (any format: natural language, LaTeX, mixed)
**Outputs**: Structured critique report (inline)
**Token**: ~3-10K
**Composition**:
- Fatal/major issues found → suggest `proof.fix`
- All clear → suggest `proof.formalize` for LaTeX version

---

## proof.fix

**Trigger**: User asks to fix proof issues identified by `proof.critique`, or asks "how do I fix this step?"

**Process**:
1. Focus on the specific issue(s) to fix
2. For each issue:
   - Rewrite the problematic step(s) with correct reasoning
   - Explain the fix and why the original was wrong
   - Verify the fix doesn't break downstream steps
3. Present the corrected proof segment in context
4. Re-check the overall proof flow with the fix applied

**Inputs**: Original proof + identified issues (from proof.critique or user)
**Outputs**: Corrected proof segment(s) with explanations
**Token**: ~3-8K
**Composition**: After fixing → may re-trigger `proof.critique` to verify, or proceed to `proof.formalize`

---

## proof.formalize

**Trigger**: User asks for LaTeX version, formal write-up, or "make this publication-ready"

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
**Composition**: Formalized proof → natural input for `writing.draft` (paper section)

---

## proof.verify

**Trigger**: User asks to check a formula, verify an algebraic step, or "does this simplify to..."

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
**Composition**: If refuted → leads to `proof.fix`
