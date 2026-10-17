"""A single checker on the board."""


class Checker:
    def __init__(self, color, position):
        if color not in ("black", "white"):
            raise ValueError("Checker color must be black or white.")
        self.color = color
        self.position = position
        self.is_king = False

    def get_directions(self):
        if self.is_king:
            return [(-1, -1), (-1, 1), (1, -1), (1, 1)]
        if self.color == "black":
            forward = 1
        else:
            forward = -1
        return [(forward, -1), (forward, 1)]

    def move_to(self, position):
        self.position = position
        if self.color == "black":
            promotion_row = 7
        else:
            promotion_row = 0
        if position[0] == promotion_row:
            self.is_king = True
