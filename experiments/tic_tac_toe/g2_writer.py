"""Convert TTT game records into v3 G2 entries appended to feedback-log.md.

One G2 entry per game from the skill's perspective. Entries within a batch
are linked as an upstream chain (n1 -> n2 -> ...) so the TD layer can
propagate reward across consecutive games.

v3 schema (5-phase block, 6 lines):
    - [DATE] session:{sid} node:{nid} upstream:{csv|-} skill:{name}
        P1_analysis: "..."
        P2_predict:  V={1-10}, conf={high|med|low}, reason="..."
        P3_td:       delta={float}, interp="..."    # omitted on root
        P4_strategy: {refine|keep|reset}, note="..."
        P5_result:   outcome={better|as_expected|worse}, reward={+1|0|-1}, ev="..."
"""
from __future__ import annotations

import datetime as _dt
from pathlib import Path
from typing import List

from .arena import GameRecord


SKILL_NAME = "play-tic-tac-toe"


def _pred_v_and_conf(game_index: int, forfeit_so_far: int) -> tuple[int, str]:
    """Self-estimate of Q^L before this game. Drops as we rack up failures."""
    base = 4
    if forfeit_so_far >= 1:
        return (2, "high")
    if game_index == 0:
        return (base, "med")
    return (base, "high")


def _classify(record: GameRecord, skill_side: str) -> tuple[str, int, str]:
    """Return (outcome, reward, strategy) from the skill's perspective.

    outcome in {better, as_expected, worse}; reward in {+1, 0, -1};
    strategy in {keep, refine, reset}.
    """
    if record.terminal == "forfeit":
        if record.forfeit_side == skill_side:
            return ("worse", -1, "refine")
        else:
            return ("better", +1, "keep")
    if record.terminal == "draw":
        return ("better", 0, "keep")  # drawing minimax IS the goal
    # win path
    if record.winner == skill_side:
        return ("better", +1, "keep")
    return ("worse", -1, "refine")


def _evidence(record: GameRecord, skill_side: str) -> str:
    moves_str = " ".join(f"{m.symbol}{m.cell}" for m in record.moves)
    parts = [
        f"skill={skill_side}",
        f"result={record.terminal}",
        f"winner={record.winner or 'draw'}",
        f"moves=[{moves_str}]",
    ]
    if record.terminal == "forfeit":
        parts.append(f"forfeit_side={record.forfeit_side}")
        last_move = record.moves[-1] if record.moves else None
        last_raw = ""
        if record.forfeit_reason and "last_raw=" in record.forfeit_reason:
            last_raw = record.forfeit_reason.split("last_raw=", 1)[1]
            last_raw = last_raw.strip("\"'")[:120]
        if last_raw:
            parts.append(f"bad_output={last_raw!r}")
    # escape double-quotes in evidence
    return "; ".join(parts).replace('"', "'")


def build_g2_block(
    session_id: str,
    node_id: str,
    upstream: List[str],
    record: GameRecord,
    skill_side: str,
    game_index: int,
    forfeit_so_far: int,
    prior_reward: int,
) -> str:
    date = _dt.date.today().isoformat()
    v, conf = _pred_v_and_conf(game_index, forfeit_so_far)
    outcome, reward, strategy = _classify(record, skill_side)
    evidence = _evidence(record, skill_side)
    analysis = (
        f"Game {game_index + 1} of batch; skill plays {skill_side} vs minimax. "
        f"Trajectory: {len(record.moves)} moves, terminal={record.terminal}."
    )
    if record.terminal == "forfeit" and record.forfeit_side == skill_side:
        analysis += " Skill FAILED to emit a legal move - output-format issue."
    elif record.terminal == "win" and record.winner != skill_side:
        analysis += " Skill lost to perfect play - tactical gap."

    predict_line = f'V={v}, conf={conf}, reason="self-estimate pre-game from running forfeit rate"'

    strategy_note = ""
    if record.terminal == "forfeit" and record.forfeit_side == skill_side:
        strategy_note = "tighten response-format instruction in spec"
    elif outcome == "worse":
        strategy_note = "add strategic heuristics (center, corners, forks)"
    strategy_line = f'{strategy}, note="{strategy_note}"'

    upstream_str = ",".join(upstream) if upstream else "-"
    header = (
        f"- [{date}] session:{session_id} node:{node_id} "
        f"upstream:{upstream_str} skill:{SKILL_NAME}"
    )
    lines = [header]
    lines.append(f'    P1_analysis: "{analysis}"')
    lines.append(f"    P2_predict:  {predict_line}")
    if upstream:
        # TD delta on non-root nodes: (this reward) - (prior reward)
        # gives a simple scalar surprise without forward value lookup
        delta = reward - prior_reward
        lines.append(
            f'    P3_td:       delta={delta:+.1f}, interp="reward change vs prior game"'
        )
    lines.append(f"    P4_strategy: {strategy_line}")
    lines.append(
        f'    P5_result:   outcome={outcome}, reward={reward:+d}, ev="{evidence}"'
    )
    return "\n".join(lines)


