"""A generic UCI adapter.

UCI (Universal Chess Interface) is the text protocol chess GUIs and engine
tooling speak. The GUI sends commands on the engine's stdin; the engine answers
on stdout. This module implements the protocol *once* and wraps any `Bot`, so
every bot in the project becomes a UCI engine for free.

Only the subset of UCI needed to actually play games is implemented.
"""

from __future__ import annotations

import sys

import chess

from chess_arena.bot import Bot

_ENGINE_AUTHOR = "Chess Bot Arena"


def _parse_position(args: list[str]) -> chess.Board:
    """Build a board from the arguments of a UCI `position` command.

    Forms: `position startpos [moves ...]`
           `position fen <6 fields> [moves ...]`
    """
    board = chess.Board()
    if not args:
        return board

    if args[0] == "startpos":
        moves = args[2:] if len(args) > 1 and args[1] == "moves" else []
    elif args[0] == "fen":
        # A FEN is exactly six space-separated fields.
        fen = " ".join(args[1:7])
        board = chess.Board(fen)
        moves = args[8:] if len(args) > 7 and args[7] == "moves" else []
    else:
        moves = []

    for token in moves:
        board.push(chess.Move.from_uci(token))
    return board


def _parse_go(args: list[str], white_to_move: bool) -> float | None:
    """Turn a UCI `go` command into a soft per-move time budget in seconds.

    Returns None when the command implies no time pressure (e.g. `go depth 4`),
    leaving it to the bot to decide how long to think.
    """
    params: dict[str, int] = {}
    for key, value in zip(args, args[1:]):
        if key in ("wtime", "btime", "winc", "binc", "movetime", "depth"):
            try:
                params[key] = int(value)
            except ValueError:
                pass

    if "movetime" in params:
        return params["movetime"] / 1000.0

    if "wtime" in params or "btime" in params:
        remaining = params.get("wtime" if white_to_move else "btime", 0)
        increment = params.get("winc" if white_to_move else "binc", 0)
        # Spend ~1/30 of the clock plus most of the increment — crude but safe.
        return max(0.05, remaining / 1000.0 / 30.0 + increment / 1000.0 * 0.8)

    return None


def run_uci(bot: Bot, *, instream=None, outstream=None) -> None:
    """Run `bot` as a UCI engine until a `quit` command (or EOF).

    Args:
        bot: The bot to expose.
        instream: Line source (defaults to stdin). Injectable for testing.
        outstream: Output sink (defaults to stdout). Injectable for testing.
    """
    instream = instream if instream is not None else sys.stdin
    outstream = outstream if outstream is not None else sys.stdout

    def send(line: str) -> None:
        outstream.write(line + "\n")
        outstream.flush()

    board = chess.Board()

    for raw in instream:
        tokens = raw.split()
        if not tokens:
            continue
        command, args = tokens[0], tokens[1:]

        if command == "uci":
            send(f"id name {bot.name}")
            send(f"id author {_ENGINE_AUTHOR}")
            send("uciok")
        elif command == "isready":
            send("readyok")
        elif command == "ucinewgame":
            board = chess.Board()
            bot.new_game()
        elif command == "position":
            board = _parse_position(args)
        elif command == "go":
            time_limit = _parse_go(args, board.turn == chess.WHITE)
            move = bot.select_move(board, time_limit)
            send(f"bestmove {move.uci()}")
        elif command == "quit":
            break
        # Unknown commands are ignored, as the UCI spec requires.
