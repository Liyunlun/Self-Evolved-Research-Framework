# idea.verify

**Trigger**: After `idea.discover`, or when user says "is this idea novel?", "has this been done?", or proposes a specific research idea.

## Process
1. **Extract verification targets**: For each idea to verify, extract:
   - Key claims / core contribution
   - Technical approach keywords
   - Expected related work search terms
2. **Automated search** (multi-source):
   a. **DBLP search**: Query `https://dblp.org/search/publ/api?q={keywords}&format=json`
      - Look for papers with similar titles or approaches
   b. **arXiv search** (via export API): Query `http://export.arxiv.org/api/query?search_query={keywords}&max_results=10`
      - Check recent papers (last 2 years) in relevant categories
   c. **Cross-model verification** (via Claude Code Agent subagent):
      - Launch an Agent (subagent_type="general-purpose") with a prompt that includes:
        - The idea description to verify
        - Instructions:
          ```
          You are a research novelty checker. Given an idea description, identify:
          1. The closest existing work (with paper titles and years)
          2. What differentiates this idea from existing work (if anything)
          3. Novelty assessment: {highly novel | somewhat novel | incremental | already exists}
          Be specific — cite actual papers, not vague references.
          ```
3. **Synthesize verification report** for each idea:
   ```
   ### Idea: {title}
   **Novelty verdict**: {highly novel | somewhat novel | incremental | already exists}

   **Closest existing work**:
   - {paper1} ({year}) — {similarity description}
   - {paper2} ({year}) — {similarity description}

   **Differentiation**: {what makes this idea different, if anything}

   **Confidence**: {high | medium | low} — {based on search coverage}

   **Recommendation**: {pursue | refine | pivot | abandon}
   ```
4. **Update idea file**: Append verification results to `methodology/ideas/YYYY-MM-DD-discovery.md`
5. **If cross-model disagreement**: Flag conflicting assessments for human review

## Suggested Next
- Novel idea confirmed → `decision.analyze` (should we pursue it?)
- Idea already exists → `paper.read` on the existing paper
- Idea needs refinement → `research.explore` to find differentiation angle
