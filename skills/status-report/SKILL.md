---
name: status-report
description: Produce a ~15-20 line project overview with per-term checklist stats, blocking items, recent activity, key outputs, and upcoming milestones. Triggers on "where are we?", "project status", "give me an overview", "progress snapshot".
---

# status-report

**Trigger**: User asks "where are we?", "project status?", or "give me an overview".

**Process**:
1. Read: `Checklist.md` (L0) and all L1 checklists (`checklists/short-term.md`, `checklists/mid-term.md`, `checklists/long-term.md`)
2. Compute completion stats from checklist tree:
   - Per-term completion: short-term {done}/{total}, mid-term {done}/{total}, long-term {done}/{total}
   - Per-category breakdown where L2 checklists exist
3. Read: config.yaml (milestones), SUMMARY.md (recent activity)
4. Generate comprehensive status:
   - Overall checklist progress (per-term, per-category)
   - Blocking items and their dependencies
   - Recent activity (last 3-5 sessions)
   - Key research outputs produced
   - Upcoming milestones
5. Keep to ~15-20 lines

**Inputs**: Checklist.md, L1/L2 checklists, config.yaml, SUMMARY.md
**Outputs**: Status report with checklist completion stats (inline)
**Token**: ~1-2K
**Composition**: Naturally leads to `plan-suggest` if user wants next steps
