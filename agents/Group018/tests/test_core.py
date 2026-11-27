import unittest

from agents.Group018.core import BoardState
from src.Board import Board
from src.Colour import Colour
from src.Move import Move


class TestBoardState(unittest.TestCase):
    def test_empty_board_legal_moves_count(self):
        board = Board(11)
        state = BoardState.from_board(board)
        self.assertEqual(len(state.legal_moves()), 121)
        for move in state.legal_moves():
            self.assertFalse(move.is_swap())

    def test_round_trip_and_apply_move(self):
        board = Board(11)
        state = BoardState.from_board(board, to_play=Colour.RED)
        self.assertEqual(state.board, board)

        move = Move(5, 5)
        self.assertIn(move, state.legal_moves())
        after = state.apply_move(move)
        self.assertEqual(len(after.legal_moves()), 120)
        self.assertEqual(after.board.tiles[5][5].colour, Colour.RED)
        self.assertEqual(after.to_play, Colour.BLUE)

    def test_has_won_red_column(self):
        board = Board(11)
        for i in range(11):
            board.set_tile_colour(i, 0, Colour.RED)
        state = BoardState.from_board(board)
        self.assertTrue(state.has_won(Colour.RED))
        self.assertFalse(state.has_won(Colour.BLUE))

    def test_to_planes_shape_and_empty_board(self):
        board = Board(11)
        state = BoardState.from_board(board, to_play=Colour.RED)
        planes = state.to_planes()
        self.assertEqual(planes.shape, (3, 11, 11))
        self.assertEqual(planes[2].sum(), 121.0)
        self.assertEqual(planes[0].sum(), 0.0)
        self.assertEqual(planes[1].sum(), 0.0)


if __name__ == "__main__":
    unittest.main()