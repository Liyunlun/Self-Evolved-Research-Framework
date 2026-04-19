# peer-review — AAAI-26-style AI peer review pipeline

Re-implementation of the multi-stage AI peer review system described in
[**AI-Assisted Peer Review at Scale: AAAI-26 Pilot** (arxiv 2604.13940)](https://arxiv.org/abs/2604.13940),
decomposed into 8 composable Claude Code skills.

## Skills in this family

| Skill | Role |
|---|---|
| `peer-review` | Orchestrator. Drives the full pipeline and writes the final review. |
| `peer-review-story` | Stage 1 — narrative / gap-claim audit (no tools). |
| `peer-review-presentation` | Stage 2 — clarity, headings, notation (no tools). |
| `peer-review-evaluations` | Stage 3 — baselines, metrics, stats; uses Bash code interpreter. |
| `peer-review-correctness` | Stage 4 — equations, proofs, algorithms; uses Bash. |
| `peer-review-significance` | Stage 5 — novelty + citation verification; uses WebSearch/WebFetch. |
| `peer-review-critique` | Stage 6 — compile → self-critique → revise into AAAI format. |
| `peer-review-qa` | Stage 7 — bias, offensive language, citation hallucination spot check. |

Preprocessing (PDF → markdown) delegates to `document-skills:pdf`.

## Usage

Trigger the orchestrator with any of:
- "Review this paper: `<arxiv URL>`"
- "Peer-review `paper/draft.pdf`"
- "Generate a reviewer report for `<path>`"

The orchestrator runs all 7 stages and writes outputs to
`outputs/peer-review/<paper_id>/`.

## Shared assets

All stages read these (under `peer-review/shared/`):

- `base_instruction.md` — reviewer objectives, factual standards, PDF/markdown complementarity.
- `review_schema.md` — YAML frontmatter + required sections for every stage's findings file.
- `output_format.md` — AAAI review format (6 sections, severity-tagged weaknesses, 400–1500 words).
- `rubric.yaml` — per-stage `must_check` lists.

## Testing

```bash
bash ~/.claude/skills/peer-review/tests/run_all_tests.sh
```

Four hermetic test layers (no LLM calls, <2s):

| Layer | Purpose |
|---|---|
| 1. Static lint | All 8 SKILL.md files have valid frontmatter; orchestrator references every stage; shared assets exist; rubric covers all stages. |
| 2. Negative cases | Schema and output-format validators correctly REJECT malformed inputs (4 crafted bad files). |
| 3. Stage findings | Golden fixture findings for each stage pass schema and contain the expected `[severity]` flag for a seeded flaw in the toy paper. |
| 4. E2E pipeline | All 7 stage outputs schema-valid; final review has all 6 AAAI sections; QA flags the seeded fabricated citation; Weaknesses list reflects fingerprints from every earlier stage. |

Test fixture `tests/fixtures/toy_paper.md` seeds six deliberate flaws (unsupported gap claim, duplicate heading, impossible accuracy 1.30, dimension-mismatched equation, fabricated citation) and six `golden_*.md` files provide the expected stage outputs. When the live LLM-driven pipeline runs, each stage's output must match the same contracts these goldens already satisfy.

## Architecture notes

The paper's five review dimensions (Story, Presentation, Evaluations, Correctness, Significance) map 1:1 to the five stage skills. The paper's compile → self-critique → revise loop is merged into `peer-review-critique` (one skill, three sub-steps) because they share context and run on the same inputs. The paper's QA critic layer is a separate skill (`peer-review-qa`) since its tool needs (WebFetch for citation verification) differ from the critique.

Each stage receives all previous stage outputs to match the paper's feed-forward design: "Inputs to each stage: PDF, markdown, base instruction, outputs from all previous stages."
