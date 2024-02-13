from board import Board

class Player:
    def __init__(self, color, name, soldiers_in_hand=3):
        self.name = name
        self.color = color
        self.territoryNumber = 0
        self.territories = []
        self.cards = []
        self.soldiers_in_hand = soldiers_in_hand
        self.isOut = False

    def reinforcement_calculator(self):
        if self.soldiers_in_hand < 11:
            return 3
        return self.soldiers_in_hand % 3




