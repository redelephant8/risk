import pygame

from territory import Territory


class Board:
    def __init__(self):
        self.territories = {}
        self.initialize_territories()
        self.setup_neighbors()

    def initialize_territories(self):
        self.territories["qatar"] = Territory("Qatar", "qatar", 50, 100, "qatar.png")
        self.territories["egypt"] = Territory("Egypt", "egypt", 100, 500, "egypt.png")
        self.territories["iran"] = Territory("Iran", "iran", 150, 200, "iran.png")
        self.territories["saudi_arabia"] = Territory("Saudi Arabia", "saudi_arabia", 200, 500, "saudi_arabia.png")
        self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", 250, 400, "afghanistan.png")

    def setup_neighbors(self):
        self.territories["qatar"].neighbors = [self.territories["egypt"], self.territories["iran"], self.territories["afghanistan"]]
        self.territories["egypt"].neighbors = [self.territories["qatar"], self.territories["iran"], self.territories["saudi_arabia"]]
        self.territories["saudi_arabia"].neighbors = [self.territories["egypt"], self.territories["afghanistan"]]
        self.territories["afghanistan"].neighbors = [self.territories["saudi_arabia"], self.territories["qatar"]]
        self.territories["iran"].neighbors = [self.territories["qatar"], self.territories["egypt"]]
