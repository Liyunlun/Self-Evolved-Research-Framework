# pixel.create

**Trigger**: User says "pixel art", "SVG illustration", "README hero image", or wants decorative visuals.

## Process

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

## Suggested Next

- If part of a tracked deliverable -> `checklist.update`
