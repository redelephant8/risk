import socket
import threading
import pickle
import time
from board import Board
from player import Player

colors = ['red', 'blue', 'yellow', 'green', 'purple', 'pink']
class RiskServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connections = []  # Store client connections
        self.game_state = {
            "board": {
                "territories": {
                    # Initialize territories here
                }
            },
            "current_player": None
        }
        self.board = Board()
        self.player_list = []
        self.player_names = []
        self.game_host = None
        self.current_player = None
        self.player_number = 0
        self.players_remaining = 0
        self.territories_remaining = len(self.board.territories)

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            #HERE ADD TO BLOCK MORE THAN 6 CLIENTS JOINING
            self.connections.append(client_socket)
            print(f"New connection from {client_socket.getpeername()}")

            if not self.game_host:
                self.game_host = client_address
                print(f"{client_address} is the host of the game.")
                # Sending message to the host
                self.send_to_client(client_socket, {"type": "join_message", "message": "You are the host."})


                # Pretty sure this has to be out of this if statement, we'll check soon
                # Start a new thread to handle client communication
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
                        self.switch_player()
                        if self.players_remaining > 0 and self.current_player.isOut is True:
                            while self.current_player.isOut is True:
                                self.switch_player()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        if self.players_remaining > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "initial_soldier_addition"})
                        else:
                            self.current_player = self.player_list[0]
                            self.current_player.soldiers_in_hand = self.current_player.reinforcement_calculator
                            self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info,
                                             "current_player": self.current_player.name}))
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": True})

                if message_type == "receiving_reinforcements":
                    time.sleep(0.1)
                    selected_territory = self.board.territories[message.get("territory")]
                    if self.check_reinforcement_territory(selected_territory):
                        packed_territory_info = self.pack_territory_info()
                        self.broadcast(({"type": "edit_board", "territory_info": packed_territory_info, "current_player": self.current_player.name}))
                        if self.current_player.soldiers_in_hand > 0:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "receiving_reinforcements", "number": self.current_player.soldiers_in_hand, "first_time": False})
                        else:
                            self.send_to_client(self.current_player.connection, {"type": "turn_message", "turn_type": "combat_phase"})
            except Exception as e:
                print(f"Error handling client: {e}")
                break

        # Client disconnected
        print(f"Client {client_socket.getpeername()} disconnected")
        self.connections.remove(client_socket)
        client_socket.close()

    def pack_territory_info(self):
        packed_territory_info = {}
        for territory_name, territory in self.board.territories.items():
            color = "grey"
            if territory.owner is not None:
                color = territory.owner.color
            packed_territory_info[territory_name] = [territory.soldierNumber, color]
        return packed_territory_info
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
            # self.broadcast({"type": "current_player", "current_player_name": self.current_player.name}, self.current_player.connection)
            # time.sleep(0.1)

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

if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose a suitable port
    server = RiskServer(HOST, PORT)
    server.start()
