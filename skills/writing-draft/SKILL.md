---
name: writing-draft
description: Draft a specific paper section (introduction, method, results, etc.) in LaTeX with venue-appropriate tone, proper citations, then auto-verify citations via citation_fetch.py. Triggers on "draft the introduction", "write the method section", "draft the related work", or similar section-specific writing requests.
---

# writing-draft

**Trigger**: User asks to write a specific paper section, or says "draft the introduction/method/results".

**Process**:
1. Read the outline (if exists) and relevant source materials:
   - Proofs from `paper/proofs/`
   - Theory from `paper/theory/`
   - Paper notes from `resources/papers/*.md`
2. Draft the requested section:
   - Academic tone appropriate for target venue
   - Proper citations (placeholder format: \cite{author_year})
   - LaTeX formatting
   - Integrate figures/tables where appropriate
3. Save draft to `paper/papers/{section_name}.tex`
4. **Post-draft citation verification**:
   - Scan draft for placeholder `\cite{author_year}` entries
   - For each placeholder, run `scripts/citation_fetch.py "{title}" --authors "{author}"`
   - Replace with verified BibTeX key if found; mark with `% [VERIFY]` if not
   - Append verified BibTeX entries to `paper/papers/references.bib`
   - Output summary: `Citations: {N} verified, {M} need manual verification`

**Inputs**: Section name + source materials + target venue
**Outputs**: `paper/papers/{section_name}.tex` + updated `references.bib`
**Token**: ~5-15K
**Composition**: Draft complete → suggest `writing-review` for feedback
