---
name: proof-critique
description: Carefully review a proof draft for logical gaps, unjustified claims, unstated assumptions, and notational issues, classifying each into Fatal / Major / Minor and returning Sound / Fixable / Fundamentally flawed. Triggers when the user shares a proof and asks "is this correct?", "what's wrong with this proof", or similar.
---

# proof-critique

**Trigger**: User presents a proof draft, asks "is this proof correct?", or shares proof text.

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
- Fatal/major issues found → suggest `proof-fix`
- All clear → suggest `proof-formalize` for LaTeX version
