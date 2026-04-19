---
name: paper-index
description: List the project's paper reading history organized by relevance, topic tag, and read/unread status, and flag gaps relative to the project methodology. Triggers on "what papers have I read", "show my reading list", "which papers do we have on X".
---

# paper-index

**Trigger**: User asks about reading list, what papers exist, or "what have I read".

**Process**:
1. Read `resources/papers/README.md` and scan `resources/papers/*.md` files
2. Output organized index:
   - By relevance (high/medium/low)
   - By topic tag
   - Unread vs. read status
3. Suggest gaps in reading based on project methodology

**Inputs**: `resources/papers/*.md` directory
**Outputs**: Index (inline)
**Token**: ~1-2K
**Composition**: May suggest `paper-read` for unread high-relevance papers
