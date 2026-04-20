---
name: peer-review-critique
description: Stage 6 of the peer-review pipeline. Compiles findings from stages 1-5 into an AAAI-format draft review, then performs a self-critique pass (check for unsupported claims, factual errors, incomplete citations), then revises the draft into the final review. When `verdict=true` is passed by the orchestrator, also emits a `## Verdict` section with Rate (strong accept / accept / weak accept / weak reject / reject / strong reject) and Confidence (1-5). Invoked by the `peer-review` orchestrator; standalone triggers include "compile these review findings into a review", "self-critique this draft review".
---

# peer-review-critique

Combined compile + self-critique + revise stage. This is one skill because the three sub-steps are cheap to keep together and share context — matching the paper's Initial Review → Self-Critique → Final Review Revision loop.

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- All prior stage outputs: `01_story.md`, `02_presentation.md`, `03_evaluations.md`, `04_correctness.md`, `05_significance.md`
- `shared/base_instruction.md`, `shared/review_schema.md`, `shared/output_format.md` (required final format)
- Optional flag `verdict` (bool, default false): when true, emit a final `## Verdict` section.

## Process (three sub-steps, one skill)

### Sub-step A: Compile draft
1. Read all 5 stage outputs.
2. Deduplicate overlapping findings.
3. Assemble a draft in AAAI format per `shared/output_format.md`:
   - Title (derived from paper's main claim)
   - Synopsis (1-2 sentences)
   - Summary (contribution, method, results)
   - Strengths (pull the paper's genuine merits from what each stage chose NOT to flag)
   - Weaknesses (every finding from stages 1-5, severity-tagged)
   - References (external works cited by `significance` stage, in APA)
4. Write draft to a scratch buffer (not disk yet).

### Sub-step B: Self-critique
5. Re-read the draft alongside the original paper_md.
6. Check for:
   - Unsupported claims in the review (every weakness must cite stage evidence)
   - Factual errors (numbers, section/equation refs that don't exist)
   - Incomplete citations (every APA entry must have author/year/venue)
   - Severity inflation (is that really [critical] or just [major]?)
7. Produce a critique list (mental or scratch).

### Sub-step C: Revise
8. Apply all critique fixes to the draft.
9. Verify all six AAAI section headings are present verbatim.

### Sub-step D: Verdict (only when `verdict=true`)
10. Compute the Rate by mapping the severity-tagged weakness counts + strengths balance:
    - 0 critical, 0-1 major, positive strength signal → `accept` or `strong accept`
    - 0 critical, 2-3 major → `weak accept`
    - 0 critical, 4+ major OR 1 critical at the edges → `weak reject`
    - 1 critical in the method/correctness core → `reject`
    - 2+ critical compounding across dimensions → `strong reject`
    Adjust up or down by one step if the Strengths section carries unusually strong (or weak) positive signal. Rate MUST be one of: `strong accept` | `accept` | `weak accept` | `weak reject` | `reject` | `strong reject`.
11. Set Confidence (integer 1-5):
    - 5: all dimensions scrutinized, evidence is self-checked, reviewer has domain expertise and all claims in the review are cited.
    - 4: same as 5 but at least one dimension relied on a shallow pass or an external reference.
    - 3: default when some findings are uncertain or lacked verification (e.g., could not re-run code).
    - 2: multiple findings hinge on assumed facts rather than cited evidence.
    - 1: outside of the reviewer's expertise or read at very high level.
12. Write a 1-2 sentence rationale that (a) maps the Strengths/Weaknesses balance to the Rate and (b) justifies the Confidence. Do NOT introduce new findings here.
13. Append the `## Verdict` section exactly per `shared/output_format.md § Optional Verdict section`.

### Sub-step E: Write
14. Write final to `outputs/peer-review/<paper_id>/06_final.md`.

## Tools
None (just Read/Write).

## Output
`outputs/peer-review/<paper_id>/06_final.md` — must conform to `shared/output_format.md`. Unlike stage outputs 01-05, this file is the **final review itself**, not a findings file.

## Failure modes to avoid
- Do NOT include findings that contradict each other without adjudication.
- Do NOT drop `[critical]` findings when revising — only clarify or re-sever.
- Do NOT add new content in Sub-step C that wasn't in the draft or the critique list.
- Do NOT emit `## Verdict` when `verdict=false` (even a placeholder is a schema violation).
- Do NOT invent a Rate outside the six allowed strings, and do NOT write Confidence as a float.

## Tests
`tests/test_critique.sh` — supply mock stage outputs missing a `## Strengths` section. Verify final review adds one. Also verify exact presence of all six AAAI headings in output.
