import pygame

from territory import Territory


class Board:
    def __init__(self):
        self.territories = {}
        self.initialize_territories()
        self.setup_neighbors()

    def initialize_territories(self):
        self.territories["alaska"] = Territory("Alaska", "alaska", 50, 50, "alaska.png")
        self.territories["north_territory"] = Territory("North Territory", "north_territory", 200, 50,
                                                        "north_territory.png")
        self.territories["greenland"] = Territory("Greenland", "greenland", 350, 50, "greenland.png")
        self.territories["alberta"] = Territory("Alberta", "alberta", 50, 200, "alberta.png")
        self.territories["ontario"] = Territory("Ontario", "ontario", 200, 200, "ontario.png")
        self.territories["quebec"] = Territory("Quebec", "quebec", 350, 200, "quebec.png")
        self.territories["united_states"] = Territory("United States", "united_states", 50, 350, "united_states.png")
        self.territories["central_america"] = Territory("Central America", "central_america", 200, 350,
                                                        "central_america.png")

        # self.territories["qatar"] = Territory("Qatar", "qatar", 50, 100, "qatar.png")
        # self.territories["egypt"] = Territory("Egypt", "egypt", 100, 500, "egypt.png")
        # self.territories["iran"] = Territory("Iran", "iran", 150, 200, "iran.png")
        # self.territories["saudi_arabia"] = Territory("Saudi Arabia", "saudi_arabia", 200, 500, "saudi_arabia.png")
        # self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", 250, 400, "afghanistan.png")

    def setup_neighbors(self):
        self.territories["alaska"].neighbors = [self.territories["north_territory"], self.territories["alberta"]]
        self.territories["north_territory"].neighbors = [self.territories["greenland"], self.territories["alberta"], self.territories["ontario"], self.territories["alaska"]]
        self.territories["greenland"].neighbors = [self.territories["quebec"], self.territories["north_territory"], self.territories["ontario"]]
        self.territories["alberta"].neighbors = [self.territories["alaska"], self.territories["north_territory"], self.territories["ontario"], self.territories["united_states"]]
        self.territories["ontario"].neighbors = [self.territories["north_territory"], self.territories["alberta"], self.territories["greenland"], self.territories["quebec"], self.territories["united_states"]]
        self.territories["quebec"].neighbors = [self.territories["greenland"], self.territories["ontario"], self.territories["united_states"]]
        self.territories["united_states"].neighbors = [self.territories["alberta"], self.territories["ontario"], self.territories["central_america"]]
        self.territories["central_america"].neighbors = [self.territories["united_states"]]
