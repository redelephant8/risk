from board import Board

class Player:
    def __init__(self, color, name, connection, soldiers_in_hand=5):
        self.name = name
        self.color = color
        self.territoryNumber = 0
        self.territories = []
        self.cards = {"infantry": 0, "cavalry": 0, "artillery": 0}
        self.has_conquered = False
        self.soldiers_in_hand = soldiers_in_hand
        self.isOut = False
        self.connection = connection

    def reinforcement_calculator(self):
        if len(self.territories) < 11:
            return 3
        return len(self.territories) % 3



