"""Round-robin tournament runner.

Each participant is launched as a separate UCI engine process (via the
`chess-arena-uci` console script) and games are driven with python-chess's
`chess.engine` module. Because everything goes through UCI, the harness never
imports a bot directly — it only knows process commands.

Usage:
    uv run python tournament/run.py                 # all registered bots
    uv run python tournament/run.py --bot random --games 4 --move-time 0.1
"""

from __future__ import annotations

import argparse
import datetime as dt
import itertools
import pathlib
import sys

import chess
import chess.engine
import chess.pgn

from chess_arena.registry import available_bots

from standings import Result, print_standings

_REPO_ROOT = pathlib.Path(__file__).resolve().parent.parent
_RESULTS_DIR = _REPO_ROOT / "results"


class Participant:
    """One entrant: a display label plus the command that launches its engine."""

    def __init__(self, label: str, bot_name: str) -> None:
        self.label = label
        self.bot_name = bot_name
        self.command = ["uv", "run", "chess-arena-uci", "--bot", bot_name]


def play_game(
    white: Participant,
    black: Participant,
    move_time: float,
    max_plies: int = 400,
) -> tuple[str, chess.pgn.Game]:
    """Play one game and return ``(outcome, pgn_game)``.

    A ply cap prevents endless shuffling between weak bots from hanging the run;
    a capped game is scored as a draw.
    """
    board = chess.Board()
    engines = {
        chess.WHITE: chess.engine.SimpleEngine.popen_uci(white.command),
        chess.BLACK: chess.engine.SimpleEngine.popen_uci(black.command),
    }
    try:
        while not board.is_game_over() and board.ply() < max_plies:
            result = engines[board.turn].play(
                board, chess.engine.Limit(time=move_time)
            )
            board.push(result.move)
    finally:
        for engine in engines.values():
            engine.quit()

    outcome = board.result(claim_draw=True)
    if outcome == "*":  # game hit the ply cap without a natural result
        outcome = "1/2-1/2"

    game = chess.pgn.Game.from_board(board)
    game.headers["White"] = white.label
    game.headers["Black"] = black.label
    game.headers["Result"] = outcome
    game.headers["Event"] = "Chess Bot Arena round-robin"
    game.headers["Date"] = dt.date.today().strftime("%Y.%m.%d")
    return outcome, game


def round_robin(
    participants: list[Participant], games_per_pairing: int, move_time: float
) -> tuple[list[Result], list[chess.pgn.Game]]:
    """Play every pair `games_per_pairing` times, alternating colors."""
    results: list[Result] = []
    pgn_games: list[chess.pgn.Game] = []

    for a, b in itertools.combinations(participants, 2):
        for game_index in range(games_per_pairing):
            # Alternate colors so neither bot keeps the first-move advantage.
            white, black = (a, b) if game_index % 2 == 0 else (b, a)
            print(f"  {white.label} (W) vs {black.label} (B) ...", flush=True)
            outcome, game = play_game(white, black, move_time)
            results.append((white.label, black.label, outcome))
            pgn_games.append(game)

    return results, pgn_games


def _build_participants(bot_names: list[str]) -> list[Participant]:
    """Make participants, suffixing labels so a bot can face a copy of itself."""
    if len(bot_names) == 1:
        name = bot_names[0]
        return [Participant(f"{name}-A", name), Participant(f"{name}-B", name)]
    return [Participant(name, name) for name in bot_names]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Run a round-robin tournament.")
    parser.add_argument(
        "--bot",
        dest="bots",
        action="append",
        choices=available_bots(),
        help="Bot to include (repeatable). Defaults to every registered bot.",
    )
    parser.add_argument(
        "--games", type=int, default=2, help="Games per pairing (default: 2)."
    )
    parser.add_argument(
        "--move-time",
        type=float,
        default=0.1,
        help="Seconds per move (default: 0.1).",
    )
    args = parser.parse_args(argv)

    participants = _build_participants(args.bots or available_bots())
    print(
        f"Round-robin: {len(participants)} participants, "
        f"{args.games} games/pairing, {args.move_time}s/move\n"
    )

    results, pgn_games = round_robin(participants, args.games, args.move_time)

    _RESULTS_DIR.mkdir(exist_ok=True)
    stamp = dt.datetime.now().strftime("%Y%m%d-%H%M%S")
    pgn_path = _RESULTS_DIR / f"tournament-{stamp}.pgn"
    with pgn_path.open("w", encoding="utf-8") as handle:
        for game in pgn_games:
            print(game, file=handle, end="\n\n")

    print()
    print_standings(results, title=f"Standings ({len(results)} games)")
    print(f"\nPGN saved to {pgn_path.relative_to(_REPO_ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
