---
name: paper-lit-search
description: Multi-source literature search — query arXiv + Semantic Scholar + the local `resources/papers/` library for a topic, dedupe across sources, rank by relevance + recency + citations + project alignment, and save a search artifact at `resources/papers/searches/{YYYY-MM-DD}-{slug}.md`. Top hits worth deeper study chain into `paper-read`. Triggers on "search arxiv", "find papers about X", "lit search", "related work", "survey this topic", "文献搜索". Complements the existing `paper-read / paper-compare / paper-index` trio by covering the *discovery* step before any paper is read.
---

# paper-lit-search

**Trigger**: User asks to find papers, do a literature search, survey a topic, or explore related work. For reading a specific paper that's already in hand use `paper-read`; for comparing papers the user has already read use `paper-compare`; for listing what's in the local library use `paper-index`.

**Process**:

### 1. Extract search parameters

Pull from the user's request (ask once if any is missing):

- **Core topic / keywords** — 2–5 terms. If the user gives a sentence, extract noun phrases + method names. Avoid single-word queries — too noisy.
- **Time range** — default **last 5 years**; adjust to "all time" only for foundational surveys.
- **Target venues / domains** — arXiv categories (e.g. `cs.LG`, `stat.ML`, `math.ST`), specific venues (NeurIPS, ICML, ACL), or "any".
- **Hard requirements** — "must have code", "theoretical (no empirical)", "must cite paper X", etc.
- **Soft preferences** — "prefer highly cited", "prefer recent", "prefer underexplored".

Pull **project context** from `config.yaml` (research domain, keywords) and `methodology/approach.md` (current direction). This feeds the alignment-score component in step 3.

### 2. Multi-source query

Hit three sources in parallel and deduplicate:

**arXiv API** — `http://export.arxiv.org/api/query`
- Query: `search_query=ti:"term1"+AND+(cat:cs.LG+OR+cat:stat.ML)&sortBy=relevance&max_results=30`
- Extract: arxiv_id, title, authors, abstract, year, categories, pdf_url
- Fetch up to 30 results; filter by time range client-side.

**Semantic Scholar API** — `https://api.semanticscholar.org/graph/v1/paper/search`
- Query: `?query=term1+term2&fields=title,authors,year,venue,citationCount,influentialCitationCount,abstract,externalIds`
- Extract: paperId, citation count, influential citation count, venue, externalIds (includes DOI, arxiv_id for join with source A)
- Fetch up to 30 results.

**Local library** — scan `resources/papers/*.md` frontmatter (title, authors, tags, arxiv_id). Match by fuzzy title + author surname. Mark already-in-library papers explicitly in the output so the user doesn't re-read them.

**Dedup key**: arxiv_id > DOI > title+first-author. If two sources disagree on citation count, prefer Semantic Scholar.

**API etiquette**:
- Semantic Scholar rate limits aggressively without an API key (~100 req/5 min). Batch where possible; back off on 429.
- arXiv requests a 3-second gap between bulk queries. Respect it.
- Never scrape the web HTML — use the APIs. If an API is down, say so and partial-result rather than falling back to scraping.

### 3. Rank by composite score

For each deduped candidate, compute:

```
score = 0.4 × relevance + 0.2 × recency + 0.2 × citations_norm + 0.2 × alignment
```

- **Relevance** (0–1): keyword hit rate in title + abstract (title matches weighted 3×). If both arXiv and Semantic Scholar returned the paper, relevance bumps +0.1 (independently-surfaced signal).
- **Recency** (0–1): `max(0, 1 − (current_year − paper_year) / 5)`. Papers >5 years old get 0 for recency; balance out via citations instead.
- **Citations normalized** (0–1): `log(1 + citations) / log(1 + max_in_batch)`. Using log avoids one mega-cited paper flattening everyone else. Use `influentialCitationCount` from Semantic Scholar when available (stronger signal than raw count).
- **Alignment** (0–1): cosine-ish overlap between paper tags/keywords and project keywords from step 1. If project context is thin (`methodology/approach.md` short / missing), set alignment = 0.5 uniform and note it.

Show weights in the saved artifact — if the user wants "prefer recent" they can change them.

### 4. Generate output table + summaries

Two views in one artifact:

**Top 10 table**:

| Rank | Title | Authors | Year | Venue | Cites | Score | Why relevant |
|---|---|---|---|---|---|---|---|
| 1 | ... | ... | ... | ... | ... | ... | ... |

**Top 5 brief summaries** — for the first 5 rows, 2–3 sentences each covering: what the paper does, key claim, and the one-line reason it's relevant to the user's query. Pull from abstract, do NOT invent.

