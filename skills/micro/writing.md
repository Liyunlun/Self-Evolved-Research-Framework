# Writing Micro-Skills

> Triggered by writing intent or paper drafting context.

## writing.outline

**Trigger**: User plans paper structure, asks "how should I organize the paper?", or starts a new paper

**Process**:
1. Read existing research outputs: `paper/`, `methodology/approach.md`
2. Propose paper outline:
   - Section structure with estimated page lengths
   - Key content for each section (2-3 bullets)
   - Figure/table plan
   - Which existing outputs map to which sections
3. Identify gaps: what research is needed before each section can be written
4. Save outline to `paper/papers/outline.md` if confirmed

**Inputs**: Research topic + existing outputs + target venue (optional)
**Outputs**: Paper outline document + Claims-Evidence Matrix
**Token**: ~2-5K
**Composition**: Outline approved → leads to `writing.draft` for individual sections

### Claims-Evidence Matrix (Outline Artifact)

When producing an outline, also generate a claims→evidence mapping table:

```markdown
## Claims-Evidence Matrix

| # | Claim | Evidence Type | Source | Status |
|---|-------|--------------|--------|--------|
| C1 | {main contribution claim} | {theorem/experiment/analysis} | {file or planned} | {have/need} |
| C2 | {secondary claim} | {experiment} | {logs/experiments/...} | {have/need} |
| ... | ... | ... | ... | ... |
```

**Purpose**: Ensures every paper claim is backed by concrete evidence before drafting begins.
**Usage in writing.draft**: When drafting a section, check the matrix — only write claims with `status: have`. Flag `status: need` claims for the user.
**Update rule**: As experiments complete or proofs are verified, update the matrix status.

---

## writing.draft

**Trigger**: User asks to write a specific paper section, or says "draft the introduction/method/results"

**Process**:
1. Read the outline (if exists) and relevant source materials:
   - Proofs from `paper/proofs/`
   - Theory from `paper/theory/`
   - Paper notes from `resources/papers/*.md`
2. Draft the requested section:
   - Academic tone appropriate for target venue
   - Proper citations (placeholder format: \cite{author_year})
   - LaTeX formatting
   - Integrate figures/tables where appropriate
3. Save draft to `paper/papers/{section_name}.tex`
4. **Post-draft citation verification**:
   - Scan draft for placeholder `\cite{author_year}` entries
   - For each placeholder, run `scripts/citation_fetch.py "{title}" --authors "{author}"`
   - Replace with verified BibTeX key if found; mark with `% [VERIFY]` if not
   - Append verified BibTeX entries to `paper/papers/references.bib`
   - Output summary: `Citations: {N} verified, {M} need manual verification`

**Inputs**: Section name + source materials + target venue
**Outputs**: `paper/papers/{section_name}.tex` + updated `references.bib`
**Token**: ~5-15K
**Composition**: Draft complete → suggest `writing.review` for feedback

---

## writing.review

**Trigger**: User asks to review a draft, "what do you think of this writing?", or wants simulated peer review

**Process**:
1. Read the draft section/paper
2. Evaluate from multiple reviewer perspectives:
   - **Clarity**: Is the writing clear? Are claims well-supported?
   - **Novelty**: Is the contribution clearly articulated?
   - **Soundness**: Are the technical claims correct?
   - **Presentation**: Figures, organization, flow
   - **Missing**: What's absent that reviewers would expect?
3. Generate review in conference format:
   - Summary (2-3 sentences)
   - Strengths (bulleted)
   - Weaknesses (bulleted, with specific suggestions)
   - Questions for authors
   - Overall: Strong Accept / Accept / Borderline / Reject
4. Output inline (save to `paper/reviews/` if full paper review)

**Inputs**: Draft text + target venue
**Outputs**: Structured review (inline or saved)
**Token**: ~5-15K (single-model) / ~10-25K (cross-model loop)
**Composition**: Weaknesses identified → suggest `writing.polish` for specific fixes

### Cross-Model Review Mode

When cross-model feedback is desired, `writing.review` can operate in **cross-model adversarial mode** for higher-quality feedback. This mode is suggested for full paper reviews or critical sections (introduction, methodology).

**Activation**: Auto-activated when reviewing full papers or when user requests "thorough review" / "adversarial review". Can be explicitly requested or skipped.

**Process**:
1. **Send draft to external reviewer** via Claude Code Agent subagent:
   - Launch an Agent (subagent_type="general-purpose") with a prompt that includes:
     - The draft text to review
     - System instructions:
       ```
       You are a rigorous peer reviewer for {venue}. Review this paper section with the standards of a top-tier venue. Provide:
       1. Summary (2-3 sentences)
       2. Strengths (bulleted, specific)
       3. Weaknesses (bulleted, with concrete fix suggestions)
       4. Questions for authors
       5. Score: {Strong Accept / Accept / Borderline / Reject}
       6. Confidence: {High / Medium / Low}
       Be critical but constructive. Cite specific passages.
       ```
