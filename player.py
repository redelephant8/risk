from board import Board


class Player:
    def __init__(self, color, name, connection, soldiers_in_hand=10):
        self.name = name
        self.color = color
        self.territoryNumber = 0
        self.territories = []
        self.cards = {"infantry": 0, "cavalry": 0, "artillery": 0}
        self.has_conquered = False
        self.soldiers_in_hand = soldiers_in_hand
        self.isOut = False
        self.is_out_initial = False
        self.connection = connection
        self.available_neighbors_list = []

    def reinforcement_calculator(self):
        if len(self.territories) < 11:
            return 3
        return int(len(self.territories) / 3)

    def create_neighbor_web(self, territory):
        self.available_neighbors_list = []
        visited_territories = []

        self.find_neighbors_of_neighbors(territory, visited_territories)

        return self.available_neighbors_list

    def find_neighbors_of_neighbors(self, territory, visited_territories):
        visited_territories.append(territory)
        neighbors = territory.neighbor_list_player(self)
        self.available_neighbors_list.extend(neighbors)
        for neighbor in neighbors:
            if neighbor not in visited_territories:
                self.find_neighbors_of_neighbors(neighbor, visited_territories)
