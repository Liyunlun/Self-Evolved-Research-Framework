# Experiment: Tic-Tac-Toe self-play skill evolution via TextGrad-TDRL

Parent: checklists/short-term.md § Experiments | Created: 2026-04-20
Status: [9/9]

## Goal

End-to-end live test of the TextGrad-with-TDRL evolution pipeline on a fresh
skill whose improvement can be graded objectively (win rate vs perfect-play
minimax). Seeds `skills/play-tic-tac-toe/` with a rules-only spec, runs
self-play to generate G2 signal, evolves the spec, and measures win-rate
delta against minimax before and after.

## Pipeline

- [x] **Setup**: Initial rules-only `skills/play-tic-tac-toe/SKILL.md` + v1 snapshot in `experiments/tic_tac_toe/history/v1-initial/`
- [x] **Game core**: `experiments/tic_tac_toe/game.py` (board, legal moves, winner detection) + 6 unit tests (all pass)
- [x] **Oracle**: `experiments/tic_tac_toe/minimax.py` — perfect player + `optimal_moves()` set-oracle for grading; tests cover empty-board draw-equivalence, forced-win single optimal, and self-play-is-draw invariants
- [x] **Arena**: `experiments/tic_tac_toe/arena.py` — `skill_agent` + `minimax_agent`; move parse with one retry then forfeit; engine exceptions (timeout, rc!=0) now caught and treated as invalid output (one retry, then forfeit)
- [x] **Smoke**: cycle 1 (vs-minimax) completed without exceptions, 2 draws confirmed
- [x] **G2 writer**: `experiments/tic_tac_toe/g2_writer.py` — both `write_batch` (vs-minimax) and `write_selfplay_batch` (minimax-graded per-move) paths emit v3 6-line blocks
- [x] **Cycle driver**: `experiments/tic_tac_toe/run_cycle.py` supports `--self-play N` mode; pre-flushes foreign pending entries; archives skill-before/skill-after to `history/cycle-NNN/`
- [x] **Run cycle 1 + cycle 2**: cycle-001 (vs-minimax, 2 draws, td below hard threshold, no edit — pipeline correctly suppressed evolution) and cycle-002 (10 self-play games, 9 draws + 1 forfeit, td=+1.11 hard, SKILL.md evolved with strategic EVOLVE NOTE)
- [x] **Report**: `experiments/tic_tac_toe/history/cycle-{001,002}/report.md` + `eval.json` written; v1 archived under `skills/td-nl/history/play-tic-tac-toe-v2.md`

## Config

| Parameter | Value |
|-----------|-------|
| model | haiku |
| games per self-play batch | 10 |
| eval games vs minimax | 10 each side (X and O) |
| cycles | 1 (this experiment) |
| G2 granularity | per-game, per-side |
| move format | keypad 1-9 |

## Results

### cycle-001 (vs-minimax, 2 games per side)
- before/after both: 2 draws, 0 forfeits (haiku plays rules-only TTT near-optimally)
- td=-0.03, strength=drop → **no proposal written** (pipeline correctly refused to evolve on zero signal)

### cycle-002 (self-play, 10 games, minimax-graded per-move)
- 9 draws, 1 forfeit (game 5: X chatty-output forfeit on move 3), 83 moves, 0 tactical mistakes
- td=+1.11, strength=hard, conf=high → proposal targeted `play-tic-tac-toe`
- V^L: 5.00 → 6.11
- EVOLVE NOTE landed (Claude Code CLI engine output):
  > Add a "Strategy" section after "Move format" that prioritizes moves: (1) take a winning cell if available this turn; (2) block opponent's winning cell if they can win next turn; (3) prefer center (5), then corners (1,3,7,9), then edges.

### Observations
- The shim+engine TGD works as designed: the engine produced a specific, actionable recommendation grounded in the evidence (10 draws, 1 forfeit).
- With haiku already near-optimal on TTT, the forfeit signal dominated the proposal — matching how a weak output-format instruction in v1 would actually fail under load.
- Evolution is **additive** in shim mode: the EVOLVE NOTE is prepended, original spec preserved below. Cleaner rewrites would need real `textgrad` (not shim) or a second prompt that rewrites in-place.

## History Invariant

Every cycle MUST preserve under `experiments/tic-tac-toe/history/cycle-NNN/`:
  - `skill-before.md` — the SKILL.md at cycle start
  - `skill-after.md` — the SKILL.md after evolve-apply
  - `games.jsonl` — one line per game (roles, move list, outcome, reason)
  - `g2-entries.md` — the v3 entries appended to feedback-log
  - `proposal.md` — the PROPOSAL block written by evolve-textgrad
  - `eval.json` — win-rate vs minimax for skill-before and skill-after
  - `report.md` — human-readable summary
