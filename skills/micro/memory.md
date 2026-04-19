# Memory Micro-Skills

> Persistent memory across sessions using a three-tier file system.
> Memory types (episodic/semantic/procedural) emerge naturally from usage patterns.

## Tier Structure

| Tier | Purpose | Max Files | Retention |
|------|---------|-----------|-----------|
| `episodes/` | Recent observations, raw insights | 20 | 7 days |
| `topics/` | Consolidated knowledge, synthesized themes | 50 | 90 days |
| `procedures/` | Stable processes, permanent decisions | 100 | permanent |

## MEMORY.md

Always-loaded index (200-line hard limit). Read at every session.open.
Contains: Topic Index, Recent Episodes, Procedure Index, Active Context.

---

## memory.write

**Trigger**: After insight-producing micro-skills, or when user says "remember this."

**Initiation** (chain from other skills):
- After `paper.read`, `decision.analyze`, `progress.capture`, `theory.formalize`
- After `proof.critique`, `experiment.analyze`, `idea.discover`, `idea.verify`, `idea.refine`
- After `lit.search`, `proof.write`, `math.dse`
- Agent self-detects novel insight during any skill execution

**Process**:
1. Read `memory/MEMORY.md` (should be in context from session.open)
2. Assess importance (1-10) using thresholds from `config.yaml § memory.write`:
   - Novelty to project
   - Decision significance
   - Error/failure severity
   - Cross-topic relevance
3. If importance < `config.yaml § memory.write.importance_threshold` (default 5) → skip
4. Check for duplicates: scan MEMORY.md index for similar content
5. If duplicate → update existing memory instead of creating new
6. Write episode file to `memory/episodes/YYYY-MM-DD-NNN.md`:
   ```markdown
   ---
   type: episode
   date: "YYYY-MM-DD"
   source_skill: "{triggering micro-skill}"
   importance: N
   tags: ["{tag1}", "{tag2}"]
   consolidated: false
   ---
   ## Context
   {What was happening}

   ## Content
   {The specific insight, decision, or finding}

   ## Connections
   - Related: {links to related memories or papers}
   ```
7. Update `memory/MEMORY.md` Recent Episodes table (prepend; keep last 10)
8. If MEMORY.md > 180 lines → flag for consolidation

**Artifact**: `memory/episodes/YYYY-MM-DD-NNN.md` + updated MEMORY.md
**Token**: ~1-2K
**Composition**: If episode count exceeds threshold → chain to `memory.consolidate`

---

## memory.retrieve

**Trigger**: Before knowledge-dependent micro-skills.

**Initiation**:
- `session.open` (always — load active context)
- Before `plan.suggest`, `status.report`
- Self-initiated when agent lacks context for current task

**Process**:
1. Determine query: what does the agent need to know right now?
2. Read `memory/MEMORY.md`
3. Score index entries using weights from `config.yaml § memory.retrieve.weights`:
   - tag_overlap (default 0.4), keyword_match (0.3), recency (0.15), importance (0.15)
4. Select top `config.yaml § memory.retrieve.top_candidates` (default 5) candidates from index
5. Read full files for top `config.yaml § memory.retrieve.top_read` (default 3) candidates
6. Surface relevant content into conversation context

**Artifact**: Inline context (not a file)
**Token**: ~1-3K
**Composition**: Provides context for the calling skill to continue

---

## memory.consolidate

**Trigger**: Capacity management and knowledge synthesis.

**Initiation**:
- `session.close` (always check conditions)
- MEMORY.md > `config.yaml § memory.consolidate.memory_md_pressure_line` (default 180) lines
- `config.yaml § memory.consolidate.episode_threshold` (default 15)+ unconsolidated episodes
- `config.yaml § memory.consolidate.cluster_min` (default 3)+ episodes sharing the same primary tag

**Process**:
1. Read all unconsolidated episodes (`consolidated: false`)
2. Cluster by: tag overlap → source skill → temporal proximity
3. For each cluster of 3+ episodes:
   a. **Topic emergence**: Synthesize into `memory/topics/{topic-slug}.md`
      ```markdown
      ---
      type: topic
      created: "YYYY-MM-DD"
      updated: "YYYY-MM-DD"
      source_episodes: []
      tags: []
      ---
      ## {Topic Name}

      ### Key Facts
      {Consolidated knowledge — synthesized, not concatenated}

      ### Evolution
      | Date | Change | Source |
      |------|--------|--------|
      ```
   b. **Procedure emergence**: If 2+ episodes describe same multi-step process:
      ```markdown
      ---
      type: procedure
      created: "YYYY-MM-DD"
      source_episodes: []
      tags: []
      ---
      ## {Procedure Name}

      ### When to Use
      {Trigger conditions}

      ### Steps
      1. ...
      ```
4. Mark source episodes as `consolidated: true`
5. Update MEMORY.md index (add topics/procedures, remove consolidated episodes)
6. If MEMORY.md still > 200 lines → chain to `memory.forget`

**Artifact**: `memory/topics/*.md` and/or `memory/procedures/*.md`
**Token**: ~2-4K

---

## memory.forget

**Trigger**: Capacity pressure or stale content cleanup.

**Initiation**:
- After `memory.consolidate` if still over capacity
- MEMORY.md > 200 lines

**Process**:
1. Identify candidates using `config.yaml § memory.forget`:
   - Episodes older than `stale_episode_days` (default 7) with no retrievals
   - Topics older than `stale_topic_days` (default 90) with no recent access
   - Consolidated episodes with importance < 7
   - Superseded decisions
2. **Never forget** types listed in `config.yaml § memory.forget.protected_types` (default: architectural_decision, key_finding, active_hypothesis)
3. Delete or archive candidates
4. Update MEMORY.md: remove entries from index

**Token**: ~1K

---

## Episode Numbering

Episodes: `YYYY-MM-DD-NNN` where NNN is zero-padded sequence within the day (001, 002, ...).

## MEMORY.md Line Budget

200-line hard limit forces consolidation. Approximate budget:
- Header + Active Context: ~5 lines
- Topic Index: ~45 lines (15 topics × 3 lines)
- Recent Episodes: ~30 lines (10 episodes × 3 lines)
- Procedure Index: ~30 lines (10 procedures × 3 lines)
- Overhead: ~15 lines
- **Headroom**: ~75 lines for growth before consolidation pressure
