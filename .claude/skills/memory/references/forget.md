# memory.forget

**Trigger**: Capacity pressure — after `memory.consolidate` if storage is still over limits.

## Process

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

## Suggested Next

- Terminal — memory.forget is a cleanup operation with no further chain
