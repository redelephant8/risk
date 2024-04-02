import socket
import pickle
import pygame
from pygame.locals import *
import threading

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)

class RiskClient:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.player_name = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_state = {}  # Store game state
        self.player_list = []
        self.prev_player_list = []
        self.is_host = False  # Variable to track whether the player is the host

    def start(self):
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Risk")
        clock = pygame.time.Clock()  # Create a clock object for controlling FPS

        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

        self.get_player_name(screen)

        # Start a separate thread for receiving data from the server
        receive_thread = threading.Thread(target=self.receive_data)
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            for event in pygame.event.get():  # Event handling loop
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_host and len(self.player_list) >= 2:
                        # Check if the mouse click is within the "Start Game" button
                        start_button_rect = pygame.Rect(250, 100 + len(self.player_list) * 40, 200, 50)
                        if start_button_rect.collidepoint(event.pos):
                            self.start_game()

            # Render the lobby screen
            if self.prev_player_list is not self.player_list:
                self.host_wait_screen(screen)
                self.prev_player_list = self.player_list

            pygame.display.flip()  # Update the display

            clock.tick(30)  # Limit frame rate to 30 FPS

    def receive_data(self):
        try:
            while True:
                # Receive messages from the server
                data = self.client_socket.recv(1024)
                print("I received new data!!!!")
                if not data:
                    break

                # Process received message
                message = pickle.loads(data)
                message_type = message.get("type")
                print(f"Message type: {message_type}")

                if message_type == "message":
                    print(message["message"])  # Print host message
                    if message.get("message") == "You are the host.":
                        self.is_host = True  # Set the player as the host
                        print("IJIOJDSOIFJSD, it worked")

                if message_type == "player_list":
                    print("hihihihih")
                    self.player_list = message.get("message")
                    print(message)
                    print(self.player_list)

                if message_type == "start_game":
                    print("We have officially began the risk game.")

        except Exception as e:
            print(f"Error in client: {e}")

    def get_player_name(self, screen):
        pygame.font.init()  # Initialize Pygame font system
        input_box = pygame.Rect(300, 300, 200, 40)
        submit_button = pygame.Rect(350, 350, 100, 40)  # Submit button rectangle
        color_inactive = pygame.Color('lightskyblue3')
        color_active = pygame.Color('dodgerblue2')
        color_submit = pygame.Color('green')  # Button color
        color = color_inactive
        active = False
        text = ''
        font = pygame.font.Font(None, 32)

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == MOUSEBUTTONDOWN:
                    # If the user clicked on the input_box rect.
                    if input_box.collidepoint(event.pos):
                        # Toggle the active variable.
                        active = not active
                    else:
                        active = False
                    # If the user clicked on the submit button
                    if submit_button.collidepoint(event.pos):
                        # Send the entered name to the server
                        self.player_name = text
                        message = {"type": "name_selection", "name": self.player_name}
                        self.client_socket.sendall(pickle.dumps(message))
                        return
                    # Change the current color of the input box.
                    color = color_active if active else color_inactive
                if event.type == KEYDOWN:
                    if active:
                        if event.key == K_RETURN:
                            # Send the entered name to the server
                            self.player_name = text
                            self.client_socket.sendall(self.player_name.encode())
                            return
                        elif event.key == K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            screen.fill((255, 255, 255))  # White background
            # Render the welcome message.
            draw_text("Welcome!", font, (0, 0, 0), screen, 300, 250)
            # Render the current text.
            txt_surface = font.render(text, True, color)
            # Resize the box if the text is too long.
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            # Blit the text.
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            # Blit the input_box rect.
            pygame.draw.rect(screen, color, input_box, 2)

            # Render the submit button
            pygame.draw.rect(screen, color_submit, submit_button)
            draw_text("Submit", font, (255, 255, 255), screen, 370, 360)

            pygame.display.flip()

    def host_wait_screen(self, screen):
        font = pygame.font.Font(None, 36)  # Font for rendering text
        print("flipflopflipflop")

        screen.fill((255, 255, 255))  # Fill the screen with white color

        # Display title
        draw_text("Players in the Lobby:", font, (0, 0, 0), screen, 300, 50)

        # Display player names
        for i, player_name in enumerate(self.player_list):
            draw_text(player_name, font, (0, 0, 0), screen, 300, 100 + i * 40)

        # Check if the client is the host and there are at least three clients including the host
        if self.is_host and len(self.player_list) >= 2:
            # Display "Start Game" button
            start_button = pygame.Rect(250, 100 + len(self.player_list) * 40, 200, 50)
            pygame.draw.rect(screen, (0, 255, 0), start_button)
            draw_text("Start Game", font, (0, 0, 0), screen, start_button.x + 50, start_button.y + 15)

    def start_game(self):
        # Send a message to the server indicating that the game should start
        message = {"type": "start_game"}
        self.client_socket.sendall(pickle.dumps(message))
        print("Start game message sent to server")

if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose the same port as the server
    # player_name = input("Enter your player name: ")
    client = RiskClient(HOST, PORT)
    client.start()
