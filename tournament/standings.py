"""Turn a set of game results into a standings table with estimated Elo.

A "result" is a tuple ``(white_name, black_name, outcome)`` where ``outcome`` is
one of ``"1-0"``, ``"0-1"``, ``"1/2-1/2"`` — the strings python-chess uses.

Can be used as a library (``print_standings``) or run on a PGN file:

    uv run python tournament/standings.py results/latest.pgn
"""

from __future__ import annotations

import sys
from collections import defaultdict

from rich.console import Console
from rich.table import Table

Result = tuple[str, str, str]

_SCORE_FOR_WHITE = {"1-0": 1.0, "0-1": 0.0, "1/2-1/2": 0.5}


def compute_elo(
    results: list[Result],
    *,
    anchor: float = 1500.0,
    iterations: int = 2000,
    k: float = 8.0,
) -> dict[str, float]:
    """Estimate Elo ratings by running Elo updates over all games repeatedly.

    Each pass nudges ratings toward the values that best explain the observed
    results; after enough passes this converges to a maximum-likelihood-style
    fit. The average rating is pinned to `anchor` so the numbers are readable.
    """
    names = {n for w, b, _ in results for n in (w, b)}
    ratings = {n: anchor for n in names}
    if not names:
        return ratings

    for _ in range(iterations):
        for white, black, outcome in results:
            score_white = _SCORE_FOR_WHITE[outcome]
            expected_white = 1.0 / (
                1.0 + 10.0 ** ((ratings[black] - ratings[white]) / 400.0)
            )
            delta = k * (score_white - expected_white)
            ratings[white] += delta
            ratings[black] -= delta

    mean = sum(ratings.values()) / len(ratings)
    return {n: r - mean + anchor for n, r in ratings.items()}


def summarize(results: list[Result]) -> list[dict]:
    """Aggregate per-bot wins/draws/losses, points, and Elo, ranked by points."""
    wins: dict[str, int] = defaultdict(int)
    draws: dict[str, int] = defaultdict(int)
    losses: dict[str, int] = defaultdict(int)

    for white, black, outcome in results:
        score_white = _SCORE_FOR_WHITE[outcome]
        if score_white == 1.0:
            wins[white] += 1
            losses[black] += 1
        elif score_white == 0.0:
            wins[black] += 1
            losses[white] += 1
        else:
            draws[white] += 1
            draws[black] += 1

    elo = compute_elo(results)
    names = sorted(elo)

    rows = []
    for name in names:
        w, d, ls = wins[name], draws[name], losses[name]
        rows.append(
            {
                "name": name,
                "games": w + d + ls,
                "wins": w,
                "draws": d,
                "losses": ls,
                "points": w + 0.5 * d,
                "elo": elo[name],
            }
        )
    rows.sort(key=lambda r: r["points"], reverse=True)
    return rows


def print_standings(results: list[Result], *, title: str = "Standings") -> None:
    """Render the standings table to the terminal."""
    rows = summarize(results)
    table = Table(title=title)
    table.add_column("#", justify="right")
    table.add_column("Bot")
    table.add_column("Games", justify="right")
    table.add_column("W", justify="right")
    table.add_column("D", justify="right")
    table.add_column("L", justify="right")
    table.add_column("Points", justify="right")
    table.add_column("Elo", justify="right")

    for rank, row in enumerate(rows, start=1):
        table.add_row(
            str(rank),
            row["name"],
            str(row["games"]),
            str(row["wins"]),
            str(row["draws"]),
            str(row["losses"]),
            f"{row['points']:.1f}",
            f"{row['elo']:.0f}",
        )

    Console().print(table)


def read_results_from_pgn(path: str) -> list[Result]:
    """Read game results from a PGN file."""
    import chess.pgn

    results: list[Result] = []
    with open(path, encoding="utf-8") as handle:
        while (game := chess.pgn.read_game(handle)) is not None:
            white = game.headers.get("White", "?")
            black = game.headers.get("Black", "?")
            outcome = game.headers.get("Result", "*")
            if outcome in _SCORE_FOR_WHITE:
                results.append((white, black, outcome))
    return results


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: python tournament/standings.py <results.pgn>", file=sys.stderr)
        sys.exit(1)
    print_standings(read_results_from_pgn(sys.argv[1]))
