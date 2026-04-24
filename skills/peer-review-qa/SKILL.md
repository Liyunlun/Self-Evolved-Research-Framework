---
name: peer-review-qa
description: Stage 7 of the peer-review pipeline — the QA critic. Checks the final review for author identity disclosure, offensive/biased language, structural completeness, and samples citations to verify they are not hallucinated. Invoked by the `peer-review` orchestrator; standalone triggers include "QA check this review", "verify citations in this review are real", "check review for bias".
---

# peer-review-qa

Final stage: an independent critic that audits the finished review. Uses web fetching to spot-check citations for hallucination (per the AAAI-26 paper's 99% validation protocol).

## Inputs
- `outputs/peer-review/<paper_id>/06_final.md` — the final review to audit
- `paper_md` — original paper, for cross-ref checks
- `shared/base_instruction.md`, `shared/review_schema.md`

## Must-check list
1. **author_identity_not_disclosed** — Review must not name the paper's authors, their institutions, or their prior work in a way that suggests the reviewer knows them.
2. **no_offensive_or_biased_language** — Flag demeaning, dismissive, or ad-hominem phrases.
3. **structural_completeness** — All six AAAI sections present verbatim (Title, Synopsis, Summary, Strengths, Weaknesses, References).
4. **citation_hallucination_spot_check** — Randomly sample up to 5 APA citations from the References section. For each, WebSearch/WebFetch to verify: (a) paper exists, (b) authors match, (c) year matches, (d) venue matches.

## Process
1. Read `06_final.md`. Parse the six sections (fail loudly if any missing).
2. Regex scan for patterns that leak identity: explicit author name mentions not present in the paper's own text; phrases like "I know the authors", "authors' prior work at X".
3. Regex scan for pejorative, dismissive, or ad-hominem language directed at the authors or the work. Judge in context: a word that is technical in one sentence may be demeaning in another. Flag only usages where the same point could be made with neutral, evidence-first language.
4. Sample up to 5 citations. For each: WebSearch the title; WebFetch the top result; compare authors/year/venue.
5. Write `07_qa.md` per `shared/review_schema.md` with:
   - `severity_counts.critical` ≥ 1 if any hallucinated citation found or identity disclosed
   - `severity_counts.major` for bias/offensive language, structural gaps
   - In `model_notes`: how many citations sampled, how many verified

## Tools
- **WebSearch** and **WebFetch** (or `better-fetch`).
- Read + Grep.

## Output
`outputs/peer-review/<paper_id>/07_qa.md` — per `shared/review_schema.md`.

## Failure modes to avoid
- Do NOT flag every informal word as offensive — context matters.
- Do NOT declare a citation hallucinated after only one failed search — try 2+ queries.
- Do NOT re-audit content correctness (that was earlier stages).

## Tests
`tests/test_qa.sh` — runs on a mock `06_final.md` with a seeded unverifiable citation and a seeded author-identity disclosure; the stage's output must flag both at `[critical]` severity.
