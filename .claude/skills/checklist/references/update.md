# checklist.update

**Trigger**: After any skill completes that produces an artifact, after `writing.draft` / `writing.review` completes, or when the user reports completing something.

## Process

### Step 1 — Identify affected items

From the skill output or user report, determine:
- Which checklist item(s) are affected (match by description, artifact path, or category)
- Whether new items need to be added (new work discovered during execution)

### Step 2 — Mark completed items

For each affected item:
- `[ ]` -> `[x]` if the work is reported done
- Add artifact path if not already present: `-- {path}`
- Add timestamp comment: `<!-- completed {YYYY-MM-DD} -->`

**Only edit the item's own file** (L2 or the L1 where the leaf lives). Do NOT propagate counts upward here — see deferred propagation note below.

### Step 3 — Add new items

If the skill discovered new work needed:
- Add new `[ ]` items in the appropriate L1 section or L2 file
- If a new task needs decomposition, trigger `checklist.create` for it

### Step 4 — Update timestamps

- Each modified file gets its `Updated:` timestamp refreshed
- Add change annotation where significant:
  ```markdown
  <!-- change {YYYY-MM-DD}: {what changed and why} -->
  ```

### Step 5 — Output

```
[CHECKLIST] Updated: +{N_added} items, {N_completed} marked [x], ~{N_modified} modified
  Completed:
  - {item description}
  New items:
  - {item description}
  (Branch counts deferred — will recompute at next status check or session.close)
```

> **Deferred count propagation**: Branch counts `[M/N]` in L1/L0 are caches.
> They are recomputed by `checklist.status` or at `session.close`. Direct item
> updates (`[x]`) only edit the item's own file. This avoids cascading file
> writes on every small completion and keeps the update operation fast (1-2 file
> writes instead of 3).

## Suggested Next

- New items added -> `checklist.verify` on existing `[x]` items
