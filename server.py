import socket
import threading
import pickle
import time
import sqlite3
import json
from board import Board
from player import Player
import random

colors = ['red', 'blue', 'yellow', 'green', 'purple', 'pink']
class RiskServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Store client connections
        self.board = Board(True)
        self.player_list = []
        self.player_names = []
        self.game_host = None
        self.current_player = None
        self.player_number = 0
        self.players_remaining = 0
        self.territories_remaining = len(self.board.territories)
        self.current_attacking_territory = None
        self.current_attack_number = 0
        self.current_defending_territory = None
        self.dice = []
        self.fortify = []
        self.cards = ["infantry"]*14 + ["cavalry"]*14 + ["artillery"]*14
        self.card_reinforcements = [4, 6, 8, 10, 15, 20, 25, 30, 35, 40, 45, 50, 55, 60]
        self.game_code = None
        self.saved_player_names = []
        self.saved_game = False
        self.saved_player_amount = 0
        self.game_stage = []

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        random.shuffle(self.cards)
        initialize_database()

        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            print(f"connections length: {len(self.connections)}")
            if len(self.connections) >= 6:
                client_socket, client_address = self.server_socket.accept()
                if len(self.connections) < 6:
                    self.connections.append(client_socket)
                    print(f"New connection from {client_socket.getpeername()}")

                    if not self.game_host:
                        self.game_host = client_socket
                        print(f"{client_socket} is the host of the game.")
                        self.game_code = generate_unique_game_code()

                        # Sending message to the host
                        self.send_to_client(client_socket, {"type": "join_message", "message": "You are the host."})

                    client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                    client_thread.start()
                    continue
                print("Rejecting connection: Maximum number of players reached.")
                self.send_to_client(client_socket, {"type": "max_players_reached"})
                client_socket.close()
            else:
                client_socket, client_address = self.server_socket.accept()
                self.connections.append(client_socket)
                self.send_to_client(client_socket, {"connections": len(self.connections), "saved_game": self.saved_game})
                # self.send_to_client(client_socket, len(self.connections))
                print(f"New connection from {client_socket.getpeername()}")

                if not self.game_host:
                    self.game_host = client_socket
                    print(f"{client_socket} is the host of the game.")
                    self.game_code = generate_unique_game_code()
                    # Sending message to the host
                    time.sleep(0.1)
                    self.send_to_client(client_socket, {"type": "join_message", "message": "You are the host."})

                client_thread = threading.Thread(target=self.handle_client, args=(client_socket,))
                client_thread.start()

    def handle_client(self, client_socket):
        while True:
            try:
                data = client_socket.recv(1024)
                if not data:
                    break

                # Process received data
                message = pickle.loads(data)
                message_type = message.get("type")
                time.sleep(0.1)

                if message_type == "name_selection":
                    print(f"Connected player name: {message.get('name')}")
                    self.player_names.append(message.get('name'))
                    self.player_list.append(Player("None", message.get('name'), client_socket))
                    self.broadcast({"type": "player_names", "message": self.player_names, "code": self.game_code, "game_type": "new", "number": 0})

                if message_type == "game_code":
                    if message.get("code") == self.game_code:
                        self.send_to_client(client_socket, True)
                    else:
                        self.send_to_client(client_socket, False)
                    # if message.get("code") == self.game_code:
                    #     self.send_to_client(client_socket, {"type": "code_result", "result": "pass"})
                    # else:
                    #     self.send_to_client(client_socket, {"type": "code_result", "result": "fail"})

                # if message_type == "saved_game_code":
                #     time.sleep(0.1)
                #     if message.get("code") == self.game_code:
                #         self.send_to_client()

                if message_type == "start_game":
                    print("Host started game")
                    for player in self.player_list:
                        player.color = colors[0]
                        colors.pop(0)
                        self.send_to_client(player.connection, {"type": "player_color", "color": player.color})
                    print(self.board)
                    packed_territory_info = self.pack_territory_info()
                    self.player_number = len(self.player_list)
                    self.switch_player()
                    self.broadcast(({"type": "start_game", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                    time.sleep(0.1)
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_territory_selection"})

                if message_type == "start_saved_game":
                    self.create_player_list()
                    for player in self.player_list:
                        self.send_to_client(player.connection, {"type": "player_color", "color": player.color})
                    time.sleep(0.1)
                    packed_territory_info = self.pack_territory_info()
                    print(packed_territory_info)
                    self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                     "current_player": self.current_player.name}))
                    time.sleep(0.1)
                    self.send_to_client(self.current_player.connection, {"type": "continue_game", "stage": self.game_stage})


                if message_type == "selected_initial_territory":
                    selected_initial_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_initial_territory(selected_initial_territory):
                        packed_territory_info = self.pack_territory_info()
                        print(packed_territory_info)
                        self.switch_player()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                        time.sleep(0.1)
                        if self.territories_remaining > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_territory_selection"})
                        else:
                            self.current_player = self.player_list[0]
                            self.players_remaining = len(self.player_names)
                            self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                            time.sleep(0.1)
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_soldier_addition"})

                if message_type == "selected_initial_soldier_territory":
                    selected_initial_soldier_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_initial_soldier_territory(selected_initial_soldier_territory):
                        packed_territory_info = self.pack_territory_info()
                        print(packed_territory_info)
                        print(self.players_remaining)
                        self.switch_player()
                        if self.players_remaining > 0 and self.current_player.is_out_initial is True:
                            while self.current_player.is_out_initial is True:
                                self.switch_player()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        time.sleep(0.1)
                        if self.players_remaining > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_soldier_addition"})
                        else:
                            # for player in self.player_list:
                            #     player.isOut = False
                            self.current_player = self.player_list[0]
                            self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
                            self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                            time.sleep(0.1)
                            card_series, forced = self.has_card_series()
                            if card_series and self.card_reinforcements != []:
                                self.send_to_client(self.current_player.connection,{"type": "turn_message", "turn_type": "card_turn_in", "number": self.card_reinforcements[0], "forced": forced})
                            else:
                                self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})

                if message_type == "selected_card_series":
                    result_index = message.get("number")
                    if result_index == 1:
                        self.send_to_client(self.current_player.connection,{"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})
                    else:
                        self.current_player.soldiers_in_hand += self.card_reinforcements.pop(0)
                        self.remove_cards()
                        packed_territory_info = self.pack_territory_info()
                        print(packed_territory_info)
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                         "current_player": self.current_player.name}))
                        time.sleep(0.1)
                        self.send_to_client(self.current_player.connection,{"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})

                if message_type == "selected_reinforcement_territory":
                    selected_territory = self.board.territories[message.get("territory")]
                    if self.check_reinforcement_territory(selected_territory):
                        packed_territory_info = self.pack_territory_info()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        if self.current_player.soldiers_in_hand > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "False"})
                        else:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_attacking_territory"})

                if message_type == "selected_attacking_territory":
                    if message.get("territory") == "end_combat":
                        if self.check_if_can_fortify():
                            packed_territory_info = self.pack_territory_info()
                            print(packed_territory_info)
                            self.broadcast({"type": "edit_board", "territory_info": packed_territory_info,
                                            "current_player": self.current_player.name})
                            time.sleep(0.1)
                            self.send_to_client(self.current_player.connection,
                                                {"type": "turn_message", "turn_type": "fortify_position"})
                        else:
                            self.end_turn()
                    else:
                        selected_territory = self.board.territories[message.get("territory")]
                        check_selected, number = self.check_attacking_territory(selected_territory)
                        if check_selected:
                            self.current_attacking_territory = selected_territory
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_attacking_soldiers", "number": number})

                if message_type == "selected_attacking_soldiers":
                    self.current_attack_number = message.get("number")
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_defending_territory"})

                if message_type == "selected_defending_territory":
                    if message.get("territory") == "end_combat":
                        if self.check_if_can_fortify():
                            packed_territory_info = self.pack_territory_info()
                            print(packed_territory_info)
                            self.broadcast({"type": "edit_board", "territory_info": packed_territory_info,
                                            "current_player": self.current_player.name})
                            time.sleep(0.1)
                            self.send_to_client(self.current_player.connection,
                                                {"type": "turn_message", "turn_type": "fortify_position"})
                        else:
                            self.end_turn()
                    else:
                        selected_territory = self.board.territories[message.get("territory")]
                        if self.check_defending_territory(selected_territory):
                            self.current_defending_territory = selected_territory
                            self.attack(self.current_attacking_territory, selected_territory)

                if message_type == "selected_transferring_soldiers":
                    num_transferring_soldiers = message.get("number")
                    self.current_defending_territory.soldierNumber = num_transferring_soldiers
                    self.current_attacking_territory.soldierNumber -= num_transferring_soldiers
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "attack_results", "attacker_dice": self.dice[0], "defender_dice": self.dice[1], "defender": self.dice[2]})

                if message_type == "selected_attack_option":
                    if self.check_win():
                        packed_territory_info = self.pack_territory_info()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                     "current_player": self.current_player.name, "win": "True"}))
                    else:
                        result_index = message.get("number")
                        if result_index == 1:
                            if self.check_if_can_fortify():
                                packed_territory_info = self.pack_territory_info()
                                print(packed_territory_info)
                                self.broadcast({"type": "edit_board", "territory_info": packed_territory_info,
                                                "current_player": self.current_player.name})
                                time.sleep(0.1)
                                self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "fortify_position"})
                            else:
                                self.end_turn()
                        else:
                            packed_territory_info = self.pack_territory_info()
                            print(packed_territory_info)
                            self.broadcast({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name})
                            time.sleep(0.1)
                            self.send_to_client(self.current_player.connection,
                                                {"type": "turn_message", "turn_type": "select_attacking_territory"})

                if message_type == "selected_if_fortify":
                    result_index = message.get("number")
                    if result_index == 1:
                        if self.current_player.has_conquered:
                            card = self.cards.pop(0)
                            self.current_player.cards[card] = self.current_player.cards[card] + 1
                            print(card)
                        self.switch_player()
                        if self.current_player.isOut:
                            while self.current_player.isOut:
                                self.switch_player()
                    packed_territory_info = self.pack_territory_info()
                    print(packed_territory_info)
                    self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                     "current_player": self.current_player.name}))
                    self.current_player.has_conquered = False
                    self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
                    if result_index == 1:
                        card_series, forced = self.has_card_series()
                        if card_series and self.card_reinforcements != []:
                            self.send_to_client(self.current_player.connection,
                                                {"type": "turn_message", "turn_type": "card_turn_in",
                                                 "number": self.card_reinforcements[0], "forced": forced})
                        else:
                            self.send_to_client(self.current_player.connection,
                                               {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})
                    else:
                        self.fortify = []
                        self.send_to_client(self.current_player.connection,
                                            {"type": "turn_message", "turn_type": "select_fortify_territory"})

                if message_type == "selected_fortify_territory_home":
                    selected_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_fortify_territory_home(selected_territory):
                        self.fortify.append(selected_territory)
                        transfer_options = [str(i) for i in range(1, selected_territory.soldierNumber)]
                        self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_fortify_territory_soldier_number", "transfer_options": transfer_options})

                if message_type == "selected_fortify_soldiers":
                    num_transferring_soldiers = message.get("number")
                    self.fortify.append(num_transferring_soldiers)
                    self.send_to_client(self.current_player.connection,{"type": "turn_message", "turn_type": "select_fortify_territory_new_home"})

                if message_type == "selected_fortify_territory_new_home":
                    selected_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_fortify_territory_new_home(selected_territory, self.fortify[0]):
                        selected_territory.soldierNumber += self.fortify[1]
                        self.fortify[0].soldierNumber -= self.fortify[1]
                        self.end_turn()

                if message_type == "save_game":
                    current_stage = message.get("stage")
                    current_player_name = self.current_player.name
                    save_name = message.get("save_name")
                    packed_territory_info = self.pack_territory_info()
                    packed_player_info = self.package_players()
                    progress = {"players_remaining": self.players_remaining, "territories_remaining": self.territories_remaining, "cards": self.cards, "card_reinforcements": self.card_reinforcements}
                    save_game_progress(self.game_code, save_name, packed_player_info, current_stage, current_player_name, packed_territory_info, progress)
                    self.broadcast({"type": "end_game"})

                if message_type == "get_saves":
                    saves = get_all_game_saves()
                    self.send_to_client(client_socket, {"type": "saves", "saves": saves})

                if message_type == "selected_save":
                    save_code = message.get("save")
                    save_file = get_save_file(save_code)
                    if save_file:
                        player_list = save_file["player_names"]
                        self.repack_players(player_list, client_socket)
                        self.game_code = save_file["game_code"]
                        self.game_stage = save_file["game_stage"]
                        progress = save_file["progress"]
                        self.current_player = self.find_player_by_name(save_file["current_player"])
                        self.players_remaining = progress["players_remaining"]
                        self.territories_remaining = progress["territories_remaining"]
                        self.cards = progress["cards"]
                        self.saved_player_amount = len(self.saved_player_names)
                        self.card_reinforcements = progress["card_reinforcements"]
                        self.saved_game = True
                        self.send_to_client(client_socket, {"type": "player_options", "player_options": self.saved_player_names})

                if message_type == "selected_player":
                    selected_player_name = message.get("save")
                    self.player_names.append(selected_player_name)
                    self.saved_player_names.remove(selected_player_name)
                    selected_player = self.find_player_by_name(selected_player_name)
                    selected_player.connection = client_socket
                    self.broadcast({"type": "player_names", "message": self.player_names, "code": self.game_code, "game_type": "saved", "number": self.saved_player_amount})

                if message_type == "pass_to_select_saved_player":
                    self.send_to_client(client_socket,{"type": "player_options", "player_options": self.saved_player_names})

            except Exception as e:
                import traceback
                traceback.print_exc()
                print(f"Error handling client: {e}")
                break

        # Client disconnected
        print(f"Client {client_socket.getpeername()} disconnected")
        self.connections.remove(client_socket)
        player = self.find_player(client_socket)
        self.player_list.remove(player)
        self.player_names.remove(player.name)
        if self.game_host == client_socket:
            self.game_host = None
            if len(self.connections) > 0:
                self.game_host = self.connections[0]
                self.send_to_client(self.game_host, {"type": "join_message", "message": "You are the host."})
                time.sleep(0.1)
        self.broadcast({"type": "player_names", "message": self.player_names, "code": self.game_code, "game_type": "new", "number": 0})
        client_socket.close()

    def pack_territory_info(self):
        packed_territory_info = {}
        for territory_name, territory in self.board.territories.items():
            color = "grey"
            if territory.owner is not None:
                color = territory.owner.color
            packed_territory_info[territory_name] = [territory.soldierNumber, color]
        return packed_territory_info

    def repack_players(self, players, connection):
        for player_name, player_info in players.items():
            player = Player(player_info["color"], player_name, connection, player_info["soldiers_in_hand"])
            player.cards = player_info["cards"]
            player.has_conquered = player_info["has_conquered"]
            player.isOut = player_info["isOut"]
            player.is_out_initial = player_info["is_out_initial"]
            territories = player_info["territory_names"]
            for territory_info in territories:
                territory = self.find_territory(territory_info)
                territory.owner = player
                player.territories.append(territory)
            self.player_list.append(player)
            self.saved_player_names.append(player.name)

    def create_player_list(self):
        self.player_names = []
        for player in self.player_list:
            self.player_names.append(player.name)

    def package_players(self):
        packed_player_info = {}
        for player in self.player_list:
            if player.isOut is False:
                name = player.name
                territory_names = self.package_owned_territories(player.territories)
                packed_player_info[name] = {"color": player.color, "cards": player.cards, "has_conquered": player.has_conquered, "soldiers_in_hand": player.soldiers_in_hand, "isOut": player.isOut, "territory_names": territory_names, "is_out_initial": player.is_out_initial}
        return packed_player_info

    def package_owned_territories(self, territories):
        territory_names = []
        for territory in territories:
            territory_names.append([territory.lower_name, territory.soldierNumber])
        return territory_names

    def find_player(self, connection):
        for player in self.player_list:
            if player.connection == connection:
                return player

    def find_player_by_name(self, name):
        for player in self.player_list:
            if player.name == name:
                return player

    def find_territory(self, territory_info):
        for territory_name, territory in self.board.territories.items():
            if territory.lower_name == territory_info[0]:
                territory.soldierNumber = territory_info[1]
                return territory

    def broadcast(self, data, exception=None):
        for connection in self.connections:
            if connection == exception:
                continue
            try:
                connection.sendall(pickle.dumps(data))
                print(f"sent to client {connection.getpeername}")
            except Exception as e:
                print(f"Error broadcasting to {connection.getpeername()}: {e}")
                connection.close()
                self.connections.remove(connection)

    def send_to_client(self, client_socket, data):
        try:
            client_socket.sendall(pickle.dumps(data))
        except Exception as e:
            print(f"Error sending data to client: {e}")
            client_socket.close()
            self.connections.remove(client_socket)

    def switch_player(self):
        if self.player_list:
            if self.current_player is None:
                self.current_player = self.player_list[0]
            else:
                current_idx = self.player_list.index(self.current_player)
                if current_idx == len(self.player_list) - 1:
                    self.current_player = self.player_list[0]
                else:
                    self.current_player = self.player_list[current_idx + 1]

    def check_selected_initial_territory(self, territory):
        if territory.owner is None:
            territory.owner = self.current_player
            self.current_player.territories.append(territory)
            territory.soldierNumber += 1
            self.current_player.soldiers_in_hand -= 1
            self.territories_remaining -= 1
            return True
        elif territory.owner == self.current_player:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": f"{self.current_player.name}, you already own {territory.name}. Please select a new territory"})
            return False
        else:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": f"{territory.name} has already been chosen by {territory.owner.name}. Please select a new territory"})
            return False

    def check_selected_initial_soldier_territory(self, territory):
        if territory.owner is self.current_player:
            territory.soldierNumber += 1
            self.current_player.soldiers_in_hand -= 1
            if self.current_player.soldiers_in_hand <= 0:
                self.players_remaining -= 1
                self.current_player.is_out_initial = True
            return True
        else:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": f"{territory.name} is owned by {territory.owner.name}. You can not add soldiers to a territory you don't own"})
            return False

    def check_reinforcement_territory(self, territory):
        if territory.owner is self.current_player:
            territory.soldierNumber += 1
            self.current_player.soldiers_in_hand -= 1
            return True
        else:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": f"{territory.name} is owned by {territory.owner.name}. You cannot add soldiers to a territory you don't own"})
            return False

    def check_attacking_territory(self, territory):
        if territory.owner is self.current_player:
            if territory.soldierNumber > 1:
                if territory.check_neighbors(self.current_player):
                    if territory.soldierNumber == 2:
                        return True, ["1 Soldier"]
                    elif territory.soldierNumber == 3:
                        return True, ["1 Soldier", "2 Soldiers"]
                    else:
                        return True, ["1 Soldier", "2 Soldiers", "3 Soldiers"]
                else:
                    self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "There are no neighboring territories to attack"})
                    return False, 0
            else:
                self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "You cannot attack with a territory that has less than 2 soldiers"})
                return False, 0
        else:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "You must select one of your own territories to attack with"})
            return False, 0

    def check_defending_territory(self, territory):
        if territory in self.current_attacking_territory.neighbors:
            if territory.owner is not self.current_player:
                return True
            else:
                self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "You can't attack your own territory"})
                return False
        else:
            self.send_to_client(self.current_player.connection,
                                {"type": "reselect_territory", "message": "You must attack a neighboring territory"})
            return False

    def check_selected_fortify_territory_home(self, territory):
        if territory.owner is self.current_player:
            if territory.check_neighbors_for_player(self.current_player):
                if territory.soldierNumber > 1:
                    return True
                else:
                    self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "You need a territory with more than 1 soldier"})
                    return False
            else:
                self.send_to_client(self.current_player.connection,{"type": "reselect_territory", "message": "You have no territories as a neighbor"})
                return False
        else:
            self.send_to_client(self.current_player.connection, {"type": "reselect_territory", "message": "You must fortify your own territory"})
            return False

    def check_selected_fortify_territory_new_home(self, territory_new_home, territory_home):
        if territory_new_home.owner is self.current_player:
            new_home_options = self.current_player.create_neighbor_web(territory_home)
            if territory_new_home in new_home_options:
                return True
            else:
                self.send_to_client(self.current_player.connection,{"type": "reselect_territory", "message": "You must choose a connecting territory"})
                return False
        else:
            self.send_to_client(self.current_player.connection,{"type": "reselect_territory", "message": "You must fortify your own territory"})
            return False

    def attack(self, attacking_territory, defending_territory):
        print(f"New Battle: {self.current_player} is attacking {defending_territory.name} with {attacking_territory.name}")
        attacker_dice = [random.randint(1, 6) for _ in
                         range(min(attacking_territory.soldierNumber - 1, self.current_attack_number))]
        defending_number = 2
        if defending_territory.soldierNumber == 1:
            defending_number = 1
        defender_dice = [random.randint(1, 6) for _ in range(min(defending_territory.soldierNumber, defending_number))]

        # Sort the dice rolls
        attacker_dice.sort(reverse=True)
        defender_dice.sort(reverse=True)

        print(f"{self.current_player.name} rolled: {attacker_dice}")
        print(f"{defending_territory.owner.name} rolled: {defender_dice}")
        attacker_losses, defender_losses = self.combat_losses(attacker_dice, defender_dice)
        attacking_territory.soldierNumber -= attacker_losses
        defending_territory.soldierNumber -= defender_losses

        print(defending_territory.soldierNumber)

        if defending_territory.soldierNumber < 1:
            flag = False
            defending_territory.owner.territories.remove(defending_territory)
            attacking_territory.owner.territories.append(defending_territory)
            if len(defending_territory.owner.territories) < 1:
                flag = defending_territory.owner
                defending_territory.owner.isOut = True
            transfer_options = [str(i) for i in range(1, attacking_territory.soldierNumber)]
            self.dice = [attacker_dice, defender_dice, defending_territory.owner.name]
            defending_territory.owner = attacking_territory.owner
            self.current_player.has_conquered = True
            if flag:
                packed_territory_info = self.pack_territory_info()
                self.send_to_client(flag.connection, {"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name, "out": "True"})
            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_transfer_soldiers", "transfer_options": transfer_options})
        else:
            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "attack_results", "attacker_dice": attacker_dice, "defender_dice": defender_dice, "attacker": attacking_territory.owner.name, "defender": defending_territory.owner.name})

    def combat_losses(self, attacker_dice, defender_dice):
        attacker_losses, defender_losses = 0, 0
        couples = [[attacker_dice[0], defender_dice[0]]]
        if len(attacker_dice) > 1 and len(defender_dice) > 1:
            couples.append([attacker_dice[1], defender_dice[1]])
        for couple in couples:
            if couple[0] > couple[1]:
                defender_losses += 1
            else:
                attacker_losses += 1
        print(f"attacker losses: {attacker_losses}, defender losses: {defender_losses}")
        return attacker_losses, defender_losses

    # def end_combat_early(self):
    #     packed_territory_info = self.pack_territory_info()
    #     self.switch_player()
    #     if self.current_player.isOut:
    #         while self.current_player.isOut:
    #             self.switch_player()
    #     self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
    #                      "current_player": self.current_player.name}))
    #     time.sleep(0.1)
    #     self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
    #     self.send_to_client(self.current_player.connection,
    #                         {"type": "turn_message", "turn_type": "receiving_reinforcements",
    #                          "number": self.current_player.soldiers_in_hand, "first_time": "True"})

    def end_turn(self):
        if self.current_player.has_conquered:
            card = self.cards.pop(0)
            self.current_player.cards[card] = self.current_player.cards[card] + 1
            print(card)
        self.switch_player()
        if self.current_player.isOut:
            while self.current_player.isOut:
                self.switch_player()
        packed_territory_info = self.pack_territory_info()
        print(packed_territory_info)
        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                      "current_player": self.current_player.name}))
        time.sleep(0.1)
        self.current_player.has_conquered = False
        self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
        card_series, forced = self.has_card_series()
        if card_series and self.card_reinforcements != []:
            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "card_turn_in",
                                                                 "number": self.card_reinforcements[0],
                                                                 "forced": forced})
        else:
            self.send_to_client(self.current_player.connection,
                             {"type": "turn_message", "turn_type": "receiving_reinforcements",
                                 "number": self.current_player.soldiers_in_hand, "first_time": "True"})

    def check_win(self):
        count = 0
        for player in self.player_list:
            if not player.isOut:
                count += 1
        if count == 1:
            return True
        return False

    def check_if_can_fortify(self):
        flag = False
        for territory in self.current_player.territories:
            if territory.soldierNumber > 1 and territory.check_neighbors_for_player(self.current_player):
                flag = True
        return flag

    def has_card_series(self):
        infantry = self.current_player.cards["infantry"]
        cavalry = self.current_player.cards["cavalry"]
        artillery = self.current_player.cards["artillery"]
        print(f"{self.current_player.name}:  infantry: {infantry},   cavalry: {cavalry},   artillery: {artillery}")
        card_total = infantry + cavalry + artillery
        if card_total == 5:
            return True, 1
        if infantry >= 1 and cavalry >= 1 and artillery >= 1:
            return True, 0
        if infantry >= 3 or cavalry >= 3 or artillery >= 3:
            return True, 0
        return False, 0

    def remove_cards(self):
        infantry = self.current_player.cards["infantry"]
        cavalry = self.current_player.cards["cavalry"]
        artillery = self.current_player.cards["artillery"]
        if infantry >= 3:
            self.current_player.cards["infantry"] -= 3
        elif cavalry >= 3:
            self.current_player.cards["cavalry"] -= 3
        elif artillery >= 3:
            self.current_player.cards["artillery"] -= 3
        else:
            self.current_player.cards["infantry"] -= 1
            self.current_player.cards["cavalry"] -= 1
            self.current_player.cards["artillery"] -= 1


