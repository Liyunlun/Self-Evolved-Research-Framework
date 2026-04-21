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
5. If the paper has a code release -> clone to `resources/repos/{repo-name}/` with `--depth 1`

### Reading & Reference Rules
- When reading existing notes in `resources/papers/`: **read Quick Reference section first**; only read full notes if deeper understanding needed
- Lookup order: `resources/papers/` -> `resources/repos/` -> fetch/clone and add
- See `resources/README.md` for full conventions

### Suggested Next
- If the paper contains a relevant theorem or conjecture worth formalizing -> `theory.formalize`
