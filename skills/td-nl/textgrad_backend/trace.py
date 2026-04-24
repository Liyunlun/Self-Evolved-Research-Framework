"""Parse feedback-log.md into per-session DAGs of skill firings.

Supports both schema v2 (with session/node/upstream) and legacy v1 lines.
Legacy lines become isolated roots in a synthetic session named 'legacy'.
"""
from __future__ import annotations

import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterator, List, Optional, Tuple

# v3 block header: - [DATE] session:s1 node:n1 upstream:- skill:name (NO pipe)
_V3_HEAD_RE = re.compile(
    r"""^\s*-\s*
        \[(?P<date>\d{4}-\d{2}-\d{2})\]\s+
        session:(?P<session>\S+)\s+
        node:(?P<node>\S+)\s+
        upstream:(?P<upstream>\S+)\s+
        skill:(?P<skill>\S+)\s*$
    """,
    re.VERBOSE,
)
_V3_P1_RE = re.compile(r'^\s*P1_analysis\s*:\s*"(?P<v>.*)"\s*$')
_V3_P2_RE = re.compile(
    r'^\s*P2_predict\s*:\s*V\s*=\s*(?P<v>[\d.]+)\s*,\s*'
    r'conf\s*=\s*(?P<conf>high|med|medium|low)\s*,\s*'
    r'reason\s*=\s*"(?P<reason>.*)"\s*$'
)
_V3_P3_RE = re.compile(
    r'^\s*P3_td\s*:\s*delta\s*=\s*(?P<d>[+\-]?[\d.]+)\s*'
    r'(?:,\s*interp\s*=\s*"(?P<interp>.*)")?\s*$'
)
_V3_P4_RE = re.compile(
    r'^\s*P4_strategy\s*:\s*(?P<strategy>refine|keep|reset)\s*'
    r'(?:,\s*note\s*=\s*"(?P<note>.*)")?\s*$'
)
_V3_P5_RE = re.compile(
    r'^\s*P5_result\s*:\s*outcome\s*=\s*(?P<outcome>better|as_expected|worse)\s*,\s*'
    r'reward\s*=\s*(?P<reward>[+\-]?\d+)\s*'
    r'(?:,\s*ev\s*=\s*"(?P<ev>.*)")?\s*$'
)

# v2: - [DATE] session:s1 node:n1 upstream:n0,n2 skill:name | outcome:o | delta:d | "ev"
_V2_RE = re.compile(
    r"""^\s*-\s*
        \[(?P<date>\d{4}-\d{2}-\d{2})\]\s+
        session:(?P<session>\S+)\s+
        node:(?P<node>\S+)\s+
        upstream:(?P<upstream>\S+)\s+
        skill:(?P<skill>\S+)\s*\|\s*
        outcome:(?P<outcome>better|as_expected|worse)\s*\|\s*
        delta:(?P<delta>[+\-]?\d+)\s*\|\s*
        "(?P<evidence>.*)"\s*$
    """,
    re.VERBOSE,
)

# v1 legacy: - [DATE] skill:name | outcome:o | delta:d | "ev"
_V1_RE = re.compile(
    r"""^\s*-\s*
        \[(?P<date>\d{4}-\d{2}-\d{2})\]\s+
        skill:(?P<skill>\S+)\s*\|\s*
        outcome:(?P<outcome>better|as_expected|worse)\s*\|\s*
        delta:(?P<delta>[+\-]?\d+)\s*\|\s*
        "(?P<evidence>.*)"\s*$
    """,
    re.VERBOSE,
)


@dataclass
class TraceNode:
    date: str
    session: str
    node_id: str
    skill: str
    outcome: str
    delta: int
    evidence: str
    upstream: List[str] = field(default_factory=list)
    # filled in during graph construction:
    upstream_nodes: List["TraceNode"] = field(default_factory=list)
    # v3 5-phase fields (None when the block used v1/v2):
    analysis: Optional[str] = None
    predicted_V: Optional[float] = None
    predicted_conf: Optional[str] = None  # high | medium | low
    predict_reason: Optional[str] = None
    inline_td: Optional[float] = None
    td_interp: Optional[str] = None
    strategy: Optional[str] = None  # refine | keep | reset
    strategy_note: Optional[str] = None

    @property
    def reward(self) -> float:
        return float(self.delta)

    @property
    def is_v3(self) -> bool:
        return self.predicted_V is not None


