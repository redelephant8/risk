import socket
import pickle
import pygame
from pygame.locals import *
import threading
from board import Board

width, height = 800, 600
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
        self.player_color = None
        self.client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.game_state = "lobby"
        self.game_stage = "start"
        self.player_list = []
        self.prev_player_list = []
        self.prev_game_state = "None"
        self.is_host = False  # Variable to track whether the player is the host
        self.board = Board()
        self.territory_information = {}
        self.current_player = None
        self.my_turn = False
        self.territory_selected = False
        self.player_message = None

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
            if self.game_state == "lobby" and self.prev_player_list is not self.player_list:
                self.host_wait_screen(screen)
                self.prev_player_list = self.player_list

            if self.prev_game_state != self.game_state:
                # if self.game_state == "initial_territories":
                #     self.edit_screen(screen)
                #     self.prev_game_state = self.game_state

                # if self.my_turn and self.game_state == "initial_territories":
                #     self.edit_screen(screen, f"{self.player_name}, please select a territory")
                #     selected_territory = self.select_territory()
                #     print(selected_territory)
                #     message = {"type": "selected_initial_territory", "territory": selected_territory.lower_name}
                #     self.client_socket.sendall(pickle.dumps(message))

                if self.my_turn and self.game_state == "select_territory":
                    self.edit_screen(screen, self.player_message)
                    selected_territory = self.select_territory()
                    print(selected_territory)

                    # Remember THIS NAME CHANGE!!!
                    if self.game_stage == "initial_territories":
                        message = {"type": "selected_initial_territory", "territory": selected_territory.lower_name}
                        self.client_socket.sendall(pickle.dumps(message))
                    self.prev_game_state = self.game_state

                if self.game_state == "print_board":
                    self.edit_screen(screen)
                    self.prev_game_state = self.game_state
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

                if message_type == "join_message":
                    if message.get("message") == "You are the host.":
                        self.is_host = True  # Set the player as the host
                        print("IJIOJDSOIFJSD, it worked")

                if message_type == "player_names":
                    print("hihihihih")
                    self.player_list = message.get("message")
                    # self.player_color = message.get("color")
                    print(message)
                    print(self.player_list)

                if message_type == "player_color":
                    self.player_color = message.get("color")

                if message_type == "start_game":
                    print("We have officially began the risk game.")
                    self.territory_information = message.get("territory_info")
                    print(message.get("territory_info"))
                    self.update_local_board()
                    self.game_state = "print_board"


                if message_type == "reselect_territory":
                    print("I need to reselect my territory")
                    self.prev_game_state = "None"
                    self.game_state = "select_territory"
                    self.player_message = message.get("message")

                if message_type == "edit_board":
                    self.territory_information = message.get("territory_info")
                    self.update_local_board()
                    self.game_state = "print_board"

                if message_type == "turn_message":
                    print("It is my turn")
                    if message.get("turn_type") == "initial_territory_selection":
                        self.player_message = f"{self.player_name}, please select a territory"
                        self.game_state = "select_territory"
                        self.game_stage = "initial_territories"
                    self.my_turn = True
        except Exception as e:
            print(f"Error in client: {e}")

    def select_territory(self):
        selection_valid = False
        selected_territory = None
        while not selection_valid:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for territory_name, territory in self.board.territories.items():
                        if territory.click(mouse_pos):
                            selected_territory = territory
                            selection_valid = True
                            # edit_screen()
                        button_rect = pygame.Rect(600, 500, 150, 50)
                        if button_rect.collidepoint(mouse_pos) and self.combat_stage_flag is True:
                            selected_territory = None
                            selection_valid = True
                            print("BENSAVIRISBEHINDME")
                            # edit_screen()
                            self.combat_stage_flag = False
        return selected_territory
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

    def update_local_board(self):
        # for territory_name, territory in self.board.territories.items
        for territory_name, territory_info in self.territory_information.items():
            self.board.territories[territory_name].soldierNumber = territory_info[0]

            #THIS ALSO NEEDS TO BE FIXED
            self.board.territories[territory_name].owner = territory_name

    def edit_screen(self, screen, message=None):
        # Clear the screen
        screen.fill((255, 255, 255))  # Fill with white background

        # Draw the territories
        for territory_name, territory in self.board.territories.items():
            territory.draw(screen, (self.territory_information[territory_name])[1])
            territory.draw_lines_to_neighbors(screen)

        # game.board.territories["qatar"].draw(screen)
        # game.board.territories["qatar"].draw_lines_to_neighbors(screen)
        #
        # game.board.territories["afghanistan"].draw(screen)
        # game.board.territories["afghanistan"].draw_lines_to_neighbors(screen)
        #
        # game.board.territories["saudi_arabia"].draw(screen)
        # game.board.territories["saudi_arabia"].draw_lines_to_neighbors(screen)
        #
        # game.board.territories["iran"].draw(screen)
        # game.board.territories["iran"].draw_lines_to_neighbors(screen)
        #
        # game.board.territories["egypt"].draw(screen)
        # game.board.territories["egypt"].draw_lines_to_neighbors(screen)

        # Draw the button
        button_rect = pygame.Rect(600, 500, 150, 50)  # Button position and size
        pygame.draw.rect(screen, (0, 0, 255), button_rect)  # Draw the button

        # Add text to the button
        font = pygame.font.SysFont(None, 30)
        text = font.render("End Combat", True, (255, 255, 255))
        text_rect = text.get_rect(center=button_rect.center)
        screen.blit(text, text_rect)

        if message:
            text_surface = font.render(message, True, (0, 0, 0))
            screen.blit(text_surface, (width // 2 - text_surface.get_width() // 2, 20))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(30)


if __name__ == "__main__":
    HOST = "192.168.86.148"  # Change this to your server's IP address
    PORT = 8080  # Choose the same port as the server
    # player_name = input("Enter your player name: ")
    client = RiskClient(HOST, PORT)
    client.start()
