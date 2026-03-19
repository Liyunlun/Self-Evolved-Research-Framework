# Checklist Engine — Scoped Context

## 3-Layer Model

- **L0** — Root `Checklist.md` in project root. Single entry point, read at every session.open.
- **L1** — Term checklists in `checklists/{short,mid,long}-term.md`. One per time horizon.
- **L2** — Task-specific checklists created on demand when a task needs decomposition.

## Item Types

- **Leaf**: A single checkable item. Has one status marker.
- **Branch**: Links to a sub-checklist. Status auto-computed from children, shown as `[3/7]`.

## 4-Stage Verification

| Marker | Meaning |
|--------|---------|
| `[ ]`  | Not started |
| `[x]`  | Done (self-reported) |
| `[v]`  | Verified (evidence checked) |
| `[U]`  | Unable to complete / blocked |

## Categories

Each L1 checklist contains four sections: **Ideas**, **Methods**, **Experiments**, **Papers**.

## Separation of Concerns

Checklists track status only. Actual artifacts (drafts, results, proofs) live in `outputs/`.

## L2 Creation

L2 checklists are created on demand via `checklist.create` when a leaf item
needs decomposition into sub-tasks. They live alongside L1 files in `checklists/`.
