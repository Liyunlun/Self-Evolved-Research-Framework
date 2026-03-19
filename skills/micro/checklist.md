# Checklist Micro-Skills

> Triggered by paper submission readiness checks, claim verification, or audit requests.
> Automates the generate → verify → update pipeline for comprehensive paper checklists.
>
> Reference implementation: `/home/shs/codeforshare/SFB/Checklist.md` (NeurIPS 2025 SFB paper)

## checklist.generate

**Trigger**: User asks to "create a checklist", "audit the paper", "track paper claims", or when a paper draft reaches a milestone (first complete draft, pre-submission, revision)

**Process**:

### Step 1 — Gather sources

- Read the paper `.tex` file(s) (identify from `paper/` directory or user-specified path)
- Scan `experiments/` structure: code files, configs, result CSVs/JSONs, figures
- Scan `paper/figures/` for submission figures, trace to source scripts
- Execute `memory.retrieve` for relevant past decisions and experiment outcomes

### Step 2 — Extract paper structure

Parse the tex into a structured inventory:

- **Formal statements**: definitions, propositions, theorems, corollaries, lemmas, assumptions — extract names, labels, tex line ranges, and any `\begin{proof}` blocks
- **Empirical claims**: grep for numerical values in running text (e.g., "5x lower", "0.03–0.05", "297,000 configurations") — record tex line and the claimed value
- **Figures and tables**: extract `\label`, `\ref`, `\includegraphics` paths, `\caption` text
- **Sections**: map section hierarchy with tex line ranges

### Step 3 — Generate `Checklist.md`

All 8 parts are mandatory. Within each part, skip sections only if no items exist. Use **hierarchical numbering** (`1.1`, `1.2`, `2.1`, ...) that maps to logical claims, not paper section numbers.

---

**PART I: THEORY & PROOFS**

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

   For items that require **flagging rather than checking**, use bold markers:
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

**PART II: EMPIRICAL CLAIMS & EVIDENCE**

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

**PART III: FIGURES & TABLES**

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

**PART IV: PAPER SECTIONS**

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

**PART V: BLOCKING ACTIONS**

Three subsections with **priority levels** (CRITICAL > HIGH > MED > LOW):

```markdown
## 5.1 Verification Pass (run scripts, fill `[ ]` → `[v]`)
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

**PART VI: RAW DATA INVENTORY**

```markdown
| Data file | Location | Contents |
|-----------|----------|----------|
```

---

**PART VII: CODE INDEX**

Bidirectional: every script maps to the claims it supports.

```markdown
| File | Purpose | Used by claims |
|------|---------|----------------|
| `{path}` | {what it does} | §{N.M}, §{N.M} |
```

---

**PART VIII: COMMENT LOG**

Collect all `<!-- TODO: ... -->` and `<!-- comment: ... -->` from the entire checklist.

```markdown
| Date | Location | Comment | Action needed? |
|------|----------|---------|----------------|
| {date} | §{N.M} | {comment text} | YES → {blocking action ref} / No ({reason}) |
```

---

### Step 4 — Apply status markers

**Standard markers** (for checkable items):
```
| Marker | Meaning | Who |
|--------|---------|-----|
| `[ ]`  | **Not Completed** — work not yet done | — |
| `[x]`  | **Completed** — work done, not yet verified | Author |
| `[v]`  | **Checked** — verified by Claude or script | Claude |
| `[U]`  | **Checked by User** — final sign-off | User |
```

**Flag markers** (for items that need flagging, not checking):
- `**NO**` — condition explicitly not met
- `**YES**` — a problem condition is true
- `**INCOMPLETE**` — partial work exists

**Initial assignment rules**:
- File exists at referenced path → `[x]`
- No evidence found → `[ ]`
- Add `<!-- TODO: ... -->` for items needing human attention
- Add `<!-- comment: ... -->` for contextual notes

### Step 5 — Add metadata header

```markdown
# {Venue} {Year} Submission — Master Checklist

