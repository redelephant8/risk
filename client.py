# client.py

import socket
import pickle
import pygame
import main


class RiskClient:
    def __init__(self, host, port, player_name):
        self.host = host
        self.port = port
        self.player_name = player_name
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_state = {}  # Store game state

    def start(self):
        game_state = 0
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Risk")
        game = main.Game()

        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

        while True:
            try:
                # Receive game state updates from server
                data = self.client_socket.recv(1024)
                if not data:
                    break

                # Process received game state
                self.game_state = pickle.loads(data)
                self.update_screen()

                # Check if it's this player's turn
                if self.game_state.get("current_player") == self.player_name:
                    self.select_territory()

            except Exception as e:
                print(f"Error in client: {e}")
                break

        self.client_socket.close()

    def update_screen(self):
        # Implement code to update the screen based on game state
        pass

    def select_territory(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for territory_name, territory in self.game_state["board"]["territories"].items():
                        if territory["rect"].collidepoint(mouse_pos):
                            # Send selected territory to server
                            message = {"type": "territory_selection", "player": self.player_name, "territory": territory_name}
                            self.client_socket.sendall(pickle.dumps(message))
                            return

if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose the same port as the server
    player_name = input("Enter your player name: ")
    client = RiskClient(HOST, PORT, player_name)
    client.start()
