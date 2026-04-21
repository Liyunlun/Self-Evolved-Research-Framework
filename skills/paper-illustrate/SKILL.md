---
name: paper-illustrate
description: Generate rigorous academic figures — architecture diagrams, pipeline illustrations, concept maps, flow charts, side-by-side method comparisons — as TikZ (LaTeX-ready) or SVG (slides/README). Triggers on "draw the architecture", "pipeline figure", "method overview diagram", "tikz figure", "画架构图", "画流程图", "illustrate the method", or any paper-facing figure request. For decorative/identity visuals (pixel art, mascots, README hero), use `pixel-create` instead.
---

# paper-illustrate

**Trigger**: User requests a diagram intended for a paper, slide deck, or technical doc — architecture, pipeline, flow chart, concept map, comparison. If the request is decorative (cute mascot, pixel art hero), route to `pixel-create`.

**Process**:

### 1. Understand the concept

1. Read `methodology/approach.md` (if it exists) to anchor terminology with the project's own method description.
2. If the figure depicts a specific section of a paper draft, peek at `paper/papers/{section}.tex` or `outputs/paper/` to match notation.
3. Identify:
   - **What is being communicated?** — system structure, data flow, algorithmic stages, side-by-side comparison, conceptual relationship
   - **Who reads it?** — conference paper (TikZ), workshop slide (SVG), internal doc (SVG)
   - **Orientation** — horizontal (left→right flow, most papers) or vertical (hierarchical)

### 2. Select diagram type

| Intent | Type | Primary format |
|---|---|---|
| System components + connections | Architecture diagram | TikZ (boxes + arrows) |
| Sequential stages | Pipeline | TikZ or SVG |
| Algorithmic control flow | Flow chart | TikZ (`flowchart` lib) |
| Concept relationships | Concept map | TikZ (`positioning`, `fit` lib) |
| Method A vs Method B | Comparison diagram | 2-column TikZ or side-by-side SVG |
| Data flow through layers | Layer diagram | TikZ (stacked boxes) |

### 3. Generate figure code

**TikZ (preferred for papers)** — self-contained, compiles standalone:

```latex
\documentclass[tikz,border=5pt]{standalone}
\usepackage{tikz}
\usetikzlibrary{arrows.meta,positioning,shapes.geometric,fit,backgrounds}

\begin{document}
\begin{tikzpicture}[
    box/.style     = {draw, rounded corners, minimum width=2.4cm,
                      minimum height=0.9cm, align=center, font=\small},
    arrow/.style   = {-Stealth, thick},
    stage/.style   = {box, fill=blue!10},
    data/.style    = {box, fill=orange!15, shape=cylinder, shape border rotate=90,
                      aspect=0.25}
]
    % Nodes
    \node[data]  (in)   {Input};
    \node[stage] (enc)  [right=1cm of in]  {Encoder};
    \node[stage] (mid)  [right=1cm of enc] {Processor};
    \node[stage] (dec)  [right=1cm of mid] {Decoder};
    \node[data]  (out)  [right=1cm of dec] {Output};

    % Edges
    \draw[arrow] (in)  -- (enc);
    \draw[arrow] (enc) -- (mid);
    \draw[arrow] (mid) -- (dec);
    \draw[arrow] (dec) -- (out);

    % Group annotation
    \begin{scope}[on background layer]
      \node[draw, dashed, inner sep=0.25cm, fit=(enc)(mid)(dec),
            label=above:{Backbone}] {};
    \end{scope}
\end{tikzpicture}
\end{document}
```

**SVG (for slides / README / web)** — use when embedding in non-LaTeX context:

