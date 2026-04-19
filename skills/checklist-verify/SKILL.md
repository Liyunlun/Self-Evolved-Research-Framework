---
name: checklist-verify
description: Walk the full checklist tree and promote [x] items to [v] by checking artifact existence, running verification scripts, spot-checking data numbers, and validating paper cross-references. Triggers on "verify the checklist", "run verification", "check what's done", or before milestone submissions.
---

# checklist-verify

**Trigger**: User asks to "verify the checklist", "run verification", "check what's done", or at project milestones (pre-submission, phase transitions).

**Shared context**: Before running this skill, Read `skills/_shared/checklist-engine.md` for the tree structure, marker semantics, and composition rules.

**Process**:

## Step 1 — Walk the tree

Starting from `Checklist.md` (L0), traverse all L1 and L2 checklists. Build a flat list of all items with their current markers.

## Step 2 — Verify each `[x]` item

For each item marked `[x]` (done but not yet verified):

1. **Artifact path check**: If the item references a file path (after `—`), verify the file exists.
   - Exists → candidate for `[v]`
   - Missing → flag: `<!-- MISSING: {path} not found -->`

2. **Script verification**: If the item has a linked verification script, run it.
   - Passes → candidate for `[v]`
   - Fails → flag with output

3. **Data spot-check**: If the item references data with specific numbers:
   - Read the data file
   - Compute the claimed statistic
   - Compare within tolerance → `[v]`
   - Mismatch → `<!-- DISCREPANCY: claimed {X}, computed {Y} from {file} -->`

4. **Cross-reference check** (for paper L2 checklists):
   - Verify `\ref{...}` targets exist in tex
   - Verify figure paths in `\includegraphics` exist
   - Verify provenance chains (figure → script → data)

## Step 3 — Promote verified items

- `[x]` with all checks passing → `[v]`
- `[x]` with any check failing → stays `[x]`, flag added
- `[ ]` items are skipped (not yet claimed done)
- `[v]` and `[U]` are never downgraded

## Step 4 — Recompute branch counts

For every branch item `[M/N]`:
- Recount from children: count items that are `[x]`, `[v]`, or `[U]` as "done"
- Update the branch display: `[{new_done}/{new_total}]`
- Propagate up: L2 → L1 → L0

## Step 5 — Update files and report

Write back all modified checklist files. Output:

```
[VERIFY] Tree walk complete
  Total items: {N_total} | Verified: {N_v} [v] | Issues: {N_issues}
  Promoted: {list of items promoted [x]→[v]}
  Issues:
  - {path} §{item}: {description}
  Missing files:
  - {path}: referenced by {item}
```

**Inputs**: Existing checklist tree (L0 + L1 + L2 files)
**Outputs**: Updated checklist files + verification report (inline)
**Token**: ~4-10K
**Composition**:
- Issues found → surface issues, suggest fixes
- All verified → report clean status
- Always → chain to `memory-write` (record verification results)
