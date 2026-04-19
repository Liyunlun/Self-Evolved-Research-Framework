---
name: paper-read
description: Read a research paper (arXiv link, PDF, or pasted text) and produce structured reading notes saved to resources/papers/. Triggers when the user discusses or shares a paper, asks "what's this paper about", "read paper X", or provides an arXiv URL. Has two modes — Standard for fast triage, Deep (Fey-R) for full Feynman-method understanding.
---

# paper-read

**Trigger**: User discusses, shares, or asks about a specific paper (arXiv link, paper title, PDF content).

**Modes**:
- **Standard** (default): Quick structured extraction — good for survey/triage
- **Deep** (Fey-R): Interactive Feynman-method reading — guided derivation for true understanding

**Mode selection**: If user says "read paper", "what's this paper about" → Standard.
If user says "study this paper", "understand this paper deeply", "let's read this carefully",
"Fey-R", or expresses intent to deeply learn the method → Deep (Fey-R).
When in doubt, offer the choice after Phase 0 triage.

## Standard Mode

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

## Deep Mode (Fey-R)

**Process**: Read and follow `skills/external/fey-r/SKILL.md` for the full 6-phase workflow.
Use `skills/external/fey-r/assets/note-template.md` as the output template.

1. Execute Fey-R phases 0-5 (First Pass → Background → Pain Points → Derivation → Comparison → Verification)
2. Save output to `resources/papers/{PAPER_ID}.md` using Fey-R's note template, with the same front-matter as Standard mode
3. If `resources/papers/README.md` exists, append to index with `[deep]` tag

**Inputs**: Paper content (any form: link, PDF, pasted text, title for lookup)
**Outputs**: `resources/papers/{PAPER_ID}.md`
**Token**: Standard ~3-8K, Deep ~15-40K (interactive, multi-turn)
**Composition**: If paper has relevant theorem → suggest `theory-formalize`
