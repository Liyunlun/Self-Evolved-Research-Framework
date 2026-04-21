---
name: paper-compile
description: Build the paper PDF via the full LaTeX pipeline (pdflatex×3 + bibtex/biber) after a pre-compile integrity check (\input / \includegraphics / \bibliography targets must resolve). Parses compiler output, auto-fixes common issues (missing packages, minor encoding), and saves PDF to `outputs/paper/{name}.pdf`. Triggers on "compile paper", "build PDF", "make the paper", "latex compile", "编译论文", or after `writing-draft` completes the last pending section.
---

# paper-compile

**Trigger**: User asks to compile the paper, build the PDF, or runs this after finishing `writing-draft` on the final section. Do **not** fire on every minor section edit — this skill is for explicit build requests.

**Process**:

### 1. Locate main `.tex`

1. Find main `.tex` under `paper/papers/` — preferred filename order: `main.tex`, `paper.tex`, `{project_slug}.tex` (from `config.yaml § project.name`), otherwise the single `.tex` file at the top level of `paper/papers/`.
2. If multiple candidates exist and none match the preferred names, ask the user which one to build. Do not guess.
3. Record the chosen main as `MAIN` — all subsequent checks and commands use it.

### 2. Pre-compile integrity checks

Before invoking any compiler, verify that every external reference resolves. This avoids wasting a 3-pass compile on a missing file.

| Check | How | Fail action |
|---|---|---|
| `\input{X}` / `\include{X}` | For each match, verify `paper/papers/{X}.tex` exists | List all missing inputs; stop if ≥1 missing |
| `\includegraphics[...]{X}` | For each match, verify `paper/figures/{X}.{tex,pdf,png,jpg,svg}` exists (try the extensions in order; allow the `\graphicspath{}` directive to extend search) | List all missing figures; stop if ≥1 missing |
| `\bibliography{X}` or `\addbibresource{X.bib}` | Verify the `.bib` file exists and is non-empty | Stop if missing |
| `\usepackage{...}` | Only flag (do not stop) — compiler will error with a clearer message if a package is actually unavailable | Informational |

**Implementation**: use `grep -oE '\\(input|include|includegraphics|bibliography|addbibresource)\{[^}]+\}' {MAIN}` (and any `.tex` it transitively `\input`s) to collect references. Do not parse LaTeX comments (`%`-prefixed lines).

If any required reference is missing, print a clear report and **stop before compiling**:

```
Pre-compile check: FAIL
Missing inputs: paper/papers/methods.tex, paper/papers/results.tex
Missing figures: paper/figures/pipeline.pdf
Fix these, then re-run paper-compile.
```

### 3. Detect bibliography tool

Inspect `MAIN` for `\addbibresource{}` (biber) vs `\bibliography{}` (bibtex). Prefer `biber` when `\addbibresource` is present AND `biber` is on `PATH`; otherwise fall back to `bibtex`. Record as `BIBTOOL`.

### 4. Run the pipeline

Run inside `paper/papers/` so relative paths resolve:

```bash
cd paper/papers
pdflatex -interaction=nonstopmode -halt-on-error {MAIN}    # 1st pass — creates .aux
{BIBTOOL} {MAIN_BASE}                                      # resolves citations
pdflatex -interaction=nonstopmode -halt-on-error {MAIN}    # 2nd pass — inserts bibliography
pdflatex -interaction=nonstopmode -halt-on-error {MAIN}    # 3rd pass — fixes cross-references
```

Capture stdout+stderr of each pass into a scratch log. Do **not** use `-interaction=batchmode` — we want readable error lines.

If any pass exits non-zero, stop the pipeline and hand off to step 5.

### 5. Parse compile output

Scan the scratch log for three categories, in priority order:

