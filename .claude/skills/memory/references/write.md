# memory.write

**Trigger**: After any insight-producing skill execution, or when user says "remember this", "save this", "note that".

## Process

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

## Suggested Next

- Episode count exceeds threshold (15+ unconsolidated): `memory.consolidate`
