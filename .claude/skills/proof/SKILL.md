---
name: proof
description: Proof critique, writing, fixing, formalization, and formula verification
---

# /proof -- Proof Skill Group

Route user intent to the appropriate sub-skill:

- **Critique a proof** (user presents a proof for correctness checking, asks "is this proof correct?") -- read `references/critique.md` and follow its instructions
- **Write a proof** (user asks to prove something from scratch, "prove this", "write a proof of") -- read `references/write.md` and follow its instructions
- **Fix a proof** (a proof has identified issues that need repair) -- read `references/fix.md` and follow its instructions
- **Formalize a proof** (user wants a validated proof made publication-ready in LaTeX) -- read `references/formalize.md` and follow its instructions
- **Verify a formula or identity** (user wants to check a specific formula, algebraic step, or simplification) -- read `references/verify.md` and follow its instructions

After completing the selected workflow, return control. Do NOT chain multiple workflows -- the chain system handles sequencing.
