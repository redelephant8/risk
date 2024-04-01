import socket
import pickle
import pygame
from pygame.locals import *

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
        self.is_host = False  # Variable to track whether the player is the host

    def start(self):
        width, height = 800, 600
        screen = pygame.display.set_mode((width, height))
        pygame.display.set_caption("Risk")
        clock = pygame.time.Clock()  # Create a clock object for controlling FPS

        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

        self.get_player_name(screen)

        while True:
            for event in pygame.event.get():  # Event handling loop
                if event.type == pygame.QUIT:
                    return

            try:
                # Receive messages from the server
                data = self.client_socket.recv(1024)
                if not data:
                    break

                # Process received message
                message = pickle.loads(data)
                if "message" in message:
                    print(message["message"])  # Print host message
                    if message["message"] == "You are the host.":
                        self.is_host = True  # Set the player as the host
                        # self.host_wait_screen(screen, 1)

            except Exception as e:
                print(f"Error in client: {e}")
                break

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


if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose the same port as the server
    # player_name = input("Enter your player name: ")
    client = RiskClient(HOST, PORT)
    client.start()
    
