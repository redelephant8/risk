import socket
import threading
import pickle
import time
from board import Board

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
        self.game_host = None

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
                self.send_to_client(client_socket, {"type": "message", "message": "You are the host."})


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

                if message_type == "territory_selection":
                    self.handle_territory_selection(message)

                if message_type == "name_selection":
                    print(f"Connected player name: {message.get('name')}")
                    self.player_list.append(message.get('name'))
                    print(self.player_list)
                    time.sleep(0.1)
                    self.broadcast({"type": "player_list", "message": self.player_list})

                if message_type == "start_game":
                    print("Host started game")
                    time.sleep(0.1)
                    print(self.board)
                    packed_territory_info = self.pack_territory_info()
                    self.broadcast(({"type": "start_game", "territory_info": packed_territory_info}))

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
            packed_territory_info[territory_name] = [territory.owner, territory.soldierNumber]
        return packed_territory_info
    def broadcast(self, data):
        for connection in self.connections:
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

if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose a suitable port
    server = RiskServer(HOST, PORT)
    server.start()
