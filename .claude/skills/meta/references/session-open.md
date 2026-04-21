## session.open

**Trigger**: Every conversation start (automatic, before any other processing).

### Process
1. **Read configuration and recent history**:
   - `config.yaml` — project settings, phase, methodology
   - Most recent `logs/digest/*.yaml` — last session log
   - `logs/digest/SUMMARY.md` — running summary of all sessions
2. **Restore memory context**:
   - Read `memory/MEMORY.md`
   - Execute `memory.retrieve` for active context relevant to likely tasks
3. **Check progress**:
   - Read `Checklist.md`, compute done/total items
4. **Generate skill recommendations**:
   - Run: `~/.claude/ser/scripts/recommend.py --samples 10`
   - This produces `.claude/.ser-recommendations.json` via Thompson Sampling over skill weights
5. **Load recommendations and chains**:
   - Read `.claude/.ser-recommendations.json` (Thompson Sampling sample queues)
   - Read `~/.claude/ser/chains.yaml` (chain templates and triggers)
6. **Output status banner**:
   ```
   [SER] {project_name} | Phase {X} | [{done}/{total} items]
   Last session ({date}): {1-line summary}
   Next milestone: {goal} ({days}d)
   ```
7. **Milestone proximity check**:
   - If milestone is <= 3 days away, append: `** MILESTONE APPROACHING **`
8. Proceed to user's request

### Suggested Next
None — session.open is always the first skill executed
