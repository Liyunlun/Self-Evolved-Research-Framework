# /idea — Idea Generation, Novelty Verification, and Refinement

When to use this skill:
- User asks to brainstorm, explore research directions, or generate ideas
- User asks "is this idea novel?", "has this been done?", or proposes a research idea
- User wants to refine, sharpen, or make an idea more concrete
- Keywords: "find research gaps", "generate ideas", "novelty check", "refine idea", "精炼想法"

## idea.discover

**Trigger**: User asks "what ideas can we explore?", "find research gaps", "generate ideas for X", or during brainstorming when exploration phase is active.

### Process
1. **Gather context**:
   - Read `config.yaml` (research domain, keywords)
   - Read `methodology/approach.md` (current research direction)
   - Read `resources/papers/*.md` Quick Reference sections (known landscape)
   - Execute `memory.retrieve` for relevant past explorations and decisions
2. **Literature gap analysis**:
   - Identify what existing papers in `resources/papers/` address
   - Identify what current methodology does NOT address
   - Cross-reference with research keywords to find under-explored intersections
3. **Generate ideas** (`config.yaml § workflows.idea_discovery.candidate_count` candidates, default 5):
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

### Idea File Format: `methodology/ideas/YYYY-MM-DD-discovery.md`

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

### Suggested Next
- Ideas generated -> `idea.verify` on top 3 for novelty check

---

## idea.verify

**Trigger**: After `idea.discover`, or when user says "is this idea novel?", "has this been done?", or proposes a specific research idea.

### Process
1. **Extract verification targets**: For each idea to verify, extract:
   - Key claims / core contribution
   - Technical approach keywords
   - Expected related work search terms
2. **Automated search** (multi-source):
   a. **DBLP search**: Query `https://dblp.org/search/publ/api?q={keywords}&format=json`
      - Look for papers with similar titles or approaches
   b. **arXiv search** (via export API): Query `http://export.arxiv.org/api/query?search_query={keywords}&max_results=10`
      - Check recent papers (last 2 years) in relevant categories
   c. **Cross-model verification** (via Claude Code Agent subagent):
      - Launch an Agent (subagent_type="general-purpose") with a prompt that includes:
        - The idea description to verify
        - Instructions:
          ```
          You are a research novelty checker. Given an idea description, identify:
          1. The closest existing work (with paper titles and years)
          2. What differentiates this idea from existing work (if anything)
          3. Novelty assessment: {highly novel | somewhat novel | incremental | already exists}
          Be specific — cite actual papers, not vague references.
          ```
3. **Synthesize verification report** for each idea:
   ```
   ### Idea: {title}
   **Novelty verdict**: {highly novel | somewhat novel | incremental | already exists}

   **Closest existing work**:
   - {paper1} ({year}) — {similarity description}
   - {paper2} ({year}) — {similarity description}

   **Differentiation**: {what makes this idea different, if anything}

   **Confidence**: {high | medium | low} — {based on search coverage}

   **Recommendation**: {pursue | refine | pivot | abandon}
   ```
4. **Update idea file**: Append verification results to `methodology/ideas/YYYY-MM-DD-discovery.md`
5. **If cross-model disagreement**: Flag conflicting assessments for human review

### Suggested Next
- Novel idea confirmed -> `decision.analyze` (should we pursue it?)
- Idea already exists -> `paper.read` on the existing paper
- Idea needs refinement -> `research.explore` to find differentiation angle

---

## idea.refine

**Trigger**: User says "精炼想法", "refine idea", "让这个想法更具体", "完善方案", or after `idea.verify` confirms novelty.

### Process
1. **Read target idea**: From `methodology/ideas/*.md` or user-provided description
2. **Problem anchoring**:
   - What exactly does this solve? (1-2 sentences)
   - What is the evaluation metric?
   - What would "success" look like concretely?
3. **Frontier alignment**:
   - How does this relate to SOTA? (cite specific papers from `resources/papers/`)
   - What is the key differentiation?
   - What assumptions does it make vs. existing work?
4. **Implementation orientation**:
   - What are the concrete algorithmic steps?
   - What data/compute is required?
   - What is the minimal experiment to validate the core claim?
5. **Output structured proposal** to `methodology/ideas/{slug}.md`:
   ```markdown
   ---
   title: "{title}"
   status: "refined"
   refined_from: "{source idea reference}"
   date: "YYYY-MM-DD"
   ---
   ## Problem Statement
   {precise problem definition}

   ## Proposed Approach
   {concrete algorithmic/methodological steps}

   ## Key Differentiation
   {what makes this different from existing work}

   ## Minimal Validation
   {smallest experiment that tests the core claim}

   ## Resource Requirements
   {data, compute, dependencies}
   ```

### Suggested Next
- Refined idea -> `checklist.create(category=method)` to track implementation
- Refined idea -> `experiment.plan` for experiment design