@dataclass
class SessionGraph:
    session: str
    nodes: Dict[str, TraceNode] = field(default_factory=dict)

    def add(self, node: TraceNode) -> None:
        self.nodes[node.node_id] = node

    def topo_order(self) -> List[TraceNode]:
        """Kahn's algorithm. Cycles are broken by insertion order (should
        never happen in a well-formed session log but we stay robust)."""
        indeg: Dict[str, int] = {nid: 0 for nid in self.nodes}
        for n in self.nodes.values():
            for u in n.upstream:
                if u in self.nodes:
                    indeg[n.node_id] += 1
        ready = [nid for nid, d in indeg.items() if d == 0]
        ordered: List[TraceNode] = []
        seen = set()
        while ready:
            nid = ready.pop(0)
            if nid in seen:
                continue
            seen.add(nid)
            ordered.append(self.nodes[nid])
            for other in self.nodes.values():
                if nid in other.upstream and other.node_id not in seen:
                    indeg[other.node_id] -= 1
                    if indeg[other.node_id] == 0:
                        ready.append(other.node_id)
        # append any stragglers (cycle-breaking)
        for nid, n in self.nodes.items():
            if nid not in seen:
                ordered.append(n)
        return ordered

    def leaves(self) -> List[TraceNode]:
        """Nodes that no other node lists as upstream."""
        upstream_of: set = set()
        for n in self.nodes.values():
            upstream_of.update(n.upstream)
        return [n for nid, n in self.nodes.items() if nid not in upstream_of]

    def skills(self) -> List[str]:
        return sorted({n.skill for n in self.nodes.values()})


def _iter_pending_lines(text: str) -> Iterator[str]:
    """Yield lines inside the '## Pending Feedback' section only, skipping
    any HTML comment blocks (<!-- ... -->). Comments are used in the log to
    document the schema with inline examples; those must not be parsed as
    live G2 entries."""
    in_pending = False
    in_comment = False
    for raw_line in text.splitlines():
        stripped = raw_line.strip()
        if stripped.startswith("## Pending Feedback"):
            in_pending = True
            continue
        if in_pending and stripped.startswith("## "):
            break
        if not in_pending:
            continue

        # Strip comment regions from this line; may leave a non-comment residue.
        s = raw_line
        out_parts: List[str] = []
        while s:
            if in_comment:
                end = s.find("-->")
                if end == -1:
                    s = ""
                    break
                s = s[end + 3 :]
                in_comment = False
            else:
                start = s.find("<!--")
                if start == -1:
                    out_parts.append(s)
                    s = ""
                else:
                    out_parts.append(s[:start])
                    s = s[start + 4 :]
                    in_comment = True
        residue = "".join(out_parts)
        if residue.strip():
            yield residue


def _norm_conf(c: Optional[str]) -> Optional[str]:
    if c is None:
        return None
    return {"med": "medium", "high": "high", "medium": "medium", "low": "low"}.get(c, c)