2. **Internal review**: Simultaneously generate own review (standard writing.review process)
3. **Synthesize**: Compare internal vs. external reviews:
   - Agreement areas → high-confidence feedback
   - Disagreement areas → flag for user judgment with both perspectives
   - External-only issues → likely blind spots worth addressing
4. **Auto-fix loop** (up to 4 rounds, governed by TD-NL):
   - Round N: Apply fixes for agreed-upon weaknesses
   - Re-submit to external reviewer with: "I've addressed your feedback. Here's the revised version: {diff summary}. Please re-review."
   - Track quality trajectory: score should improve each round
   - **Stopping criteria** (TD-NL learned):
     - External score reaches "Accept" or better → stop
     - Score unchanged for 2 consecutive rounds → stop (diminishing returns)
     - 4 rounds reached → stop (hard cap)
     - User interrupts → stop
5. **Output**: Final synthesized review + revision history:
   ```
   ## Cross-Model Review Summary
   Rounds: {N}
   Score trajectory: {R1: Reject → R2: Borderline → R3: Accept}
   Key improvements made: {bulleted list}
   Remaining issues: {what couldn't be auto-fixed}
   Internal vs External agreement: {high/medium/low}
   ```
6. Save review to `paper/reviews/{section_name}-cross-review.md`

**TD-NL tracking**: Performance tracked via `memory/td-nl/option-values/cross-review.md`
- Key metrics: rounds-to-accept, score improvement per round, agreement rate with internal review
- Learns optimal stopping: if early rounds show little improvement, reduces max rounds

---

## writing.polish

**Trigger**: User asks to improve specific text, "make this clearer", or "fix the writing"

**Process**:
1. Read the specific text to polish
2. Improve:
   - Sentence structure and flow
   - Technical precision
   - Conciseness (cut filler)
   - Transition quality
   - Grammar and style
3. Present side-by-side: original vs. polished
4. Explain key changes made

**Inputs**: Text to polish + style preferences (if any)
**Outputs**: Polished text (inline, user copies to document)
**Token**: ~2-5K
**Composition**: Standalone — typically doesn't chain

---

## paper.figure

**Trigger**: User says "画图", "作图", "generate figures", "paper figures", "plot results", or after `experiment.analyze` when visualization is needed

**Process**:
1. **Identify data source**:
   - Read experiment results from `experiments/` or user-specified path
   - Parse CSV, JSON, YAML, or log files for plottable data
2. **Determine figure type**:
   - Line plot: training curves, ablation trends
   - Bar chart: comparison across methods/baselines
   - Scatter plot: correlation analysis
   - Heatmap: attention maps, confusion matrices
   - Table: numerical comparisons (LaTeX `tabular`)
   - Custom: architecture diagrams, algorithm visualization
3. **Generate code**:
   - Python/matplotlib for data-driven figures
   - TikZ/PGFPlots for publication-quality LaTeX figures
   - Include proper axis labels, legends, font sizes for target venue
4. **Output**:
   - Save figure script to `paper/figures/scripts/{figure_name}.py`
   - Save generated figure to `paper/figures/{figure_name}.{pdf|png}`
   - If TikZ: save to `paper/figures/{figure_name}.tex`

**Inputs**: Experiment data + figure requirements + target venue style
**Outputs**: Figure files + generation scripts in `paper/figures/`
**Token**: ~3-10K
**Composition**: Figures generated → suggest `checklist.update` + `writing.draft` for results section

---

## paper.compile

**Trigger**: User says "编译论文", "compile paper", "build PDF", "生成PDF", or after `writing.draft` completes all sections

**Process**:
1. **Locate main tex file**: Search `paper/papers/` for main `.tex` file (contains `\begin{document}`)
2. **Pre-compile checks**:
   - Verify all `\input{}` / `\include{}` targets exist
   - Verify all `\includegraphics{}` image paths exist
   - Verify `\bibliography{}` bib file exists
3. **Compile** (multi-pass):
   ```bash
   pdflatex -interaction=nonstopmode main.tex
   bibtex main
   pdflatex -interaction=nonstopmode main.tex
   pdflatex -interaction=nonstopmode main.tex
   ```
4. **Parse output** for errors and warnings:
   - **Errors**: Missing packages, undefined references, syntax errors → attempt auto-fix
   - **Warnings**: Overfull hboxes, missing citations → report but continue
5. **Auto-fix common issues**:
   - Missing `\usepackage{}` → add to preamble
   - Undefined `\ref{}` → scan for closest `\label{}` match
   - Missing figure files → flag with path suggestion
6. **Output**:
   - PDF file to `outputs/paper/{slug}.pdf`
   - Compilation log summary (inline)
   ```
   [COMPILE] {main.tex} → {output.pdf}
   Status: {success|warnings|errors}
   Pages: {N} | Errors: {N} | Warnings: {N}
   {Error details if any}
   ```

**Inputs**: Path to main `.tex` file (or auto-detected)
**Outputs**: PDF + compilation log
**Token**: ~1-3K
**Composition**: Compile success → suggest `checklist.update`. Errors → fix and re-compile
