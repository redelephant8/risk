from board import Board

class Player:
    def __init__(self, color, name, position=None):
        self.name = name
        self.color = color
        self.territoryNumber = 0
        self.territories = []
        self.cards = []



