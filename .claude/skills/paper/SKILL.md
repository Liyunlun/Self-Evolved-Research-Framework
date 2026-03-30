# /paper — Paper Reading, Comparison, and Literature Management

When to use this skill:
- User shares, discusses, or asks questions about a specific paper
- User wants to compare multiple papers or approaches
- User asks about their reading list, paper library, or coverage gaps
- User needs to find related work, search for papers, or do a literature review
- Keywords: "read this paper", "compare these", "reading list", "找论文", "文献检索", "related work", "search arxiv"

## read

**Trigger**: User discusses or shares a paper (PDF, arXiv link, or title+authors).

### Process
1. Extract key information from the paper:
   - Title, authors, venue, year
   - Problem statement and motivation
   - Core method / architecture / algorithm
   - Key theoretical claims and results
   - Experimental setup and main results (tables/figures)
   - Limitations acknowledged by authors
   - Connections to user's current research
2. Generate structured reading notes with YAML frontmatter:
   ```
   paper_id, title, authors, year, venue, arxiv_id
   tags, status (read/skimmed/cited), relevance (1-5)
   ```
3. Body sections: Summary, Method, Key Results, Strengths, Weaknesses, Relevance to Our Work, Key Equations/Theorems, Open Questions
4. Save to `resources/papers/{PAPER_ID}.md`
   - PAPER_ID format: `{FirstAuthorLastName}{Year}{KeyWord}` (e.g., `Vaswani2017Attention`)

### Suggested Next
- If the paper contains a relevant theorem or conjecture worth formalizing -> `theory.formalize`

## compare

**Trigger**: User wants to compare two or more papers, methods, or approaches side-by-side.

### Process
1. Read the paper files from `resources/papers/` for each paper being compared
2. Generate a structured comparison table covering:
   - Method / Architecture
   - Training data and preprocessing
   - Evaluation metrics and benchmarks
   - Main quantitative results
   - Theoretical guarantees (if any)
   - Computational cost / scalability
   - Limitations and failure modes
3. Below the table, provide:
   - Key differentiators (what each paper does that others don't)
   - Complementary strengths (what could be combined)
   - Implications for user's research direction
4. If comparing >3 papers, organize by sub-groups sharing similar approaches

### Suggested Next
- If comparison reveals a design decision to make -> `decision.analyze`

## index

**Trigger**: User asks about their reading list, wants an overview of papers read, or asks "what have I read about X?".

### Process
1. Read all files in `resources/papers/` directory
2. Parse YAML frontmatter from each paper file (status, tags, relevance)
3. Output an organized index:
   - Group by topic/tag clusters
   - Within each group, sort by relevance score (descending)
   - Show status indicators: read / skimmed / cited / unread
   - Include one-line summary per paper
4. Identify and report gaps:
   - Topics with few papers
   - Highly relevant papers only skimmed
   - Missing foundational references suggested by citation patterns

### Suggested Next
- For unread or skimmed papers that seem important -> `paper.read`

## lit-search

**Trigger**: User asks to find papers, do a literature search, or explore related work. Common phrases: "找论文", "文献检索", "related work", "search arxiv", "find papers about X".

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
