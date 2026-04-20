---
name: peer-review
description: Run a multi-stage AI peer review on a research paper (AAAI-26-style pipeline). Triggers on "review this paper", "peer-review <arxiv URL or PDF>", "generate a reviewer report", "write a review for this paper". Orchestrates 5 specialized review stages (story, presentation, evaluations, correctness, significance) plus self-critique and QA, and produces a final AAAI-format review. Supports an optional `--verdict` flag that additionally emits a conference-style Rate (strong accept / accept / weak accept / weak reject / reject / strong reject) and Confidence (1-5).
---

# peer-review (orchestrator)

Implements the AAAI-26 AI-assisted peer review pipeline (arxiv.org/abs/2604.13940). You are the orchestrator. You do NOT do the analysis yourself — you **invoke** the specialized stage skills in order, pass their outputs forward, and assemble the final review.

## Inputs

- A paper, given as:
  - arXiv URL (`arxiv.org/abs/...`), OR
  - local PDF path, OR
  - local markdown path (skip preprocessing)
- Optional: a paper_id slug (auto-generated from filename/URL if missing).
- Optional: `--verdict` flag (or "with verdict" / "给出评分" in the user request) — when set, the final review also includes a `## Verdict` section with a conference-style Rate + Confidence. See `shared/output_format.md § Optional Verdict section` for the exact format.

## Pipeline (strict order)

```
[00] Preprocess     → document-skills:pdf (PDF → markdown)
[01] Story          → Skill(peer-review-story)
[02] Presentation   → Skill(peer-review-presentation)
[03] Evaluations    → Skill(peer-review-evaluations)
[04] Correctness    → Skill(peer-review-correctness)
[05] Significance   → Skill(peer-review-significance)
[06] Critique       → Skill(peer-review-critique)   # compile + self-critique + revise
[07] QA             → Skill(peer-review-qa)
```

## Output layout

```
outputs/peer-review/<paper_id>/
  00_preprocess/paper.pdf
  00_preprocess/paper.md
  00_preprocess/metadata.yaml
  01_story.md  02_presentation.md  03_evaluations.md
  04_correctness.md  05_significance.md
  06_final.md  07_qa.md
```

## Orchestration steps

1. **Resolve input**: if arXiv URL, download PDF via `better-fetch` or curl; if PDF path given, copy to `00_preprocess/paper.pdf`. Derive `paper_id` (e.g., `arxiv_2604.13940`).
2. **Preprocess**: invoke `document-skills:pdf` to extract text → `00_preprocess/paper.md`. Store page count, title, authors in `metadata.yaml`.
3. **Stages 01–05**: invoke each stage skill with:
   - paper_pdf path, paper_md path, paper_id
   - list of prior stage output files (accumulates)
   - `shared/base_instruction.md`, `shared/review_schema.md`, relevant rubric entry from `shared/rubric.yaml`
   Each stage writes its own `NN_<stage>.md` conforming to `shared/review_schema.md`.
4. **Stage 06 — Critique**: invoke `peer-review-critique` with all prior stage files + `shared/output_format.md`. Pass `verdict=true` when `--verdict` was set on the orchestrator. Produces `06_final.md` (compiled + self-critiqued + revised, optionally with a `## Verdict` section).
5. **Stage 07 — QA**: invoke `peer-review-qa` on `06_final.md`. Writes `07_qa.md`. If QA reports `critical > 0`, report to the user and offer to loop back through stage 06. If `--verdict` was set, QA also sanity-checks that Rate is one of the six allowed strings and Confidence is an integer 1-5.

## Guardrails

- **Validate schema after every stage**: run `tests/test_schema.py <file>` on each emitted `NN_<stage>.md`. If it fails, re-invoke that stage once with the schema validation error as additional context. If it fails again, halt and report.
- **Never skip stages**. Order is fixed.
- **Idempotent**: if `NN_<stage>.md` already exists and passes schema, skip regeneration unless user passed `--force`.

## When NOT to use this skill

- Single-paper quick reads (use `fey-r` instead — that's learning, not reviewing).
- Comparing two paper versions (use `pdf-version-compare`).

## Related skills

- `peer-review-story`, `peer-review-presentation`, `peer-review-evaluations`, `peer-review-correctness`, `peer-review-significance`, `peer-review-critique`, `peer-review-qa` — the 7 pipeline skills this orchestrator invokes.
- `document-skills:pdf` — preprocessing dependency.

## Tests

See `tests/run_all_tests.sh` at this skill's root. Covers (1) static lint of all 8 SKILL.md files, (2) schema conformance, (3) per-stage unit tests against seeded-flaw fixtures, (4) end-to-end pipeline smoke test.
