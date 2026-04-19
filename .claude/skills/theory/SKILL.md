# /theory — Mathematical Theory Development and Analysis

When to use this skill:
- User states an informal theorem, conjecture, or mathematical claim that needs formalization
- User has a complex proof goal and needs it broken into sub-problems
- User is stuck on a proof and needs techniques from other mathematical domains
- User wants to verify whether a claim is true or find counterexamples
- User wants to generalize or extend a proven result
- Keywords: "formalize", "prove this", "how do I prove", "is this true?", "can we generalize?", "stuck on proof"

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

## decompose

**Trigger**: User has a complex proof goal, asks "how do I prove this?", or a formalized theorem needs a proof roadmap.

### Process
1. Analyze the main claim and identify its logical structure
2. Break into sub-lemmas, each with:
   - Precise statement
   - Role in the overall proof (why this lemma is needed)
   - Difficulty classification:
     - **Routine**: standard technique, < 1 page
     - **Moderate**: requires some insight, 1-3 pages
     - **Hard**: requires novel ideas or deep technique
     - **Open**: no known proof, may be a research contribution
3. Draw dependency graph:
   - Which lemmas depend on which
   - Identify independent sub-problems (can be tackled in parallel)
   - Mark the critical path (longest chain of dependencies)
4. For each sub-lemma, suggest proof approaches and known related results
5. Save the proof roadmap with dependency structure

### Suggested Next
- For a hard sub-lemma where known techniques might help -> `theory.search`
- If user provides a proof attempt for a sub-lemma -> `proof.critique`

## search

**Trigger**: User is stuck on a proof step and needs techniques from other mathematical domains, or wants to find existing tools that apply.

### Process
1. Identify the mathematical structure of the problem:
   - What objects are involved (matrices, functions, graphs, measures, etc.)
   - What properties are needed (bounds, convergence, existence, uniqueness)
   - What makes the problem hard (non-convexity, infinite dimension, dependencies)
2. Search across mathematical domains for applicable techniques:
   - Spectral graph theory (eigenvalue methods, Cheeger inequality, expanders)
   - Functional analysis (operator theory, Banach space methods, fixed-point theorems)
   - Optimization (convex relaxation, duality, gradient methods, proximal operators)
   - Information geometry (Fisher information, natural gradient, divergence measures)
   - Statistical learning theory (VC dimension, Rademacher complexity, PAC-Bayes)
   - Topology and geometry (covering numbers, metric entropy, manifold structure)
   - Algebra (group actions, representation theory, polynomial methods)
3. For each candidate technique, assess applicability:
   - **Direct**: theorem applies as-is with minor verification of conditions
   - **Needs adaptation**: core idea applies but assumptions differ; specify what changes
   - **Inspirational**: proof strategy may transfer but substantial new work needed
4. Rank candidates by relevance and provide for each:
   - The specific theorem/technique name and reference
   - How it connects to the current problem
   - What assumptions need to be verified
   - Estimated effort to apply

### Suggested Next
- If a directly applicable theorem is found that needs formalization -> `theory.formalize`

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

## generalize

**Trigger**: User asks "can we generalize this?", "does this extend to...?", or wants to push a proven result further.

### Process
1. Identify the proven result precisely:
   - Statement, assumptions, proof technique used
   - Which assumptions are actually used in the proof (vs. stated but unused)
2. Propose generalization directions:
   - **Weaker assumptions**: which hypotheses can be relaxed? (e.g., convexity -> quasi-convexity, bounded -> sub-Gaussian)
   - **Higher dimensions**: does the result extend from R^n to Hilbert spaces, manifolds?
   - **Different norms / metrics**: L2 -> Lp, Frobenius -> operator norm
   - **Stochastic / approximate versions**: exact -> high-probability, deterministic -> in expectation
   - **Broader object classes**: matrices -> operators, graphs -> hypergraphs, distributions -> measures
3. For each proposed generalization, assess feasibility:
   - Does the existing proof technique still work? If not, where does it break?
   - Identify the specific step in the proof that uses the assumption being relaxed
   - Is there a known technique to handle the more general case?
   - Rate as: likely provable / plausible but hard / probably false / unknown
4. Prioritize generalizations by impact (how useful is the stronger result) and feasibility

### Suggested Next
- For a promising generalization that seems provable -> `theory.decompose`
