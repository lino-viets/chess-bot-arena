"""Bot 1: MinimaxBot — fixed-depth search with a material evaluation.

This bot searches the game tree `depth` plies deep and assumes both sides play
optimally. It uses the *negamax* formulation: because chess is zero-sum, a score
that is good for one side is exactly as bad for the other, so we always maximize
and negate the score on each recursive step instead of writing separate min/max
branches.

Deliberately NO pruning here — alpha-beta pruning is Bot 2. Keeping Bot 1
unpruned means the speedup pruning gives can be measured directly.

>>> SKELETON <<<
`evaluate()` and `negamax()` have their bodies left as TODOs for you to fill in.
`select_move()` (the search root) and everything else is already wired up, so
once those two functions work, the bot works. Each docstring tells you exactly
what to return.
"""

from __future__ import annotations

import chess

from chess_arena.bot import Bot

#: Centipawn value of each piece type. The king has no material value — losing
#: it is handled separately via checkmate scoring.
PIECE_VALUES: dict[chess.PieceType, int] = {
    chess.PAWN: 100,
    chess.KNIGHT: 320,
    chess.BISHOP: 330,
    chess.ROOK: 500,
    chess.QUEEN: 900,
    chess.KING: 0,
}

#: Score representing a checkmate. Far larger than any possible material
#: difference, so the search always prefers mating over winning material.
MATE_SCORE = 1_000_000


def evaluate(board: chess.Board) -> int:
    """Score `board` from the perspective of the side to move.

    Positive means the side to move is better; negative means worse. This is the
    negamax convention — `negamax` relies on it.

    TODO (you write this):
      1. Terminal positions first:
         - `board.is_checkmate()` -> the side to move has been mated, which is
           the worst possible outcome. Return `-MATE_SCORE`.
         - any other game-over (`board.is_stalemate()`,
           `board.is_insufficient_material()`, the draw rules, or simply
           `board.is_game_over()`) -> a draw. Return `0`.
      2. Otherwise, material balance:
         - Sum `PIECE_VALUES` for White's pieces, subtract them for Black's.
           `board.piece_map()` gives every `square -> Piece`; each `Piece` has
           `.piece_type` and `.color`. That sum is from White's point of view.
         - Convert to the side-to-move's point of view: return it as-is when
           `board.turn == chess.WHITE`, negated when it is Black's move.

    Returns:
        The position's score in centipawns, from the side to move's view.
    """
    raise NotImplementedError("evaluate() is yours to implement")


def negamax(board: chess.Board, depth: int) -> int:
    """Return the negamax score of `board`, searching `depth` plies ahead.

    TODO (you write this):
      1. Base case: if `depth == 0` or `board.is_game_over()`, the search stops
         here — return `evaluate(board)`.
      2. Recursive case: try every legal move and keep the best reply score.
         For each `move` in `board.legal_moves`:
            board.push(move)
            score = -negamax(board, depth - 1)   # opponent's view, negated
            board.pop()
         Track the maximum `score` seen and return it.

      The minus sign in step 2 is the heart of negamax: the child position is
      scored from the opponent's perspective, so negating it gives the value
      from the current side's perspective.

    Args:
        board: Position to search. Leave it unchanged on return (push/pop pairs).
        depth: Plies left to search.

    Returns:
        Best achievable score for the side to move, from its own perspective.
    """
    raise NotImplementedError("negamax() is yours to implement")


class MinimaxBot(Bot):
    name = "MinimaxBot"

    def __init__(self, depth: int = 3) -> None:
        self.depth = depth

    def select_move(self, board: chess.Board, time_limit: float | None) -> chess.Move:
        """Search root: pick the move with the best negamax score.

        This is the one place the search starts. It mirrors the recursive step
        in `negamax` — push a move, score the resulting position from the
        opponent's perspective, negate it — but here we also remember *which*
        move produced the best score. `time_limit` is ignored: this bot's
        thinking time is fixed by `depth`.
        """
        best_move: chess.Move | None = None
        best_score = -MATE_SCORE - 1

        for move in board.legal_moves:
            board.push(move)
            score = -negamax(board, self.depth - 1)
            board.pop()
            if score > best_score:
                best_score = score
                best_move = move

        assert best_move is not None, "select_move called with no legal moves"
        return best_move
