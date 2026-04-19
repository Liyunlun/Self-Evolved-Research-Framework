---
name: theory-formalize
description: Turn an informal theorem, conjecture, or mathematical claim into a precise formal statement in LaTeX, with assumptions, notation, and candidate proof strategies. Triggers when the user states a math claim informally ("I conjecture that...", "I think this is true...", "can you make this rigorous?").
---

# theory-formalize

**Trigger**: User states a theorem, conjecture, or mathematical claim informally.

**Process**:
1. Parse the informal statement
2. Identify: assumptions, variables, domains, claim type (existence/uniqueness/bound/equivalence)
3. Output formal mathematical statement in LaTeX
4. List required definitions and notation
5. Identify proof strategy candidates (direct, contradiction, induction, construction)
6. Save to `outputs/{topic}/theory/` if user confirms

**Inputs**: Informal mathematical statement
**Outputs**: Formalized theorem statement + proof strategy suggestions
**Token**: ~3-8K
**Composition**: Naturally leads to `theory-decompose` for complex claims, or `proof-critique` if proof already exists