```xml
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 800 200" font-family="sans-serif">
  <defs>
    <marker id="arrow" markerWidth="10" markerHeight="10" refX="9" refY="3"
            orient="auto" markerUnits="strokeWidth">
      <path d="M0,0 L0,6 L9,3 z" fill="#333"/>
    </marker>
  </defs>

  <g font-size="14">
    <!-- Stages (rounded boxes) -->
    <rect x="40"  y="70" width="120" height="60" rx="8" fill="#e8f4fd" stroke="#4a9eda"/>
    <text x="100" y="105" text-anchor="middle">Input</text>

    <rect x="210" y="70" width="120" height="60" rx="8" fill="#fff3e0" stroke="#da8a4a"/>
    <text x="270" y="105" text-anchor="middle">Encoder</text>
    <!-- ... more stages ... -->
  </g>

  <!-- Arrows -->
  <line x1="160" y1="100" x2="210" y2="100" stroke="#333" stroke-width="2" marker-end="url(#arrow)"/>
</svg>
```

### 4. Apply academic conventions

- **Font**: match paper (sans-serif `\small` for TikZ nodes; 12–14 px for SVG). Never mix >2 font sizes in one figure.
- **Line weights**: edges 0.8–1.2 pt; box strokes 0.6–1.0 pt; emphasis edges thicker, not a different color.
- **Color**: restrained palette — 2–4 hues (blue / orange / gray is a safe default). Pastel fills for boxes, solid strokes. Use color for *categorical* distinction, not decoration. Check for **colorblind safety** (avoid red/green pairs carrying information).
- **Spacing**: consistent gaps (`node distance=1cm` in TikZ). Align nodes on a grid.
- **Labels**: short noun phrases, not sentences. Sub-labels beneath arrows for dataflow type.
- **No clutter**: drop shadows, gradients, 3D extrusion are distracting in publications. Flat is better.

### 5. Save

- TikZ → `outputs/paper/figures/{name}.tex`. Also emit a compile note:
  ```
  To compile standalone: pdflatex outputs/paper/figures/{name}.tex
  To include in paper:   \input{figures/{name}}  (then wrap with \begin{figure}...)
  ```
- SVG → `outputs/paper/figures/{name}.svg`
- Optionally emit rendered preview (`.pdf` or `.png`) if user's tooling supports it, but keep the `.tex` / `.svg` as canonical source.

### 6. Iterate

- Ask user for feedback on a preview (common revisions: node rearrangement, edge routing, label wording, color assignment).
- Use `Edit` for small tweaks; rewrite with `Write` only on major redesigns.
- Typical 2–4 iterations.

**Inputs**: user concept + `methodology/approach.md` + relevant paper source (`paper/papers/*.tex`, `outputs/paper/*`)
**Outputs**: `outputs/paper/figures/{name}.tex` (TikZ) or `outputs/paper/figures/{name}.svg`
**Token**: ~3-10K (3-6K for first draft + 2-4K for iteration)
**Composition**:
- Figure done and belongs to a section → suggest `writing-draft` to integrate (`\includegraphics` + caption)
- Figure depicts a novel method comparison → suggest `paper-compare` if a tabular version would also help
- Figure tracked as a deliverable → `checklist-update`

## Common pitfalls

- **Graphviz dot temptation**: auto-layout produces edges that cross and unlabeled nodes — hand-placed TikZ almost always beats auto-layout for paper figures.
- **Arrow-head overshoot**: in TikZ use `-Stealth` (not `->`) for crisp heads; in SVG set `refX` to marker width, not 0.
- **Text inside boxes overflowing**: set `minimum width` and `align=center`, let TikZ expand; for SVG, measure text length before sizing the box.
- **Two fonts don't match**: if the figure will be in LaTeX, TikZ already uses the document font — don't hard-code `\sffamily` unless you want sans-serif specifically.
- **Color-only encoding**: always pair color with shape/texture/label so colorblind readers don't lose information.
- **viewBox too wide**: SVG figures embedded in papers should match the column width ratio (e.g. 2:1 for wide figures, 4:3 for method boxes). Export with tight bounds.
- **Version rot**: when the method changes, the figure lies. If `methodology/approach.md` was recently edited, re-read before finalizing.
