# Paper Micro-Skills

> Triggered by paper-related content in conversation.

## paper.read

**Trigger**: User discusses, shares, or asks about a specific paper (arXiv link, paper title, PDF content)

**Modes**:
- **Standard** (default): Quick structured extraction — good for survey/triage
- **Deep** (Fey-R): Interactive Feynman-method reading — guided derivation for true understanding

**Mode selection**: If user says "read paper", "what's this paper about" → Standard.
If user says "study this paper", "understand this paper deeply", "let's read this carefully",
"Fey-R", or expresses intent to deeply learn the method → Deep (Fey-R).
When in doubt, offer the choice after Phase 0 triage.

### Standard Mode

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

### Deep Mode (Fey-R)

**Process**: Read and follow `skills/external/fey-r/SKILL.md` for the full 6-phase workflow.
Use `skills/external/fey-r/assets/note-template.md` as the output template.

1. Execute Fey-R phases 0-5 (First Pass → Background → Pain Points → Derivation → Comparison → Verification)
2. Save output to `resources/papers/{PAPER_ID}.md` using Fey-R's note template, with the same front-matter as Standard mode
3. If `resources/papers/README.md` exists, append to index with `[deep]` tag

**Inputs**: Paper content (any form: link, PDF, pasted text, title for lookup)
**Outputs**: `resources/papers/{PAPER_ID}.md`
**Token**: Standard ~3-8K, Deep ~15-40K (interactive, multi-turn)
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
