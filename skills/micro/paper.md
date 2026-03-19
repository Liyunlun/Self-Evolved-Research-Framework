# Paper Micro-Skills

> Triggered by paper-related content in conversation.

## paper.read

**Trigger**: User discusses, shares, or asks about a specific paper (arXiv link, paper title, PDF content)

**Process**:
1. If paper content is provided (PDF/text/link), extract key information:
   - Title, authors, venue, year
   - Core contribution (1-2 sentences)
   - Method summary (3-5 bullet points)
   - Key results/claims
   - Relevance to the current project and research goals
2. Generate structured reading notes
3. Save to `resources/papers/{PAPER_ID}.md` with front-matter:
   ```yaml
   ---
   title: "{title}"
   authors: ["{author1}", "{author2}"]
   year: YYYY
   venue: "{venue}"
   relevance: "{high/medium/low}"
   tags: ["{tag1}", "{tag2}"]
   read_date: "YYYY-MM-DD"
   ---
   ```
4. If `resources/papers/README.md` exists, append to index

**Inputs**: Paper content (any form: link, PDF, pasted text, title for lookup)
**Outputs**: `resources/papers/{PAPER_ID}.md`
**Token**: ~3-8K
**Composition**: If paper has relevant theorem → suggest `theory.formalize`

---

## paper.compare

**Trigger**: User compares two or more papers, or asks about differences between methods

**Process**:
1. Read relevant `resources/papers/*.md` files
2. Generate comparison table:
   - Method / Architecture / Training data / Results / Limitations
3. Highlight implications for current project
4. Output inline (not saved unless user requests)

**Inputs**: 2+ paper references (files or titles)
**Outputs**: Comparison table (inline)
**Token**: ~2-5K
**Composition**: May lead to `decision.analyze` if comparing approaches for adoption

---

## paper.index

**Trigger**: User asks about reading list, what papers exist, or "what have I read"

**Process**:
1. Read `resources/papers/README.md` and scan `resources/papers/*.md` files
2. Output organized index:
   - By relevance (high/medium/low)
   - By topic tag
   - Unread vs. read status
3. Suggest gaps in reading based on project methodology

**Inputs**: `resources/papers/*.md` directory
**Outputs**: Index (inline)
**Token**: ~1-2K
**Composition**: May suggest `paper.read` for unread high-relevance papers

---

## lit.search

**Trigger**: User says "找论文", "文献检索", "related work", "search arxiv", "find papers on X", or during `idea.discover` when landscape context is needed

**Process**:
1. **Extract search parameters**:
   - Keywords from user request
   - Research domain from `config.yaml § research.keywords`
   - Time range (default: last 2 years)
   - Optional: specific venue, author, or topic constraints
2. **Multi-source search**:
   a. **arXiv API**: `http://export.arxiv.org/api/query?search_query={keywords}&max_results=20`
      - Filter by relevance and recency
   b. **Semantic Scholar API**: `https://api.semanticscholar.org/graph/v1/paper/search?query={keywords}`
      - Retrieve citation counts and influential citations
   c. **Local library**: Scan `resources/papers/*.md` for existing notes matching keywords
3. **Rank results** by composite score:
   - Relevance to query: 0.4
   - Recency: 0.2
   - Citation impact: 0.2
   - Alignment with project goals: 0.2
4. **Generate structured output** (top 10, inline):
   ```
   ### Literature Search: {query}
   Date: {YYYY-MM-DD} | Sources: arXiv, Semantic Scholar, local

   | # | Title | Authors | Year | Venue | Relevance | Already Read? |
   |---|-------|---------|------|-------|-----------|---------------|

   **Top 3 — One-sentence summaries:**
   1. {title}: {core contribution in one sentence}
   2. ...
   3. ...

   **Gaps identified**: {what the literature does NOT cover that's relevant}
   ```
5. **Cross-reference with local library**: Flag papers already in `resources/papers/`

**Inputs**: Search query + `config.yaml § research.keywords`
**Outputs**: Structured literature list (inline)
**Token**: ~3-8K
**Composition**: Found key paper → suggest `paper.read` + `checklist.update`
