---
name: meta
description: Session lifecycle management, self-evolution, and general system operations
---

# /meta — Router

Choose the sub-skill that best matches the user intent:

- **Session initialization** (conversation start, loading context and config) — read `references/session-open.md` and follow its instructions
- **Session closing** (conversation end, persisting logs, memory, and evolution) — read `references/session-close.md` and follow its instructions
- **Evolution proposal** (aggregating observations, proposing spec edits) — read `references/evolve-suggest.md` and follow its instructions
- **Evolution application** (applying approved spec edit proposals) — read `references/evolve-apply.md` and follow its instructions
- **General research fallback** (any request not matched by a specialized skill) — read `references/general-research.md` and follow its instructions

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