def initialize_database():
    conn = sqlite3.connect('game_progress.db')
    cursor = conn.cursor()

    # Create table if it doesn't exist
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS game_progress (
        game_code TEXT PRIMARY KEY,
        save_name TEXT,
        player_names TEXT,
        game_stage TEXT,
        current_player TEXT,
        territories TEXT
        progress TEXT
    )
    ''')

    # Check if save_name column exists, if not, add it
    cursor.execute("PRAGMA table_info(game_progress);")
    columns = [column[1] for column in cursor.fetchall()]
    if 'save_name' not in columns:
        cursor.execute("ALTER TABLE game_progress ADD COLUMN save_name TEXT;")
    if 'progress' not in columns:
        cursor.execute("ALTER TABLE game_progress ADD COLUMN progress TEXT;")

    conn.commit()
    conn.close()


def save_game_progress(game_code, save_name, player_names, game_stage, current_player, territories, progress):
    conn = sqlite3.connect('game_progress.db')
    cursor = conn.cursor()
    player_names_str = json.dumps(player_names)
    territories_str = json.dumps(territories)
    game_stage_str = json.dumps(game_stage)
    progress_str = json.dumps(progress)

    cursor.execute('''
    INSERT INTO game_progress (game_code, save_name, player_names, game_stage, current_player, territories, progress)
    VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (game_code, save_name, player_names_str, game_stage_str, current_player, territories_str, progress_str))
    conn.commit()
    conn.close()
    print(f"Game progress saved locally with game code: {game_code}")


