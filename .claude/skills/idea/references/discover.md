# idea.discover

**Trigger**: User asks "what ideas can we explore?", "find research gaps", "generate ideas for X", or during brainstorming when exploration phase is active.

## Process
1. **Gather context**:
   - Read `config.yaml` (research domain, keywords)
   - Read `methodology/approach.md` (current research direction)
   - Read `resources/papers/*.md` Quick Reference sections (known landscape)
   - Execute `memory.retrieve` for relevant past explorations and decisions
2. **Literature gap analysis**:
   - Identify what existing papers in `resources/papers/` address
   - Identify what current methodology does NOT address
   - Cross-reference with research keywords to find under-explored intersections
3. **Generate ideas** (`config.yaml` workflows.idea_discovery.candidate_count candidates, default 5):
   - For each idea, produce:
     ```
     ### Idea {N}: {title}
     - **Core insight**: {1-2 sentences}
     - **Approach**: {how it would work}
     - **Novelty claim**: {what's new vs. existing work}
     - **Feasibility**: {H/M/L} — {brief rationale}
     - **Alignment**: {H/M/L} — {relation to project goals}
     - **Required resources**: {what's needed — data, compute, theory}
     ```
4. **Rank ideas** by composite score: `0.4 * novelty + 0.3 * feasibility + 0.3 * alignment`
5. **Output top 5** with ranking rationale
6. **Save artifact**: Write to `methodology/ideas/YYYY-MM-DD-discovery.md`

## Idea File Format: `methodology/ideas/YYYY-MM-DD-discovery.md`

```markdown
---
date: "YYYY-MM-DD"
domain: "{research domain}"
num_generated: N
num_verified: M
top_idea: "{title of highest-ranked idea}"
---

## Discovery Session: {date}

### Context
{What prompted this exploration — project phase, gap identified, etc.}

### Ideas (ranked)
{idea entries as described above}

### Verification Results
{verification entries appended by idea.verify}

### Selected for Pursuit
{Which ideas were chosen and why — filled in after decision.analyze}
```

## Suggested Next
- Ideas generated → `idea.verify` on top 3 for novelty check
