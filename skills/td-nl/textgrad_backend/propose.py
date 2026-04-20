"""Write proposals produced by the backward pass into feedback-log.md.

Policy:
  - One PROPOSAL per session (pick highest |td_error| among 'hard' strength
    skills). This matches the existing one-edit-per-session invariant.
  - PROPOSAL is appended to the '## Pending Proposals' section; evolve-apply
    consumes it on user approval.
  - G2 entries are then moved from Pending Feedback to Processed Feedback
    with a cycle summary.
"""
from __future__ import annotations

import datetime as _dt
import re
from pathlib import Path
from typing import List, Optional

from .backward import BackwardResult, Proposal


PENDING_FEEDBACK_HEADER = "## Pending Feedback"
PENDING_PROPOSALS_HEADER = "## Pending Proposals"
PROCESSED_HEADER = "## Processed Feedback"


def _pick_proposal(results: List[BackwardResult]) -> Optional[Proposal]:
    best: Optional[Proposal] = None
    for r in results:
        for p in r.proposals:
            if best is None or abs(p.td_error) > abs(best.td_error):
                best = p
    return best


def _format_proposal(p: Proposal, date: str) -> str:
    # Keep the diff_text readable but bounded - we only preview first 2000 chars.
    preview = p.diff_text[:2000]
    if len(p.diff_text) > 2000:
        preview += "\n... (truncated; full candidate stored in evolve-apply staging)"
    return (
        f"- [{date}] PROPOSAL target:{p.skill} "
        f"(Q^L: {p.old_value:.2f}->{p.new_value:.2f}, td:{p.td_error:+.2f}, strength:{p.strength})\n"
        f"    problem: aggregated G2 evidence indicates sub-optimal behavior.\n"
        f"    gradient: |\n      {p.gradient_text.strip().replace(chr(10), chr(10)+'      ')}\n"
        f"    diff: |\n      {preview.replace(chr(10), chr(10)+'      ')}\n"
        f"    evidence: {p.evidence_summary}\n"
        f"    risk: {p.risk_note}\n"
    )


def _format_cycle_summary(results: List[BackwardResult], date: str) -> str:
    lines: List[str] = []
    for r in results:
        n_entries = sum(
            a.n_better + a.n_expected + a.n_worse for a in r.aggregates.values()
        )
        lines.append(
            f"- Cycle {date} [session:{r.session}]: {n_entries} entries across "
            f"{len(r.aggregates)} skills (V^L {r.v_l_old:.2f}->{r.v_l_new:.2f})"
        )
        for skill, a in sorted(r.aggregates.items()):
            lines.append(
                f"  - {skill}: net_delta={a.net_delta}, td_error={a.td_error:+.2f}, "
                f"strength={a.strength}"
            )
        has_prop = "yes" if r.proposals else "none"
        lines.append(f"  - Spec proposal: {has_prop}")
    return "\n".join(lines)


def _split_sections(text: str) -> dict:
    """Split feedback-log.md into named sections keyed by header line.
    Order is preserved in 'order' list."""
    sections: dict = {"__preamble__": []}
    order: List[str] = ["__preamble__"]
    current = "__preamble__"
    for line in text.splitlines():
        if line.startswith("## "):
            current = line.strip()
            sections[current] = []
            order.append(current)
        else:
            sections[current].append(line)
    return {"sections": sections, "order": order}


def _rebuild(sec: dict) -> str:
    out: List[str] = []
    for key in sec["order"]:
        if key == "__preamble__":
            out.extend(sec["sections"][key])
        else:
            out.append(key)
            out.extend(sec["sections"][key])
    return "\n".join(out).rstrip() + "\n"


def write_proposal(
    feedback_log: Path,
    results: List[BackwardResult],
    today: Optional[str] = None,
) -> Optional[str]:
    """Append proposal + cycle summary; move Pending -> Processed. Returns the
    proposal block that was written (or None if no proposal)."""
    date = today or _dt.date.today().isoformat()
    text = feedback_log.read_text(encoding="utf-8")
    sec = _split_sections(text)

    # collect pending G2 lines (non-comment, non-blank starting with '- [')
    pending_key = next((k for k in sec["order"] if k.startswith("## Pending Feedback")), None)
    processed_key = next((k for k in sec["order"] if k.startswith("## Processed Feedback")), None)
    proposals_key = next((k for k in sec["order"] if k.startswith("## Pending Proposals")), None)

    # 1) append proposal block (if any)
    proposal = _pick_proposal(results)
    block = None
    if proposal is not None and proposals_key is not None:
        block = _format_proposal(proposal, date)
        sec["sections"][proposals_key].append("")
        sec["sections"][proposals_key].extend(block.rstrip().splitlines())

    # 2) move pending G2 lines -> processed, stamp with cycle summary.
    #    v3 entries span multiple lines (header + indented P1..P5 body). We
    #    must move the WHOLE block, not just the header line, otherwise the
    #    body lines accumulate as orphans that poison later parses.
    if pending_key and processed_key:
        pending_lines = sec["sections"][pending_key]
        keep: List[str] = []
        moved: List[str] = []
        i = 0
        while i < len(pending_lines):
            line = pending_lines[i]
            if line.strip().startswith("- [") and "skill:" in line:
                # start of a G2 entry: attach indented body + trailing blank
                moved.append(line)
                i += 1
                while i < len(pending_lines):
                    nxt = pending_lines[i]
                    if nxt.startswith("    ") or nxt.startswith("\t"):
                        moved.append(nxt)
                        i += 1
                    else:
                        break
                # consume a single trailing blank for readability
                if i < len(pending_lines) and pending_lines[i].strip() == "":
                    i += 1
            elif line.strip() == "" or line.lstrip().startswith("<!--"):
                # preserve blanks and comment blocks in pending
                keep.append(line)
                i += 1
            else:
                # orphan body line left over from the pre-fix era: DROP rather
                # than keep. (A live entry always has a header above its body.)
                i += 1
        sec["sections"][pending_key] = keep
        if moved:
            sec["sections"][processed_key].append("")
            sec["sections"][processed_key].append(
                f"<!-- === cycle {date} === -->"
            )
            sec["sections"][processed_key].append(
                _format_cycle_summary(results, date)
            )
            sec["sections"][processed_key].append("<!-- moved G2 entries: -->")
            sec["sections"][processed_key].extend(moved)

    feedback_log.write_text(_rebuild(sec), encoding="utf-8")
    return block
