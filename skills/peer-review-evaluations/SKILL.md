---
name: peer-review-evaluations
description: Stage 3 of the peer-review pipeline. Audits empirical methodology — baselines, datasets, metrics, seed/errorbar support — and uses a code interpreter to test any embedded code snippets and sanity-check reported numbers. Invoked by the `peer-review` orchestrator; standalone triggers include "audit the experiments", "are these baselines enough", "check if reported numbers are sane".
---

# peer-review-evaluations

Third stage of the AAAI-26 AI peer-review pipeline. **Uses Bash as code interpreter.**

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- Previous stage outputs: `01_story.md`, `02_presentation.md`
- `shared/base_instruction.md`, `shared/review_schema.md`

## Must-check list
1. **baselines_adequate** — Do baselines cover standard comparisons? Missing obvious ones?
2. **datasets_appropriate** — Are datasets standard for the claim? Sufficient diversity?
3. **metrics_appropriate** — Do metrics actually measure the claimed property?
4. **statistical_support_seeds_errorbars** — Enough seeds (≥3)? Error bars or significance tests?
5. **reproducibility_of_reported_numbers** — Sample 1–2 numbers; check if an embedded code snippet or formula reproduces them (via Bash).
6. **sanity_of_reported_values** — Accuracy in [0,1]; probabilities sum to 1; percentages ≤ 100; timing ≥ 0.

## Process
1. Enumerate baselines and datasets from tables/text.
2. Read all claimed metrics from Tables and Figures.
3. **Sanity sweep**: grep the markdown for numeric cells. Any out-of-range values → `[critical]`.
4. **Code snippet sweep**: if the paper embeds code in appendix or main body, extract it and run it via Bash (`python -c` or `python script.py` in a temp dir). Report what ran and what didn't.
5. Write findings with concrete table/figure citations.

## Tools
- **Bash** — for running snippets and doing arithmetic sanity checks (e.g., `python -c "assert 0 <= 0.95 <= 1"`).
- Read, Grep on markdown.

## Output
`outputs/peer-review/<paper_id>/03_evaluations.md` — per `shared/review_schema.md`. Include in `model_notes` the number of code snippets run and passed.

## Failure modes to avoid
- Do NOT run untrusted code that touches the network or filesystem outside a temp dir.
- Do NOT flag missing baselines the paper explicitly justifies as out-of-scope.

## Tests
`tests/test_evaluations.sh` — fixture paper reports accuracy `1.3` in a results table. Output must contain `[critical]` flagging impossible/out-of-range value.