def get_all_game_saves():
    conn = sqlite3.connect('game_progress.db')
    cursor = conn.cursor()
    cursor.execute('SELECT game_code, save_name FROM game_progress')
    saves = cursor.fetchall()
    conn.close()
    return saves


def get_save_file(save_code):
    # Connect to the SQLite database
    conn = sqlite3.connect('game_progress.db')
    cursor = conn.cursor()

    # Query the database for the game save with the specified save code
    cursor.execute(
        'SELECT save_name, player_names, game_stage, current_player, territories, progress FROM game_progress WHERE game_code = ?',
        (save_code,))
    save = cursor.fetchone()

    if save:
        save_name, player_names_str, game_stage_str, current_player, territories_str, progress_str = save
        # Convert JSON strings back to Python lists
        player_names = json.loads(player_names_str)
        territories = json.loads(territories_str)
        game_stage = json.loads(game_stage_str)
        progress = json.loads(progress_str)

        # Delete the save from the database

        #temporary commented!!!!!!
        cursor.execute('DELETE FROM game_progress WHERE game_code = ?', (save_code,))
        conn.commit()

        # Close the database connection
        conn.close()

        return {
            'game_code': save_code,
            'save_name': save_name,
            'player_names': player_names,
            'game_stage': game_stage,
            'current_player': current_player,
            'territories': territories,
            'progress': progress
        }
    else:
        conn.close()
        print(f"No save found with game code: {save_code}")
        return None


def generate_unique_game_code():
    conn = sqlite3.connect('game_progress.db')
    cursor = conn.cursor()
    while True:
        game_code = ''.join(random.choices('0123456789', k=5))
        cursor.execute('SELECT game_code FROM game_progress WHERE game_code = ?', (game_code,))
        if cursor.fetchone() is None:
            conn.commit()
            conn.close()
            return game_code


if __name__ == "__main__":
    HOST = "192.168.86.250"  # Change this to your server's IP address
    PORT = 8080  # Choose a suitable port
    server = RiskServer(HOST, PORT)
    server.start()
