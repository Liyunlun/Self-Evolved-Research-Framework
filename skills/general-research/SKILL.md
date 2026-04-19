---
name: general-research
description: Context-aware fallback for research-adjacent requests that don't fit a more specific skill. Leverages config.yaml, methodology/, logs/, and resources/papers/ to respond with project awareness and, where appropriate, suggest the right specialized skill.
---

# general-research

**Trigger**: Fallback — anything research-related not caught by other micro-skills.

**Process**:
1. Respond to user's request with full project context awareness
2. Leverage knowledge of:
   - Current project state (config.yaml)
   - Research direction (methodology/)
   - Recent progress (logs/)
   - Paper reading history (resources/papers/)
3. If the response involves research artifacts, suggest the appropriate specialized micro-skill
4. This is NOT a dumb fallback — it's a context-aware general assistant

**Inputs**: User's request + project context
**Outputs**: Context-aware response
**Token**: varies
**Composition**: May suggest specialized micro-skills when relevant
