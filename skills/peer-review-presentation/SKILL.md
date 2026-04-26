---
name: peer-review-presentation
description: Stage 2 of the peer-review pipeline. Audits clarity, organization, readability, notation consistency, and figure/table caption quality. Invoked by the `peer-review` orchestrator; standalone triggers include "is this paper well-written", "check the presentation of this paper", "find clarity issues".
---

# peer-review-presentation

Second stage of the AAAI-26 AI peer-review pipeline. No external tools.

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- Previous stage output: `01_story.md`
- `shared/base_instruction.md`, `shared/review_schema.md`

## Must-check list
1. **section_organization** — Are sections in a sensible order? Any duplicates, gaps, or missing expected sections (e.g., no Related Work)?
2. **heading_consistency** — Same style across sections? Any two consecutive headings that are identical?
3. **figure_caption_quality** — Does every figure have a caption that explains what the reader sees (not just restating the figure title)?
4. **notation_consistency** — Are symbols introduced before use? Any symbol with two meanings or two symbols for one concept?
5. **readability_and_flow** — Dense walls of text, run-on sentences, undefined acronyms.

## Process
1. Scan the markdown structure (heading tree). Flag structural issues.
2. Read every figure/table caption. Flag low-quality captions.
3. Sample 3–5 notation-heavy paragraphs. Verify symbols are defined at first use.
4. Do NOT re-flag items already caught by `story`. Add only presentation-level findings.

## Tools
None. Read + Grep.

## Output
`outputs/peer-review/<paper_id>/02_presentation.md` — per `shared/review_schema.md`.

## Failure modes to avoid
- Do NOT nitpick every typo — list up to 3 representative typos under one `[minor]` bullet.
- Do NOT evaluate content correctness — that's a later stage.

## Tests
`tests/test_presentation.sh` — runs on a fixture paper with a seeded heading-consistency flaw; the stage's output must flag a heading-consistency issue at `[minor]` severity.
