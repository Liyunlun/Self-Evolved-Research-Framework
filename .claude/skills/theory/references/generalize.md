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
