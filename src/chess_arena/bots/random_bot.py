"""Bot 0: RandomBot — the baseline.

Picks a uniformly random legal move. It plays no chess at all; its only purpose
is to be the floor that every later bot must beat by a wide margin.
"""

from __future__ import annotations

import random

import chess

from chess_arena.bot import Bot


class RandomBot(Bot):
    name = "RandomBot"

    def __init__(self, seed: int | None = None) -> None:
        # A dedicated RNG (rather than the global one) keeps games reproducible
        # when a seed is given, without disturbing randomness elsewhere.
        self._rng = random.Random(seed)

    def select_move(self, board: chess.Board, time_limit: float | None) -> chess.Move:
        return self._rng.choice(list(board.legal_moves))
