class Checker:
    def __init__(self, color, row, col):
        self.color = color
        self.row = row
        self.col = col
        self.is_king = False
    
    def move(self, new_row, new_col):
        self.row = new_row
        self.col = new_col
    
    def make_king(self):
        self.is_king = True
    
checker1 = Checker('white', 5, 0)
checker1.move(4,1)
checker1.make_king()
print(checker1.color, checker1.row, checker1.col)
print(checker1.is_king)