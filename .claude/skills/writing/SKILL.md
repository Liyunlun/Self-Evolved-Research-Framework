---
name: writing
description: Academic paper writing -- outlining, drafting, reviewing, polishing, figure generation, and compilation
---

# /writing -- Writing Skill Group

Route user intent to the appropriate sub-skill:

- **Outline a paper** (user wants to plan paper structure, start a new paper, or reorganize a draft) -- read `references/outline.md` and follow its instructions
- **Draft a section** (user wants to write a specific paper section, or outline is approved and ready to draft) -- read `references/draft.md` and follow its instructions
- **Review a draft** (user wants feedback on a draft, says "review this") -- read `references/review.md` and follow its instructions
- **Polish writing** (user says "polish", "improve writing", or wants to refine text quality) -- read `references/polish.md` and follow its instructions
- **Generate figures** (user says "make a plot", "generate figures", or needs visualizations for a paper) -- read `references/figure.md` and follow its instructions
- **Compile paper to PDF** (user says "compile paper", "build PDF", or wants to generate the final PDF) -- read `references/compile.md` and follow its instructions

After completing the selected workflow, return control. Do NOT chain multiple workflows -- the chain system handles sequencing.
