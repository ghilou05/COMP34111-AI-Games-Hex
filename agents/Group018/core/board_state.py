from __future__ import annotations

import copy
from dataclasses import dataclass

import numpy as np

from src.Board import Board
from src.Colour import Colour
from src.Move import Move


@dataclass(frozen=True)
class BoardState:
    """Copy of the engine board for internal search / knowledge / ML."""

    _board: Board
    to_play: Colour

    @classmethod
    def from_board(cls, board: Board, *, to_play: Colour = Colour.RED) -> BoardState:
        return cls(_board=copy.deepcopy(board), to_play=to_play)

    @property
    def board(self) -> Board:
        """Engine board copy (do not mutate in place; use apply_move)."""
        return self._board

    @property
    def size(self) -> int:
        return self._board.size

    def legal_moves(self) -> list[Move]:
        """Empty cells only; swap is excluded (handled in MyAgent)."""
        moves: list[Move] = []
        for row in self._board.tiles:
            for tile in row:
                if tile.colour is None:
                    moves.append(Move(tile.x, tile.y))
        return moves

    def apply_move(self, move: Move) -> BoardState:
        if move.is_swap():
            raise ValueError("swap is not applied via BoardState.apply_move")
        tile = self._board.tiles[move.x][move.y]
        if tile.colour is not None:
            raise ValueError(f"illegal move: cell ({move.x}, {move.y}) is not empty")
        next_board = copy.deepcopy(self._board)
        next_board.set_tile_colour(move.x, move.y, self.to_play)
        return BoardState(_board=next_board, to_play=Colour.opposite(self.to_play))

    def has_won(self, colour: Colour) -> bool:
        probe = copy.deepcopy(self._board)
        return probe.has_ended(colour)

    def to_planes(self) -> np.ndarray:
        """Planes from ``to_play`` perspective: own stones, opponent, empty.

        Shape: ``(3, size, size)`` with ``dtype=float32``, values 0 or 1.
        """
        size = self._board.size
        planes = np.zeros((3, size, size), dtype=np.float32)
        opponent = Colour.opposite(self.to_play)
        for x, row in enumerate(self._board.tiles):
            for y, tile in enumerate(row):
                if tile.colour is None:
                    planes[2, x, y] = 1.0
                elif tile.colour == self.to_play:
                    planes[0, x, y] = 1.0
                elif tile.colour == opponent:
                    planes[1, x, y] = 1.0
        return planes