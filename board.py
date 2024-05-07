import pygame

from territory import Territory


class Board:
    def __init__(self):
        self.territories = {}
        self.initialize_territories()
        self.setup_neighbors()

    def initialize_territories(self):
        self.territories["alaska"] = Territory("Alaska", "alaska", "america", 50, 50, "alaska.png")
        self.territories["north_territory"] = Territory("North Territory", "north_territory", "america", 200, 50,
                                                        "north_territory.png")
        self.territories["greenland"] = Territory("Greenland", "greenland", "america", 350, 50, "greenland.png")
        self.territories["alberta"] = Territory("Alberta", "alberta", "america", 50, 200, "alberta.png")
        self.territories["ontario"] = Territory("Ontario", "ontario", "america", 200, 200, "ontario.png")
        self.territories["quebec"] = Territory("Quebec", "quebec", "america", 350, 200, "quebec.png")
        self.territories["united_states"] = Territory("United States", "united_states", "america", 50, 350, "united_states.png")
        self.territories["central_america"] = Territory("Central America", "central_america", "america", 200, 350,
                                                        "central_america.png")
        self.territories["venezuela"] = Territory("Venezuela", "venezuela", "south_america", 50, 350, "venezuela.png")
        self.territories["brazil"] = Territory("Brazil", "brazil", "south_america", 50, 350, "brazil.png")
        self.territories["peru"] = Territory("Peru", "peru", "south_america", 50, 350, "peru.png")
        self.territories["iceland"] = Territory("Iceland", "iceland", "europe", 50, 350, "iceland.png")
        self.territories["scandinavia"] = Territory("Scandinavia", "scandinavia", "europe", 50, 350, "scandinavia.png")
        self.territories["great_britain"] = Territory("Great Britain", "great_britain", "europe", 50, 350, "great_britain.png")
        self.territories["poland"] = Territory("Poland", "poland", "europe", 50, 350, "poland.png")
        self.territories["greece"] = Territory("Greece", "greece", "europe", 50, 350, "greece.png")
        self.territories["spain"] = Territory("Spain", "spain", "europe", 50, 350, "spain.png")
        self.territories["ukraine"] = Territory("Ukraine", "ukraine", "europe", 50, 350, "ukraine.png")
        self.territories["morocco"] = Territory("Morocco", "morocco", "africa", 50, 350, "morocco.png")
        self.territories["egypt"] = Territory("Egypt", "egypt", "africa", 50, 350, "egypt.png")
        self.territories["sudan"] = Territory("Sudan", "sudan", "africa", 50, 350, "sudan.png")
        self.territories["congo"] = Territory("Congo", "congo", "africa", 50, 350, "congo.png")
        self.territories["south_africa"] = Territory("South Africa", "south_africa", "africa", 50, 350, "south_africa.png")
        self.territories["madagascar"] = Territory("Madagascar", "madagascar", "africa", 50, 350, "madagascar.png")
        self.territories["siberia"] = Territory("Siberia", "siberia", "asia", 50, 350, "siberia.png")
        self.territories["yakutsk"] = Territory("Yakutsk", "yakutsk", "asia", 50, 350, "yakutsk.png")
        self.territories["kamchatka"] = Territory("Kamchatka", "kamchatka", "asia", 50, 350, "kamchatka.png")
        self.territories["ural"] = Territory("Ural", "ural", "asia", 50, 350, "ural.png")
        self.territories["irkutsk"] = Territory("Irkutsk", "irkutsk", "asia", 50, 350, "irkutsk.png")
        self.territories["mongolia"] = Territory("Mongolia", "mongolia", "asia", 50, 350, "mongolia.png")
        self.territories["japan"] = Territory("Japan", "japan", "asia", 50, 350, "japan.png")
        self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", "asia", 50, 350, "afghanistan.png")
        self.territories["china"] = Territory("China", "china", "asia", 50, 350, "china.png")
        self.territories["israel"] = Territory("Israel", "israel", "asia", 50, 350, "israel.png")
        self.territories["india"] = Territory("India", "india", "asia", 50, 350, "india.png")
        self.territories["siam"] = Territory("Siam", "siam", "asia", 50, 350, "siam.png")
        self.territories["indonesia"] = Territory("Indonesia", "indonesia", "oceania", 50, 350, "indonesia.png")
        self.territories["new_guinea"] = Territory("New Guinea", "new_guinea", "oceania", 50, 350, "new_guinea.png")
        self.territories["western_australia"] = Territory("Western Australia", "western_australia", "oceania", 50, 350, "western_australia.png")
        self.territories["eastern_australia"] = Territory("Eastern Australia", "eastern_australia", "oceania", 50, 350, "eastern_australia.png")




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
