---
name: peer-review-significance
description: Stage 5 of the peer-review pipeline. Assesses novelty and positioning against the literature using web search. Verifies cited work (authors/year/venue) and flags missing key related work. Invoked by the `peer-review` orchestrator; standalone triggers include "how novel is this paper", "find related work this paper missed", "verify the citations in this paper".
---

# peer-review-significance

Fifth stage of the AAAI-26 AI peer-review pipeline. **Uses WebSearch + WebFetch.**

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- Previous stage outputs: `01_story.md` through `04_correctness.md`
- `shared/base_instruction.md`, `shared/review_schema.md`

## Must-check list
1. **novelty_vs_recent_work** — Search for 2–5 closely related recent papers (last 3 years). Does this paper's contribution overlap substantially?
2. **positioning_in_literature** — Does the paper correctly situate itself in the lineage of prior work?
3. **cited_work_accuracy** — Spot-check 3–5 citations from the bibliography. Does the cited author/year/venue exist? Use WebSearch.
4. **missing_key_related_work** — Any widely-cited work on the same topic that the paper fails to cite?

## Taste probes (from `shared/taste-priors.md`)
Primary probe at this stage:
- **`terminology_audit`** — When the paper names its mechanism with a term that carries a loaded theoretical or methodological connotation, check whether the underlying equations reduce to a standard, established operation. If they do, and the paper does not contrast against the standard version, tag the finding with `probe: terminology_audit`. Propose a rename in the resolution text — it both shows the concern and gives the authors an actionable path.

This probe is *structural*, not stylistic: the trigger is "the math equals a standard operation", not "the name sounds fancy." The definition of "loaded term" is contextual — any term whose ordinary technical meaning implies a stronger claim than the underlying operation realizes qualifies.

## Process
1. Extract the paper's main claim and 3–5 keywords.
2. Run WebSearch on `<keyword> <year-range>` (2023–present for AI/ML). Scan top-10 results; pick 2–3 closest papers.
3. For each, fetch abstract via WebFetch/better-fetch. Compare against this paper's claim.
4. Randomly sample up to 5 citations from the bibliography. For each, WebSearch the title; verify it exists with the cited authors/year.
5. Produce findings: novelty verdict, positioning assessment, list of missing references, list of mis-cited references.

## Tools
- **WebSearch** — for literature scans.
- **WebFetch** / `better-fetch` — for pulling abstracts of specific papers.
- Read + Grep on the paper's bibliography.

## Output
`outputs/peer-review/<paper_id>/05_significance.md` — per schema. Include APA-formatted external references at the end of the findings (these feed into the final review's References section).

## Failure modes to avoid
- Do NOT declare "not novel" without naming ≥2 specific prior works.
- Do NOT flag a citation as fabricated without searching at least twice with varied queries.
- Do NOT rely on a single search result — corroborate.

## Tests
`tests/test_significance.sh` — runs on a fixture paper containing a seeded unverifiable citation. The stage's output OR the downstream QA stage must flag it at `[critical]` as hallucinated/unverifiable; the static test accepts a flag in either location.
