---
name: peer-review
description: Run a multi-stage AI peer review on a research paper (AAAI-26-style pipeline) with selectable venue level (poster/oral/best_paper), optional multi-reviewer mode with a Senior Area Chair (SAC) synthesizer, and an optional accept/weak accept/weak reject/reject recommendation. Triggers on "review this paper", "peer-review <arxiv URL or PDF>", "generate a reviewer report", "write a review for this paper", "run a 3-reviewer peer review", "best-paper-level review". Orchestrates 5 specialized review stages (story, presentation, evaluations, correctness, significance) plus self-critique, QA, and optional SAC summarization.
---

# peer-review (orchestrator)

Implements a venue-aware, optionally multi-reviewer extension of the AAAI-26 AI-assisted peer review pipeline. You are the orchestrator. You do NOT do the analysis yourself — you **collect run configuration from the user**, **invoke** the specialized stage skills, and **assemble** the final artifacts.

## Inputs

- A paper, given as:
  - arXiv URL (`arxiv.org/abs/...`), OR
  - local PDF path, OR
  - local markdown path (skip preprocessing)
- Optional inline overrides to skip interactive prompts:
  - `level=poster|oral|best_paper`
  - `reviewers=1|2|3`
  - `rec=yes|no`
  - `level_bar_override=<path to custom bar file>`
- Optional `paper_id` slug (auto-generated from filename/URL if missing).

## Step 0 — Interactive launch (ALWAYS runs before any pipeline work)

Before downloading or preprocessing anything, collect the run configuration. Use `AskUserQuestion` for any field not provided via inline override.

1. **Venue level** (`level`): one of `poster` / `oral` / `best_paper`.
   - Poster: NeurIPS/ICML/ICLR poster track — sound + useful result.
   - Oral: additionally requires genuine new insight AND strong method validation.
   - Best Paper: additionally requires transformative insight, best-in-class method, flawless presentation.
2. **Reviewer count** (`reviewers`): `1 (solo)` / `2` / `3`.
3. **Reviewer backgrounds** (only if `reviewers > 1`): free-text persona per reviewer describing the subfield, methodological orientation, or role the reviewer is meant to embody. Ask via `AskUserQuestion` Other/free-text field or a follow-up prompt. Accept any short descriptor the user supplies; do not suggest specific fields.
4. **Recommendation emission** (`rec`): `yes (default)` / `no`. Default-on means every final review contains a `## Recommendation` section.

After collecting Q1, load the default bar block from `shared/review_level.yaml[<level>].bar` and show it to the user:

> "Here is the draft bar that will be appended to every stage's base instruction. Want to edit before dispatch?" — options: `Use as-is` / `Edit`.

If the user picks `Edit`, accept the replacement text and save it to `outputs/peer-review/<paper_id>/level_bar.md`. Otherwise save the default bar text to the same file verbatim. Every downstream stage reads this file, NOT the YAML — so user edits take effect for this run without mutating the shared asset.

Save all answers to `outputs/peer-review/<paper_id>/run_config.yaml`:

```yaml
level: <poster|oral|best_paper>
reviewers: <1|2|3>
recommendation: <yes|no>
reviewer_backgrounds:  # only if reviewers > 1; one free-text descriptor per reviewer
  - "<reviewer 1 background>"
  - "<reviewer 2 background>"
```

## Step 1 — Resolve input & preprocess

1. If arXiv URL, download PDF via `better-fetch` or curl; if PDF path given, copy to `00_preprocess/paper.pdf`. Derive `paper_id` as an alphanumeric slug from the arXiv identifier or the PDF filename (strip extension, lowercase, replace non-alphanumerics with `_`).
2. Invoke `document-skills:pdf` to extract text → `00_preprocess/paper.md`. Store page count, title, authors in `metadata.yaml`.

Preprocessing is ALWAYS done once, regardless of reviewer count (shared across reviewers).

## Step 2 — Dispatch based on mode

### Solo mode (`reviewers == 1`)

Run stages 01–07 sequentially, exactly as before:

```
[01] Story          → Skill(peer-review-story)
[02] Presentation   → Skill(peer-review-presentation)
[03] Evaluations    → Skill(peer-review-evaluations)
[04] Correctness    → Skill(peer-review-correctness)
[05] Significance   → Skill(peer-review-significance)
[06] Critique       → Skill(peer-review-critique)   # compile + self-critique + revise + emit recommendation
[07] QA             → Skill(peer-review-qa)
```

Pass to every stage:
- paper_pdf path, paper_md path, paper_id
- list of prior stage output files (accumulates)
- `shared/base_instruction.md` + `shared/review_schema.md` + `shared/output_format.md`
- `outputs/.../level_bar.md` (append under `## Level bar` when constructing the stage prompt)
- `run_config.yaml` (so critique knows whether to emit recommendation)
- relevant rubric entry from `shared/rubric.yaml`

