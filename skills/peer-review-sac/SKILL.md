---
name: peer-review-sac
description: Senior Area Chair (SAC) synthesizer for the peer-review multi-reviewer pipeline. Reads N independent reviewer `06_final.md` files (each produced by `peer-review-critique`) and emits a SHORT meta-summary `sac_summary.md` with reviewer list, points of consensus, points of disagreement, and (if enabled) a unified accept/weak accept/weak reject/reject recommendation. Deliberately NOT an AAAI-format review — the individual reviewer files remain the primary deliverables. Invoked only by the `peer-review` orchestrator in multi-reviewer mode (reviewers > 1); standalone triggers include "synthesize these reviews", "run SAC over reviewer_1 reviewer_2 reviewer_3".
---

# peer-review-sac

Short meta-summary synthesizer for multi-reviewer peer-review runs. The individual reviewer `06_final.md` files are the primary deliverables; this skill produces a thin synthesis layer on top that reports where reviewers agree, where they disagree, and how their recommendations combine into a single unified decision.

## Inputs

- N paths to reviewer final reviews: `reviewer_1/06_final.md`, `reviewer_2/06_final.md`, (`reviewer_3/06_final.md`)
- `run_config.yaml` (for `level`, `recommendation` flag, and per-reviewer `reviewer_backgrounds`)
- `shared/review_level.yaml` (for the current level's recommendation thresholds — used only when tie-breaking toward stricter side at oral/best_paper)

Never invoked in solo mode (reviewers == 1).

## Process

1. Load each reviewer's `06_final.md`. For each, extract:
   - The one-line Synopsis.
   - The bullet lists under `## Strengths` and `## Weaknesses` (preserving severity tags).
   - The `## Recommendation` section's first-line token (accept / weak accept / weak reject / reject), if present.
   - The reviewer's background from `run_config.yaml.reviewer_backgrounds[i]`.
2. Build a **consensus table** of weaknesses:
   - Normalize each weakness bullet to a short key (first 60 chars, lowercased, whitespace-collapsed).
   - For each key, record which reviewer(s) flagged it and their severity.
   - Rows where all N reviewers agree (with matching severities) → "consensus weakness" (tag with the max severity across reviewers).
   - Rows where at least one but not all reviewers flagged it, OR severities differ → "disagreement".
3. Build a **consensus strengths** list: strengths mentioned by all N reviewers.
4. Compute the **unified recommendation** (only if `run_config.yaml` has `recommendation: yes`):
   - Read each reviewer's `## Recommendation` first-line token.
   - Map to ordinal: `reject=0, weak_reject=1, weak_accept=2, accept=3`.
   - Take the median across the N tokens.
   - If N is even and the two middle values differ: at `oral` or `best_paper` level, round DOWN (stricter side); at `poster` level, round UP (leniency).
   - Map the median back to the label.
   - Record each reviewer's individual vote for transparency.
5. Write the output file (layout below).

## Output

`outputs/peer-review/<paper_id>/sac_summary.md`, with EXACTLY these four sections (when `recommendation: no`, omit the fourth):

```markdown
# SAC Meta-Summary: <paper title>

## Reviewers
- R1 (<background>): <one-line synopsis from R1>
- R2 (<background>): <one-line synopsis from R2>
- R3 (<background>): <one-line synopsis from R3>

## Points of consensus
Strengths (all reviewers agree):
- <consensus strength 1>
- ...

Weaknesses (all reviewers agree, tagged with max severity across reviewers):
- [major] <consensus weakness 1>
- [minor] <consensus weakness 2>
- ...

## Points of disagreement
- <normalized weakness key> — R1: <severity or not flagged>; R2: <severity or not flagged>; R3: <severity or not flagged>.
  SAC note: <one-line adjudication stating which reviewer's severity is supported by the strongest internal evidence and citing the section / equation / table in the paper that resolves the disagreement.>
- ...

## Unified Recommendation  <!-- only when run_config.yaml has recommendation: yes -->
<one of: accept | weak accept | weak reject | reject>
Vote: R1=<label>, R2=<label>, R3=<label>
Justification: <1-2 sentences citing the dominant consensus weaknesses (if any) or the reason the paper cleared the bar.>
```

### Formatting rules

- The first four section headings must appear verbatim in this order: `## Reviewers`, `## Points of consensus`, `## Points of disagreement`, and (optionally) `## Unified Recommendation`.
- The file MUST NOT contain `## Synopsis`, `## Summary`, `## Strengths`, `## Weaknesses`, or `## References` sections — those belong to the individual reviewer files. This is a hard rule: `sac_summary.md` is a meta-summary, not a replacement AAAI review.
- Each severity tag in consensus weaknesses is `[critical]`, `[major]`, or `[minor]`, chosen as the max across reviewers who flagged that item.
- When `run_config.yaml` is missing or has `recommendation: no`, omit the entire `## Unified Recommendation` section — do not emit a placeholder.

## Tools

None (just Read/Write).

## Failure modes to avoid

- Do NOT invent weaknesses or strengths that no reviewer flagged.
- Do NOT upgrade a severity beyond the max that any reviewer assigned.
- Do NOT paraphrase the recommendation tokens — they must be exact strings from the four allowed labels.
- Do NOT duplicate: if a weakness appears in `## Points of consensus`, it must not also appear in `## Points of disagreement`.
- Do NOT include any section other than the four specified above.

## Tests

`tests/test_sac.sh` — runs on mock reviewer final reviews whose recommendation tokens and configured venue level exercise the median-with-tie-break logic. The stage's output must:
- emit a `## Unified Recommendation` section whose first token is the label selected by the documented median and tie-break rules;
- contain only the four specified section headings (in order);
- contain none of the AAAI per-reviewer section headings (`## Synopsis`, `## Summary`, `## Strengths`, `## Weaknesses`, `## References`).