def build_selfplay_block(
    session_id: str,
    node_id: str,
    upstream: List[str],
    record: GameRecord,
    grading: dict,
    game_index: int,
    prior_reward: int,
) -> str:
    """G2 entry for a SELF-PLAY game graded by minimax per-move.
    Reward is derived from per-game mistake count (summed across both sides
    since both sides used the same skill):
        reward = +1  if total_mistakes == 0
        reward =  0  if total_mistakes == 1
        reward = -1  if total_mistakes >= 2  OR any forfeit
    """
    date = _dt.date.today().isoformat()
    xm = grading.get("X_mistakes", 0)
    om = grading.get("O_mistakes", 0)
    total_mistakes = xm + om
    is_forfeit = record.terminal == "forfeit"

    if is_forfeit:
        reward = -1
        outcome = "worse"
        strategy = "refine"
        strategy_note = "tighten response-format instruction in spec (forfeit observed)"
    elif total_mistakes == 0:
        reward = +1
        outcome = "better"
        strategy = "keep"
        strategy_note = ""
    elif total_mistakes == 1:
        reward = 0
        outcome = "as_expected"
        strategy = "refine"
        strategy_note = "add guidance for the tactical pattern that was missed"
    else:
        reward = -1
        outcome = "worse"
        strategy = "refine"
        strategy_note = "add tactical strategy heuristics (center, corners, forks, blocks)"

    # self-estimate Q^L before game — drop prior expectation if we've seen mistakes
    base_v = 5 if game_index == 0 else (6 if prior_reward >= 0 else 4)
    conf = "high" if game_index >= 2 else "med"

    analysis = (
        f"Self-play game {game_index + 1}: both sides use current skill. "
        f"terminal={record.terminal}, winner={record.winner or 'draw'}, "
        f"X_mistakes={xm}/{grading.get('X_moves', 0)}, "
        f"O_mistakes={om}/{grading.get('O_moves', 0)}."
    )

    moves_str = " ".join(f"{m.symbol}{m.cell}" for m in record.moves)
    mistake_cells = [
        f"{t['symbol']}{t['cell']}(opt:{','.join(map(str, t['optimal']))})"
        for t in grading.get("move_trace", [])
        if t.get("mistake")
    ]
    ev_parts = [
        f"result={record.terminal}",
        f"moves=[{moves_str}]",
        f"total_mistakes={total_mistakes}",
    ]
    if mistake_cells:
        ev_parts.append(f"suboptimal_moves=[{'; '.join(mistake_cells[:4])}]")
    if is_forfeit:
        ev_parts.append(f"forfeit_side={record.forfeit_side}")
        if record.forfeit_reason and "last_raw=" in record.forfeit_reason:
            bad = record.forfeit_reason.split("last_raw=", 1)[1].strip("\"'")[:100]
            ev_parts.append(f"bad_output={bad!r}")
    evidence = "; ".join(ev_parts).replace('"', "'")

    upstream_str = ",".join(upstream) if upstream else "-"
    header = (
        f"- [{date}] session:{session_id} node:{node_id} "
        f"upstream:{upstream_str} skill:{SKILL_NAME}"
    )
    lines = [header, f'    P1_analysis: "{analysis}"']
    lines.append(
        f'    P2_predict:  V={base_v}, conf={conf}, '
        f'reason="self-play expectation based on running mistake rate"'
    )
    if upstream:
        delta = reward - prior_reward
        lines.append(
            f'    P3_td:       delta={delta:+.1f}, '
            f'interp="per-move grading vs minimax"'
        )
    lines.append(f'    P4_strategy: {strategy}, note="{strategy_note}"')
    lines.append(
        f'    P5_result:   outcome={outcome}, reward={reward:+d}, ev="{evidence}"'
    )
    return "\n".join(lines)


