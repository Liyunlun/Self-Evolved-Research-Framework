# paper.illustrate

**Trigger**: User says "illustration", "architecture diagram", "draw the pipeline", or needs conceptual figures for a paper.

## Process

1. **Understand the concept**:
   - Read relevant methodology from `methodology/approach.md` or user description
   - Identify what needs to be visually communicated (architecture, flow, comparison, pipeline)
2. **Select diagram type**:
   - Flow chart: sequential processes, algorithms
   - Architecture diagram: system components and connections
   - Concept map: relationships between ideas
   - Pipeline diagram: data flow through stages
   - Comparison diagram: side-by-side method differences
3. **Generate code**:
   - **TikZ** (preferred for papers): publication-quality, integrates with LaTeX
   - **SVG** (for presentations/docs): scalable, web-compatible
   - Follow academic figure conventions:
     - Consistent font sizes and line widths
     - Clear labels and annotations
     - Logical flow direction (left-to-right or top-to-bottom)
     - Minimal visual clutter
4. **Output**:
   - TikZ: Save to `paper/figures/{name}.tex`
   - SVG: Save to `paper/figures/{name}.svg`
   - Include compilation instructions if TikZ

## Suggested Next

- Illustration created for a paper -> `writing.draft` for integration into paper section
