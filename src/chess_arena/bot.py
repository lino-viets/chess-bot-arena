"""The shared interface every chess bot implements.

Everything else in the project — the UCI adapter, the tournament harness — is
written against this `Bot` interface, never against a specific bot. That keeps
bots completely decoupled from how they are run.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

import chess


class Bot(ABC):
    """Abstract base class for a chess-playing agent.

    A bot's only job is: given a position, return a move. How it decides — random
    choice, tree search, a neural network — is entirely up to the subclass.
    """

    #: Human-readable name, shown in tournaments and UCI output.
    name: str = "Bot"

    @abstractmethod
    def select_move(self, board: chess.Board, time_limit: float | None) -> chess.Move:
        """Return a legal move for the side to move in `board`.

        Args:
            board: The current position. Treat it as read-only; if you need to
                explore moves, push/pop on a copy or restore what you push.
            time_limit: Soft budget in seconds for this move, or None for no
                limit. Bots may use less; they should try not to exceed it.

        Returns:
            A legal `chess.Move` for `board`.
        """

    def new_game(self) -> None:
        """Hook called once before each new game.

        Override to reset per-game state (e.g. transposition tables). The default
        does nothing.
        """
