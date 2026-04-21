## formalize

**Trigger**: User states a theorem, conjecture, or mathematical claim informally and it needs rigorous formulation.

### Process
1. Parse the informal statement to identify:
   - All variables and their domains (e.g., "for all x in R^n")
   - Assumptions and preconditions (what must hold for the claim to apply)
   - The precise claim being made (existential, universal, equivalence, bound)
   - Claim type: theorem / lemma / proposition / conjecture / definition
2. Output formal statement in LaTeX:
   - Use standard theorem environment formatting
   - Explicitly state all quantifiers
   - Define all notation not previously established
3. List all definitions required (reference or provide each one)
4. Identify candidate proof strategies:
   - Direct proof, contradiction, contrapositive
   - Induction (standard, strong, structural, transfinite)
   - Construction, probabilistic method, compactness argument
   - Rate the apparent difficulty and note which strategies seem most promising
5. Save formalized statement to `methodology/{topic}.md` with:
   - Statement, assumptions, proof strategy candidates
   - Cross-references to related results in the workspace

### Suggested Next
- If the claim is complex with multiple components -> `theory.decompose`
- If a proof already exists and needs checking -> `proof.critique`
