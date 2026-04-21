## general.research

**Trigger**: Fallback — any user request not matched by a specialized skill.

### Process
1. Respond with full project context awareness:
   - Load `config.yaml` for project scope and methodology
   - Reference relevant `memory/` entries
   - Consider `logs/digest/` for recent session context
   - Check `papers/` for literature if relevant
2. If the response involves research artifacts (writing, proofs, experiments, ideas), suggest the appropriate specialized skill rather than handling it inline
3. Act as a context-aware general assistant — not a dumb fallback. Use all available project knowledge to give informed responses.

### Suggested Next
- May suggest specialized skills when the request touches their domain (e.g., "This looks like a proof task — want me to run `proof.sketch`?")
