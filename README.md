# Chess Bot Arena

A personal project for learning machine learning by building a series of chess
bots of increasing sophistication — from brute-force search to deep
reinforcement learning — and pitting them against each other in a round-robin
tournament.

## Idea

Each bot is a different architecture. They all share one interface and are
exposed as [UCI](https://en.wikipedia.org/wiki/Universal_Chess_Interface)
engines, so they can play in any chess GUI, in the built-in tournament, or
(bonus) online on Lichess.

| # | Bot | What it explores |
|---|-----|------------------|
| 0 | RandomBot | baseline |
| 1 | MinimaxBot | game-tree search, evaluation functions |
| 2 | AlphaBetaBot | pruning, iterative deepening, transposition tables |
| 3 | ML-eval bot | supervised learning: a neural-network position evaluator |
| 4 | RL bot | reinforcement learning via self-play |
| 5 | Deep-RL bot | AlphaZero-style MCTS + deep network self-play |

## Setup

Requires [`uv`](https://docs.astral.sh/uv/). Python 3.12 is fetched automatically.

```bash
uv sync
```

## Usage

Run a bot as a UCI engine:

```bash
uv run chess-arena-uci --bot random
```

Run a round-robin tournament:

```bash
uv run python tournament/run.py
```

Play against a bot by loading `uv run chess-arena-uci --bot <name>` as an
engine in a chess GUI such as [Cute Chess](https://cutechess.com/).

## Status

Foundation in place: shared bot interface, UCI adapter, tournament harness, and
RandomBot. Search and ML bots are added incrementally.
