# Checklist Engine — Shared Infrastructure

> Shared reference for the `checklist-*` skills. Defines the hierarchical tree,
> status markers, category templates, design principles, composition rules,
> and the 8-part paper audit template.
>
> Not a skill itself (no `SKILL.md`). Each `checklist-*/SKILL.md` directs Claude
> to read this file when a skill firing needs the shared vocabulary.

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
| `[v]`  | **Verified** — evidence checked by Claude or script | `checklist-verify` |
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

## L2 Category Templates

### Idea template
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

### Method template
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

### Experiment template
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

### Paper template

Use the **Paper Audit Template (L2)** defined at the bottom of this file. Produces the full 8-part structure.

---

## Design Principles

1. **Every claim links to evidence**: No item exists without a path to its artifact. The chain: task → artifact → verification is always traceable.
2. **Bidirectional traceability**: L2 checklists link up to their L1 parent. L1 branch items link down to their L2 file. Any item can be traced in either direction.
3. **Incremental maintenance**: The checklist tree is a living structure. `checklist-update` keeps it synchronized with evolving work without regenerating from scratch. Change annotations preserve edit history.
4. **Four-stage verification**: `[ ]` → `[x]` (author marks done) → `[v]` (Claude/script verifies) → `[U]` (blocked/unable). Prevents "checked my own homework" blindness.
5. **Separation of concerns**: Checklists track status only. Actual artifacts live in their own directories. Checklists point to artifacts via paths, never duplicate content.
6. **Branch completion propagates**: Completing a child item eventually updates the parent branch count, all the way to the root. See deferred-propagation rule in `checklist-update` / `checklist-status`.
7. **Category-specific templates**: Each category has a purpose-built L2 template. Paper tasks get the full 8-part audit. Experiments get a pipeline checklist. Ensures nothing is missed for the task type.
8. **Comment-driven discovery**: `<!-- TODO: ... -->` and `<!-- MISSING: ... -->` comments surface issues without breaking the checklist format.

---

## Composition Rules

> **Batch G2 entries**: If the same checklist skill fires N>1 times in rapid
> succession on similar inputs (e.g., marking 5 items `[x]` in a row, or
> creating 3 leaf items from a single plan-suggest output), a single G2 entry
> covering all N firings is acceptable. Note the count in the entry:
> `skill:{name} (x{N})`. This avoids N near-identical feedback entries flooding
> the TD-NL feedback log.

| After Skill A Completes | Condition | Chain to |
|------------------------|-----------|----------|
| ANY skill that produces an artifact | Always | → `checklist-update` |
| `session-open` | Always | → read `Checklist.md` for banner (via `checklist-status` condensed) |
| `plan-suggest` | Always (needs context) | ← read checklist tree to find `[ ]` items, prioritize |
| `progress-capture` | Always | → `checklist-update` to mark items `[x]` |
| `experiment-run` | Launch successful | → `checklist-update` (mark setup items `[x]`) |
| `experiment-analyze` | Results captured | → `checklist-update` + `checklist-verify` |
| `writing-draft` | Section complete | → `checklist-update` |
| `writing-review` | Review complete | → `checklist-update` |
| `theory-formalize` | Theorem formalized | → `checklist-update` |
| `proof-critique` | Critique complete | → `checklist-update` |
| `idea-discover` | Ideas generated | → `checklist-create` (add to short-term/ideas) |
| `idea-verify` | Novelty confirmed | → `checklist-update` (mark verification `[x]`) |
| `checklist-create` | Paper category | → use 8-part paper audit template for L2 |
| `checklist-create` | Always | → `memory-write` (log creation) |
| `checklist-verify` | Issues found | → surface issues, suggest fixes |
| `checklist-verify` | Always | → `memory-write` (record verification) |
| `checklist-update` | New items added | → `checklist-verify` on existing `[x]` items |

---

## Paper Audit Template (L2)

> Used when `checklist-create` is invoked with `category=paper`. Produces a
> comprehensive 8-part audit checklist for paper submission readiness.
> L2 file is created at `checklists/{term}/paper-{slug}.md`.

### Template Header

```markdown
# Paper Audit: {Title}

Parent: checklists/{term}.md § Papers | Created: {YYYY-MM-DD}
Source: `{tex_file_path}` | Last updated: {YYYY-MM-DD}
Phase: {prospective|active|pre-submission|post-review}
Status: [{done}/{total}]
```

**Phase definitions**:
- **prospective**: No tex file yet — checklist is a planning scaffold. Parts I-IV use TBD placeholders. Part V (Blocking Actions) is immediately useful.
- **active**: Paper draft exists — full checklist with tex line references.
- **pre-submission**: Final verification pass — all items should be `[x]` or `[v]`.
- **post-review**: Revision tracking — add reviewer comments, track changes.

### Generation Process

When creating a paper audit L2 checklist:

1. **Gather sources**: Read the paper `.tex` file(s), scan `experiments/` for code/configs/results, scan `paper/figures/` for figures, execute `memory-retrieve` for past decisions.

2. **Extract paper structure**: Parse tex into a structured inventory:
   - **Formal statements**: definitions, propositions, theorems, corollaries, lemmas, assumptions — extract names, labels, tex line ranges, proof blocks
   - **Empirical claims**: grep for numerical values in running text — record tex line and claimed value
   - **Figures and tables**: extract `\label`, `\ref`, `\includegraphics` paths, `\caption` text
   - **Sections**: map section hierarchy with tex line ranges

3. **Generate all 8 parts** (below), applying status markers.

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
   - `**NO**` — explicitly not satisfied
   - `**YES**` — a problem condition is true

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