**Identified gaps**:
- If the top-5 cluster around one method family, name the under-represented families (e.g. "all top hits are Transformer-based; no CNN/RNN baselines in top 10").
- If the top-5 all pre-date a key development, note it ("all top hits are pre-2023; LLM-era developments not surfaced — try adding 'LLM' / '2024' to the query").
- If zero results met the relevance floor (>0.3), report that explicitly and suggest query refinements.

**Refinement suggestions** (3 alternates):
- Narrower query if > 30 strong hits
- Broader query if < 5 strong hits
- Orthogonal query surfacing adjacent sub-fields

### 5. Save the search artifact

Write to `resources/papers/searches/{YYYY-MM-DD}-{slug}.md` where slug is a kebab-case phrase from the core topic:

```markdown
---
search_date: "YYYY-MM-DD"
query: "{topic + keywords}"
time_range: "YYYY–YYYY"
venues: "[cs.LG, stat.ML, NeurIPS, ICML]"
weights: {relevance: 0.4, recency: 0.2, citations: 0.2, alignment: 0.2}
sources: ["arxiv", "semantic-scholar", "local"]
hits_returned: {N_arxiv, N_s2, N_local}
hits_after_dedup: N
---

## Summary
{1-line summary of what was searched and top takeaway}

## Top 10 Hits
{table from step 4}

## Top 5 Summaries
{expanded entries from step 4}

## Already in Library
- `{arxiv_id}` — {title} — `resources/papers/{paper_id}.md`
- ...

## Gaps Identified
{gap list from step 4}

## Refinement Suggestions
1. {narrower query}
2. {broader query}
3. {orthogonal query}

## Raw Results
<details>
{all N deduped results as a compact JSONL block for reproducibility}
</details>
```

The `Raw Results` block lets a follow-up `paper-read` or `paper-compare` fetch details without re-querying the APIs.

### 6. Handoff

Emit a 4-line summary (query, N hits after dedup, top paper + score, suggested next). Chain to the appropriate skill.

**Inputs**: User topic + `config.yaml` + `methodology/approach.md` + `resources/papers/` local library
**Outputs**: `resources/papers/searches/{YYYY-MM-DD}-{slug}.md`
**Token**: ~4-12K (dominated by the 3 API fetches + summarization; quick searches ~4K, exhaustive surveys ~12K)
**Composition**:
- Top hit worth a deep read → `paper-read` (Standard or Fey-R mode) on the arxiv_id
- Several hits to contrast with a candidate method → `paper-compare`
- Gap identified in the literature → natural input to `idea-discover` (feed the gap list as prompt context)
- Candidate idea already exists, this is a novelty check → `idea-verify` (paper-lit-search produces the prior-work evidence)
- Survey belongs in the paper's Related Work → after reading the top 5, chain into `writing-draft` for the Related Work section
- Library grew substantially → `paper-index` to refresh the reading-list view

## Common pitfalls

- **Single-source searches miss systematic biases** — arXiv skews CS / ML / physics; Semantic Scholar skews English + highly-cited. If the topic is niche (e.g. econometrics, bioinformatics), either add a domain-appropriate source or note the bias in the artifact.
- **Over-weighting citations for recent papers** — a 2025 paper has had no time to accumulate citations. The log normalization helps but doesn't eliminate the bias. For queries with time_range including the current year, mentally add a recency premium when reading the ranked list.
- **Dedup by title alone** — conference + journal + arXiv versions of the same paper may differ by title casing or a subtitle. Use `arxiv_id > DOI > fuzzy_title+first_author`.
- **Reporting abstracts as conclusions** — abstracts over-claim. The "Why relevant" column should be a factual claim from the abstract, not "this paper solves X" unless the abstract literally says so.
- **Stale local library** — `resources/papers/` entries may be outdated (paper revised on arXiv). For high-confidence matches, check `updated` field from arXiv API vs. local `read_date`; flag if > 6 months stale.
- **API rate-limiting silently truncating results** — if Semantic Scholar returns 429, the search may look complete but be missing ~50% of candidates. Always log per-source hit counts in the `hits_returned` field so the user can see which source failed.
- **Query with punctuation / special chars** — arXiv API is tolerant; Semantic Scholar is picky. URL-encode everything, strip quotation marks, and replace operators.
- **Recommending Google Scholar / Connected Papers / etc.** — they have no public API. Don't promise integrations the skill can't deliver. Stick to arXiv + Semantic Scholar and be honest about the coverage.
- **Searches without saving the raw results** — if the user asks a follow-up ("what was the 3rd hit?") and the artifact only has the top-10 table, you have to re-query. The `Raw Results` block prevents this.
- **Promoting hits to the library without reading** — don't `paper-read`-save every hit automatically. Let the user pick. Auto-ingesting search results pollutes `paper-index` with never-read entries.
