---
name: writing-outline
description: Propose a paper outline (section structure, page lengths, figure plan) plus a Claims-Evidence Matrix mapping every intended claim to its evidence source. Triggers on "how should I organize the paper?", "draft an outline", "starting a new paper", or "what sections should I have?".
---

# writing-outline

**Trigger**: User plans paper structure, asks "how should I organize the paper?", or starts a new paper.

**Process**:
1. Read existing research outputs: `paper/`, `methodology/approach.md`
2. Propose paper outline:
   - Section structure with estimated page lengths
   - Key content for each section (2-3 bullets)
   - Figure/table plan
   - Which existing outputs map to which sections
3. Identify gaps: what research is needed before each section can be written
4. Save outline to `paper/papers/outline.md` if confirmed

**Inputs**: Research topic + existing outputs + target venue (optional)
**Outputs**: Paper outline document + Claims-Evidence Matrix
**Token**: ~2-5K
**Composition**: Outline approved → leads to `writing-draft` for individual sections

## Claims-Evidence Matrix (Outline Artifact)

When producing an outline, also generate a claims→evidence mapping table:

```markdown
## Claims-Evidence Matrix

| # | Claim | Evidence Type | Source | Status |
|---|-------|--------------|--------|--------|
| C1 | {main contribution claim} | {theorem/experiment/analysis} | {file or planned} | {have/need} |
| C2 | {secondary claim} | {experiment} | {logs/experiments/...} | {have/need} |
| ... | ... | ... | ... | ... |
```

**Purpose**: Ensures every paper claim is backed by concrete evidence before drafting begins.
**Usage in writing-draft**: When drafting a section, check the matrix — only write claims with `status: have`. Flag `status: need` claims for the user.
**Update rule**: As experiments complete or proofs are verified, update the matrix status.
