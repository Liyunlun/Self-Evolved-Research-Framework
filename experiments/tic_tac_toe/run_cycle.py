"""End-to-end TTT skill evolution cycle:

    1. Play N eval games (skill vs minimax, half each role) with current
       SKILL.md  -> game records saved.
    2. Write one v3 G2 entry per game to skills/td-nl/feedback-log.md,
       targeting skill:play-tic-tac-toe.
    3. Run evolve_textgrad with the Claude Code CLI engine; --apply-proposal
       so a PROPOSAL block lands in feedback-log.
    4. Rewrite SKILL.md with the new spec text from the proposal (archiving
       the previous version to experiments/tic_tac_toe/history/cycle-NNN/
       and to skills/td-nl/history/).
    5. Play N eval games with the evolved spec.
    6. Write a cycle report.

Usage:
    python -m experiments.tic_tac_toe.run_cycle --games-per-side 1 --cycle 1

The script is idempotent per --cycle index: it creates history/cycle-NNN/
if missing, else refuses to overwrite.
"""
from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import List, Optional, Tuple

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent.parent
sys.path.insert(0, str(HERE.parent))
sys.path.insert(0, str(REPO_ROOT / "skills" / "td-nl"))

from tic_tac_toe.arena import (  # type: ignore[import-not-found]
    GameRecord,
    grade_game,
    minimax_agent,
    play_one_game,
    skill_agent,
)
from tic_tac_toe.g2_writer import (  # type: ignore[import-not-found]
    SKILL_NAME,
    write_batch,
    write_selfplay_batch,
)
from tic_tac_toe.logging_engine import LoggingEngine  # type: ignore[import-not-found]

from textgrad_backend.engines import ClaudeCodeCLIEngine  # noqa: E402


SKILL_PATH = REPO_ROOT / "skills" / SKILL_NAME / "SKILL.md"
FEEDBACK_LOG = REPO_ROOT / "skills" / "td-nl" / "feedback-log.md"
TD_NL_HISTORY = REPO_ROOT / "skills" / "td-nl" / "history"
EXP_HISTORY = HERE / "history"


def play_selfplay_batch(
    engine: ClaudeCodeCLIEngine,
    n_games: int,
) -> List[Tuple[GameRecord, dict]]:
    """Play n_games self-play games (both sides use the current SKILL.md),
    grade each with minimax per-move. Returns [(record, grading), ...]."""
    out: List[Tuple[GameRecord, dict]] = []
    for i in range(n_games):
        x = skill_agent(engine, SKILL_PATH, name="skill-X")
        o = skill_agent(engine, SKILL_PATH, name="skill-O")
        print(f"  [self-play] game {i + 1}/{n_games}", flush=True)
        rec = play_one_game(x, o)
        grading = grade_game(rec)
        total = grading["X_mistakes"] + grading["O_mistakes"]
        print(
            f"    -> terminal={rec.terminal} winner={rec.winner} "
            f"moves={len(rec.moves)} mistakes=X{grading['X_mistakes']}+O{grading['O_mistakes']}={total}",
            flush=True,
        )
        out.append((rec, grading))
    return out


def summarize_selfplay(graded: List[Tuple[GameRecord, dict]]) -> dict:
    out = {
        "games": len(graded),
        "forfeits": 0,
        "decisive_wins": 0,
        "draws": 0,
        "total_moves": 0,
        "total_mistakes": 0,
        "clean_games": 0,  # no mistakes
    }
    for rec, grading in graded:
        if rec.terminal == "forfeit":
            out["forfeits"] += 1
        elif rec.terminal == "draw":
            out["draws"] += 1
        else:
            out["decisive_wins"] += 1
        m = grading["X_mistakes"] + grading["O_mistakes"]
        out["total_mistakes"] += m
        out["total_moves"] += grading["X_moves"] + grading["O_moves"]
        if m == 0 and rec.terminal != "forfeit":
            out["clean_games"] += 1
    out["mistake_rate"] = out["total_mistakes"] / max(1, out["total_moves"])
    return out


