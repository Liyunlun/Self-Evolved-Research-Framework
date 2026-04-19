# /memory — Persistent Knowledge Management

When to use this skill:
- After any skill produces an insight worth remembering
- Before any skill that needs prior context or decisions
- At session boundaries (open/close) for context continuity
- When memory storage exceeds capacity limits
- "Remember this", "what did we decide about X?"

## Tier Structure

| Tier | Purpose | Max Files | Retention |
|------|---------|-----------|-----------|
| `episodes/` | Recent observations | 20 | 7 days |
| `topics/` | Consolidated knowledge | 50 | 90 days |
| `procedures/` | Stable processes | 100 | permanent |

Episode files use `YYYY-MM-DD-NNN` numbering (e.g., `2026-03-30-001.md`).
`MEMORY.md` line budget: ~200 lines. Flag when exceeding 180 lines.

## memory.write

**Trigger**: After any insight-producing skill execution, or when user says "remember this", "save this", "note that".

### Process
1. Read `memory/MEMORY.md` to understand current state and avoid duplicates
2. Assess importance on a 1-10 scale using thresholds from `config.yaml` section `memory.write`:
   - 1-3: Trivial, skip unless explicitly requested
   - 4-6: Useful context, write as episode
   - 7-9: Important insight or decision, write and flag for consolidation
   - 10: Critical (architectural decision, key finding), write with protection
3. Check for duplicates — if a substantially similar episode exists, update rather than create new
4. Write episode to `memory/episodes/YYYY-MM-DD-NNN.md` with YAML frontmatter:
   ```yaml
   ---
   type: episode
   date: YYYY-MM-DD
   source_skill: {skill that produced this}
   importance: {1-10}
   tags: [tag1, tag2]
   consolidated: false
   ---
   ```
5. Update `memory/MEMORY.md` index with a one-line reference to the new episode
6. If `MEMORY.md` exceeds 180 lines, flag for consolidation

### Suggested Next
- Episode count exceeds threshold (15+ unconsolidated): `memory.consolidate`

## memory.retrieve

**Trigger**: Before any knowledge-dependent skill, at `session.open`, or when user asks about prior work/decisions.

### Process
1. Determine query from the calling context (skill name, user question, topic keywords)
2. Read `memory/MEMORY.md` to get the full index
3. Score each entry using weights from `config.yaml` section `memory.retrieve.weights`:
   | Factor | Weight | Description |
   |--------|--------|-------------|
   | `tag_overlap` | 0.4 | How many tags match the query context |
   | `keyword_match` | 0.3 | Keyword similarity between query and entry |
   | `recency` | 0.15 | How recent the entry is |
   | `importance` | 0.15 | The stored importance score |
4. Select top candidates by composite score
5. Read full files for the top 3 candidates
6. Surface retrieved content into the active context for the calling skill

### Suggested Next
- Provides context for whatever skill triggered the retrieval

## memory.consolidate

**Trigger**: At `session.close`, when `MEMORY.md` exceeds 180 lines, or when there are 15+ unconsolidated episodes.

### Process
1. Read all unconsolidated episodes (frontmatter `consolidated: false`)
2. Cluster episodes by:
   - Tag overlap
   - Source skill similarity
   - Temporal proximity (episodes from same session or adjacent days)
3. For clusters of 3+ episodes:
   - **Topic emergence**: Synthesize into `memory/topics/{topic-slug}.md` — a consolidated summary preserving key insights, decisions, and references from all source episodes
   - **Procedure emergence**: If the cluster describes a repeatable process, write to `memory/procedures/{procedure-slug}.md`
4. Mark all source episodes as `consolidated: true` in their frontmatter
5. Update `memory/MEMORY.md`:
   - Replace individual episode references with topic/procedure references
   - Ensure index stays within ~200 line budget

### Suggested Next
- If `MEMORY.md` still exceeds 200 lines after consolidation: `memory.forget`

## memory.forget

**Trigger**: Capacity pressure — after `memory.consolidate` if storage is still over limits.

### Process
1. Identify deletion candidates:
   - Episodes older than 7 days with zero retrievals since creation
   - Topics older than 90 days with no access in that period
   - Consolidated episodes with importance < 7 (their content lives in topics now)
2. **NEVER forget protected types** (defined in `config.yaml`):
   - `architectural_decision`
   - `key_finding`
   - `active_hypothesis`
3. Delete or archive identified candidates
4. Update `memory/MEMORY.md` to remove references to deleted entries

### Suggested Next
- Terminal — memory.forget is a cleanup operation with no further chain
