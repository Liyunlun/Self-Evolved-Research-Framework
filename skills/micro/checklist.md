# Checklist Engine — Hierarchical Project Tracking

> The checklist engine is the single source of truth for project progress.
> It manages a 3-layer tree (L0 root, L1 term checklists, L2 task checklists)
> and provides create/verify/update/status operations over that tree.
>
> The engine is generic: it tracks ideas, methods, experiments, and papers.
> Paper-specific tasks get an L2 checklist using the 8-part audit template
> defined at the bottom of this file.

---

## Tree Structure

```
Checklist.md                          ← L0 root (project root)
├── checklists/short-term.md          ← L1 (4 categories each)
│   ├── checklists/short-term/idea-{slug}.md    ← L2 (on demand)
│   ├── checklists/short-term/method-{slug}.md
│   ├── checklists/short-term/experiment-{slug}.md
│   └── checklists/short-term/paper-{slug}.md   ← uses 8-part audit template
├── checklists/mid-term.md
│   └── checklists/mid-term/{category}-{slug}.md
└── checklists/long-term.md
    └── checklists/long-term/{category}-{slug}.md
```

### Item Types

- **Leaf**: A single checkable item. Has one status marker.
  ```
  - [x] Run ablation study on learning rate — `experiments/lr_ablation/`
  ```
- **Branch**: Links to a sub-checklist. Status auto-computed from children.
  ```
  - [3/7] NeurIPS 2025 paper audit → checklists/mid-term/paper-neurips25.md
  ```

### 4-Stage Verification Markers

| Marker | Meaning | Who sets it |
|--------|---------|-------------|
| `[ ]`  | **Not started** — work not yet done | Default |
| `[x]`  | **Done** — self-reported complete, not yet verified | Author / skill |
| `[v]`  | **Verified** — evidence checked by Claude or script | `checklist.verify` |
| `[U]`  | **Blocked / unable to complete** — needs intervention | Author / skill |

**Flag markers** (for items needing flagging rather than checking):
- `**NO**` — condition explicitly not met
- `**YES**` — a problem condition is true
- `**INCOMPLETE**` — partial work exists

### Categories

Each L1 checklist has four sections:

| Category | Typical L2 template | Examples |
|----------|-------------------|----------|
| **Ideas** | Simple checklist | Literature check, novelty assessment, feasibility |
| **Methods** | Design checklist | Formalization, implementation, validation |
| **Experiments** | Pipeline checklist | Setup, run, analyze, verify |
| **Papers** | 8-part audit (see template below) | Full paper submission audit |

---

## checklist.create

**Trigger**: User wants to add a new task/goal to the project, OR a skill completes and needs to register its output as a tracked item.

**Process**:

### Step 1 — Classify the item

Determine two properties:
1. **Term**: `short-term` (days–1 week), `mid-term` (weeks–1 month), `long-term` (months+)
2. **Category**: `idea`, `method`, `experiment`, `paper`

If the user does not specify, infer from context:
- "run this experiment" → short-term / experiment
- "write the NeurIPS paper" → mid-term / paper
- "explore whether X is feasible" → short-term / idea
- "develop a new algorithm for Y" → mid-term / method

### Step 2 — Determine leaf vs. branch

**Add as leaf** if the task is atomic (single action, single deliverable):
```markdown
- [ ] {description} — `{artifact_path}`  <!-- added {YYYY-MM-DD} -->
```

**Add as branch** if the task needs decomposition (multiple steps, sub-deliverables):
```markdown
- [0/N] {description} → checklists/{term}/{category}-{slug}.md  <!-- added {YYYY-MM-DD} -->
```

### Step 3 — Create L2 file (branch items only)

Create `checklists/{term}/{category}-{slug}.md` using the appropriate template:

**idea template**:
```markdown
# Idea: {Title}

Parent: checklists/{term}.md § Ideas | Created: {YYYY-MM-DD}

## Checklist

- [ ] Literature search — are there existing approaches?
- [ ] Novelty assessment — what is genuinely new?
- [ ] Feasibility check — can this be done with available resources?
- [ ] Write up 1-paragraph summary in `methodology/ideas/{slug}.md`
- [ ] Decision: pursue / park / abandon

## Notes

{Space for free-form notes during exploration}
```

