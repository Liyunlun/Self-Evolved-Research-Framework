"""Unit tests for game.py + minimax.py. Pure - no LLM, no I/O."""
from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE.parent))

from tic_tac_toe.game import Board  # type: ignore[import-not-found]
from tic_tac_toe import minimax  # type: ignore[import-not-found]


def test_board_legal_moves():
    b = Board()
    assert b.legal_moves() == list(range(1, 10))
    b.play(5, "X")
    assert 5 not in b.legal_moves()
    print("  ok board_legal_moves")


def test_board_winner_detection():
    b = Board()
    for c in (1, 2, 3):
        b.cells[c - 1] = "X"
    assert b.winner() == "X"

    b2 = Board()
    for c in (1, 5, 9):
        b2.cells[c - 1] = "O"
    assert b2.winner() == "O"

    b3 = Board()  # full, no winner
    for i, s in enumerate(["X", "O", "X", "X", "O", "O", "O", "X", "X"]):
        b3.cells[i] = s
    assert b3.winner() is None
    assert b3.is_full()
    print("  ok board_winner_detection")


def test_minimax_first_move_center_or_corner():
    b = Board()
    move = minimax.best_move(b, "X")
    assert move in (1, 3, 5, 7, 9), f"unexpected opening: {move}"
    print(f"  ok minimax_first_move (best={move})")


def test_minimax_blocks_immediate_win():
    # X threatens row 1-2-3: O must block at 3.
    b = Board()
    b.play(1, "X")
    b.play(5, "O")
    b.play(2, "X")
    # O to move; X threatens at 3. O best_move must be 3.
    move = minimax.best_move(b, "O")
    assert move == 3, f"O failed to block - chose {move}, board=\n{b.render()}"
    print("  ok minimax_blocks_immediate_win")


def test_minimax_takes_immediate_win():
    # X has 1 and 2 filled; next X must be 3.
    b = Board()
    b.play(1, "X")
    b.play(4, "O")
    b.play(2, "X")
    b.play(7, "O")
    # X to move, can win at 3
    move = minimax.best_move(b, "X")
    assert move == 3, f"X failed to take win - chose {move}"
    print("  ok minimax_takes_immediate_win")


def test_minimax_self_play_is_draw():
    """Two perfect players always draw."""
    b = Board()
    to_move = "X"
    while not b.is_terminal():
        m = minimax.best_move(b, to_move)
        b.play(m, to_move)
        to_move = "O" if to_move == "X" else "X"
    assert b.winner() is None, f"minimax vs minimax gave winner {b.winner()}"
    print("  ok minimax_self_play_is_draw")


def main():
    test_board_legal_moves()
    test_board_winner_detection()
    test_minimax_first_move_center_or_corner()
    test_minimax_blocks_immediate_win()
    test_minimax_takes_immediate_win()
    test_minimax_self_play_is_draw()
    print("[ttt] all game/minimax tests passed")


if __name__ == "__main__":
    main()
