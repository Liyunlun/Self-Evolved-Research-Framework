---
name: paper-figure
description: Generate data-driven figures — line plots, bar charts, scatter plots, heatmaps, confusion matrices, tables — from experiment results. Preserves the generation script under `paper/figures/scripts/{name}.py` and renders to `paper/figures/{name}.{pdf,png}` so reviewers can reproduce. Matplotlib/seaborn for quick iteration; PGFPlots/TikZ for camera-ready. Triggers on "generate figures", "make a plot", "plot the results", "bar chart", "heatmap", "confusion matrix", "画图", or auto-chains after `experiment-analyze`. For structural diagrams (architecture / pipeline / flow) use `paper-illustrate`; for decorative / identity visuals (mascot, README hero) use `paper-art`.
---

# paper-figure

**Trigger**: User asks for a data-driven plot, or `experiment-analyze` just produced results that need visualization. For structural diagrams (architecture, pipeline, flow) route to `paper-illustrate`; for decorative / identity visuals (pixel mascot, README hero) route to `paper-art`.

**Process**:

### 1. Locate the data source

1. Check `experiments/` for the most recent result artifact (`results.csv`, `results.json`, `metrics.jsonl`, or a run-specific directory named in `experiments/{run_id}/`).
2. If the user just ran `experiment-analyze`, prefer its summary table over the raw log — it has already aggregated seeds / splits.
3. If multiple candidate sources exist, ask the user which run to plot. Do **not** guess across runs — a silent wrong-run plot is worse than no plot.
4. Record the chosen source path; it will appear in a comment at the top of the generation script for reproducibility.

### 2. Determine figure type

| Data shape | Figure type | When to use |
|---|---|---|
| Metric vs. epoch/step/parameter | Line plot | Training curves, ablation sweeps, scaling laws |
| Categorical comparison (few groups) | Bar chart | Method comparisons, ablation deltas |
| Two continuous variables | Scatter plot | Correlations, per-example analysis |
| Matrix of values | Heatmap | Attention, confusion matrix, pairwise sim |
| Precise numerical comparison | Table (LaTeX) | Main results with stat-sig markers |
| Distribution of a metric | Box / violin plot | Robustness across seeds, per-group variance |

If the choice is non-obvious (e.g. 3+ factors), propose two options with a one-line tradeoff each and let the user pick. Don't spend an iteration on the wrong encoding.

### 3. Pick the rendering backend

| Backend | Use when | File output |
|---|---|---|
| `matplotlib` (default) | Fast iteration, ad-hoc exploration | `.png` + `.pdf` |
| `matplotlib` + `seaborn` | Statistical plots (box, violin, pairgrid, regression bands) | `.pdf` preferred |
| `pandas.DataFrame.to_latex()` | Results table destined for the paper | `.tex` |
| PGFPlots / TikZ | Camera-ready, font-matched to paper, no rasterization | `.tex` compiled via `pdflatex` |

**Rule of thumb**: iterate in matplotlib, promote the final plot to PGFPlots only when the paper is near submission and font mismatch becomes visible.

### 4. Generate the script

Save as `paper/figures/scripts/{name}.py` (Python) or `paper/figures/scripts/{name}.tex` (PGFPlots). Every script must:

1. Load from the recorded data source (relative path from repo root, resolved via `pathlib`).
2. Have a `if __name__ == "__main__":` block so it can be re-run standalone.
3. Emit both `.pdf` (vector, for LaTeX inclusion) and `.png` (for README / slide preview) when using matplotlib.
4. Save to `paper/figures/{name}.{pdf,png}` — the script output path is hard-coded, not a CLI arg (reproducibility > flexibility here).
5. Be deterministic — set `random_state` / `np.random.seed` if any sampling is involved.

**Matplotlib skeleton**:

```python
"""Generate {figure-name} from {run-id}.

Source : experiments/{run_id}/results.csv
Output : paper/figures/{name}.{pdf,png}
"""
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

REPO = Path(__file__).resolve().parents[3]
SRC  = REPO / "experiments" / "{run_id}" / "results.csv"
OUT  = REPO / "paper" / "figures" / "{name}"

def main() -> None:
    df = pd.read_csv(SRC)
    fig, ax = plt.subplots(figsize=(4.0, 2.8))   # single-column: 3.3 in, double: 6.8 in
    # ... plot here ...
    ax.set_xlabel("...")
    ax.set_ylabel("...")
    ax.legend(frameon=False)
    fig.tight_layout()
    fig.savefig(OUT.with_suffix(".pdf"))
    fig.savefig(OUT.with_suffix(".png"), dpi=200)

if __name__ == "__main__":
    main()
```

**PGFPlots skeleton** (for camera-ready):

```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{pgfplots}
\pgfplotsset{compat=1.18}
\begin{document}
\begin{tikzpicture}
  \begin{axis}[
      width=6cm, height=4cm,
      xlabel={...}, ylabel={...},
      legend pos=north east, legend cell align=left,
      grid=major, grid style={dashed,gray!30},
  ]
    \addplot+[mark=none, thick] table[x=step, y=loss, col sep=comma]
            {../../experiments/{run_id}/results.csv};
    \addlegendentry{Ours}
  \end{axis}
\end{tikzpicture}
\end{document}
```

