# game/player.py

class Player:

    def __init__(self, row, col):
        self.row = row
        self.col = col

    def move_to(self, row, col):
        self.row = row
        self.col = col