def play_eval_batch(
    engine: ClaudeCodeCLIEngine,
    games_per_side: int,
) -> List[Tuple[GameRecord, str]]:
    """Play `games_per_side` games with skill as X, then as O. Returns
    list of (record, skill_side) pairs in order."""
    mm = minimax_agent(name="minimax")
    out: List[Tuple[GameRecord, str]] = []
    for i in range(games_per_side):
        sk = skill_agent(engine, SKILL_PATH, name="skill")
        print(f"  [eval] game X{i + 1}/{games_per_side} (skill=X)", flush=True)
        rec = play_one_game(sk, mm)
        print(
            f"    -> terminal={rec.terminal} winner={rec.winner} "
            f"moves={len(rec.moves)}",
            flush=True,
        )
        out.append((rec, "X"))
    for i in range(games_per_side):
        sk = skill_agent(engine, SKILL_PATH, name="skill")
        print(f"  [eval] game O{i + 1}/{games_per_side} (skill=O)", flush=True)
        rec = play_one_game(mm, sk)
        print(
            f"    -> terminal={rec.terminal} winner={rec.winner} "
            f"moves={len(rec.moves)}",
            flush=True,
        )
        out.append((rec, "O"))
    return out


def summarize(records: List[Tuple[GameRecord, str]]) -> dict:
    counts = {"draw": 0, "win": 0, "loss": 0, "forfeit": 0}
    for rec, side in records:
        if rec.terminal == "forfeit":
            if rec.forfeit_side == side:
                counts["forfeit"] += 1
            else:
                counts["win"] += 1  # opponent forfeited
        elif rec.terminal == "draw":
            counts["draw"] += 1
        else:
            if rec.winner == side:
                counts["win"] += 1
            else:
                counts["loss"] += 1
    counts["total"] = len(records)
    counts["draw_rate"] = counts["draw"] / max(1, counts["total"])
    counts["forfeit_rate"] = counts["forfeit"] / max(1, counts["total"])
    return counts


def games_to_jsonl(records: List[Tuple[GameRecord, str]]) -> str:
    lines = []
    for rec, side in records:
        d = rec.to_dict()
        d["skill_side"] = side
        lines.append(json.dumps(d, ensure_ascii=False))
    return "\n".join(lines) + "\n"


def extract_last_proposal(feedback_log: Path) -> str:
    """Return the text of the most recent PROPOSAL block in Pending Proposals."""
    text = feedback_log.read_text(encoding="utf-8")
    marker = "## Pending Proposals"
    if marker not in text:
        return ""
    rest = text[text.index(marker) + len(marker) :]
    end = rest.find("\n## ")
    section = rest if end == -1 else rest[:end]
    blocks = [b for b in section.split("\n- [") if "PROPOSAL" in b]
    if not blocks:
        return ""
    return "- [" + blocks[-1].rstrip()


def extract_proposal_spec(proposal_block: str) -> str:
    """Pull the `diff:` field contents out of a PROPOSAL block.
    propose._format_proposal emits the diff as a YAML block-literal:
        diff: |
          <line 1>
          <line 2>
          ...
          evidence: ...
    where nested spec lines are indented 6 spaces and the next sibling
    field (evidence/risk) is indented 4 spaces. We dedent 6 and stop at
    the first line indented < 6 (sibling-field boundary).
    """
    lines = proposal_block.splitlines()
    # find "    diff: |" opener
    start = None
    for i, ln in enumerate(lines):
        if ln.lstrip().startswith("diff:"):
            start = i + 1
            break
    if start is None:
        return ""
    out: list[str] = []
    for ln in lines[start:]:
        stripped = ln[6:] if ln.startswith("      ") else None
        if stripped is None:
            # end of block-literal (sibling field or out-dent)
            break
        out.append(stripped)
    # truncation marker added by _format_proposal
    while out and out[-1].startswith("... (truncated"):
        out.pop()
    return "\n".join(out).rstrip() + "\n"


