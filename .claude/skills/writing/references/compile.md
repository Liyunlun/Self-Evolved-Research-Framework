# paper.compile

**Trigger**: User says "compile paper", "build PDF", or wants to generate the final PDF.

## Process

1. Locate main `.tex` file in `paper/papers/`.
2. Pre-compile checks:
   - Verify all `\input{}` targets exist
   - Verify all `\includegraphics{}` targets exist
   - Verify `\bibliography{}` target `.bib` file exists
   - Flag any missing files before attempting compilation
3. Compile with full pipeline: `pdflatex` x3 + `bibtex` (handles cross-references and citations).
4. Parse compilation output:
   - Errors -- report with line numbers and context
   - Warnings -- report undefined references, overfull boxes, missing citations
5. Auto-fix common issues:
   - Missing packages -> add `\usepackage{}`
   - Undefined references -> flag for manual review
   - Encoding issues -> suggest fixes
6. Save final PDF to `outputs/paper/`.

## Suggested Next

- Compilation errors -> fix issues and re-compile.