Source: `{tex_file_path}` | Last updated: {YYYY-MM-DD}
```

### Step 6 — Save and report

- Write to `Checklist.md` in the project root (or paper directory if user specifies)
- Output summary:
  ```
  [CHECKLIST] Generated: {N_total} items across {N_parts} parts
  Completion: {N_done}/{N_total} ({pct}%)
  Blocking: {top 3 blocking issues with priorities}
  ```

**Inputs**: Paper tex file + experiment code + results data
**Outputs**: `Checklist.md` (comprehensive, typically 200-900 lines)
**Token**: ~8-20K (depends on paper complexity)
**Composition**: After generation → suggest `checklist.verify` for automated verification pass

---

## checklist.verify

**Trigger**: User asks to "verify the checklist", "run verification", "check paper numbers", or periodically during paper writing

**Process**:
1. **Read current `Checklist.md`**
2. **Automated verification pass** — for each `[ ]` or `[x]` item that has a linked script or data file:
   a. **Data existence checks**: Verify all referenced files exist
      - Data CSVs, result JSONs, checkpoint files
      - Scripts referenced in Code Index
      - Figures referenced in Figure Provenance
      - Flag missing files: `<!-- MISSING: {path} not found -->`
   b. **Script execution** (if verification scripts exist):
      - Run `verify_paper_numbers.py` or equivalent
      - Capture output, match against claimed values
   c. **Tex cross-reference checks**:
      - Verify all `\ref{...}` targets exist (compile tex if possible)
      - Check for undefined references
      - Verify figure/table labels match `\includegraphics`/`\begin{table}`
   d. **Numerical claim spot-checks** (sample up to 10 highest-priority):
      - Read the data file
      - Compute the claimed statistic
      - Compare: if match within tolerance → `[v]`, else flag
      - `<!-- DISCREPANCY: claimed {X}, computed {Y} from {file} -->`
   e. **Provenance chain validation**:
      - For each figure in Part III: verify source file exists, script exists, data file exists
      - Flag broken chains
3. **Update statuses**:
   - `[ ]` → `[v]` if verified by script/data check
   - `[x]` → `[v]` if automated verification passes
   - Never downgrade: `[v]` and `[U]` stay as-is
4. **Generate verification report** (inline):
   ```
   [VERIFY] {N_total} items | {N_verified}[v] | {N_issues} issues
   Verified:
   - §{N.M}: {item} ✓
   Issues:
   - §{N.M}: {description of problem}
   Missing files:
   - {path}: referenced by §{N.M}
   ```
5. **Update `Checklist.md`** with new statuses and comments

**Inputs**: Existing `Checklist.md` + data files + scripts
**Outputs**: Updated `Checklist.md` + verification report (inline)
**Token**: ~4-10K
**Composition**:
- All verified → suggest `checklist.update` for any new claims added since last generation
- Issues found → surface issues, suggest fixes
- Always → chain to `memory.write` (record verification results as episode)

---

## checklist.update

**Trigger**: User reports changes to paper (new experiment, revised proof, added section), or after `writing.draft`/`writing.review` completes

**Process**:
1. **Read current `Checklist.md`** and **paper tex file**
2. **Diff detection** — identify what changed since the checklist was last updated:
   - New definitions/propositions/theorems in tex
   - New empirical claims or revised numbers
   - New figures or tables
   - New experiment code or data files
   - Deleted or renamed items
   - Reclassified statements (e.g., theorem → corollary)
3. **Incremental update**:
   - Add new items with `[ ]` status in the correct part and numbering position
   - Mark deleted items with `~~strikethrough~~` + date and reason
   - Update tex line numbers if they shifted (re-scan tex)
   - Update "Last updated" timestamp in header
   - Add change annotations where applicable:
     ```markdown
     **Change ({date}):** {description of what changed and why}
     ```
   - For reclassified statements, update the section header flags
4. **Consistency check**:
   - Every formal statement in tex → has Part I entry
   - Every numerical claim in tex → has Part II entry
   - Every figure/table in tex → has Part III entry
   - No orphaned items (checklist item but claim removed from tex)
   - Part VIII Comment Log includes all new `<!-- TODO: -->` comments
5. **Save updated `Checklist.md`**
6. **Output change summary**:
   ```
   [CHECKLIST] Updated: +{N_added} items, ~{N_modified} modified, -{N_removed} removed
   New items needing attention:
   - §{N.M}: {description}
   Orphaned items (removed from tex):
   - §{N.M}: {description} — suggest removal
   ```

**Inputs**: Current `Checklist.md` + updated tex file
**Outputs**: Updated `Checklist.md` + change summary (inline)
**Token**: ~3-6K
**Composition**: After update → suggest `checklist.verify` on new items

---

## Design Principles

1. **Every claim links to evidence**: No numerical claim exists without a path to raw data + analysis script + output artifact. The chain: claim → data → script → figure is always traceable.
2. **Bidirectional traceability**: Code Index (Part VII) maps code → claims; empirical claims (Part II) map claims → code. Any file or claim can be traced in either direction.
3. **Incremental maintenance**: The checklist is a living document. `checklist.update` keeps it synchronized with the evolving paper without regenerating from scratch. Change annotations preserve the edit history.
4. **Four-stage verification**: `[ ]` → `[x]` (author marks done) → `[v]` (Claude/script verifies) → `[U]` (user signs off). This prevents "checked my own homework" blindness.
5. **Comment-driven TODO discovery**: `<!-- TODO: ... -->` comments in the checklist body are automatically collected in Part VIII, ensuring nothing gets lost in a large document.
6. **Rich annotations over bare checkmarks**: Issue flags, change logs, options tables, key insights, and background notes make the checklist a living research document — not just a list of boxes. When a problem is found, the checklist records the analysis and resolution options, not just "broken."
7. **Cross-referencing**: Theory items (Part I) link to their empirical validation (Part II) via `See §N.M`. Blocking actions (Part V) link to the items they unblock. This creates a navigable web, not isolated lists.
8. **Experiment evolution**: Experiments get redesigned. The checklist tracks this explicitly: old experiments get `BEING REDESIGNED` / `REPLACED BY` flags, new proposals get priority-tagged design tables (P1, P2, ...), and the old items are preserved for reference.

## TD-NL Integration

Track performance via option-values (to be created on first use):
- `memory/td-nl/option-values/checklist-generate.md`
- `memory/td-nl/option-values/checklist-verify.md`

Key metrics for TD assessment:
- `checklist.generate`: Coverage (% of paper claims captured), accuracy of initial status assignments, usefulness of structure to the user, richness of annotations
- `checklist.verify`: Accuracy of automated verification, false positive/negative rate, discrepancy detection rate, provenance chain completeness
- `checklist.update`: Completeness of diff detection, correct tex line number updates, no orphaned items, change annotation quality
