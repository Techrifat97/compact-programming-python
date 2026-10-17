"""Run the logic tests with: python3 -m unittest -v"""

import unittest
from unittest.mock import patch

from board import Board
from checker import Checker
from game import Game, format_duration
from player import Player


def empty_board(board):
    board.squares = []
    for row in range(8):
        board.squares.append([None] * 8)


def place(board, color, position, king=False):
    checker = Checker(color, position)
    checker.is_king = king
    board.squares[position[0]][position[1]] = checker
    return checker


class BoardTests(unittest.TestCase):
    def setUp(self):
        self.board = Board()

    def test_initial_board(self):
        self.assertEqual(len(self.board.squares), 8)
        for color in ("black", "white"):
            self.assertEqual(len(self.board.get_checkers(color)), 12)
        for checker in self.board.get_checkers():
            row, column = checker.position
            self.assertEqual((row + column) % 2, 1)
            self.assertFalse(checker.is_king)

    def test_normal_piece_cannot_move_or_capture_backward(self):
        empty_board(self.board)
        place(self.board, "black", (4, 3))
        place(self.board, "white", (3, 2))
        self.assertEqual(set(self.board.get_valid_moves((4, 3))),
                         {(5, 2), (5, 4)})
        self.assertEqual(self.board.get_valid_moves((4, 3), True), {})

    def test_white_moves_toward_top(self):
        self.assertEqual(set(self.board.get_valid_moves((5, 2))),
                         {(4, 1), (4, 3)})

    def test_capture_is_mandatory_across_all_checkers(self):
        empty_board(self.board)
        place(self.board, "black", (2, 1))
        place(self.board, "black", (2, 5))
        place(self.board, "white", (3, 2))
        self.assertEqual(self.board.get_legal_moves("black"),
                         {(2, 1): {(4, 3): (3, 2)}})
        with self.assertRaises(ValueError):
            self.board.move_checker((2, 5), (3, 4))

    def test_capture_removes_opponent_and_updates_position(self):
        empty_board(self.board)
        checker = place(self.board, "black", (2, 1))
        opponent = place(self.board, "white", (3, 2))
        captured, promoted = self.board.move_checker((2, 1), (4, 3))
        self.assertIs(captured, opponent)
        self.assertFalse(promoted)
        self.assertIsNone(self.board.get_checker((2, 1)))
        self.assertIsNone(self.board.get_checker((3, 2)))
        self.assertIs(self.board.get_checker((4, 3)), checker)
        self.assertEqual(checker.position, (4, 3))

    def test_cannot_jump_own_checker_or_land_on_occupied_square(self):
        empty_board(self.board)
        place(self.board, "black", (2, 1))
        place(self.board, "black", (3, 2))
        self.assertNotIn((4, 3), self.board.get_valid_moves((2, 1)))
        place(self.board, "white", (3, 2))
        place(self.board, "white", (4, 3))
        self.assertNotIn((4, 3), self.board.get_valid_moves((2, 1)))

    def test_board_edges_and_invalid_destinations(self):
        self.assertIsNone(self.board.get_checker((-1, 0)))
        self.assertIsNone(self.board.get_checker((8, 0)))
        for destination in [(-1, 0), (9, 8), (2, 3), (3, 3)]:
            with self.assertRaises(ValueError):
                self.board.move_checker((2, 1), destination)
        self.assertEqual(len(self.board.get_checkers()), 24)

    def test_both_colors_are_promoted(self):
        for color, start, end in [("black", (6, 1), (7, 2)),
                                  ("white", (1, 2), (0, 1))]:
            empty_board(self.board)
            checker = place(self.board, color, start)
            _, promoted = self.board.move_checker(start, end)
            self.assertTrue(promoted)
            self.assertTrue(checker.is_king)

    def test_king_moves_one_square_in_each_direction(self):
        empty_board(self.board)
        place(self.board, "black", (4, 3), king=True)
        self.assertEqual(set(self.board.get_valid_moves((4, 3))),
                         {(3, 2), (3, 4), (5, 2), (5, 4)})
        with self.assertRaises(ValueError):
            self.board.move_checker((4, 3), (2, 1))

    def test_king_can_capture_backward(self):
        empty_board(self.board)
        place(self.board, "white", (3, 2), king=True)
        place(self.board, "black", (4, 3))
        self.board.move_checker((3, 2), (5, 4))
        self.assertIsNone(self.board.get_checker((4, 3)))


