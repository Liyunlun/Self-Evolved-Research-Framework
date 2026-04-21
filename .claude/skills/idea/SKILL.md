---
name: idea
description: Research idea generation, novelty verification, and refinement into actionable proposals
---

# /idea — Idea Generation, Novelty Verification, and Refinement

Route the user's intent to the appropriate sub-skill:

- **Discover or brainstorm ideas** (user wants to explore research directions, find gaps, generate new ideas) → read `references/discover.md` and follow its instructions
- **Verify idea novelty** (user asks "is this novel?", "has this been done?", or wants to check an idea against existing literature) → read `references/verify.md` and follow its instructions
- **Refine an idea into a concrete proposal** (user wants to sharpen, formalize, or make an idea more actionable) → read `references/refine.md` and follow its instructions

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