**method template**:
```markdown
# Method: {Title}

Parent: checklists/{term}.md § Methods | Created: {YYYY-MM-DD}

## Checklist

- [ ] Formal problem statement
- [ ] Algorithm design / pseudocode
- [ ] Theoretical analysis (if applicable)
- [ ] Implementation — `{expected_code_path}`
- [ ] Unit tests
- [ ] Validation on toy problem
- [ ] Integration with experiment pipeline

## Design Decisions

| Decision | Options | Chosen | Rationale | Date |
|----------|---------|--------|-----------|------|
```

**experiment template**:
```markdown
# Experiment: {Title}

Parent: checklists/{term}.md § Experiments | Created: {YYYY-MM-DD}

## Pipeline

- [ ] **Setup**: Config, data preparation, environment
- [ ] **Implementation**: Script/code ready to run
- [ ] **Run**: Execute on cluster — `{expected_log_path}`
- [ ] **Analyze**: Process results, generate figures
- [ ] **Verify**: Numbers match claims, results reproducible

## Config

| Parameter | Value |
|-----------|-------|

## Results

{Populated after experiment completes}
```

**paper template**: Use the **Paper Audit Template (L2)** defined at the bottom of this file. This produces the full 8-part structure.

### Step 4 — Update L1 completion count

In `checklists/{term}.md`, under the appropriate `## {Category}` section:
- Add the new leaf or branch item
- Recompute the header count: `Updated: {YYYY-MM-DD} | Status: [{done}/{total}]`

### Step 5 — Update L0 root

In `Checklist.md`:
- Recompute the `[{done}/{total}]` count for the affected term
- Update the `Updated:` timestamp

### Step 6 — Output

```
[CHECKLIST] Created: {leaf|branch} in {term}/{category}
  "{description}"
  {If branch: L2 file at checklists/{term}/{category}-{slug}.md with {N} items}
  Progress: {term} [{done}/{total}] | Root [{done}/{total} phases]
```

**Inputs**: User request or skill output describing the task
**Outputs**: Updated L0 + L1 files, optionally new L2 file
**Token**: ~3-5K

---

## checklist.verify

**Trigger**: User asks to "verify the checklist", "run verification", "check what's done", or at project milestones (pre-submission, phase transitions).

**Process**:

### Step 1 — Walk the tree

Starting from `Checklist.md` (L0), traverse all L1 and L2 checklists. Build a flat list of all items with their current markers.

### Step 2 — Verify each `[x]` item

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

### Step 3 — Promote verified items

- `[x]` with all checks passing → `[v]`
- `[x]` with any check failing → stays `[x]`, flag added
- `[ ]` items are skipped (not yet claimed done)
- `[v]` and `[U]` are never downgraded

### Step 4 — Recompute branch counts

For every branch item `[M/N]`:
- Recount from children: count items that are `[x]`, `[v]`, or `[U]` as "done"
- Update the branch display: `[{new_done}/{new_total}]`
- Propagate up: L2 → L1 → L0

### Step 5 — Update files and report

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
- Always → chain to `memory.write` (record verification results)

---

## checklist.update

**Trigger**: After any skill completes that produces an artifact, after `writing.draft` / `writing.review` completes, or when the user reports completing something.

**Process**:

### Step 1 — Identify affected items

From the skill output or user report, determine:
- Which checklist item(s) are affected (match by description, artifact path, or category)
- Whether new items need to be added (new work discovered during execution)

### Step 2 — Mark completed items

For each affected item:
- `[ ]` → `[x]` if the work is reported done
- Add artifact path if not already present: `— {path}`
- Add timestamp comment: `<!-- completed {YYYY-MM-DD} -->`

### Step 3 — Add new items

If the skill discovered new work needed:
- Add new `[ ]` items in the appropriate L1 section or L2 file
- If a new task needs decomposition, trigger `checklist.create` for it

### Step 4 — Recompute branch counts

Walk up from modified items:
- Recount each branch `[M/N]` from its children
- Update L1 header counts
- Update L0 root counts

### Step 5 — Update timestamps

- Each modified file gets its `Updated:` timestamp refreshed
- Add change annotation where significant:
  ```markdown
  <!-- change {YYYY-MM-DD}: {what changed and why} -->
  ```

