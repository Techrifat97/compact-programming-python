"""The standard 8 by 8 board and legal checker movements."""

from checker import Checker


class Board:
    SIZE = 8

    def __init__(self):
        self.squares = []
        self.initialize_board()

    def initialize_board(self):
        self.squares = []
        for row in range(self.SIZE):
            self.squares.append([None] * self.SIZE)

        for row in range(self.SIZE):
            for column in range(self.SIZE):
                if (row + column) % 2 == 0:
                    continue

                position = (row, column)
                if row < 3:
                    self.squares[row][column] = Checker("black", position)
                elif row > 4:
                    self.squares[row][column] = Checker("white", position)

    def is_inside(self, position):
        row, column = position
        return 0 <= row < self.SIZE and 0 <= column < self.SIZE

    def get_checker(self, position):
        if not self.is_inside(position):
            return None
        row, column = position
        return self.squares[row][column]

    def get_checkers(self, color=None):
        checkers = []
        for row in self.squares:
            for checker in row:
                if checker is None:
                    continue
                if color is None or checker.color == color:
                    checkers.append(checker)
        return checkers

    def get_valid_moves(self, position, capture_only=False):
        """Find moves for one checker, before checking other checkers."""
        checker = self.get_checker(position)
        if checker is None:
            return {}
        # Each destination stores the captured square, or None for a step.
        moves = {}
        row, column = position
        for row_step, column_step in checker.get_directions():
            adjacent = (row + row_step, column + column_step)
            if not self.is_inside(adjacent):
                continue
            neighbor = self.get_checker(adjacent)
            if neighbor is None:
                if not capture_only:
                    moves[adjacent] = None
            elif neighbor.color != checker.color:
                landing = (row + 2 * row_step, column + 2 * column_step)
                if (self.is_inside(landing)
                        and self.get_checker(landing) is None):
                    moves[landing] = adjacent
        return moves

    def get_legal_moves(self, color, forced_position=None):
        if forced_position is not None:
            checker = self.get_checker(forced_position)
            if checker is None or checker.color != color:
                return {}
            captures = self.get_valid_moves(forced_position, capture_only=True)
            if captures:
                return {forced_position: captures}
            return {}

        captures = {}
        ordinary_moves = {}
        for checker in self.get_checkers(color):
            moves = self.get_valid_moves(checker.position)
            jumps = {}
            for destination, jumped in moves.items():
                if jumped is not None:
                    jumps[destination] = jumped
            if jumps:
                captures[checker.position] = jumps
            if moves:
                ordinary_moves[checker.position] = moves
        if captures:
            return captures
        return ordinary_moves

    def move_checker(self, start, destination):
        """Apply a legal board move and return (captured_checker, promoted)."""
        checker = self.get_checker(start)
        if checker is None:
            raise ValueError("There is no checker on that square.")
        legal_moves = self.get_legal_moves(checker.color)
        if destination not in legal_moves.get(start, {}):
            raise ValueError(
                "That move is not legal. Check for required captures.")

        jumped = legal_moves[start][destination]
        captured = None
        if jumped is not None:
            captured = self.get_checker(jumped)
            jumped_row, jumped_column = jumped
            self.squares[jumped_row][jumped_column] = None

        was_king = checker.is_king
        start_row, start_column = start
        end_row, end_column = destination
        self.squares[start_row][start_column] = None
        self.squares[end_row][end_column] = checker
        checker.move_to(destination)
        promoted = checker.is_king and not was_king
        return captured, promoted
