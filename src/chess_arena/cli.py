"""Entry point for the `chess-arena-uci` console script.

Runs a registered bot as a UCI engine, so it can be loaded by a chess GUI, the
tournament harness, or a Lichess bridge.
"""

from __future__ import annotations

import argparse
import sys

from chess_arena.registry import available_bots, create_bot
from chess_arena.uci import run_uci


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="chess-arena-uci",
        description="Run a Chess Bot Arena bot as a UCI engine.",
    )
    parser.add_argument(
        "--bot",
        required=True,
        choices=available_bots(),
        help="Which registered bot to run.",
    )
    args = parser.parse_args(argv)

    bot = create_bot(args.bot)
    run_uci(bot)
    return 0


if __name__ == "__main__":
    sys.exit(main())