### Step 6 — Output

```
[CHECKLIST] Updated: +{N_added} items, {N_completed} marked [x], ~{N_modified} modified
  Completed:
  - {item description}
  New items:
  - {item description}
  Progress: {affected_term} [{done}/{total}]
```

**Inputs**: Skill output or user report + existing checklist tree
**Outputs**: Updated checklist files + change summary (inline)
**Token**: ~2-4K
**Composition**: After update with new items → suggest `checklist.verify` on existing `[x]` items

---

## checklist.status

**Trigger**: User asks "project status", "what's done", "where are we", "progress report", or at session.open for the banner.

**Process**:

### Step 1 — Read the tree

Read `Checklist.md` (L0). For each term, read the L1 file. Do NOT read L2 files unless the user asks for detail on a specific task.

### Step 2 — Compute summary statistics

For each term (short/mid/long) and each category (idea/method/experiment/paper):

| Metric | How |
|--------|-----|
| Total items | Count all leaf + branch items |
| Done | Count `[x]` + `[v]` + `[U]` |
| Verified | Count `[v]` only |
| Blocked | Count `[U]` only |
| Not started | Count `[ ]` only |

### Step 3 — Identify priorities

From the checklist tree:
1. Items marked `[U]` (blocked) — highest priority to unblock
2. Items in `short-term` with `[ ]` — should be started soon
3. Branch items with low completion ratio — may need attention
4. Items approaching deadlines (if annotated)

### Step 4 — Output

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

For session.open banner integration, output a condensed single line:
```
[CKL] {total_done}/{total_all} items | {N_blocked} blocked | Next: {top priority}
```

**Inputs**: Checklist tree (L0 + L1, optionally L2)
**Outputs**: Progress report (inline)
**Token**: ~2-4K

---

## Design Principles

1. **Every claim links to evidence**: No item exists without a path to its artifact. The chain: task → artifact → verification is always traceable.
2. **Bidirectional traceability**: L2 checklists link up to their L1 parent. L1 branch items link down to their L2 file. Any item can be traced in either direction.
3. **Incremental maintenance**: The checklist tree is a living structure. `checklist.update` keeps it synchronized with evolving work without regenerating from scratch. Change annotations preserve edit history.
4. **Four-stage verification**: `[ ]` → `[x]` (author marks done) → `[v]` (Claude/script verifies) → `[U]` (blocked/unable). This prevents "checked my own homework" blindness.
5. **Separation of concerns**: Checklists track status only. Actual artifacts (drafts, results, proofs, code) live in their own directories. Checklists point to artifacts via paths, never duplicate content.
6. **Branch completion propagates**: Completing a child item automatically updates the parent branch count, all the way to the root. No manual count maintenance.
7. **Category-specific templates**: Each category (idea/method/experiment/paper) has a purpose-built L2 template. Paper tasks get the full 8-part audit. Experiments get a pipeline checklist. This ensures nothing is missed for the task type.
8. **Comment-driven discovery**: `<!-- TODO: ... -->` and `<!-- MISSING: ... -->` comments in checklist files surface issues without breaking the checklist format.

---

## Composition Rules

| After Skill A Completes | Condition | Chain to |
|------------------------|-----------|----------|
| ANY skill that produces an artifact | Always | → `checklist.update` |
| `session.open` | Always | → read `Checklist.md` for banner (via `checklist.status` condensed) |
| `plan.suggest` | Always (needs context) | ← read checklist tree to find `[ ]` items, prioritize |
| `progress.capture` | Always | → `checklist.update` to mark items `[x]` |
| `experiment.run` | Launch successful | → `checklist.update` (mark setup items `[x]`) |
| `experiment.analyze` | Results captured | → `checklist.update` + `checklist.verify` |
| `writing.draft` | Section complete | → `checklist.update` |
| `writing.review` | Review complete | → `checklist.update` |
| `theory.formalize` | Theorem formalized | → `checklist.update` |
| `proof.critique` | Critique complete | → `checklist.update` |
| `idea.discover` | Ideas generated | → `checklist.create` (add to short-term/ideas) |
| `idea.verify` | Novelty confirmed | → `checklist.update` (mark verification `[x]`) |
| `checklist.create` | Paper category | → use 8-part paper audit template for L2 |
| `checklist.create` | Always | → `memory.write` (log creation) |
| `checklist.verify` | Issues found | → surface issues, suggest fixes |
| `checklist.verify` | Always | → `memory.write` (record verification) |
| `checklist.update` | New items added | → `checklist.verify` on existing `[x]` items |

