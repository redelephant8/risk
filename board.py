import pygame

from territory import Territory


class Board:
    def __init__(self, demo):
        self.demo = demo
        self.territories = {}
        if demo:
            self.initialize_territories_demo()
            self.setup_neighbors_demo()
        else:
            self.initialize_territories()
            self.setup_neighbors()

    def initialize_territories(self):
        # North America
        self.territories["alaska"] = Territory("Alaska", "alaska", "america", 50, 50, "alaska.png")
        self.territories["north_territory"] = Territory("North Territory", "north_territory", "america", 150, 50,
                                                        "north_territory.png")
        self.territories["greenland"] = Territory("Greenland", "greenland", "america", 250, 50, "greenland.png")
        self.territories["alberta"] = Territory("Alberta", "alberta", "america", 50, 150, "alberta.png")
        self.territories["ontario"] = Territory("Ontario", "ontario", "america", 150, 150, "ontario.png")
        self.territories["quebec"] = Territory("Quebec", "quebec", "america", 250, 150, "quebec.png")
        self.territories["united_states"] = Territory("United States", "united_states", "america", 150, 250,
                                                      "united_states.png")
        self.territories["central_america"] = Territory("Central America", "central_america", "america", 50, 250,
                                                        "central_america.png")

        # South America
        self.territories["venezuela"] = Territory("Venezuela", "venezuela", "south_america", 50, 350, "venezuela.png")
        self.territories["brazil"] = Territory("Brazil", "brazil", "south_america", 150, 350, "brazil.png")
        self.territories["argentina"] = Territory("Argentina", "argentina", "south_america", 50, 550, "argentina.png")
        self.territories["peru"] = Territory("Peru", "peru", "south_america", 50, 450, "peru.png")

        # Europe
        self.territories["iceland"] = Territory("Iceland", "iceland", "europe", 400, 50, "iceland.png")
        self.territories["scandinavia"] = Territory("Scandinavia", "scandinavia", "europe", 500, 50, "scandinavia.png")
        self.territories["great_britain"] = Territory("Great Britain", "great_britain", "europe", 400, 150,
                                                      "great_britain.png")
        self.territories["poland"] = Territory("Poland", "poland", "europe", 500, 150, "poland.png")
        self.territories["greece"] = Territory("Greece", "greece", "europe", 500, 250, "greece.png")
        self.territories["spain"] = Territory("Spain", "spain", "europe", 400, 250, "spain.png")
        self.territories["ukraine"] = Territory("Ukraine", "ukraine", "europe", 575, 150, "ukraine.png")

        # Africa
        self.territories["morocco"] = Territory("Morocco", "morocco", "africa", 350, 350, "morocco.png")
        self.territories["egypt"] = Territory("Egypt", "egypt", "africa", 450, 350, "egypt.png")
        self.territories["sudan"] = Territory("Sudan", "sudan", "africa", 450, 450, "sudan.png")
        self.territories["congo"] = Territory("Congo", "congo", "africa", 350, 450, "congo.png")
        self.territories["south_africa"] = Territory("South Africa", "south_africa", "africa", 350, 550,
                                                     "south_africa.png")
        self.territories["madagascar"] = Territory("Madagascar", "madagascar", "africa", 450, 550, "madagascar.png")

        # Asia
        self.territories["siberia"] = Territory("Siberia", "siberia", "asia", 750, 50, "siberia.png")
        self.territories["yakutsk"] = Territory("Yakutsk", "yakutsk", "asia", 850, 50, "yakutsk.png")
        self.territories["kamchatka"] = Territory("Kamchatka", "kamchatka", "asia", 950, 50, "kamchatka.png")
        self.territories["ural"] = Territory("Ural", "ural", "asia", 650, 50, "ural.png")
        self.territories["irkutsk"] = Territory("Irkutsk", "irkutsk", "asia", 750, 150, "irkutsk.png")
        self.territories["mongolia"] = Territory("Mongolia", "mongolia", "asia", 850, 150, "mongolia.png")
        self.territories["japan"] = Territory("Japan", "japan", "asia", 950, 150, "japan.png")
        self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", "asia", 650, 150, "afghanistan.png")
        self.territories["china"] = Territory("China", "china", "asia", 850, 250, "china.png")
        self.territories["israel"] = Territory("Israel", "israel", "asia", 650, 250, "israel.png")
        self.territories["india"] = Territory("India", "india", "asia", 750, 250, "india.png")
        self.territories["siam"] = Territory("Siam", "siam", "asia", 950, 250, "siam.png")

        # Oceania
        self.territories["indonesia"] = Territory("Indonesia", "indonesia", "oceania", 750, 350, "indonesia.png")
        self.territories["new_guinea"] = Territory("New Guinea", "new_guinea", "oceania", 850, 350, "new_guinea.png")
        self.territories["western_australia"] = Territory("Western Australia", "western_australia", "oceania", 750, 450,
                                                          "western_australia.png")
        self.territories["eastern_australia"] = Territory("Eastern Australia", "eastern_australia", "oceania", 850, 450,
                                                          "australia.png")

        # self.territories["qatar"] = Territory("Qatar", "qatar", 50, 100, "qatar.png")
        # self.territories["egypt"] = Territory("Egypt", "egypt", 100, 500, "egypt.png")
        # self.territories["iran"] = Territory("Iran", "iran", 150, 200, "iran.png")
        # self.territories["saudi_arabia"] = Territory("Saudi Arabia", "saudi_arabia", 200, 500, "saudi_arabia.png")
        # self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", 250, 400, "afghanistan.png")

    def setup_neighbors(self):
        self.territories["alaska"].neighbors = [self.territories["north_territory"], self.territories["alberta"], self.territories["kamchatka"]]
        self.territories["north_territory"].neighbors = [self.territories["greenland"], self.territories["alberta"], self.territories["ontario"], self.territories["alaska"]]
        self.territories["greenland"].neighbors = [self.territories["quebec"], self.territories["north_territory"], self.territories["ontario"], self.territories["iceland"]]
        self.territories["alberta"].neighbors = [self.territories["alaska"], self.territories["north_territory"], self.territories["ontario"], self.territories["united_states"]]
        self.territories["ontario"].neighbors = [self.territories["north_territory"], self.territories["alberta"], self.territories["greenland"], self.territories["quebec"], self.territories["united_states"]]
        self.territories["quebec"].neighbors = [self.territories["greenland"], self.territories["ontario"], self.territories["united_states"]]
        self.territories["united_states"].neighbors = [self.territories["alberta"], self.territories["ontario"], self.territories["central_america"]]
        self.territories["central_america"].neighbors = [self.territories["united_states"], self.territories["venezuela"]]
        self.territories["venezuela"].neighbors = [self.territories["central_america"], self.territories["brazil"], self.territories["peru"]]
        self.territories["peru"].neighbors = [self.territories["venezuela"], self.territories["brazil"], self.territories["argentina"]]
        self.territories["argentina"].neighbors = [self.territories["peru"], self.territories["brazil"]]
        self.territories["brazil"].neighbors = [self.territories["venezuela"], self.territories["peru"], self.territories["argentina"], self.territories["morocco"]]
        self.territories["iceland"].neighbors = [self.territories["greenland"], self.territories["scandinavia"], self.territories["great_britain"]]
        self.territories["great_britain"].neighbors = [self.territories["iceland"], self.territories["scandinavia"], self.territories["spain"], self.territories["poland"]]
        self.territories["scandinavia"].neighbors = [self.territories["iceland"], self.territories["poland"], self.territories["ukraine"]]
        self.territories["ukraine"].neighbors = [self.territories["scandinavia"], self.territories["poland"], self.territories["greece"], self.territories["israel"], self.territories["afghanistan"], self.territories["ural"]]
        self.territories["poland"].neighbors = [self.territories["great_britain"], self.territories["scandinavia"], self.territories["ukraine"], self.territories["greece"], self.territories["spain"]]
        self.territories["greece"].neighbors = [self.territories["poland"], self.territories["spain"], self.territories["ukraine"], self.territories["morocco"], self.territories["egypt"], self.territories["israel"]]
        self.territories["spain"].neighbors = [self.territories["great_britain"], self.territories["poland"], self.territories["greece"], self.territories["morocco"]]
        self.territories["morocco"].neighbors = [self.territories["brazil"], self.territories["spain"], self.territories["greece"], self.territories["egypt"], self.territories["sudan"], self.territories["congo"]]
        self.territories["egypt"].neighbors = [self.territories["greece"], self.territories["israel"], self.territories["sudan"], self.territories["morocco"]]
        self.territories["sudan"].neighbors = [self.territories["egypt"], self.territories["morocco"], self.territories["israel"], self.territories["congo"], self.territories["south_africa"], self.territories["madagascar"]]
        self.territories["congo"].neighbors = [self.territories["morocco"], self.territories["sudan"], self.territories["south_africa"]]
        self.territories["south_africa"].neighbors = [self.territories["congo"], self.territories["sudan"], self.territories["madagascar"]]
        self.territories["madagascar"].neighbors = [self.territories["south_africa"], self.territories["sudan"]]
        self.territories["ural"].neighbors = [self.territories["ukraine"], self.territories["siberia"], self.territories["afghanistan"], self.territories["china"]]
        self.territories["siberia"].neighbors = [self.territories["ural"], self.territories["yakutsk"], self.territories["irkutsk"], self.territories["mongolia"], self.territories["china"]]
        self.territories["yakutsk"].neighbors = [self.territories["siberia"], self.territories["irkutsk"], self.territories["kamchatka"]]
        self.territories["kamchatka"].neighbors = [self.territories["yakutsk"], self.territories["irkutsk"], self.territories["mongolia"], self.territories["japan"], self.territories["alaska"]]
        self.territories["irkutsk"].neighbors = [self.territories["siberia"], self.territories["yakutsk"], self.territories["kamchatka"], self.territories["mongolia"]]
        self.territories["mongolia"].neighbors = [self.territories["siberia"], self.territories["irkutsk"], self.territories["kamchatka"], self.territories["japan"], self.territories["china"]]
        self.territories["japan"].neighbors = [self.territories["kamchatka"], self.territories["mongolia"]]
        self.territories["afghanistan"].neighbors = [self.territories["ukraine"], self.territories["ural"], self.territories["china"], self.territories["india"], self.territories["israel"]]
        self.territories["china"].neighbors = [self.territories["afghanistan"], self.territories["ural"], self.territories["siberia"], self.territories["mongolia"], self.territories["siam"], self.territories["india"]]
        self.territories["israel"].neighbors = [self.territories["ukraine"], self.territories["greece"], self.territories["afghanistan"], self.territories["india"], self.territories["egypt"], self.territories["sudan"]]
        self.territories["india"].neighbors = [self.territories["afghanistan"], self.territories["china"], self.territories["siam"], self.territories["israel"]]
        self.territories["siam"].neighbors = [self.territories["india"], self.territories["china"], self.territories["indonesia"]]
        self.territories["indonesia"].neighbors = [self.territories["siam"], self.territories["new_guinea"], self.territories["western_australia"]]
        self.territories["new_guinea"].neighbors = [self.territories["indonesia"], self.territories["western_australia"], self.territories["eastern_australia"]]
        self.territories["western_australia"].neighbors = [self.territories["indonesia"], self.territories["new_guinea"], self.territories["eastern_australia"]]
        self.territories["eastern_australia"].neighbors = [self.territories["new_guinea"], self.territories["western_australia"]]

    def initialize_territories_demo(self):
        # Asia
        self.territories["siberia"] = Territory("Siberia", "siberia", "asia", 400, 150, "siberia.png")
        self.territories["yakutsk"] = Territory("Yakutsk", "yakutsk", "asia", 600, 100, "yakutsk.png")
        self.territories["kamchatka"] = Territory("Kamchatka", "kamchatka", "asia", 800, 100, "kamchatka.png")
        self.territories["ural"] = Territory("Ural", "ural", "asia", 200, 100, "ural.png")
        self.territories["irkutsk"] = Territory("Irkutsk", "irkutsk", "asia", 400, 300, "irkutsk.png")
        self.territories["mongolia"] = Territory("Mongolia", "mongolia", "asia", 600, 300, "mongolia.png")
        self.territories["japan"] = Territory("Japan", "japan", "asia", 800, 300, "japan.png")
        self.territories["afghanistan"] = Territory("Afghanistan", "afghanistan", "asia", 200, 300, "afghanistan.png")
        self.territories["china"] = Territory("China", "china", "asia", 600, 500, "china.png")
        self.territories["israel"] = Territory("Israel", "israel", "asia", 200, 500, "israel.png")
        self.territories["india"] = Territory("India", "india", "asia", 400, 500, "india.png")
        self.territories["siam"] = Territory("Siam", "siam", "asia", 800, 500, "siam.png")

    def setup_neighbors_demo(self):
        self.territories["ural"].neighbors = [self.territories["siberia"], self.territories["afghanistan"], self.territories["china"]]
        self.territories["siberia"].neighbors = [self.territories["ural"], self.territories["yakutsk"], self.territories["irkutsk"], self.territories["mongolia"], self.territories["china"]]
        self.territories["yakutsk"].neighbors = [self.territories["siberia"], self.territories["irkutsk"], self.territories["kamchatka"]]
        self.territories["kamchatka"].neighbors = [self.territories["yakutsk"], self.territories["irkutsk"], self.territories["mongolia"], self.territories["japan"]]
        self.territories["irkutsk"].neighbors = [self.territories["siberia"], self.territories["yakutsk"], self.territories["kamchatka"], self.territories["mongolia"]]
        self.territories["mongolia"].neighbors = [self.territories["siberia"], self.territories["irkutsk"], self.territories["kamchatka"], self.territories["japan"], self.territories["china"]]
        self.territories["japan"].neighbors = [self.territories["kamchatka"], self.territories["mongolia"]]
        self.territories["afghanistan"].neighbors = [self.territories["ural"], self.territories["china"], self.territories["india"], self.territories["israel"]]
        self.territories["china"].neighbors = [self.territories["afghanistan"], self.territories["ural"], self.territories["siberia"], self.territories["mongolia"], self.territories["siam"], self.territories["india"]]
        self.territories["israel"].neighbors = [self.territories["afghanistan"], self.territories["india"]]
        self.territories["india"].neighbors = [self.territories["afghanistan"], self.territories["china"], self.territories["siam"], self.territories["israel"]]
        self.territories["siam"].neighbors = [self.territories["india"], self.territories["china"]]



