# Final Review Output Format (AAAI-26 style)

The final review (produced by `peer-review-critique` after revision) MUST have exactly these six sections, in this order, each marked by a level-2 heading — plus an OPTIONAL seventh section (`## Recommendation`) when the run was configured with `recommendation: yes`:

```markdown
# <Descriptive review title, ~12 words>

## Synopsis
<1-2 sentence capsule: what the paper claims, in the reviewer's voice.>

## Summary
<1-2 paragraphs: contribution, method, and main results as described by the paper.>

## Strengths
- <bullet 1>
- <bullet 2>
- ...

## Weaknesses
- <bullet 1, severity-tagged: [critical]/[major]/[minor]>
- <bullet 2>
- ...

## References
<APA-formatted list of any external works cited in the review. If none, write "None.">

## Recommendation   <!-- OPTIONAL: include only when run_config.yaml has recommendation: yes -->
<one of exactly: accept | weak accept | weak reject | reject>
Justification: <1-2 sentences citing the severity counts and top 1-2 weaknesses that drove the decision.>
```

## Hard requirements

1. The first six section headings (Synopsis, Summary, Strengths, Weaknesses, References, plus the H1 title) must always be present verbatim (case-sensitive, including the leading `#` for title and `##` for the other five).
2. Every weakness bullet must carry a severity tag.
3. References in APA style: `Author, A. B. (Year). Title. Venue.`
4. No markdown footnotes, no HTML.
5. Total length 400–1500 words (excluding the optional Recommendation section).
6. When the `## Recommendation` section is present:
   - The first non-blank line under it MUST be exactly one of `accept`, `weak accept`, `weak reject`, `reject` (lowercase).
   - The next line MUST start with `Justification:` and cite either severity counts or specific weakness bullets.

## Decision mapping (peer-review-critique uses this)

Let `C = critical_count`, `M = major_count`, `m = minor_count` aggregated across stages 01-05. Let `level` be the current venue level from `shared/review_level.yaml`.

```
if C >= level.critical_threshold:
    -> reject
elif M > level.major_threshold:
    -> weak reject
elif missing any of level.required_qualities (inferred from stage findings):
    -> weak reject
elif level == best_paper and m > 3:
    -> weak accept     # best-paper intolerant of minor polish issues
elif (C + M + m) == 0:
    -> accept
else:
    -> weak accept     # default middle ground
```

For oral / best_paper levels, if the `story` stage or `significance` stage contains no
finding that supports the presence of a "novel insight" AND the paper's contribution is
incremental per those findings, degrade the result by one step (accept -> weak accept,
weak accept -> weak reject).
