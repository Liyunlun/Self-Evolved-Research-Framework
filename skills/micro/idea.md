# Idea Discovery Micro-Skills

> Triggered by idea generation, novelty checking, or research direction brainstorming.
> Automates the gap analysis → idea generation → novelty verification pipeline.

## idea.discover

**Trigger**: User asks "what ideas can we explore?", "find research gaps", "generate ideas for X", or during `plan.suggest` when exploration phase is active

**Process**:
1. **Gather context**:
   - Read `config.yaml` (research domain, keywords)
   - Read `methodology/approach.md` (current research direction)
   - Read `resources/papers/*.md` Quick Reference sections (known landscape)
   - Execute `memory.retrieve` for relevant past explorations and decisions
2. **Literature gap analysis**:
   - Identify what existing papers in `resources/papers/` address
   - Identify what current methodology does NOT address
   - Cross-reference with research keywords to find under-explored intersections
3. **Generate ideas** (8-12 candidates):
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
4. **Rank ideas** by composite score: `0.4 × novelty + 0.3 × feasibility + 0.3 × alignment`
5. **Output top 5** with ranking rationale
6. **Save artifact**: Write to `methodology/ideas/YYYY-MM-DD-discovery.md`

**Inputs**: Research domain context + paper notes + methodology
**Outputs**: Ranked idea list in `methodology/ideas/YYYY-MM-DD-discovery.md`
**Token**: ~4-8K
**Composition**: Ideas generated → suggest `idea.verify` on top 3 for novelty check

---

## idea.verify

**Trigger**: After `idea.discover`, or when user says "is this idea novel?", "has this been done?", or proposes a specific research idea

**Process**:
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

**Inputs**: Idea descriptions (from idea.discover or user-provided)
**Outputs**: Verification report appended to idea file
**Token**: ~3-6K
**Composition**:
- Novel idea confirmed → chain to `decision.analyze` (should we pursue it?)
- Idea already exists → suggest reading the existing paper via `paper.read`
- Idea needs refinement → suggest `research.explore` to find differentiation angle

---

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
{verification entries as described above, appended by idea.verify}

### Selected for Pursuit
{Which ideas were chosen and why — filled in after decision.analyze}
```

## TD-NL Integration

Both options track performance via:
- `memory/td-nl/option-values/idea-discover.md`
- `memory/td-nl/option-values/idea-verify.md`

Key metrics for TD assessment:
- `idea.discover`: Were generated ideas relevant to project? Did ranking match user preferences? Diversity of ideas?
- `idea.verify`: Were novelty assessments accurate? Did search find relevant prior work? Cross-model agreement level?
