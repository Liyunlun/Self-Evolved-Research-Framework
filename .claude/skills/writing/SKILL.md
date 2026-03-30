# /writing — Academic Paper Writing

When to use this skill:
- User wants to plan, draft, review, polish, or compile a paper
- User needs figures or visualizations for a paper
- User says "write", "draft", "outline", "review", "polish", "compile" in a paper context
- User uses Chinese equivalents: "写论文", "审阅论文", "润色", "画图", "编译论文"

## writing.outline

**Trigger**: User wants to plan paper structure, start a new paper, or reorganize an existing draft.

### Process
1. Read existing outputs — check `paper/papers/`, `experiments/`, `proofs/`, `SUMMARY.md` for available material.
2. Propose outline with:
   - Sections with target page lengths
   - Key content per section (main arguments, theorems, results to include)
   - Figure and table plan (what goes where, data source for each)
   - Gaps — missing experiments, proofs, or analysis needed before writing
3. Generate a Claims-Evidence Matrix: rows = paper claims, columns = evidence type (theorem, experiment, ablation, baseline comparison), cells = status (done/partial/missing).
4. Save outline to `paper/papers/outline.md`.

### Suggested Next
- Outline approved → `writing.draft` to begin section-by-section writing.

## writing.draft

**Trigger**: User wants to write a specific paper section, or outline is approved and ready to draft.

### Process
1. Read `paper/papers/outline.md` for structure and section plan.
2. Read source materials relevant to the target section:
   - Proofs and theorems from `proofs/`
   - Theory documents from `theory/`
   - Experiment results from `experiments/`
   - Related work notes and references
3. Draft the section:
   - Academic tone, precise language
   - All citations use `\cite{}` format with BibTeX keys
   - Full LaTeX formatting (equations, theorems, algorithms as needed)
   - Follow outline's page length targets
4. Save draft to `paper/papers/{section_name}.tex`.
5. Post-draft citation verification: run `scripts/citation_fetch.py` to check all `\cite{}` keys resolve and flag missing references.

### Suggested Next
- Draft complete → `writing.review` for feedback before polishing.

## writing.review

**Trigger**: User wants a draft reviewed, says "review this", "审阅论文", or wants feedback on writing quality.

### Process
1. Read the draft (full section or paper).
2. Evaluate from multiple reviewer perspectives:
   - **Clarity**: Is the writing clear and well-structured?
   - **Novelty**: Are contributions clearly distinguished from prior work?
   - **Soundness**: Are claims properly supported by evidence?
   - **Presentation**: Are figures, tables, and equations effective?
   - **Missing elements**: What's absent that reviewers would expect?
3. Generate review in conference format:
   - Summary (2-3 sentences)
   - Strengths (bulleted)
   - Weaknesses (bulleted, with specific suggestions)
   - Questions for authors
   - Rating (Accept / Weak Accept / Borderline / Weak Reject / Reject)

Note: For cross-model review (using external LLMs for diverse perspectives), use the `review` skill group instead.

### Suggested Next
- Weaknesses identified → `writing.polish` to address specific issues.

## writing.polish

**Trigger**: User says "polish", "润色", "improve writing", or wants to refine text quality without structural changes.

### Process
1. Read the target text (section, paragraph, or full draft).
2. Improve along these dimensions:
   - Sentence structure — vary length, eliminate run-ons
   - Flow — logical transitions between paragraphs and ideas
   - Precision — replace vague terms with specific ones
   - Conciseness — remove redundancy and filler
   - Transitions — connect sections smoothly
   - Grammar — fix errors, improve academic register
3. Present changes side-by-side (original vs. polished) with brief explanations for each significant change.

### Suggested Next
- Standalone skill — no automatic follow-up needed.

## paper.figure

**Trigger**: User says "画图", "作图", "generate figures", "make a plot", or after `experiment.analyze` produces results that need visualization.

### Process
1. Identify data source — experiment results, theoretical comparisons, or architectural diagrams.
2. Determine figure type based on data and purpose:
   - Line plot (trends over time/parameters)
   - Bar chart (discrete comparisons)
   - Scatter plot (correlations)
   - Heatmap (matrices, attention, confusion)
   - Table (precise numerical comparisons)
   - Custom (architecture diagrams, workflow illustrations)
3. Generate code:
   - Python with matplotlib/seaborn for data-driven figures
   - TikZ/PGFPlots for LaTeX-native figures (preferred for camera-ready)
4. Save generation script to `paper/figures/scripts/`.
5. Save rendered figure to `paper/figures/`.

### Suggested Next
- Figures ready → `writing.draft` for the results section that references them.

## paper.compile

**Trigger**: User says "编译论文", "compile paper", "build PDF", or wants to generate the final PDF.

### Process
1. Locate main `.tex` file in `paper/papers/`.
2. Pre-compile checks:
   - Verify all `\input{}` targets exist
   - Verify all `\includegraphics{}` targets exist
   - Verify `\bibliography{}` target `.bib` file exists
   - Flag any missing files before attempting compilation
3. Compile with full pipeline: `pdflatex` x3 + `bibtex` (handles cross-references and citations).
4. Parse compilation output:
   - Errors — report with line numbers and context
   - Warnings — report undefined references, overfull boxes, missing citations
5. Auto-fix common issues:
   - Missing packages → add `\usepackage{}`
   - Undefined references → flag for manual review
   - Encoding issues → suggest fixes
6. Save final PDF to `outputs/paper/`.

### Suggested Next
- Compilation errors → fix issues and re-compile.
