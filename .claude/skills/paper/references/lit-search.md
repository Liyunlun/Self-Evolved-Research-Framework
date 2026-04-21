## lit-search

**Trigger**: User asks to find papers, do a literature search, or explore related work. Common phrases: "related work", "search arxiv", "find papers about X".

### Process
1. Extract search parameters from user request:
   - Core topic / keywords
   - Time range (default: last 5 years, adjustable)
   - Target venues or domains
   - Specific requirements (e.g., "must have code", "theoretical")
2. Multi-source search:
   - arXiv API (cs.*, math.*, stat.*)
   - Semantic Scholar API (citation graph, influential citations)
   - Local library (`resources/papers/`) for already-collected papers
3. Rank results by composite score:
   - Relevance to query: weight 0.4
   - Recency: weight 0.2
   - Citation count (normalized): weight 0.2
   - Alignment with user's research goals: weight 0.2
4. Generate structured output:
   - Top 10 results table (Title | Authors | Year | Venue | Score | Why relevant)
   - Brief summaries for top 5 (2-3 sentences each)
   - Identified gaps in the literature
   - Suggested search refinements if results are sparse

### Suggested Next
- For a key paper found that warrants deep reading -> `paper.read`
