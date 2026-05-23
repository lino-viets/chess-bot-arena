"""Bot registry: maps a short name to a factory that builds the bot.

The factory is a zero-argument callable so each lookup yields a fresh instance
(important for stateful bots and for running a bot against itself).
"""

from __future__ import annotations

from collections.abc import Callable

from chess_arena.bot import Bot
from chess_arena.bots.random_bot import RandomBot

BotFactory = Callable[[], Bot]

_REGISTRY: dict[str, BotFactory] = {
    "random": RandomBot,
}


def available_bots() -> list[str]:
    """Return the sorted list of registered bot names."""
    return sorted(_REGISTRY)


def create_bot(name: str) -> Bot:
    """Build a fresh instance of the bot registered under `name`.

    Raises:
        KeyError: if no bot is registered under that name.
    """
    try:
        factory = _REGISTRY[name]
    except KeyError:
        raise KeyError(
            f"Unknown bot {name!r}. Available: {', '.join(available_bots())}"
        ) from None
    return factory()