def _apply_proposal_if_ours(
    cycle: int,
    skill_before_text: str,
    cycle_dir: Path,
    game_idx: Optional[int] = None,
) -> tuple[bool, str, str]:
    """If the latest PROPOSAL in feedback-log targets our skill, apply it.
    Returns (applied, new_spec_text, proposal_text).  proposal_text is empty
    when no matching proposal exists."""
    proposal = extract_last_proposal(FEEDBACK_LOG)
    if not proposal or f"target:{SKILL_NAME}" not in proposal:
        return (False, skill_before_text, proposal or "")
    new_spec = extract_proposal_spec(proposal) or skill_before_text
    if new_spec == skill_before_text:
        return (False, skill_before_text, proposal)
    TD_NL_HISTORY.mkdir(exist_ok=True)
    import time as _t

    game_tag = f"-g{game_idx:02d}" if game_idx else ""
    tag = f"c{cycle:03d}{game_tag}-{int(_t.time())}"
    archive = TD_NL_HISTORY / f"{SKILL_NAME}-{tag}.md"
    archive.write_text(skill_before_text, encoding="utf-8")
    SKILL_PATH.write_text(new_spec, encoding="utf-8")
    return (True, new_spec, proposal)


def run_online_evolve_cycle(
    cycle: int,
    n_games: int,
    model: str,
    timeout: float,
) -> int:
    """Play n_games self-play games; after EACH game, run evolve_textgrad
    --apply-proposal and apply the proposal if it targets the TTT skill."""
    cycle_dir = EXP_HISTORY / f"cycle-{cycle:03d}"
    if cycle_dir.exists():
        print(f"[cycle] {cycle_dir} exists; refusing to overwrite", file=sys.stderr)
        return 2
    cycle_dir.mkdir(parents=True)
    versions_dir = cycle_dir / "versions"
    versions_dir.mkdir()

    # Wrap the engine with a logger so every CLI call (both in-game moves and
    # TGD evolve notes) is recorded to engine-calls.jsonl
    raw_engine = ClaudeCodeCLIEngine(model=model, timeout=timeout)
    engine = LoggingEngine(
        raw_engine,
        log_path=cycle_dir / "engine-calls.jsonl",
        label="arena+tgd",
    )
    script = REPO_ROOT / "scripts" / "evolve_textgrad.py"

    # pre-flush any foreign pending entries
    log_text = FEEDBACK_LOG.read_text(encoding="utf-8")
    pstart = log_text.index("## Pending Feedback")
    rest = log_text[pstart + 1 :]
    nxt = rest.find("\n## ")
    pend = rest[:nxt] if nxt != -1 else rest
    if any(ln.strip().startswith("- [") and "skill:" in ln for ln in pend.splitlines()):
        print(f"[cycle {cycle}] pre-flushing foreign pending entries")
        pre = subprocess.run(
            [sys.executable, str(script), "--apply-proposal", "--no-engine"],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=300,
        )
        (cycle_dir / "pre-flush.stdout.txt").write_text(pre.stdout, encoding="utf-8")
        (cycle_dir / "pre-flush.stderr.txt").write_text(pre.stderr, encoding="utf-8")

    # snapshot v0 (game-0 = starting spec)
    skill_v0 = SKILL_PATH.read_text(encoding="utf-8")
    (versions_dir / "after-game-00.md").write_text(skill_v0, encoding="utf-8")
    (cycle_dir / "skill-before.md").write_text(skill_v0, encoding="utf-8")

    # Snapshot the current per-skill Q^L (skill-values) BEFORE the cycle
    sv_dir = REPO_ROOT / "skills" / "td-nl" / "skill-values"
    sv_before = sv_dir / f"{SKILL_NAME}.md"
    (cycle_dir / "skill-values-before.md").write_text(
        sv_before.read_text(encoding="utf-8") if sv_before.exists() else "",
        encoding="utf-8",
    )

    applied_log: List[dict] = []
    all_graded: List[Tuple[GameRecord, dict]] = []
    games_jsonl = cycle_dir / "games-selfplay.jsonl"
    games_jsonl.write_text("", encoding="utf-8")  # truncate for append

    for i in range(n_games):
        game_idx = i + 1
        print(f"[cycle {cycle}] game {game_idx}/{n_games}", flush=True)
        graded = play_selfplay_batch(engine, 1)
        rec, grading = graded[0]
        all_graded.append((rec, grading))

        # incremental games.jsonl
        with games_jsonl.open("a", encoding="utf-8") as fh:
            d = rec.to_dict()
            d["grading"] = grading
            d["game_idx"] = game_idx
            fh.write(json.dumps(d, ensure_ascii=False) + "\n")

        # append 1 G2 entry with a fresh session_id per game so the td layer
        # treats each game as its own session (no cross-game TD chain)
        session_id = f"ttt-c{cycle:03d}-g{game_idx:02d}"
        blocks = write_selfplay_batch(FEEDBACK_LOG, graded, session_id=session_id)
        (cycle_dir / f"g2-g{game_idx:02d}.md").write_text(
            "\n".join(blocks) + "\n", encoding="utf-8"
        )

        # run evolve with --json so we capture the full structured TD state
        before = SKILL_PATH.read_text(encoding="utf-8")
        ev = subprocess.run(
            [
                sys.executable, str(script),
                "--apply-proposal", "--json",
                "--engine-model", model,
            ],
            capture_output=True, text=True, cwd=str(REPO_ROOT), timeout=600,
        )
        (cycle_dir / f"evolve-g{game_idx:02d}.stdout.txt").write_text(
            ev.stdout, encoding="utf-8"
        )
        (cycle_dir / f"evolve-g{game_idx:02d}.stderr.txt").write_text(
            ev.stderr, encoding="utf-8"
        )
        # Parse JSON from stdout. evolve_textgrad.py emits the proposal
        # block (may contain braces inside indented spec text) BEFORE the
        # JSON summary. The JSON summary starts with "{" at line-start.
        # Find the LAST newline-followed-by-brace to locate the JSON start.
        td_json = None
        try:
            jstart = ev.stdout.rfind("\n{")
            jstart = (jstart + 1) if jstart != -1 else ev.stdout.find("{")
            td_json = json.loads(ev.stdout[jstart:])
            (cycle_dir / f"evolve-g{game_idx:02d}.td.json").write_text(
                json.dumps(td_json, indent=2, ensure_ascii=False), encoding="utf-8"
            )
        except (ValueError, json.JSONDecodeError) as e:
            (cycle_dir / f"evolve-g{game_idx:02d}.td.json").write_text(
                json.dumps({"parse_error": str(e), "stdout_tail": ev.stdout[-1000:]}),
                encoding="utf-8",
            )

        applied, after, proposal_text = _apply_proposal_if_ours(
            cycle, before, cycle_dir, game_idx=game_idx
        )
        (versions_dir / f"after-game-{game_idx:02d}.md").write_text(after, encoding="utf-8")
        if proposal_text:
            (cycle_dir / f"proposal-g{game_idx:02d}.md").write_text(
                proposal_text, encoding="utf-8"
            )
        # also snapshot skill-values after this game for visibility
        if sv_before.exists():
            (cycle_dir / f"skill-values-g{game_idx:02d}.md").write_text(
                sv_before.read_text(encoding="utf-8"), encoding="utf-8"
            )

        xm = grading["X_mistakes"]
        om = grading["O_mistakes"]
        # Pull the headline TD stats out of the JSON for a compact summary row
        td_row = {}
        if td_json and td_json.get("sessions"):
            s0 = td_json["sessions"][0]
            skills = s0.get("skills", {})
            sk = skills.get(SKILL_NAME, {})
            td_row = {
                "v_l_old": s0.get("v_l_old"),
                "v_l_new": s0.get("v_l_new"),
                "td_error": sk.get("td_error"),
                "strength": sk.get("strength"),
                "V": sk.get("V"),
                "V_next": sk.get("V_next"),
                "net_delta": sk.get("net_delta"),
                "confidence": sk.get("confidence"),
                "n_proposals": len(s0.get("proposals", [])),
            }
        applied_log.append({
            "game": game_idx,
            "session_id": session_id,
            "terminal": rec.terminal,
            "winner": rec.winner,
            "x_mistakes": xm,
            "o_mistakes": om,
            "forfeit_side": rec.forfeit_side,
            "applied": applied,
            "spec_len_before": len(before),
            "spec_len_after": len(after),
            **td_row,
        })
        tag = "APPLIED" if applied else "no-edit"
        print(
            f"  -> {tag} terminal={rec.terminal} winner={rec.winner} "
            f"mistakes={xm+om} td={td_row.get('td_error')} "
            f"strength={td_row.get('strength')} "
            f"spec_len {len(before)}->{len(after)}",
            flush=True,
        )
        # flush applied_log each iter for live inspection
        (cycle_dir / "applied-log.json").write_text(
            json.dumps(applied_log, indent=2), encoding="utf-8"
        )

    (cycle_dir / "skill-after.md").write_text(
        SKILL_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )
    # Also snapshot the final skill-values Q^L file
    if sv_before.exists():
        (cycle_dir / "skill-values-after.md").write_text(
            sv_before.read_text(encoding="utf-8"), encoding="utf-8"
        )

    summary = summarize_selfplay(all_graded)
    edits = sum(1 for r in applied_log if r["applied"])
    report = [
        f"# Cycle {cycle} — {SKILL_NAME} (online-evolve, n={n_games})",
        "",
        f"- model: {model}",
        f"- games: {n_games}",
        f"- per-game batch summary: {summary}",
        f"- edits applied: {edits}/{n_games}",
        "",
        "## Per-game log",
    ]
    for r in applied_log:
        report.append(
            f"- g{r['game']:02d}: terminal={r['terminal']} winner={r['winner']} "
            f"mistakes=X{r['x_mistakes']}+O{r['o_mistakes']} "
            f"applied={'YES' if r['applied'] else 'no'} "
            f"spec_len {r['spec_len_before']}->{r['spec_len_after']}"
        )
    (cycle_dir / "report.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    (cycle_dir / "eval.json").write_text(
        json.dumps(
            {
                "cycle": cycle,
                "mode": "online-evolve",
                "games": n_games,
                "edits_applied": edits,
                "model": model,
                "summary": summary,
            },
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"[cycle {cycle}] done. Edits applied: {edits}/{n_games}. Artifacts at {cycle_dir}")
    return 0


def run_cycle(
    cycle: int,
    games_per_side: int,
    model: str,
    timeout: float,
    self_play_games: int = 0,
) -> int:
    cycle_dir = EXP_HISTORY / f"cycle-{cycle:03d}"
    if cycle_dir.exists():
        print(f"[cycle] {cycle_dir} exists; refusing to overwrite", file=sys.stderr)
        return 2
    cycle_dir.mkdir(parents=True)

    engine = ClaudeCodeCLIEngine(model=model, timeout=timeout)
    script = REPO_ROOT / "scripts" / "evolve_textgrad.py"

    # Step 0a: pre-flush any non-TTT pending entries so our proposal isn't
    # outvoted by older sessions' max|td|.
    log_text = FEEDBACK_LOG.read_text(encoding="utf-8")
    pending_start = log_text.index("## Pending Feedback")
    pending_end_marker = "\n## "
    rest = log_text[pending_start + 1 :]
    next_sec = rest.find(pending_end_marker)
    pending_section = rest[:next_sec] if next_sec != -1 else rest
    has_preexisting = any(
        ln.strip().startswith("- [") and "skill:" in ln
        for ln in pending_section.splitlines()
    )
    if has_preexisting:
        print(f"[cycle {cycle}] pre-flushing existing pending G2 entries")
        pre = subprocess.run(
            [sys.executable, str(script), "--apply-proposal", "--no-engine"],
            capture_output=True,
            text=True,
            cwd=str(REPO_ROOT),
            timeout=300,
        )
        (cycle_dir / "pre-flush.stdout.txt").write_text(
            pre.stdout, encoding="utf-8"
        )
        (cycle_dir / "pre-flush.stderr.txt").write_text(
            pre.stderr, encoding="utf-8"
        )
        print(f"  pre-flush rc={pre.returncode}")

    # Step 0b: snapshot skill-before
    skill_before_text = SKILL_PATH.read_text(encoding="utf-8")
    (cycle_dir / "skill-before.md").write_text(skill_before_text, encoding="utf-8")
    print(f"[cycle {cycle}] snapshotted skill-before.md")

    # Step 1: generate training data
    session_id = f"ttt-c{cycle:03d}"
    if self_play_games > 0:
        print(f"[cycle {cycle}] self-play training: {self_play_games} games")
        graded = play_selfplay_batch(engine, self_play_games)
        lines = []
        for rec, grading in graded:
            d = rec.to_dict()
            d["grading"] = grading
            lines.append(json.dumps(d, ensure_ascii=False))
        (cycle_dir / "games-selfplay.jsonl").write_text(
            "\n".join(lines) + "\n", encoding="utf-8"
        )
        summary_before = summarize_selfplay(graded)
        print(f"  summary_selfplay: {summary_before}")
        print(f"[cycle {cycle}] writing {len(graded)} G2 entries to feedback-log")
        blocks = write_selfplay_batch(FEEDBACK_LOG, graded, session_id=session_id)
    else:
        print(
            f"[cycle {cycle}] eval v_before "
            f"({games_per_side} games X + {games_per_side} games O)"
        )
        records_before = play_eval_batch(engine, games_per_side)
        (cycle_dir / "games-before.jsonl").write_text(
            games_to_jsonl(records_before), encoding="utf-8"
        )
        summary_before = summarize(records_before)
        print(f"  summary_before: {summary_before}")
        print(f"[cycle {cycle}] writing {len(records_before)} G2 entries to feedback-log")
        blocks = write_batch(FEEDBACK_LOG, records_before, session_id=session_id)
    (cycle_dir / "g2-entries.md").write_text("\n".join(blocks) + "\n", encoding="utf-8")

    # Step 3: run evolve_textgrad --apply-proposal
    print(f"[cycle {cycle}] running evolve_textgrad --apply-proposal")
    proc = subprocess.run(
        [sys.executable, str(script), "--apply-proposal", "--engine-model", model],
        capture_output=True,
        text=True,
        cwd=str(REPO_ROOT),
        timeout=600,
    )
    (cycle_dir / "evolve.stdout.txt").write_text(proc.stdout, encoding="utf-8")
    (cycle_dir / "evolve.stderr.txt").write_text(proc.stderr, encoding="utf-8")
    if proc.returncode != 0:
        print(f"  evolve_textgrad failed: rc={proc.returncode}", file=sys.stderr)
        print(proc.stderr[:1000], file=sys.stderr)
        return 3
    print("  evolve_textgrad ok")

    # Step 4: extract proposal + apply to SKILL.md
    proposal = extract_last_proposal(FEEDBACK_LOG)
    (cycle_dir / "proposal.md").write_text(proposal, encoding="utf-8")
    if f"target:{SKILL_NAME}" not in proposal:
        print(
            f"[cycle {cycle}] no PROPOSAL for '{SKILL_NAME}' in this cycle "
            "(td strength may not have hit 'hard'); leaving SKILL.md unchanged.",
            flush=True,
        )
        new_spec = skill_before_text
    else:
        # Archive to skills/td-nl/history/
        TD_NL_HISTORY.mkdir(exist_ok=True)
        archive = TD_NL_HISTORY / f"{SKILL_NAME}-v{cycle}.md"
        archive.write_text(skill_before_text, encoding="utf-8")
        # Apply the diff_text from the proposal
        new_spec = extract_proposal_spec(proposal) or skill_before_text
        if new_spec == skill_before_text:
            print(
                f"[cycle {cycle}] proposal diff was empty; leaving SKILL.md unchanged.",
                flush=True,
            )
        else:
            SKILL_PATH.write_text(new_spec, encoding="utf-8")
            print(f"[cycle {cycle}] wrote evolved SKILL.md (archived to {archive})")
    (cycle_dir / "skill-after.md").write_text(
        SKILL_PATH.read_text(encoding="utf-8"), encoding="utf-8"
    )

    # Step 5: eval v_after (skip in self-play mode to keep cycle cost bounded;
    # run a separate cycle with games_per_side > 0 to evaluate).
    if self_play_games > 0:
        summary_after = {"skipped": True, "reason": "self-play mode; run separate eval cycle"}
        print(f"[cycle {cycle}] eval v_after skipped (self-play mode)")
    else:
        print(f"[cycle {cycle}] eval v_after")
        records_after = play_eval_batch(engine, games_per_side)
        (cycle_dir / "games-after.jsonl").write_text(
            games_to_jsonl(records_after), encoding="utf-8"
        )
        summary_after = summarize(records_after)
        print(f"  summary_after: {summary_after}")

    # Step 6: write report
    eval_json = {
        "cycle": cycle,
        "mode": "self-play" if self_play_games > 0 else "vs-minimax",
        "games_per_side": games_per_side,
        "self_play_games": self_play_games,
        "model": model,
        "before": summary_before,
        "after": summary_after,
    }
    (cycle_dir / "eval.json").write_text(
        json.dumps(eval_json, indent=2), encoding="utf-8"
    )
    mode = "self-play" if self_play_games > 0 else "vs-minimax"
    report_lines = [
        f"# Cycle {cycle} report — {SKILL_NAME} ({mode})",
        "",
        f"- model: {model}",
        f"- self-play games: {self_play_games}" if self_play_games else f"- games per side: {games_per_side}",
        "",
        "## Training-batch summary",
        f"- {summary_before}",
        "",
        "## After",
        f"- {summary_after}",
    ]
    if self_play_games == 0:
        delta_w = summary_after["win"] - summary_before["win"]
        delta_d = summary_after["draw"] - summary_before["draw"]
        delta_l = summary_after["loss"] - summary_before["loss"]
        delta_f = summary_after["forfeit"] - summary_before["forfeit"]
        report_lines += [
            "",
            "## Delta",
            f"- wins: {delta_w:+d}  draws: {delta_d:+d}  losses: {delta_l:+d}  forfeits: {delta_f:+d}",
        ]
    (cycle_dir / "report.md").write_text("\n".join(report_lines) + "\n", encoding="utf-8")

    print(f"[cycle {cycle}] done. Artifacts at {cycle_dir}")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--cycle", type=int, required=True)
    ap.add_argument("--games-per-side", type=int, default=1)
    ap.add_argument(
        "--self-play",
        type=int,
        default=0,
        help="N self-play games (both sides use current skill; minimax-graded).",
    )
    ap.add_argument(
        "--online-evolve",
        action="store_true",
        help="With --self-play N: run evolve_textgrad after EVERY game and "
             "apply the proposal if it targets the TTT skill. Per-game "
             "spec snapshots saved to history/cycle-NNN/versions/.",
    )
    ap.add_argument("--model", default="haiku")
    ap.add_argument("--timeout", type=float, default=180.0)
    args = ap.parse_args(argv)
    if args.online_evolve:
        if args.self_play <= 0:
            print("--online-evolve requires --self-play N > 0", file=sys.stderr)
            return 2
        return run_online_evolve_cycle(
            cycle=args.cycle,
            n_games=args.self_play,
            model=args.model,
            timeout=args.timeout,
        )
    return run_cycle(
        cycle=args.cycle,
        games_per_side=args.games_per_side,
        model=args.model,
        timeout=args.timeout,
        self_play_games=args.self_play,
    )


if __name__ == "__main__":
    sys.exit(main())