| Category | Pattern | Report as |
|---|---|---|
| Hard error | `^! ` lines (TeX error) + the following 2–3 lines for context, plus `l.{N}` line-number hint | **Error** — includes filename:line |
| Missing package | `! LaTeX Error: File .*\.sty' not found` | **Missing package** — suggest `\usepackage{…}` audit |
| Missing citation | `Warning: Citation .* undefined` | **Undefined citation** — list all keys |
| Missing reference | `Warning: Reference .* undefined` | **Undefined reference** — list all labels |
| Overfull box | `Overfull \\hbox.*at lines N--M` | **Overfull box** (informational, do not stop) |
| Encoding | `Package inputenc Error.*` or `.sty utf8` | **Encoding issue** — suggest `\usepackage[utf8]{inputenc}` or switch to XeLaTeX |

For errors, print a compact summary with `file:line` locations — not the full compiler dump. Users can re-run with `-v` if they want the raw log.

### 6. Auto-fix the easy ones (user-confirmed)

For each fixable finding, propose a patch and ask the user to confirm before applying:

- **Missing `\usepackage{X}`**: offer to add to preamble if the error message is unambiguous. Do not guess between multiple candidate packages.
- **Minor encoding issue (single character)**: offer to escape or replace; do not apply automated Unicode rewrites without confirmation.
- **Undefined citation**: do **not** auto-fix. Report the key list and suggest the user run `scripts/citation_fetch.py` (per `writing-draft`) to verify `.bib` coverage.
- **Undefined reference**: report label list; do not attempt to fabricate missing `\label{…}`.

If the user confirms, apply the patch (via Edit) and re-run **only the affected passes** (step 4 from scratch if preamble changed; just passes 2–3 if only a citation/label changed).

### 7. Save the final PDF

On success:

1. Move `paper/papers/{MAIN_BASE}.pdf` → `outputs/paper/{MAIN_BASE}.pdf` (create `outputs/paper/` if needed).
2. Emit a 1-line summary with file size, page count (via `pdfinfo` if available), and elapsed time.
3. Clean up intermediate files: delete `*.aux`, `*.log`, `*.out`, `*.toc`, `*.bbl`, `*.blg`, `*.run.xml`, `*.bcf` from `paper/papers/` unless the user said to keep them. Keep the scratch log for one more run in case of follow-up debugging.

### 8. If compile fails irrecoverably

Do not delete intermediate files on failure — the user (or a follow-up `code-debug` session) needs the `.log` to investigate.

**Inputs**: main `.tex` under `paper/papers/`, transitive `\input` targets, figures under `paper/figures/`, bib file
**Outputs**: `outputs/paper/{name}.pdf` + 1-line compile summary; scratch log retained only on failure
**Token**: ~2-6K (most of the work is shell; token budget is parsing the compile log)
**Composition**:
- Compile failed → propose fixes per step 6; for non-trivial errors route to `code-debug` with the error extract
- Compile succeeded but reviewers-visible issues remain (overfull box, undefined reference) → flag for manual review before submission
- Clean build before submission → suggest `writing-review` on the final PDF for a last peer-review pass

## Common pitfalls

- **Compiling without the pre-check** — a missing `\includegraphics` target burns three pdflatex passes for nothing. Always run step 2 first.
- **Mixing bibtex and biber** — the two are not interchangeable. Detect which the paper uses (`\addbibresource` vs `\bibliography`) and pick one; never run both in the same build.
- **Auxiliary file staleness** — if the preamble changed, the `.aux`/`.bbl` from a prior build can wedge the new compile. When fixing preamble, delete `.aux` and `.bbl` before re-running pass 1.
- **`shell-escape` silently required** — some packages (minted, standalone with external tools) need `-shell-escape`. If the first pass errors with `\write18` or `shell-escape`, retry once with `-shell-escape` and note the requirement in the summary so the user knows to include it in CI.
- **Unicode in file paths** — LaTeX errors on non-ASCII filenames in some configurations. Prefer ASCII-only names under `paper/papers/` and `paper/figures/`.
- **`\cite{}` key drift** — bibtex/biber silently drops unresolved keys. Always surface the "undefined citation" warnings even when the compile exits 0, because the final PDF will show `[?]` where the citation should be.
- **Multiple mains** — if `paper/papers/` has `main.tex` + `supplement.tex`, don't compile both automatically. Ask which one.