class GameTests(unittest.TestCase):
    def setUp(self):
        self.game = Game("Alex", "Sam")

    def test_new_game_and_moves_by_both_players(self):
        self.assertEqual(self.game.current_player.color, "black")
        self.assertEqual(self.game.state, "playing")
        self.assertIsNone(self.game.end_time)
        self.game.make_move((2, 1), (3, 0))
        self.assertEqual(self.game.current_player.color, "white")
        self.game.make_move((5, 0), (4, 1))
        self.assertEqual(self.game.current_player.color, "black")
        self.assertEqual(self.game.total_moves, 2)
        self.assertEqual([p.moves for p in self.game.players], [1, 1])

    def test_cannot_move_an_opponent_or_empty_square(self):
        for start in [(5, 0), (4, 1)]:
            with self.assertRaises(ValueError):
                self.game.make_move(start, (4, 1))
        self.assertEqual(self.game.total_moves, 0)
        self.assertEqual(self.game.current_player.color, "black")

    def test_invalid_move_does_not_change_game(self):
        with self.assertRaises(ValueError):
            self.game.make_move((2, 1), (4, 1))
        self.assertEqual(len(self.game.board.get_checkers()), 24)
        self.assertEqual(self.game.total_moves, 0)
        self.assertIsNotNone(self.game.board.get_checker((2, 1)))

    def test_multiple_captures_lock_checker_and_count_one_turn(self):
        board = self.game.board
        empty_board(board)
        place(board, "black", (2, 1))
        place(board, "black", (2, 5))
        for position in [(3, 2), (5, 4), (3, 6), (7, 0)]:
            place(board, "white", position)
        self.game.make_move((2, 1), (4, 3))
        self.assertEqual(self.game.current_player.color, "black")
        self.assertEqual(self.game.forced_position, (4, 3))
        self.assertEqual(self.game.get_legal_moves(),
                         {(4, 3): {(6, 5): (5, 4)}})
        with self.assertRaises(ValueError):
            self.game.make_move((2, 5), (4, 7))
        with self.assertRaises(ValueError):
            self.game.make_move((4, 3), (5, 2))
        self.game.make_move((4, 3), (6, 5))
        self.assertEqual(self.game.total_moves, 1)
        self.assertEqual(self.game.players[0].moves, 1)
        self.assertEqual(self.game.current_player.color, "white")
        self.assertIsNone(self.game.forced_position)
        self.assertEqual(len(board.get_checkers("white")), 2)

    def test_can_choose_either_available_capture(self):
        board = self.game.board
        empty_board(board)
        place(board, "black", (2, 3))
        place(board, "white", (3, 2))
        place(board, "white", (3, 4))
        self.assertEqual(set(self.game.get_legal_moves()[(2, 3)]),
                         {(4, 1), (4, 5)})

    def test_promotion_ends_capture_turn_for_both_colors(self):
        for color in ("black", "white"):
            with self.subTest(color=color):
                game = Game("Alex", "Sam")
                empty_board(game.board)
                if color == "black":
                    start, jumped, end, extra = (5, 0), (6, 1), (7, 2), (6, 3)
                else:
                    game.current_player = game.players[1]
                    start, jumped, end, extra = (2, 1), (1, 2), (0, 3), (1, 4)
                opponent = "white" if color == "black" else "black"
                checker = place(game.board, color, start)
                place(game.board, opponent, jumped)
                place(game.board, opponent, extra)
                game.make_move(start, end)
                self.assertTrue(checker.is_king)
                self.assertTrue(game.board.get_valid_moves(end, True))
                self.assertIsNone(game.forced_position)
                self.assertEqual(game.current_player.color, opponent)
                self.assertEqual(game.state, "playing")

    def test_win_when_opponent_has_no_checkers(self):
        empty_board(self.game.board)
        place(self.game.board, "black", (2, 1))
        place(self.game.board, "white", (3, 2))
        self.game.make_move((2, 1), (4, 3))
        self.assertEqual(self.game.state, "completed")
        self.assertIs(self.game.winner, self.game.players[0])
        self.assertEqual([p.result for p in self.game.players],
                         ["Winner", "Lost"])
        self.assertIn("Opponent has no checkers", self.game.get_summary())

    def test_win_when_opponent_has_no_legal_moves(self):
        empty_board(self.game.board)
        place(self.game.board, "black", (2, 1))
        place(self.game.board, "white", (0, 1))
        self.game.make_move((2, 1), (3, 0))
        self.assertEqual(self.game.state, "completed")
        self.assertEqual(len(self.game.board.get_checkers("white")), 1)
        self.assertIn("Opponent has no legal moves", self.game.get_summary())

    def test_white_can_win(self):
        empty_board(self.game.board)
        place(self.game.board, "black", (2, 1))
        place(self.game.board, "white", (4, 3))
        self.game.make_move((2, 1), (3, 2))
        self.game.make_move((4, 3), (2, 1))
        self.assertIs(self.game.winner, self.game.players[1])

    def test_manual_finish_and_final_summary(self):
        self.game.make_move((2, 1), (3, 0))
        self.game.finish()
        summary = self.game.get_summary()
        self.assertEqual(self.game.state, "terminated")
        self.assertIsNone(self.game.winner)
        self.assertIsNotNone(self.game.end_time)
        for text in ["Manually terminated", "No winner", "Total moves: 1",
                     "Alex (Black)", "Sam (White)", "Remaining checkers: 12",
                     "Moves: 1", "Moves: 0", "Game duration:", "Turn time:"]:
            self.assertIn(text, summary)
        self.assertTrue(all(p.result == "Unfinished"
                            for p in self.game.players))
        end_time = self.game.end_time
        self.game.finish()
        self.assertEqual(self.game.end_time, end_time)
        with self.assertRaises(ValueError):
            self.game.make_move((5, 0), (4, 1))
        self.assertEqual(self.game.get_legal_moves(), {})

    def test_finish_during_capture_sequence(self):
        empty_board(self.game.board)
        place(self.game.board, "black", (2, 1))
        place(self.game.board, "white", (3, 2))
        place(self.game.board, "white", (5, 4))
        self.game.make_move((2, 1), (4, 3))
        self.game.finish()
        self.assertEqual(self.game.state, "terminated")
        self.assertEqual(self.game.total_moves, 1)
        self.assertEqual(self.game.get_legal_moves(), {})

    def test_new_game_is_independent_after_finish(self):
        self.game.make_move((2, 1), (3, 0))
        self.game.finish()
        another_game = Game("New Black", "New White")
        self.assertEqual(another_game.total_moves, 0)
        self.assertEqual(another_game.current_player.name, "New Black")
        self.assertEqual(len(another_game.board.get_checkers()), 24)
        self.assertEqual(another_game.state, "playing")
        self.assertIsNone(another_game.winner)
        self.assertIsNone(another_game.end_time)
        self.assertEqual([p.game_time for p in another_game.players], [0, 0])

    def test_turn_timers_and_final_duration_stop(self):
        with patch("game.monotonic", return_value=100):
            game = Game("Alex", "Sam")
        with patch("game.monotonic", return_value=110):
            game.make_move((2, 1), (3, 0))
        with patch("game.monotonic", return_value=125):
            self.assertEqual(game.get_player_time(game.players[0]), 10)
            self.assertEqual(game.get_player_time(game.players[1]), 15)
            game.finish()
        with patch("game.monotonic", return_value=500):
            self.assertEqual(game.get_duration(), 25)
            self.assertEqual(game.get_player_time(game.players[1]), 15)
        self.assertEqual(sum(p.game_time for p in game.players), 25)

    def test_names_colors_and_duration_format(self):
        self.assertEqual(Player("  Alex  ", "black").name, "Alex")
        with self.assertRaises(ValueError):
            Player("  ", "white")
        with self.assertRaises(ValueError):
            Player("Alex", "blue")
        self.assertEqual(format_duration(3661.9), "01:01:01")


if __name__ == "__main__":
    unittest.main()
