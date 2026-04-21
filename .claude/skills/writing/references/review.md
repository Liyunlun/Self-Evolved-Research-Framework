# writing.review

**Trigger**: User wants a draft reviewed, says "review this", or wants feedback on writing quality.

## Process

1. Read the draft (full section or paper).
2. Evaluate from multiple reviewer perspectives:
   - **Clarity**: Is the writing clear and well-structured?
   - **Novelty**: Are contributions clearly distinguished from prior work?
   - **Soundness**: Are claims properly supported by evidence?
   - **Presentation**: Are figures, tables, and equations effective?
   - **Missing elements**: What's absent that reviewers would expect?
3. Generate review in conference format:
   - Summary (2-3 sentences)
   - Strengths (bulleted)
   - Weaknesses (bulleted, with specific suggestions)
   - Questions for authors
   - Rating (Accept / Weak Accept / Borderline / Weak Reject / Reject)

Note: For cross-model review (using external LLMs for diverse perspectives), use the `review` skill group instead.

## Suggested Next

- Weaknesses identified -> `writing.polish` to address specific issues.
