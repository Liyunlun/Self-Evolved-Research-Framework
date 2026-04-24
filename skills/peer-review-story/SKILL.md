---
name: peer-review-story
description: Stage 1 of the peer-review pipeline. Audits a research paper's narrative — problem formulation, claimed research gap, core contributions — and checks that evidence in the paper supports the story. Invoked by the `peer-review` orchestrator; can also be used standalone when the user asks "does this paper's story hold up" or "is the claimed gap real".
---

# peer-review-story

First stage of the AAAI-26 AI peer-review pipeline. No external tools — pure reading.

## Inputs
- `paper_pdf`: path to PDF
- `paper_md`: path to markdown rendering
- `paper_id`: slug
- `shared/base_instruction.md` (read and internalize)
- `shared/review_schema.md` (required output format)

## Must-check list (from `shared/rubric.yaml`)
1. **problem_statement_clarity** — Is the problem crisply defined in the intro?
2. **claimed_gap_supported_by_related_work** — The paper says "prior work fails to X". Does the related work section actually show this, or is it assertion without citation?
3. **contribution_list_matches_content** — Every bullet in the contributions list must map to a concrete section/experiment. Flag orphan contributions and flag undisclosed contributions.
4. **narrative_coherence** — Does motivation → method → experiments → claim form a straight line, or are there non-sequiturs?

## Taste probes (from `shared/taste-priors.md`)
Primary probe at this stage:
- **`mechanism_attribution`** — For each contribution the paper claims, ask: *would the reported results survive if this mechanism were removed?* If the paper does not provide (or could not provide given its setup) an experiment that would isolate the claimed mechanism, fire this probe. Tag the finding with `probe: mechanism_attribution`.

Apply `terminology_audit` lightly here only when a loaded term appears in the contribution list; it will be audited in depth by `peer-review-significance`.

## Process
1. Read the markdown. Locate: abstract, introduction (esp. final 1-2 paragraphs listing contributions), related work, conclusion.
2. For each must-check item, find concrete evidence in the paper. Cite it.
3. For each claimed gap, verify at least one cited prior work actually matches the claim.
4. Write findings to `outputs/peer-review/<paper_id>/01_story.md` per schema.

## Tools
None. Use Read + Grep on the markdown. Open the PDF only for figure/table captions that might reveal contributions (rare at this stage).

## Output
`outputs/peer-review/<paper_id>/01_story.md` — must conform to `shared/review_schema.md`.

## Failure modes to avoid
- Do NOT flag vague prose as critical. Vague prose is `minor`.
- Do NOT invent gaps the paper doesn't claim.
- Do NOT evaluate method quality here — that's `correctness`.
- Do NOT evaluate experiments here — that's `evaluations`.

## Tests
`tests/test_story.sh` — runs this stage on fixture `toy_paper.pdf` (which has a seeded [major] gap-claim flaw) and verifies the output contains `[major]` flagging the unsupported gap.
