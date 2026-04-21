---
name: writing-review
description: Simulate a conference peer review of a draft (Clarity / Novelty / Soundness / Presentation / Missing) and produce a review with Strong Accept to Reject verdict. Optionally runs in cross-model adversarial mode with a subagent reviewer plus auto-fix loop. Triggers on "review my draft", "peer review this", "simulate reviewer feedback", "thorough review".
---

# writing-review

**Trigger**: User asks to review a draft, "what do you think of this writing?", or wants simulated peer review.

**Process**:
1. Read the draft section/paper
2. Evaluate from multiple reviewer perspectives:
   - **Clarity**: Is the writing clear? Are claims well-supported?
   - **Novelty**: Is the contribution clearly articulated?
   - **Soundness**: Are the technical claims correct?
   - **Presentation**: Figures, organization, flow
   - **Missing**: What's absent that reviewers would expect?
3. Generate review in conference format:
   - Summary (2-3 sentences)
   - Strengths (bulleted)
   - Weaknesses (bulleted, with specific suggestions)
   - Questions for authors
   - Overall: Strong Accept / Accept / Borderline / Reject
4. Output inline (save to `paper/reviews/` if full paper review)

**Inputs**: Draft text + target venue
**Outputs**: Structured review (inline or saved)
**Token**: ~5-15K (single-model) / ~10-25K (cross-model loop)
**Composition**: Weaknesses identified → suggest `writing-polish` for specific fixes

## Cross-Model Review Mode

When cross-model feedback is desired, `writing-review` can operate in **cross-model adversarial mode** for higher-quality feedback. Suggested for full paper reviews or critical sections (introduction, methodology).

**Activation**: Auto-activated when reviewing full papers or when user requests "thorough review" / "adversarial review". Can be explicitly requested or skipped.

**Process**:
1. **Send draft to external reviewer** via Claude Code Agent subagent:
   - Launch an Agent (subagent_type="general-purpose") with a prompt that includes:
     - The draft text to review
     - System instructions:
       ```
       You are a rigorous peer reviewer for {venue}. Review this paper section with the standards of a top-tier venue. Provide:
       1. Summary (2-3 sentences)
       2. Strengths (bulleted, specific)
       3. Weaknesses (bulleted, with concrete fix suggestions)
       4. Questions for authors
       5. Score: {Strong Accept / Accept / Borderline / Reject}
       6. Confidence: {High / Medium / Low}
       Be critical but constructive. Cite specific passages.
       ```
2. **Internal review**: Simultaneously generate own review (standard writing-review process)
3. **Synthesize**: Compare internal vs. external reviews:
   - Agreement areas → high-confidence feedback
   - Disagreement areas → flag for user judgment with both perspectives
   - External-only issues → likely blind spots worth addressing
4. **Auto-fix loop** (up to 4 rounds, governed by TD-NL):
   - Round N: Apply fixes for agreed-upon weaknesses
   - Re-submit to external reviewer with: "I've addressed your feedback. Here's the revised version: {diff summary}. Please re-review."
   - Track quality trajectory: score should improve each round
   - **Stopping criteria** (TD-NL learned):
     - External score reaches "Accept" or better → stop
     - Score unchanged for 2 consecutive rounds → stop (diminishing returns)
     - 4 rounds reached → stop (hard cap)
     - User interrupts → stop
5. **Output**: Final synthesized review + revision history:
   ```
   ## Cross-Model Review Summary
   Rounds: {N}
   Score trajectory: {R1: Reject → R2: Borderline → R3: Accept}
   Key improvements made: {bulleted list}
   Remaining issues: {what couldn't be auto-fixed}
   Internal vs External agreement: {high/medium/low}
   ```
6. Save review to `paper/reviews/{section_name}-cross-review.md`

**TD-NL tracking**: Performance tracked via `skills/td-nl/skill-values/writing-review.md`.
Key metrics: rounds-to-accept, score improvement per round, agreement rate with internal review.
Learns optimal stopping: if early rounds show little improvement, reduces max rounds.