---

## Paper Audit Template (L2)

> This is the template used when `checklist.create` is called with `category=paper`.
> It produces a comprehensive 8-part audit checklist for paper submission readiness.
> The L2 file is created at `checklists/{term}/paper-{slug}.md`.

### Template Header

```markdown
# Paper Audit: {Title}

Parent: checklists/{term}.md § Papers | Created: {YYYY-MM-DD}
Source: `{tex_file_path}` | Last updated: {YYYY-MM-DD}
Status: [{done}/{total}]
```

### Generation Process

When creating a paper audit L2 checklist:

1. **Gather sources**: Read the paper `.tex` file(s), scan `experiments/` for code/configs/results, scan `paper/figures/` for figures, execute `memory.retrieve` for past decisions.

2. **Extract paper structure**: Parse tex into a structured inventory:
   - **Formal statements**: definitions, propositions, theorems, corollaries, lemmas, assumptions — extract names, labels, tex line ranges, proof blocks
   - **Empirical claims**: grep for numerical values in running text — record tex line and claimed value
   - **Figures and tables**: extract `\label`, `\ref`, `\includegraphics` paths, `\caption` text
   - **Sections**: map section hierarchy with tex line ranges

3. **Generate all 8 parts** (defined below), applying status markers.

4. **Apply initial status markers**:
   - File exists at referenced path → `[x]`
   - No evidence found → `[ ]`
   - Add `<!-- TODO: ... -->` for items needing human attention
   - Add `<!-- comment: ... -->` for contextual notes

---

### PART I: THEORY & PROOFS

One subsection per formal statement. Section header format:
```markdown
## 1.N {Type} {N} — {Name} (tex L{start}–{end}) [optional flags]
```

Optional flags in header (bold, after `—`):
- `— **INCOMPLETE, {reason}**` for statements with known issues
- `— DOWNGRADED from {original type}` for reclassified statements
- `— **DEPENDS ON {other statement}**` for dependency chains

Each subsection contains:

1. **Status table** (mandatory):
   ```markdown
   | Item | Status | Detail |
   |------|--------|--------|
   | Statement well-formed | [x] | {describe key mathematical content} |
   | Proof provided | [x] | {inline/appendix, tex location, proof technique} |
   | Proof verified | [ ] | <!-- TODO: formal proof-check pass needed --> |
   | Consistency with experiments | [x] | {which experiment validates this, with § cross-ref} |
   | All references correct | [x] | {label name, count of \ref uses} |
   ```

   For items requiring **flagging rather than checking**, use bold markers:
   - `**NO**` — explicitly not satisfied (e.g., "Empirically validated | **NO**")
   - `**YES**` — a problem condition is true (e.g., "Too strong | **YES**")

2. **Change log** (when applicable):
   ```markdown
   **Change ({date}):** {Description of what changed, why, and what was updated}
   ```

3. **Issue analysis** (when problems are identified):
   ```markdown
   **Issue ({date}):** {Description of the problem}

   **Options for resolution:**
   | Option | Description | Difficulty | Status |
   |--------|-------------|------------|--------|
   | (a) {name} | {description} | {Easy/Medium/Hard} | [ ] Not started |
   ```

4. **Key insights** (when the analysis reveals something non-obvious):
   ```markdown
   **Key insight:** {What the paper has but underemphasizes, or a reframing}
   ```

5. **Background notes** (for statements requiring domain context):
   ```markdown
   **Background:** {Relevant mathematical/domain context for the reader}
   ```

---

### PART II: EMPIRICAL CLAIMS & EVIDENCE

One subsection per claim or experiment. For complex experiments, expand with sub-subsections.

Basic claim format:
```markdown
## 2.N Claim: "{claim text}" (tex L{start}–{end})

| Item | Status | Evidence |
|------|--------|----------|
| {Specific subclaim} | [x] | {How verified — cross-ref to data, figure} |
| **Data** | [x] | `{path/to/results.csv}` |
| **Script** | [x] | `{path/to/analysis.py}` |
| **Figure** | [x] | `{path/to/figure.png}` |
```

