"""Sanity tests for the bots and the UCI adapter."""

from __future__ import annotations

import io

import chess
import pytest

from chess_arena.registry import available_bots, create_bot
from chess_arena.uci import _parse_go, _parse_position, run_uci

# A few representative positions: opening, a midgame position, and a
# position with a mate available on the move.
POSITIONS = [
    chess.STARTING_FEN,
    "r1bqkbnr/pppp1ppp/2n5/4p3/2B1P3/5N2/PPPP1PPP/RNBQK2R w KQkq - 4 4",
    "6k1/5ppp/8/8/8/8/8/R3K2R w KQ - 0 1",  # Ra8# is available
]


@pytest.mark.parametrize("bot_name", available_bots())
@pytest.mark.parametrize("fen", POSITIONS)
def test_bot_returns_legal_move(bot_name: str, fen: str) -> None:
    bot = create_bot(bot_name)
    board = chess.Board(fen)
    move = bot.select_move(board, time_limit=0.1)
    assert move in board.legal_moves


def test_unknown_bot_raises() -> None:
    with pytest.raises(KeyError):
        create_bot("does-not-exist")


def test_parse_position_startpos_with_moves() -> None:
    board = _parse_position(["startpos", "moves", "e2e4", "e7e5"])
    assert board.fen().startswith(
        "rnbqkbnr/pppp1ppp/8/4p3/4P3/8/PPPP1PPP/RNBQKBNR w"
    )


def test_parse_position_fen() -> None:
    fen = "8/8/8/8/8/8/8/R3K2R w KQ - 0 1"
    board = _parse_position(["fen", *fen.split()])
    assert board.fen() == fen


def test_parse_go_movetime() -> None:
    assert _parse_go(["movetime", "2500"], white_to_move=True) == 2.5


def test_parse_go_clock_uses_side_to_move() -> None:
    args = ["wtime", "60000", "btime", "30000"]
    white_budget = _parse_go(args, white_to_move=True)
    black_budget = _parse_go(args, white_to_move=False)
    assert white_budget > black_budget


def test_parse_go_no_time_info() -> None:
    assert _parse_go(["infinite"], white_to_move=True) is None


def test_uci_adapter_handshake_and_bestmove() -> None:
    bot = create_bot("random")
    instream = io.StringIO(
        "uci\nisready\nposition startpos\ngo movetime 100\nquit\n"
    )
    outstream = io.StringIO()

    run_uci(bot, instream=instream, outstream=outstream)
    lines = outstream.getvalue().splitlines()

    assert "uciok" in lines
    assert "readyok" in lines

    bestmove_lines = [ln for ln in lines if ln.startswith("bestmove ")]
    assert len(bestmove_lines) == 1
    move = chess.Move.from_uci(bestmove_lines[0].split()[1])
    assert move in chess.Board().legal_moves
