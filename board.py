import pygame

from territory import Territory


class Board:
    def __init__(self):
        self.pieces = {}
        self.initialize_territories()
        self.setup_neighbors()

    def initialize_territories(self):
        self.pieces["qatar"] = Territory("Qatar", 50, 100, "qatar.png")
        self.pieces["egypt"] = Territory("Egypt", 500, 150, "egypt.png")
        self.pieces["iran"] = Territory("Iran", 150, 200, "iran.png")
        self.pieces["saudi_arabia"] = Territory("Saudi Arabia", 200, 250, "saudi_arabia.png")
        self.pieces["afghanistan"] = Territory("Afghanistan", 250, 300, "afghanistan.png")

    def setup_neighbors(self):
        self.pieces["qatar"].neighbors = [self.pieces["egypt"], self.pieces["iran"], self.pieces["afghanistan"]]
        self.pieces["egypt"].neighbors = [self.pieces["qatar"], self.pieces["iran"], self.pieces["saudi_arabia"]]
        self.pieces["saudi_arabia"].neighbors = [self.pieces["egypt"], self.pieces["afghanistan"]]
        self.pieces["afghanistan"].neighbors = [self.pieces["saudi_arabia"], self.pieces["qatar"]]
        self.pieces["iran"].neighbors = [self.pieces["qatar"], self.pieces["egypt"]]



