class Player:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.move = 0
        self.result = None
        self.game_time = 0
    
player1 = Player('Shaon', 'White')
player2 = Player('Rifat', 'Black')

print(player1.name, player1.color)
print(player2.name, player2.color)