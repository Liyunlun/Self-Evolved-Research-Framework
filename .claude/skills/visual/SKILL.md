# /visual — Visual Creation: Pixel Art, Diagrams, and Paper Illustrations

When to use this skill:
- User wants pixel art, SVG illustrations, or decorative visuals
- User needs architecture diagrams, pipeline illustrations, or conceptual figures for a paper
- Keywords: "画像素图", "pixel art", "SVG illustration", "README hero image", "论文插图", "architecture diagram", "draw the pipeline", "画示意图"

## pixel.create

**Trigger**: User says "画像素图", "pixel art", "SVG illustration", "README hero image", or wants decorative visuals.

### Process
1. **Understand requirements**:
   - Subject/theme (e.g., robot, neural network, algorithm mascot)
   - Style: pixel art, flat SVG, isometric
   - Purpose: README header, presentation slide, documentation decoration
   - Size constraints (if any)
2. **Design composition**:
   - Choose palette (limited colors for pixel art, consistent with project theme)
   - Plan layout and key visual elements
   - Determine grid size for pixel art (typically 16x16 to 64x64)
3. **Generate SVG code**:
   - Hand-crafted SVG with `<rect>` elements for pixel art
   - Clean, well-structured SVG with viewBox and proper scaling
   - No external dependencies (self-contained SVG)
4. **Output**:
   - Save to `outputs/visuals/{name}.svg`
   - Display inline preview description

### Suggested Next
- If part of a tracked deliverable -> `checklist.update`

---

## paper.illustrate

**Trigger**: User says "论文插图", "illustration", "画示意图", "architecture diagram", "draw the pipeline", or needs conceptual figures for a paper.

### Process
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

### Suggested Next
- Illustration created for a paper -> `writing.draft` for integration into paper section
