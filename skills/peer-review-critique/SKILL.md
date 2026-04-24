---
name: peer-review-critique
description: Stage 6 of the peer-review pipeline. Compiles findings from stages 1-5 into an AAAI-format draft review, then performs a self-critique pass (check for unsupported claims, factual errors, incomplete citations), then revises the draft into the final review. When run_config.yaml has recommendation=yes, also emits a venue-level-aware accept/weak accept/weak reject/reject recommendation. Invoked by the `peer-review` orchestrator; standalone triggers include "compile these review findings into a review", "self-critique this draft review".
---

# peer-review-critique

Combined compile + self-critique + revise stage. This is one skill because the three sub-steps are cheap to keep together and share context — matching the paper's Initial Review → Self-Critique → Final Review Revision loop.

## Inputs
- `paper_pdf`, `paper_md`, `paper_id`
- All prior stage outputs: `01_story.md`, `02_presentation.md`, `03_evaluations.md`, `04_correctness.md`, `05_significance.md`
- `shared/base_instruction.md`, `shared/review_schema.md`, `shared/output_format.md` (required final format)
- `shared/review_level.yaml` (for the level's `critical_threshold`, `major_threshold`, `required_qualities`)
- `run_config.yaml` (to look up `level` and `recommendation` flag; and `reviewer_backgrounds[i]` when running under a reviewer sub-agent)
- `level_bar.md` (appended to `base_instruction.md` under `## Level bar`; affects how you weigh findings)

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

### Sub-step C: Revise (and emit recommendation)
8. Apply all critique fixes to the draft.
9. Verify all six AAAI section headings are present verbatim.
10. **Recommendation** (only if `run_config.yaml` has `recommendation: yes`):
    - Aggregate severity counts across stages 01–05 (sum the `severity_counts` YAML frontmatter from each `NN_<stage>.md`).
    - Load `shared/review_level.yaml[<level>]` for `critical_threshold`, `major_threshold`, `required_qualities`.
    - Apply the decision logic documented in `shared/output_format.md` (§ "Decision mapping"):

      ```
      if critical_count >= level.critical_threshold:
          rec = reject
      elif major_count > level.major_threshold:
          rec = weak_reject
      elif any required_quality is missing per stage findings:
          rec = weak_reject
      elif level == best_paper and minor_count > 3:
          rec = weak_accept
      elif (critical + major + minor) == 0:
          rec = accept
      else:
          rec = weak_accept
      ```

      For `oral` / `best_paper`: if neither the `story` nor `significance` stage surfaces a
      finding supporting a "novel insight" AND the paper's contribution reads as
      incremental, degrade the result by one step (accept→weak accept, weak accept→weak
      reject).
    - Append a `## Recommendation` section to the review. The first non-blank line is the
      literal token (`accept` / `weak accept` / `weak reject` / `reject`). The next line
      begins with `Justification:` and cites (a) the aggregate severity counts, and (b)
      the top 1–2 weakness bullets (by severity) that drove the decision — especially
      when the recommendation is `weak reject` or `reject`.
11. Write final to `outputs/peer-review/<paper_id>/06_final.md` (or `reviewer_<i>/06_final.md` when invoked from a reviewer sub-agent).

## Tools
None (just Read/Write).

## Output
`outputs/peer-review/<paper_id>/06_final.md` (or `reviewer_<i>/06_final.md`) — must conform to `shared/output_format.md`. Unlike stage outputs 01-05, this file is the **final review itself**, not a findings file. When `recommendation: yes`, it also contains a `## Recommendation` section after `## References`.

## Failure modes to avoid
- Do NOT include findings that contradict each other without adjudication.
- Do NOT drop `[critical]` findings when revising — only clarify or re-sever.
- Do NOT add new content in Sub-step C that wasn't in the draft or the critique list, except for the `## Recommendation` section.
- Do NOT emit a recommendation when `run_config.yaml` has `recommendation: no` (or the file is absent) — in that case, omit the section entirely.
- Do NOT invent severity counts; always aggregate from the stage findings' YAML frontmatter.

## Tests
`tests/test_critique.sh` — supply mock stage outputs missing a `## Strengths` section. Verify final review adds one. Also verify exact presence of all six AAAI headings in output, and that (when recommendation is requested) the `## Recommendation` section is present and its first token matches one of the four allowed labels.
