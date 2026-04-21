# memory.consolidate

**Trigger**: At `session.close`, when `MEMORY.md` exceeds 180 lines, or when there are 15+ unconsolidated episodes.

## Process

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

## Suggested Next

- If `MEMORY.md` still exceeds 200 lines after consolidation: `memory.forget`
