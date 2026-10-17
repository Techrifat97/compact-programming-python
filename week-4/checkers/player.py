"""Information about one human player."""


class Player:
    def __init__(self, name, color):
        name = name.strip()
        if not name:
            raise ValueError("Please enter a player name.")
        if color not in ("black", "white"):
            raise ValueError("Checker color must be black or white.")
        self.name = name
        self.color = color
        self.moves = 0
        self.result = "In progress"
        self.game_time = 0.0
