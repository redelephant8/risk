import socket
import threading
import pickle
import time
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
        self.board = Board()
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
        self.cards = ["infantry"]*14 + ["cavalry"]*14 + ["artillery"]*14

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        random.shuffle(self.cards)

        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            #HERE ADD TO BLOCK MORE THAN 6 CLIENTS JOINING
            self.connections.append(client_socket)
            print(f"New connection from {client_socket.getpeername()}")

            if not self.game_host:
                self.game_host = client_socket
                print(f"{client_socket} is the host of the game.")
                # Sending message to the host
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

                # if message_type == "territory_selection":
                #     self.handle_territory_selection(message)

                if message_type == "name_selection":
                    print(f"Connected player name: {message.get('name')}")
                    self.player_names.append(message.get('name'))
                    player_color = colors[0]
                    self.player_list.append(Player(player_color, message.get('name'), client_socket))

                    # self.player_list[message.get('name')] = Player(colors[0], message.get('name'), client_socket)
                    colors.pop(0)
                    print(self.player_list)
                    time.sleep(0.1)
                    self.broadcast({"type": "player_names", "message": self.player_names})
                    self.send_to_client(client_socket, {"type": "player_color", "color": player_color})

                if message_type == "start_game":
                    print("Host started game")
                    time.sleep(0.1)
                    print(self.board)
                    packed_territory_info = self.pack_territory_info()
                    self.player_number = len(self.player_list)
                    self.switch_player()
                    self.broadcast(({"type": "start_game", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                    time.sleep(0.1)
                    # current_player_index = self.player_list.index(self.current_player)
                    # current_player_connection = self.connections[current_player_index]
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_territory_selection"})

                if message_type == "selected_initial_territory":
                    time.sleep(0.1)
                    selected_initial_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_initial_territory(selected_initial_territory):
                        packed_territory_info = self.pack_territory_info()
                        print(packed_territory_info)
                        self.switch_player()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                        if self.territories_remaining > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_territory_selection"})
                        else:
                            self.current_player = self.player_list[0]
                            self.players_remaining = self.player_number
                            self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_soldier_addition"})

                if message_type == "selected_initial_soldier_territory":
                    selected_initial_soldier_territory = self.board.territories[message.get("territory")]
                    if self.check_selected_initial_soldier_territory(selected_initial_soldier_territory):
                        packed_territory_info = self.pack_territory_info()
                        print(packed_territory_info)
                        print(self.players_remaining)
                        self.switch_player()
                        if self.players_remaining > 0 and self.current_player.isOut is True:
                            while self.current_player.isOut is True:
                                self.switch_player()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        time.sleep(0.1)
                        if self.players_remaining > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_soldier_addition"})
                        else:
                            for player in self.player_list:
                                player.isOut = False
                            self.current_player = self.player_list[0]
                            self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
                            self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                            time.sleep(0.1)
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})

                if message_type == "selected_reinforcement_territory":
                    time.sleep(0.1)
                    selected_territory = self.board.territories[message.get("territory")]
                    if self.check_reinforcement_territory(selected_territory):
                        packed_territory_info = self.pack_territory_info()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        if self.current_player.soldiers_in_hand > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "False"})
                        else:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_attacking_territory"})

                if message_type == "selected_attacking_territory":
                    time.sleep(0.1)
                    if message.get("territory") == "end_combat":
                        self.end_combat_early()
                    else:
                        selected_territory = self.board.territories[message.get("territory")]
                        check_selected, number = self.check_attacking_territory(selected_territory)
                        if check_selected:
                            self.current_attacking_territory = selected_territory
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_attacking_soldiers", "number": number})

                if message_type == "selected_attacking_soldiers":
                    time.sleep(0.1)
                    self.current_attack_number = message.get("number")
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_defending_territory"})

                if message_type == "selected_defending_territory":
                    time.sleep(0.1)
                    if message.get("territory") == "end_combat":
                        self.end_combat_early()
                    else:
                        selected_territory = self.board.territories[message.get("territory")]
                        if self.check_defending_territory(selected_territory):
                            self.current_defending_territory = selected_territory
                            self.attack(self.current_attacking_territory, selected_territory)

                if message_type == "selected_transferring_soldiers":
                    time.sleep(0.1)
                    num_transferring_soldiers = message.get("number")
                    self.current_defending_territory.soldierNumber = num_transferring_soldiers
                    self.current_attacking_territory.soldierNumber -= num_transferring_soldiers
                    self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "attack_results", "attacker_dice": self.dice[0], "defender_dice": self.dice[1], "defender": self.dice[2]})

                if message_type == "selected_attack_option":
                    time.sleep(0.1)
                    if self.check_win():
                        packed_territory_info = self.pack_territory_info()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                     "current_player": self.current_player.name, "win": "True"}))
                    else:
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
                        time.sleep(0.1)
                        self.current_player.has_conquered = False
                        self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
                        if result_index == 1:
                            self.send_to_client(self.current_player.connection,
                                                {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": "True"})
                        else:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "select_attacking_territory"})

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
                self.broadcast({"type": "player_names", "message": self.player_names})
        client_socket.close()

    def pack_territory_info(self):
        packed_territory_info = {}
        for territory_name, territory in self.board.territories.items():
            color = "grey"
            if territory.owner is not None:
                color = territory.owner.color
            packed_territory_info[territory_name] = [territory.soldierNumber, color]
        return packed_territory_info

    def find_player(self, connection):
        for player in self.player_list:
            if player.connection == connection:
                return player

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
                self.current_player.isOut = True
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
            defending_territory.owner = attacking_territory.owner
            transfer_options = [str(i) for i in range(1, attacking_territory.soldierNumber)]
            self.dice = [attacker_dice, defender_dice, defending_territory.owner.name]
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

    def end_combat_early(self):
        packed_territory_info = self.pack_territory_info()
        self.switch_player()
        if self.current_player.isOut:
            while self.current_player.isOut:
                self.switch_player()
        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                         "current_player": self.current_player.name}))
        time.sleep(0.1)
        self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator()
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


if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose a suitable port
    server = RiskServer(HOST, PORT)
    server.start()
