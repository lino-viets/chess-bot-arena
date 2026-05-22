# Chess Bot Arena

Personal ML **learning project**: implement chess bots of increasing
sophistication and run them in a round-robin arena. Also a GitHub portfolio
piece, so structure, docs, and reproducibility matter.

## Collaboration style — IMPORTANT

The user is doing this to **learn machine learning**, not to delegate. Do the
boring scaffolding (repo plumbing, UCI adapter, harness, configs, debugging),
but the user writes or co-writes the *interesting* algorithmic and ML code.
**Explain concepts** as you go — favor teaching over silently implementing.
When proposing ML code, walk through the *why*, not just the *what*.

## Stack

- **Python 3.12**, managed by `uv`. The system Python is 3.14, which is too new
  for PyTorch wheels — never use it; always run via `uv run`.
- `python-chess` (imported as `chess`) for board, rules, and UCI engine driving.
- PyTorch (ROCm build) for the ML bots — added when Bot 3 is reached.
- `rich` for terminal tables.
- Bots integrate via **UCI**: one generic adapter (`uci.py`) wraps any `Bot`.
- Tournaments: `tournament/run.py` runs a round-robin, driving bots over UCI via
  `python-chess`'s `chess.engine` module — no external binary needed.
- Play interactively via a chess GUI (e.g. Cute Chess) loading
  `chess-arena-uci --bot <name>`.
- Online bonus: **Lichess Bot API** (not chess.com — it has no bot API and
  automated play violates its ToS).

## Hardware

- GPU: AMD RX 6800 XT (`gfx1030`, RDNA2/Navi 21), officially ROCm-supported.
- ROCm's PyTorch build reuses the CUDA API surface (`device="cuda"`,
  `torch.cuda.is_available()`). The user has prior PyTorch/CUDA experience on an
  A100, so that knowledge transfers almost directly.
- If the GPU is not detected after installing ROCm, try the env var
  `HSA_OVERRIDE_GFX_VERSION=10.3.0`.
- Bots 0–2 are CPU-only; ROCm is only needed from Bot 3 onward.

## Architecture

- `Bot` ABC (`bot.py`): `select_move(board, time_limit) -> chess.Move`. Every
  bot satisfies this; the UCI adapter and tournament harness are bot-agnostic.
- Bots are registered by name in `registry.py`.
- `cli.py` exposes the `chess-arena-uci` console script.

## Layout

`src/` layout, package `chess_arena`. Tournament scripts in `tournament/`,
tests in `tests/` (run with `uv run pytest`).

## Roadmap

0. RandomBot — baseline.
1. MinimaxBot — fixed-depth negamax, material evaluation.
2. AlphaBetaBot — pruning, iterative deepening, time control, piece-square
   tables, quiescence, transposition tables.
3. ML-eval bot — supervised NN position evaluator inside alpha-beta (first
   GPU/ROCm bot).
4. RL bot — self-play policy/value network.
5. Deep-RL bot — AlphaZero-style MCTS + deep residual net, self-play (scaled to
   a single 6800 XT).

A round-robin tournament + standings is run after each new bot lands, so
progress stays measurable.