Each stage writes its own `NN_<stage>.md` conforming to `shared/review_schema.md`. Final review lands at `06_final.md`, QA at `07_qa.md`.

### Multi-reviewer mode (`reviewers > 1`)

1. **Launch N reviewer sub-agents in parallel** (single message, multiple `Agent` tool calls, `subagent_type: general-purpose`). Each sub-agent prompt MUST include:
   - paper_pdf + paper_md absolute paths
   - Its output subdir: `outputs/peer-review/<paper_id>/reviewer_<i>/`
   - Its assigned background from `run_config.yaml` (so the sub-agent passes it to every stage via base_instruction)
   - The path to `level_bar.md`
   - Explicit instruction to run stages 01 → 06 via the `peer-review-story`, `peer-review-presentation`, `peer-review-evaluations`, `peer-review-correctness`, `peer-review-significance`, `peer-review-critique` skills in order, writing each `NN_<stage>.md` into its subdir
   - Explicit instruction to NOT run stage 07 (QA) — the orchestrator handles QA centrally
2. Wait for all N to return.
3. Run **QA per reviewer**: for each `reviewer_<i>/06_final.md`, invoke `peer-review-qa`, writing `reviewer_<i>/07_qa.md`. (Each reviewer's review is a primary deliverable, so each gets a full QA pass.) If any QA reports `critical > 0`, surface it to the user and offer to re-run that reviewer's critique stage.
4. Invoke **`peer-review-sac`** with:
   - Paths to all `reviewer_<i>/06_final.md`
   - `run_config.yaml`
   - `shared/review_level.yaml`
   Produces `outputs/peer-review/<paper_id>/sac_summary.md` (short meta-summary only — not an AAAI-format review).
5. Inline lightweight QA on the SAC summary: re-read `sac_summary.md` and check for author-identity disclosure and offensive/biased language. If either is present, flag and re-invoke `peer-review-sac` with the issue as additional context. Do NOT run the full `peer-review-qa` skill on the SAC summary — that skill expects AAAI structure, which `sac_summary.md` deliberately lacks.

## Output layout

### Solo mode
```
outputs/peer-review/<paper_id>/
  run_config.yaml
  level_bar.md
  00_preprocess/paper.pdf
  00_preprocess/paper.md
  00_preprocess/metadata.yaml
  01_story.md  02_presentation.md  03_evaluations.md
  04_correctness.md  05_significance.md
  06_final.md  07_qa.md
```

### Multi-reviewer mode (N reviewers)
```
outputs/peer-review/<paper_id>/
  run_config.yaml
  level_bar.md
  00_preprocess/...
  reviewer_1/01_story.md ... reviewer_1/06_final.md  reviewer_1/07_qa.md
  reviewer_2/01_story.md ... reviewer_2/06_final.md  reviewer_2/07_qa.md
  ...
  sac_summary.md
```

## Guardrails

- **Always run Step 0 first.** Never preprocess or dispatch a stage before the run_config is captured.
- **Validate schema after every stage**: run `tests/test_schema.py <file>` on each emitted `NN_<stage>.md`. If it fails, re-invoke that stage once with the schema validation error as additional context. If it fails again, halt and report.
- **Validate output format on `06_final.md`**: run `tests/test_output_format.py <file>`. For oral/best_paper runs with recommendation, this test accepts (but does not require) the optional `## Recommendation` section.
- **Never skip stages within a reviewer.** Order is fixed (01 → 06).
- **Multi-reviewer sub-agents must be launched in a single parallel dispatch** (one assistant message, N `Agent` tool calls) per `superpowers:dispatching-parallel-agents`.
- **Idempotent**: if the expected output file already exists and passes schema, skip regeneration unless user passed `--force` / `force=true`.

## When NOT to use this skill

- Single-paper quick reads (use `fey-r` instead — that's learning, not reviewing).
- Comparing two paper versions (use `pdf-version-compare`).

## Related skills

- `peer-review-story`, `peer-review-presentation`, `peer-review-evaluations`, `peer-review-correctness`, `peer-review-significance`, `peer-review-critique`, `peer-review-qa` — the 7 per-reviewer pipeline skills this orchestrator invokes.
- `peer-review-sac` — synthesizes N independent reviews in multi-reviewer mode (short meta-summary, NOT an AAAI-format review).
- `document-skills:pdf` — preprocessing dependency.
- `superpowers:dispatching-parallel-agents` — reference pattern for launching reviewer sub-agents in parallel.

## Tests

See `tests/run_all_tests.sh` at this skill's root. Covers (1) static lint of all SKILL.md files (including `peer-review-sac`), (2) schema conformance, (3) per-stage unit tests against seeded-flaw fixtures, (4) end-to-end pipeline smoke test including the optional Recommendation section.