def _build_v3_node(header_match: re.Match, body: List[str]) -> Optional[TraceNode]:
    """Assemble a TraceNode from a v3 header + body lines (P1..P5).
    Returns None if the mandatory P5_result line is missing."""
    d = header_match.groupdict()
    upstream = [] if d["upstream"] == "-" else d["upstream"].split(",")
    buf: Dict[str, object] = {
        "analysis": None,
        "predicted_V": None,
        "predicted_conf": None,
        "predict_reason": None,
        "inline_td": None,
        "td_interp": None,
        "strategy": None,
        "strategy_note": None,
        "outcome": None,
        "reward": None,
        "evidence": None,
    }
    for ln in body:
        m = _V3_P1_RE.match(ln)
        if m:
            buf["analysis"] = m.group("v")
            continue
        m = _V3_P2_RE.match(ln)
        if m:
            buf["predicted_V"] = float(m.group("v"))
            buf["predicted_conf"] = _norm_conf(m.group("conf"))
            buf["predict_reason"] = m.group("reason")
            continue
        m = _V3_P3_RE.match(ln)
        if m:
            buf["inline_td"] = float(m.group("d"))
            buf["td_interp"] = m.group("interp") or ""
            continue
        m = _V3_P4_RE.match(ln)
        if m:
            buf["strategy"] = m.group("strategy")
            buf["strategy_note"] = m.group("note") or ""
            continue
        m = _V3_P5_RE.match(ln)
        if m:
            buf["outcome"] = m.group("outcome")
            buf["reward"] = int(m.group("reward"))
            buf["evidence"] = m.group("ev") or ""
            continue
    if buf["outcome"] is None or buf["reward"] is None:
        return None
    return TraceNode(
        date=d["date"],
        session=d["session"],
        node_id=d["node"],
        skill=d["skill"],
        outcome=str(buf["outcome"]),
        delta=int(buf["reward"]),  # type: ignore[arg-type]
        evidence=str(buf["evidence"] or ""),
        upstream=upstream,
        analysis=buf["analysis"],  # type: ignore[arg-type]
        predicted_V=buf["predicted_V"],  # type: ignore[arg-type]
        predicted_conf=buf["predicted_conf"],  # type: ignore[arg-type]
        predict_reason=buf["predict_reason"],  # type: ignore[arg-type]
        inline_td=buf["inline_td"],  # type: ignore[arg-type]
        td_interp=buf["td_interp"],  # type: ignore[arg-type]
        strategy=buf["strategy"],  # type: ignore[arg-type]
        strategy_note=buf["strategy_note"],  # type: ignore[arg-type]
    )


def parse_feedback_log(path: str | Path) -> List[SessionGraph]:
    """Parse the 'Pending Feedback' section into per-session graphs.

    v3 blocks, v2 single-lines, and v1 legacy lines may be interleaved. The
    dispatcher looks at the first line of each '- [' entry: no '|' means v3
    block header, presence of '|' means v2 or v1 single-line."""
    text = Path(path).read_text(encoding="utf-8")
    lines = list(_iter_pending_lines(text))
    graphs: Dict[str, SessionGraph] = {}
    legacy_counter = 0
    i = 0
    while i < len(lines):
        line = lines[i]
        # v3 block header has no pipe
        if line.lstrip().startswith("- [") and "|" not in line:
            m = _V3_HEAD_RE.match(line)
            if m:
                body: List[str] = []
                j = i + 1
                while j < len(lines):
                    nxt = lines[j]
                    if nxt.lstrip().startswith("- ["):
                        break
                    body.append(nxt)
                    j += 1
                node = _build_v3_node(m, body)
                if node is not None:
                    g = graphs.setdefault(
                        node.session, SessionGraph(session=node.session)
                    )
                    g.add(node)
                i = j
                continue
        # v2 single-line
        m = _V2_RE.match(line)
        if m:
            d = m.groupdict()
            upstream = [] if d["upstream"] == "-" else d["upstream"].split(",")
            node = TraceNode(
                date=d["date"],
                session=d["session"],
                node_id=d["node"],
                skill=d["skill"],
                outcome=d["outcome"],
                delta=int(d["delta"]),
                evidence=d["evidence"],
                upstream=upstream,
            )
            g = graphs.setdefault(node.session, SessionGraph(session=node.session))
            g.add(node)
            i += 1
            continue
        # v1 legacy
        m = _V1_RE.match(line)
        if m:
            d = m.groupdict()
            legacy_counter += 1
            node = TraceNode(
                date=d["date"],
                session="legacy",
                node_id=f"legacy{legacy_counter}",
                skill=d["skill"],
                outcome=d["outcome"],
                delta=int(d["delta"]),
                evidence=d["evidence"],
                upstream=[],
            )
            g = graphs.setdefault("legacy", SessionGraph(session="legacy"))
            g.add(node)
        i += 1
    # resolve upstream_nodes references
    for g in graphs.values():
        for n in g.nodes.values():
            n.upstream_nodes = [g.nodes[u] for u in n.upstream if u in g.nodes]
    return list(graphs.values())
