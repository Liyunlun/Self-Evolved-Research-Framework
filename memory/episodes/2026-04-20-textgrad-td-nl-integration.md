---
name: 2026-04-20 TextGrad x TD-NL integration
description: Session delivering the textgrad_backend package, v3 5-phase G2 schema, and the example-driven walkthrough PDF.
type: episodic
tier: episode
session_date: 2026-04-20
tags: [textgrad, td-nl, evolve-suggest, skill-evolution, pdf-report]
---

## Context

User asked for (in order):

1. Find TextGrad literature and explain how it fits the existing TD-NL framework.
2. Implement option C (Trace-ification): make TD-NL run on top of TextGrad via a DAG.
3. Confirm whether TD-NL flow matches a 5-phase reflection template (ANALYSIS / VALUE PREDICTION / TD / STRATEGY / EXECUTION); selected option C — upgrade G2 to 5-phase inline (v3).
4. Explain what was built in detail (technical depth).
5. Produce an example-driven complete mechanism explanation.
6. End the session, record the summary task, generate a PDF with two examples.

## What shipped (commit ae4b157)

- skills/td-nl/textgrad_backend/ — variables.py (real + shim Variable/TextLoss/TGD), trace.py (v1/v2/v3 parser + Kahn DAG), td_layer.py (TD(0) aggregation + strength gates), backward.py (spec_var + firing_var dual-layer graph), propose.py (single-proposal per session), test_smoke.py (4 offline tests).
- scripts/evolve_textgrad.py — CLI (--dry-run / --apply-proposal / --gamma / --json).
- skills/_shared/evolve-cycle.md — rewrote G2 section for v3 5-phase and TD(0) layer documentation.
- skills/evolve-suggest/SKILL.md — preferred Python CLI path + manual 6-phase fallback.
- skills/td-nl/feedback-log.md — schema v3 header comments, Pending Proposals section formalized.

## What also shipped post-commit (this session continuation)

- scripts/make_session_pdf.py — fpdf2 + CJK/Latin fallback font PDF generator.
- outputs/session-artifacts/2026-04-20-textgrad-td-nl-walkthrough.pdf — two worked examples (paper-read TextGrad chain + this session's summarize-project chain).

## Key decisions

- One-edit-per-session invariant preserved: propose.py picks max|td| hard skill only.
- V(s') prefers mean(P2.V) from v3 blocks; bootstrap retained as fallback.
- Inline TD and batch TD blended 50/50.
- Shim fallback keeps the pipeline runnable without a real textgrad install (CI-safe).
- Smoke test's last v3 case proves P2.conf=high can override entry-count bin (2 entries would default to low), pushing evolve-suggest td from -2.775 to -2.925.

## User feedback captured

- "这个记录非常有用" — the example-driven explanation was highly valued; next time default to numeric walkthroughs when explaining mechanism.
