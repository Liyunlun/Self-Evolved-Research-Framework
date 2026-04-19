---
name: checklist-status
description: Read the checklist tree, recompute cached branch counts, and produce per-term + per-category progress stats plus priorities ([U] blocked first, then short-term [ ]). Also emits a one-line condensed form for the session-open banner. Triggers on "project status", "what's done", "progress report".
---

# checklist-status

**Trigger**: User asks "project status", "what's done", "where are we", "progress report", or at session-open for the banner.

**Shared context**: Before running this skill, Read `skills/_shared/checklist-engine.md` for the tree structure and marker semantics.

**Process**:

## Step 1 — Read the tree

Read `Checklist.md` (L0). For each term, read the L1 file. Do NOT read L2 files unless the user asks for detail on a specific task.

## Step 1.5 — Recount branch caches

Because `checklist-update` defers count propagation, cached `[M/N]` counts in L1 and L0 may be stale. Recompute them now:

1. For each **branch item** in L1 files: read its linked L2 file header, count items by status (`[x]`, `[v]`, `[U]` = done; `[ ]` = not done), and update the branch's `[M/N]` display in the L1 file.
2. For each **L1 file**: recount all items (leaf + branch) and update the L1 header `Status: [{done}/{total}]`.
3. Update **L0 root** (`Checklist.md`): recompute `[{done}/{total}]` for each term from the L1 headers. Update timestamps.
4. Write back any files whose counts changed.

This step ensures all counts are authoritative before reporting.

## Step 2 — Compute summary statistics

For each term (short/mid/long) and each category (idea/method/experiment/paper):

| Metric | How |
|--------|-----|
| Total items | Count all leaf + branch items |
| Done | Count `[x]` + `[v]` + `[U]` |
| Verified | Count `[v]` only |
| Blocked | Count `[U]` only |
| Not started | Count `[ ]` only |

## Step 3 — Identify priorities

From the checklist tree:
1. Items marked `[U]` (blocked) — highest priority to unblock
2. Items in `short-term` with `[ ]` — should be started soon
3. Branch items with low completion ratio — may need attention
4. Items approaching deadlines (if annotated)

## Step 4 — Output

```
[STATUS] Project Progress
  Short-term: [{done}/{total}] — {1-line summary of what's active}
  Mid-term:   [{done}/{total}] — {1-line summary}
  Long-term:  [{done}/{total}] — {1-line summary}

  By category:
  | Category    | [ ] | [x] | [v] | [U] | Total |
  |-------------|-----|-----|-----|-----|-------|
  | Ideas       |     |     |     |     |       |
  | Methods     |     |     |     |     |       |
  | Experiments |     |     |     |     |       |
  | Papers      |     |     |     |     |       |

  Priorities:
  1. {highest priority item}
  2. {next}
  3. {next}
```

For session-open banner integration, output a condensed single line:
```
[CKL] {total_done}/{total_all} items | {N_blocked} blocked | Next: {top priority}
```

**Inputs**: Checklist tree (L0 + L1, optionally L2)
**Outputs**: Progress report (inline)
**Token**: ~2-4K
