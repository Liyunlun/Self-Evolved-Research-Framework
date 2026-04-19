---
name: paper-compare
description: Build a side-by-side comparison table of two or more papers (method / architecture / training data / results / limitations) and highlight implications for the current project. Triggers when the user compares papers, asks "what's the difference between X and Y", or weighs methods from different papers.
---

# paper-compare

**Trigger**: User compares two or more papers, or asks about differences between methods.

**Process**:
1. Read relevant `resources/papers/*.md` files
2. Generate comparison table:
   - Method / Architecture / Training data / Results / Limitations
3. Highlight implications for current project
4. Output inline (not saved unless user requests)

**Inputs**: 2+ paper references (files or titles)
**Outputs**: Comparison table (inline)
**Token**: ~2-5K
**Composition**: May lead to `decision-analyze` if comparing approaches for adoption
