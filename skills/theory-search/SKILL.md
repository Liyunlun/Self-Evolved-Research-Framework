---
name: theory-search
description: Search across mathematical domains (spectral graph theory, functional analysis, information geometry, etc.) for known results or techniques that apply to the user's problem. Triggers on "is there a known result for...", "I'm stuck on this step", or when the user needs cross-domain technique transfer.
---

# theory-search

**Trigger**: User is stuck on a proof step, asks "is there a known result for...", or needs cross-domain techniques.

**Process**:
1. Identify the mathematical structure of the problem
2. Search across domains:
   - Spectral graph theory, functional analysis, optimization
   - Information geometry, statistical learning theory
   - Topology, algebra (if relevant)
3. For each candidate result:
   - State the theorem with reference
   - Assess applicability (direct / needs adaptation / inspirational)
   - Sketch how to apply it
4. Rank by relevance and feasibility

**Inputs**: Problem description + what's been tried
**Outputs**: Cross-domain technique report (inline)
**Token**: ~3-8K
**Composition**: Found applicable theorem → suggest `theory-formalize` to adapt it
