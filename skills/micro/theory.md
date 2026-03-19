# Theory Micro-Skills

> Triggered by mathematical/theoretical content in conversation.

## theory.formalize

**Trigger**: User states a theorem, conjecture, or mathematical claim informally

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
**Composition**: Naturally leads to `theory.decompose` for complex claims, or `proof.critique` if proof already exists

---

## theory.decompose

**Trigger**: User has a complex proof goal, asks "how do I prove this?", or faces a multi-step argument

**Process**:
1. Break the main claim into sub-lemmas / intermediate results
2. For each sub-lemma:
   - State precisely
   - Classify difficulty (routine / moderate / hard / open)
   - Suggest technique
3. Draw dependency graph (text-based)
4. Identify the critical path (hardest sub-lemma)
5. Save roadmap to `outputs/{topic}/roadmaps/` if substantial

**Inputs**: Theorem/goal statement + any partial progress
**Outputs**: Proof roadmap with dependency structure
**Token**: ~3-8K
**Composition**:
- Hard sub-lemma → suggest `theory.search` for cross-domain techniques
- If user provides attempt → chain to `proof.critique`

---

## theory.search

**Trigger**: User is stuck on a proof step, asks "is there a known result for...", or needs cross-domain techniques

**Process**:
1. Identify the mathematical structure of the problem
2. Search across domains:
   - Spectral graph theory, functional analysis, optimization
   - Information geometry, statistical learning theory
   - Topology, algebra (if relevant)
3. For each candidate result:
   - State the theorem with reference
   - Assess applicability (direct / needs adaptation / inspirational)
   - Sketch how to apply it
4. Rank by relevance and feasibility

**Inputs**: Problem description + what's been tried
**Outputs**: Cross-domain technique report (inline)
**Token**: ~3-8K
**Composition**: Found applicable theorem → suggest `theory.formalize` to adapt it

---

## theory.counterexample

**Trigger**: User wants to verify a claim, asks "is this true?", or proposes a conjecture

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
- Counterexample found → may trigger `theory.formalize` with corrected statement
- No counterexample → strengthens case for `proof.critique` or direct proof

---

## theory.generalize

**Trigger**: User asks "can we generalize?", "does this extend to...", or has proven a special case

**Process**:
1. Identify the proven result and its specific assumptions
2. Propose generalizations along multiple axes:
   - Weaker assumptions (e.g., convex → quasi-convex)
   - Higher dimensions / larger spaces
   - Different norms / metrics
   - Stochastic / approximate versions
3. For each generalization:
   - State the generalized claim
   - Assess feasibility (likely true / unclear / likely false)
   - Identify which proof steps break
4. Recommend most promising generalization direction

**Inputs**: Proven theorem + proof sketch
**Outputs**: Generalization analysis (inline)
**Token**: ~3-8K
**Composition**: Promising generalization → chain to `theory.decompose` for the generalized proof
