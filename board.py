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
        self.territories["eastern_australia"] = Territory("Eastern Australia", "eastern_australia", "oceania", 50, 350, "australia.png")




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



