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
