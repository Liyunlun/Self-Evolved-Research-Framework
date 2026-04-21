# paper.figure

**Trigger**: User says "generate figures", "make a plot", or after `experiment.analyze` produces results that need visualization.

## Process

1. Identify data source -- experiment results, theoretical comparisons, or architectural diagrams.
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

## Suggested Next

- Figures ready -> `writing.draft` for the results section that references them.