Complex experiment format (for major experimental setups):
```markdown
## 2.N {Experiment Name} — Setup

| Item | Status | Code | Data |
|------|--------|------|------|
| {Design element} | [x] | `{script}` | {data location or —} |

### 2.N.1 Detailed Experimental Pipeline ({M} steps)

**Step 1 — {Name}** (`{script}`)
{Description of what this step does, including key code snippets:}
```python
# Key implementation detail (not full code — just the critical logic)
result = critical_operation(params)
```

### 2.N.2 Experimental Design Rationale
| Design choice | Why |
|---------------|-----|
| {choice} | {justification — isolation, fairness, matching theory} |
```

**Experiment evolution tracking** — when experiments are redesigned:
```markdown
## 2.N {Experiment Name} — BEING REDESIGNED

**Decision ({date}):** {Why the redesign is happening. What replaces what.}

### 2.Na Existing Experiment (may move to appendix)
{old experiment items — kept for reference}

### 2.Nb New Experiment — TODO
| # | Design proposal | Status | Priority | Detail |
|---|----------------|--------|----------|--------|
| P1 | **{proposal}** | [ ] | **CRITICAL** | {description} |
```

Cross-reference empirical validation back to theory: use `See §1.N` links.

---

### PART III: FIGURES & TABLES

Three subsections:

```markdown
## 3.1 Main Paper Figures
| Fig | Tex ref | Description | Status | Paper file | Script | Data |
|-----|---------|-------------|--------|------------|--------|------|

## 3.2 Tables
| Table | Tex ref | Description | Status | Data source |
|-------|---------|-------------|--------|-------------|

## 3.3 Appendix / Supplementary Figures
| Figure | Status | Script | Data |
|--------|--------|--------|------|

## 3.4 Figure Provenance (paper/figures/ ← source)
| Submission file | Source file |
|-----------------|-------------|
```

Every figure in the submission directory must have a provenance entry. Flag missing entries.

---

### PART IV: PAPER SECTIONS

One subsection per major section. For **key sections** (intro, methods, experiments), include paragraph-level structure analysis:

```markdown
## 4.N {Section Name} — {status flag if applicable}

**Structure ({M} paragraphs):**
| # | Paragraph | Purpose | Status |
|---|-----------|---------|--------|
| 1 | {topic} | {what it does for the reader} | [x] |

| Item | Status | Detail |
|------|--------|--------|
| {Content element} | [x] | {description} |

**TODOs ({date}) — gaps flagged in tex:**
| # | Gap | What to add | Status |
|---|-----|-------------|--------|
```

For **revised sections**, include before/after comparison:
```markdown
**Key differences from previous version:**
| Aspect | Before | After |
|--------|--------|-------|
```

---

### PART V: BLOCKING ACTIONS

Three subsections with **priority levels** (CRITICAL > HIGH > MED > LOW):

```markdown
## 5.1 Verification Pass (run scripts, fill [ ] → [v])
| # | Action | Status | Script | Priority |
|---|--------|--------|--------|----------|

## 5.2 Missing Experiments
| # | Experiment | Status | Priority | Expert consensus | Code |
|---|-----------|--------|----------|-----------------|------|

## 5.3 Paper Writing
| # | Action | Status | Priority |
|---|--------|--------|----------|
```

Mark superseded items with `~~strikethrough~~` and replacement reference.
Add `<!-- comment: {rationale} -->` for priority decisions.

---

### PART VI: RAW DATA INVENTORY

```markdown
| Data file | Location | Contents |
|-----------|----------|----------|
```

---

### PART VII: CODE INDEX

Bidirectional: every script maps to the claims it supports.

```markdown
| File | Purpose | Used by claims |
|------|---------|----------------|
| `{path}` | {what it does} | §{N.M}, §{N.M} |
```

---

### PART VIII: COMMENT LOG

Collect all `<!-- TODO: ... -->` and `<!-- comment: ... -->` from the entire checklist.

```markdown
| Date | Location | Comment | Action needed? |
|------|----------|---------|----------------|
| {date} | §{N.M} | {comment text} | YES → {blocking action ref} / No ({reason}) |
```
