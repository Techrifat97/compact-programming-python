"""Turns, player statistics, game timing, and results, without a GUI."""

from datetime import datetime
from time import monotonic

from board import Board
from player import Player


def format_duration(seconds):
    seconds = max(0, int(seconds))
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    seconds = seconds % 60
    return f"{hours:02d}:{minutes:02d}:{seconds:02d}"


class Game:
    def __init__(self, black_name, white_name):
        self.players = [Player(black_name, "black"),
                        Player(white_name, "white")]
        self.board = Board()
        self.current_player = self.players[0]
        self.total_moves = 0
        self.start_time = datetime.now()
        self.end_time = None
        self.state = "playing"
        self.winner = None
        self.forced_position = None
        # Use monotonic time so clock changes do not affect elapsed time.
        self._start_tick = monotonic()
        self._turn_start_tick = self._start_tick
        self._end_tick = None

    def get_legal_moves(self):
        if self.state != "playing":
            return {}
        return self.board.get_legal_moves(
            self.current_player.color, self.forced_position)

    def make_move(self, start, destination):
        if self.state != "playing":
            raise ValueError(
                "The game has ended. Start a new game to play again.")
        checker = self.board.get_checker(start)
        if checker is None or checker.color != self.current_player.color:
            raise ValueError("Select one of your own checkers.")
        if self.forced_position is not None and start != self.forced_position:
            raise ValueError("Continue capturing with the same checker.")
        legal_moves = self.get_legal_moves()
        destinations = legal_moves.get(start, {})
        if destination not in destinations:
            raise ValueError(
                "That move is not allowed. Captures must be taken.")

        captured, promoted = self.board.move_checker(start, destination)
        # Count a turn once, on its first step, including an interrupted turn.
        if self.forced_position is None:
            self.total_moves += 1
            self.current_player.moves += 1

        if captured is not None and not promoted:
            next_captures = self.board.get_valid_moves(
                destination, capture_only=True)
            if next_captures:
                self.forced_position = destination
                return

        # In English draughts, promotion ends the turn, even after a capture.
        self.forced_position = None
        if self.current_player is self.players[0]:
            opponent = self.players[1]
        else:
            opponent = self.players[0]
        if not self.board.get_legal_moves(opponent.color):
            self._end_game("completed", winner=self.current_player)
        else:
            now = monotonic()
            self.current_player.game_time += now - self._turn_start_tick
            self.current_player = opponent
            self._turn_start_tick = now

    def finish(self):
        if self.state == "playing":
            self._end_game("terminated")

    def _end_game(self, state, winner=None):
        self._end_tick = monotonic()
        elapsed = self._end_tick - self._turn_start_tick
        self.current_player.game_time += elapsed
        self.end_time = datetime.now()
        self.state = state
        self.winner = winner
        for player in self.players:
            if winner is None:
                player.result = "Unfinished"
            elif player is winner:
                player.result = "Winner"
            else:
                player.result = "Lost"

    def get_duration(self):
        if self._end_tick is None:
            return monotonic() - self._start_tick
        return self._end_tick - self._start_tick

    def get_player_time(self, player):
        seconds = player.game_time
        if self.state == "playing" and player is self.current_player:
            seconds += monotonic() - self._turn_start_tick
        return seconds

    def get_summary(self):
        if self.state == "completed":
            if self.winner.color == "black":
                opponent_color = "white"
            else:
                opponent_color = "black"
            if not self.board.get_checkers(opponent_color):
                reason = "Opponent has no checkers."
            else:
                reason = "Opponent has no legal moves."
            heading = (f"Completed game\nWinner: {self.winner.name} "
                       f"({self.winner.color.title()})\n{reason}")
        elif self.state == "terminated":
            heading = "Manually terminated game\nNo winner was declared."
        else:
            heading = "Game in progress"
        duration = format_duration(self.get_duration())
        lines = [
            heading,
            "",
            f"Total moves: {self.total_moves}",
            f"Game duration: {duration}",
            f"Started: {self.start_time:%Y-%m-%d %H:%M:%S}",
        ]
        if self.end_time is not None:
            lines.append(f"Ended: {self.end_time:%Y-%m-%d %H:%M:%S}")
        for player in self.players:
            remaining = len(self.board.get_checkers(player.color))
            turn_time = format_duration(self.get_player_time(player))
            lines.extend([
                "",
                f"{player.name} ({player.color.title()})",
                f"Result: {player.result}",
                f"Moves: {player.moves} | Remaining checkers: {remaining}",
                f"Turn time: {turn_time}",
            ])
        return "\n".join(lines)