def write_selfplay_batch(
    feedback_log: Path,
    graded_records: List[tuple[GameRecord, dict]],
    session_id: str,
) -> list[str]:
    """Append G2 entries for a self-play batch where each game has been
    graded by minimax. One entry per game, chained upstream."""
    blocks = []
    prior_reward = 0
    for i, (rec, grading) in enumerate(graded_records):
        nid = f"g{i + 1}"
        upstream = [f"g{i}"] if i > 0 else []
        block = build_selfplay_block(
            session_id=session_id,
            node_id=nid,
            upstream=upstream,
            record=rec,
            grading=grading,
            game_index=i,
            prior_reward=prior_reward,
        )
        blocks.append(block)
        # recompute reward for prior-reward chaining
        xm = grading.get("X_mistakes", 0)
        om = grading.get("O_mistakes", 0)
        total = xm + om
        if rec.terminal == "forfeit":
            prior_reward = -1
        elif total == 0:
            prior_reward = +1
        elif total == 1:
            prior_reward = 0
        else:
            prior_reward = -1

    text = feedback_log.read_text(encoding="utf-8")
    marker = "## Pending Feedback"
    if marker not in text:
        raise RuntimeError(f"{feedback_log} missing '{marker}' section")
    idx = text.index(marker) + len(marker)
    end_of_line = text.index("\n", idx)
    injection = "\n\n" + "\n".join(blocks) + "\n"
    new_text = text[: end_of_line + 1] + injection + text[end_of_line + 1 :]
    feedback_log.write_text(new_text, encoding="utf-8")
    return blocks


def write_batch(
    feedback_log: Path,
    records: List[tuple[GameRecord, str]],  # list of (record, skill_side)
    session_id: str,
) -> list[str]:
    """Append a batch of G2 blocks for the given records. Returns the blocks
    as strings (for archival into experiments/.../history/)."""
    blocks = []
    forfeit_so_far = 0
    prior_reward = 0
    for i, (rec, side) in enumerate(records):
        nid = f"g{i + 1}"
        upstream = [f"g{i}"] if i > 0 else []
        block = build_g2_block(
            session_id=session_id,
            node_id=nid,
            upstream=upstream,
            record=rec,
            skill_side=side,
            game_index=i,
            forfeit_so_far=forfeit_so_far,
            prior_reward=prior_reward,
        )
        blocks.append(block)
        if rec.terminal == "forfeit" and rec.forfeit_side == side:
            forfeit_so_far += 1
        _, reward, _ = _classify(rec, side)
        prior_reward = reward

    text = feedback_log.read_text(encoding="utf-8")
    marker = "## Pending Feedback"
    if marker not in text:
        raise RuntimeError(f"{feedback_log} missing '{marker}' section")
    idx = text.index(marker) + len(marker)
    end_of_line = text.index("\n", idx)
    injection = "\n\n" + "\n".join(blocks) + "\n"
    new_text = text[: end_of_line + 1] + injection + text[end_of_line + 1 :]
    feedback_log.write_text(new_text, encoding="utf-8")
    return blocks
