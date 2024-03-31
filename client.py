# server.py

import socket
import threading
import pickle

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
        self.game_host = None

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()

        print(f"Server is listening on {self.host}:{self.port}")

        while True:
            client_socket, client_address = self.server_socket.accept()
            self.connections.append(client_socket)
            print(f"New connection from {client_socket.getpeername()}")

            if not self.game_host:
                self.game_host = client_address
                print(f"{client_address} is the host of the game.")

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

            except Exception as e:
                print(f"Error handling client: {e}")
                break

        # Client disconnected
        print(f"Client {client_socket.getpeername()} disconnected")
        self.connections.remove(client_socket)
        client_socket.close()

    def handle_territory_selection(self, message):
        player = message["player"]
        territory = message["territory"]
        if self.game_state["current_player"] == player:
            # Update game state
            self.game_state["board"]["territories"][territory]["owner"] = player
            # Example: Increment player's territories count
            self.game_state[player]["territories_count"] += 1

            # Inform next player it's their turn
            self.next_player_turn()

            # Broadcast updated game state to all clients
            self.broadcast(self.game_state)

    def next_player_turn(self):
        # Determine next player and update game state
        # For example:
        current_player_index = self.game_state["players"].index(self.game_state["current_player"])
        next_player_index = (current_player_index + 1) % len(self.game_state["players"])
        self.game_state["current_player"] = self.game_state["players"][next_player_index]

    def broadcast(self, data):
        for connection in self.connections:
            try:
                connection.sendall(pickle.dumps(data))
            except Exception as e:
                print(f"Error broadcasting to {connection.getpeername()}: {e}")
                connection.close()
                self.connections.remove(connection)


if __name__ == "__main__":
    HOST = "10.116.3.115"  # Change this to your server's IP address
    PORT = 8080  # Choose a suitable port
    server = RiskServer(HOST, PORT)
    server.start()
