---
name: checklist-create
description: Add a new task to the project checklist tree — auto-classify term (short/mid/long) and category (idea/method/experiment/paper), then produce a leaf item or a branch with an L2 sub-checklist (8-part audit template for papers). Triggers on "add a task for X", "track Y as a goal", "create a checklist for the NeurIPS paper".
---

# checklist-create

**Trigger**: User wants to add a new task/goal to the project, OR a skill completes and needs to register its output as a tracked item.

**Shared context**: Before running this skill, Read `skills/_shared/checklist-engine.md` for the tree structure, marker vocabulary, and L2 category templates (including the full 8-part paper audit template).

**Process**:

## Step 1 — Classify the item

Determine two properties:
1. **Term**: `short-term` (days–1 week), `mid-term` (weeks–1 month), `long-term` (months+)
2. **Category**: `idea`, `method`, `experiment`, `paper`

If the user does not specify, infer from context:
- "run this experiment" → short-term / experiment
- "write the NeurIPS paper" → mid-term / paper
- "explore whether X is feasible" → short-term / idea
- "develop a new algorithm for Y" → mid-term / method

## Step 2 — LEAF or BRANCH fast-path decision

Determine whether this task is **simple** (no sub-steps needed) or **complex** (needs decomposition):

- **LEAF fast-path** — the task is atomic (single action, single deliverable): skip to **Step 2L**. Completes in 3 steps and 2 file writes.
- **BRANCH path** — the task needs decomposition: continue to **Step 2B**. Full 6-step process.

---

### LEAF fast-path (Steps 2L → 4L)

#### Step 2L — Append leaf item to L1

Add the item to `checklists/{term}.md` under the appropriate `## {Category}` section:
```markdown
- [ ] {description} — `{artifact_path}`  <!-- added {YYYY-MM-DD} -->
```

#### Step 3L — Update L0 root count

In `Checklist.md`:
- Recompute the `[{done}/{total}]` count for the affected term
- Update the `Updated:` timestamp

#### Step 4L — Output

```
[CHECKLIST] Created: leaf in {term}/{category}
  "{description}"
  Progress: {term} [{done}/{total}] | Root [{done}/{total} phases]
```

**Done.** (3 steps, 2 file writes: L1 + L0)

---

### BRANCH path (Steps 2B → 7B)

#### Step 2B — Add branch item to L1

Add the branch item to `checklists/{term}.md` under the appropriate `## {Category}` section:
```markdown
- [0/N] {description} → checklists/{term}/{category}-{slug}.md  <!-- added {YYYY-MM-DD} -->
```

#### Step 3B — Create L2 file

Create `checklists/{term}/{category}-{slug}.md` using the appropriate template from
`skills/_shared/checklist-engine.md § L2 Category Templates`. For `category=paper`, use the
full 8-part audit template in `skills/_shared/checklist-engine.md § Paper Audit Template (L2)`.

#### Step 4B — Update L1 completion count

In `checklists/{term}.md`, under the appropriate `## {Category}` section:
- Recompute the header count: `Updated: {YYYY-MM-DD} | Status: [{done}/{total}]`

#### Step 5B — Update L0 root

In `Checklist.md`:
- Recompute the `[{done}/{total}]` count for the affected term
- Update the `Updated:` timestamp

#### Step 6B — Output

```
[CHECKLIST] Created: branch in {term}/{category}
  "{description}"
  L2 file at checklists/{term}/{category}-{slug}.md with {N} items
  Progress: {term} [{done}/{total}] | Root [{done}/{total} phases]
```

**Inputs**: User request or skill output describing the task
**Outputs**: Updated L0 + L1 files, optionally new L2 file
**Token**: ~2K (leaf) / ~3-5K (branch)
**Composition**: Always → `memory-write` (log creation)
