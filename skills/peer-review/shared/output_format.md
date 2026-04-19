# Final Review Output Format (AAAI-26 style)

The final review (produced by `peer-review-critique` after revision) MUST have exactly these six sections, in this order, each marked by a level-2 heading:

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
```

## Hard requirements

1. All six section headings must be present verbatim (case-sensitive, including the leading `#` for title and `##` for the other five).
2. Every weakness bullet must carry a severity tag.
3. References in APA style: `Author, A. B. (Year). Title. Venue.`
4. No markdown footnotes, no HTML.
5. Total length 400–1500 words.
