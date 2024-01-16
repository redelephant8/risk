from board import Board

class Player:
    def __init__(self, color, name, starting_soldiers=35):
        self.name = name
        self.color = color
        self.territoryNumber = 0
        self.territories = []
        self.cards = []
        self.starting_soldiers = starting_soldiers



