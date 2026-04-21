---
name: checklist
description: Hierarchical project tracking engine — create, verify, update, and report on multi-level task checklists
---

# /checklist — Hierarchical Project Tracking Engine

Route the user's request to the matching sub-skill below:

- **Create a new checklist item** — adding a task or goal, registering a skill output as a tracked item, decomposing work into sub-items: read `references/create.md` and follow its instructions.
- **Verify checklist items** — running verification passes, checking artifact existence, promoting items from done to verified: read `references/verify.md` and follow its instructions.
- **Update checklist after work** — marking items complete, adding new items discovered during execution, refreshing timestamps: read `references/update.md` and follow its instructions.
- **Report project status** — progress summary, category breakdown, priority identification, session banner: read `references/status.md` and follow its instructions.

After completing the selected workflow, return control. Do NOT chain multiple workflows — the chain system handles sequencing.
