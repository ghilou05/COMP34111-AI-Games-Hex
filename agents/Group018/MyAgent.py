from random import choice

from agents.Group018.core import BoardState
from src.AgentBase import AgentBase
from src.Board import Board
from src.Colour import Colour
from src.Move import Move


class MyAgent(AgentBase):
    """Stage 0 agent: legal random play (and optional turn-2 swap for Blue)."""

    def __init__(self, colour: Colour):
        super().__init__(colour)

    def make_move(self, turn: int, board: Board, opp_move: Move | None) -> Move:
        if turn == 2 and self.colour == Colour.BLUE and choice([0, 1]) == 1:
            return Move(-1, -1)

        state = BoardState.from_board(board, to_play=self.colour)
        return choice(state.legal_moves())