### 5. Apply academic conventions

Share the palette / typography conventions with `paper-illustrate` so paper figures read as one family:

- **Palette**: 2–4 hues, colorblind-safe. Default: Okabe–Ito or `tab10` (first 4 entries). Never encode information by color alone — also use marker shape, line style, or direct label.
- **Font size**: 8–10 pt inside figures (matches `\small` in paper body). `plt.rcParams["font.size"] = 9` for matplotlib.
- **Figure dimensions**: match column width. ACL/NeurIPS single column ≈ 3.3 in; double column ≈ 6.8 in. Height = width × (2/3) unless time-series demands wider.
- **Line weight**: 1.2 pt for data series; 0.6 pt for grid/axis. Grid: light gray, dashed, behind data.
- **Markers**: one per 5–10 data points (not every point) when the line itself carries the signal.
- **Error bars / CI**: shaded region at 1σ or 95% CI is preferred over error bars when > 3 methods are compared.
- **No chartjunk**: drop gridlines for bar charts, drop top / right spines by default (`sns.despine()`), never use 3D, never use pie charts.
- **Table style**: use `booktabs` (`\toprule`, `\midrule`, `\bottomrule`), never vertical rules. Right-align numbers, left-align labels. Bold the best row/column; mark stat-sig with `*` / `†` footnote.

### 6. Save outputs + keep the script

1. Run the script (`python paper/figures/scripts/{name}.py`) and confirm both `.pdf` and `.png` land in `paper/figures/`.
2. Do **not** delete or overwrite the script — it is the canonical source. If the user wants to tweak the plot, edit the script and re-run, don't hand-edit the rendered file.
3. Emit a 1-line summary: figure name, type, dims, source run, output paths.

### 7. Iterate

Typical 2–4 iterations. Common revisions: axis scale (log vs. linear), legend position, color reassignment, marker density, method ordering. Use `Edit` on the script for small tweaks; rewrite with `Write` only on type changes (e.g. bar → line).

If the user requests a visual change that breaks a convention from step 5 (e.g. "use red/green for pass/fail"), push back once with the colorblind note — then honor the request and leave a comment in the script.

**Inputs**: data source under `experiments/`, user concept (type + variables), optional style from prior figures in `paper/figures/`
**Outputs**: `paper/figures/scripts/{name}.py` (or `.tex`) + `paper/figures/{name}.pdf` + `paper/figures/{name}.png`
**Token**: ~2-8K (2-4K first draft + 1-4K iteration)
**Composition**:
- Figure done and belongs to a Results section → `writing-draft` for the prose that cites it (`\includegraphics` + caption)
- Figure is a structural diagram, not data-driven → route to `paper-illustrate` instead
- Figure is a decorative asset (mascot, README hero) → route to `paper-art` instead
- Figure tracked as a deliverable → `checklist-update` to mark completion
- Multiple runs compared → suggest `paper-compare` for a tabular companion

## Common pitfalls

- **Plotting before results stabilize** — if seeds vary by ≥5%, plot the mean + CI band across seeds, not a single seed. A pretty single-seed curve that doesn't replicate is worse than no figure.
- **Pixelated PDFs** — using `plt.savefig("foo.pdf", dpi=72)` rasterizes the output. `.pdf` should be vector: omit `dpi` or set `savefig.format` explicitly.
- **Font embedding** — LaTeX picks up system fonts that reviewers don't have. Set `plt.rcParams["pdf.fonttype"] = 42` (TrueType, embedded) or match paper font via `usetex=True` only when the env has TeX.
- **Legend outside the axes** — crops on `savefig` unless `bbox_inches="tight"`. Prefer legends inside the axes with `frameon=False`.
- **Axis auto-scaling hides effects** — if the interesting range is 0.85–0.90, set `ax.set_ylim(0.80, 0.92)` explicitly. But note the clipped axis in the caption so reviewers aren't misled.
- **Hard-coded data paths** — never `/home/user/...`. Always resolve relative to the script via `Path(__file__).parents[N]`. Reviewers re-running the script from their checkout must succeed.
- **Color-only categorical encoding** — repeat the conventions in `paper-illustrate § 4`: pair color with marker shape / line style / direct label so colorblind readers don't lose information.
- **Regenerating without version** — running the script silently overwrites the prior `.pdf`. If the paper cites a specific figure version, tag the script (`git add paper/figures/scripts/`) before re-running.
- **Seaborn default style overriding paper font** — `sns.set_theme()` resets rcParams. Call it once at the top of the script, then re-apply `rcParams["font.size"]` etc.
- **Table as image** — never save a results table as `.png`. Use `df.to_latex()` or `tabulate(..., tablefmt="latex_booktabs")` and include via `\input{figures/table.tex}`.
