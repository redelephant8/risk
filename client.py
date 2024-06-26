import socket
import pickle
import sys

import pygame
from pygame.locals import *
import threading
from board import Board

def draw_text(text, font, color, surface, x, y):
    text_obj = font.render(text, True, color)
    text_rect = text_obj.get_rect()
    text_rect.topleft = (x, y)
    surface.blit(text_obj, text_rect)


width, height = 1000, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Risk")
clock = pygame.time.Clock()

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
        self.board = None
        self.demo = False
        self.territory_information = {}
        self.current_player = None
        self.prev_player = None
        self.territory_selected = False
        self.player_message = None
        self.edited = False
        self.number = []
        self.attacker_dice = None
        self.defender_dice = None
        self.game_code = None
        self.code_result = False
        self.saved_game = False
        self.save_game_count = 0
        self.saves = None
        self.player_options = None
        self.game_ended = False
        self.saved_game_state = None
        self.can_attack = True
        self.spectator = False

    def start(self):
        self.client_socket.connect((self.host, self.port))
        print(f"Connected to server {self.host}:{self.port}")

        data = self.client_socket.recv(1024)
        message = pickle.loads(data)
        connection_num = message.get("connections")
        if connection_num <= 2:
            if message.get("saved_game") is True:
                self.saved_game = True

            if connection_num == 1:
                self.game_options(screen, False)
            else:
                self.game_options(screen, True)
                while self.code_result == False:
                    data = self.client_socket.recv(1024)
                    self.code_result = pickle.loads(data)
                    if self.code_result is False:
                        self.get_player_input(screen, "code", True)
                if self.saved_game:
                    self.client_socket.sendall(pickle.dumps({"type": "pass_to_select_saved_player"}))
                else:
                    self.get_player_input(screen, "name", False)
        else:
            self.spectator = True
            if message.get("demo"):
                self.demo = message.get("demo")
                self.create_board(self.demo)
        # Start a separate thread for receiving data from the server
        receive_thread = threading.Thread(target=self.receive_data, args=(screen,))
        receive_thread.daemon = True
        receive_thread.start()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.is_host:
                        if (self.saved_game and len(self.player_list) == self.save_game_count) or (self.saved_game is False and len(self.player_list) >= 2):
                            # Check if the mouse click is within the "Start Game" button
                            start_button_rect = pygame.Rect(250, 150 + len(self.player_list) * 40, 200, 50)
                            if start_button_rect.collidepoint(event.pos):
                                if self.saved_game:
                                    self.start_saved_game()
                                else:
                                    self.start_game()

            # Render the lobby screen
            if self.game_state == "lobby" and self.prev_player_list is not self.player_list:
                if self.spectator is False:
                    self.host_wait_screen(screen)
                    self.prev_player_list = self.player_list
                else:
                    self.spectator_wait_screen(screen)

            if (self.edited is False and self.game_ended is False) or (self.game_ended and self.game_state == "end_game"):
                self.edited = True
                if self.game_state == "select_territory":
                    self.edit_screen(screen, self.player_message)
                    selected_territory = self.select_territory()
                    territory_name = "end_combat"
                    message = ""
                    if selected_territory:
                        territory_name = selected_territory.lower_name

                    if self.game_stage == "initial_territories":
                        message = {"type": "selected_initial_territory", "territory": territory_name}
                    elif self.game_stage == "initial_soldiers":
                        message = {"type": "selected_initial_soldier_territory", "territory": territory_name}
                    elif self.game_stage == "receiving_reinforcements":
                        message = {"type": "selected_reinforcement_territory", "territory": territory_name}
                    elif self.game_stage == "attacking_territory":
                        message = {"type": "selected_attacking_territory", "territory": territory_name}
                    elif self.game_stage == "defending_territory":
                        message = {"type": "selected_defending_territory", "territory": territory_name}
                    elif self.game_stage == "fortify_territory_home":
                        message = {"type": "selected_fortify_territory_home", "territory": territory_name}
                    elif self.game_stage == "fortify_territory_new_home":
                        message = {"type": "selected_fortify_territory_new_home", "territory": territory_name}
                    if message != "":
                        self.client_socket.sendall(pickle.dumps(message))
                    self.prev_game_state = self.game_state

                if self.game_state == "select_soldiers":
                    if self.game_stage == "attacking_territory_soldiers":
                        number = self.create_popup(screen, self.player_message, self.number) + 1
                        message = {"type": "selected_attacking_soldiers", "number": number}
                    elif self.game_stage == "transferring_territory_soldiers":
                        number = self.create_popup(screen, self.player_message, self.number) + 1
                        message = {"type": "selected_transferring_soldiers", "number": number}
                    elif self.game_stage == "attack_summary":
                        result_options = ["Continue Fighting", "End Combat"]
                        if self.can_attack is False:
                            result_options = ["End Combat"]
                        result_index = self.create_popup(screen, self.player_message, result_options,
                                                         added_results=self.attacker_dice + self.defender_dice)
                        if self.can_attack is False:
                            result_index += 1
                        message = {"type": "selected_attack_option", "number": result_index}
                    elif self.game_stage == "select_if_fortify":
                        result_options = ["Fortify", "End Turn"]
                        result_index = self.create_popup(screen, self.player_message, result_options)
                        message = {"type": "selected_if_fortify", "number": result_index}
                    elif self.game_stage == "select_fortify_soldiers":
                        number = self.create_popup(screen, self.player_message, self.number) + 1
                        message = {"type": "selected_fortify_soldiers", "number": number}
                    elif self.game_stage == "card_series":
                        result_options = ["Yes", "No"]
                        if self.number == 1:
                            result_options = ["Yes"]
                        result_index = self.create_popup(screen, self.player_message, result_options)
                        message = {"type": "selected_card_series", "number": result_index}
                    elif self.game_stage == "round_summary":
                        self.create_summary(screen, self.player_message, self.number)
                        message = {"type": "accepted_turn_end"}

                    self.client_socket.sendall(pickle.dumps(message))
                    self.prev_game_state = self.game_state

                if self.game_state == "print_board":
                    if self.game_stage == "out_of_game":
                        self.edit_screen(screen, f"All of your territories have been conquered. You are out of the game")
                    elif self.game_stage == "win_phase":
                        message = f"{self.current_player} has won the game! They have conquered all of the territories and win the game of Risk!"
                        if self.current_player == self.player_name:
                            message = "You win the game!"
                        self.edit_screen(screen, message)
                    else:
                        self.edit_screen(screen, f"It's {self.current_player}'s turn")
                    self.prev_game_state = self.game_state

                if self.game_state == "end_game":
                    self.end_game(screen)

                if self.game_state == "pick_saves":
                    self.present_saves(screen, self.saves, "saves")

                if self.game_state == "pick_save_player_options":
                    self.present_saves(screen, self.player_options, "players")

                if self.game_state == "pick_save_name":
                    self.game_ended = True
                    self.get_player_input(screen, "save_name", False)
            pygame.display.flip()  # Update the display

            clock.tick(30)  # Limit frame rate to 30 FPS

    def receive_data(self, game_screen):
        try:
            while True:
                # Receive messages from the server
                data = self.client_socket.recv(1024)
                print("I received new data!!!!")
                if not data:
                    break

                # Process received message
                self.edited = False
                message = pickle.loads(data)
                message_type = message.get("type")
                print(f"Message type: {message_type}")

                if message_type == "max_players_reached":
                    pygame.quit()
                    sys.exit()

                if message_type == "join_message":
                    if message.get("message") == "You are the host.":
                        self.is_host = True  # Set the player as the host

                if message_type == "player_names":
                    self.player_list = message.get("message")
                    self.game_code = message.get("code")
                    self.game_state = "lobby"
                    if not self.demo:
                        self.demo = message.get("demo")
                        self.create_board(self.demo)
                    game_type = message.get("game_type")
                    if message.get("number") != 0:
                        self.save_game_count = message.get("number")
                    if game_type == "saved":
                        self.saved_game = True
                    print(message)
                    print(self.player_list)

                if message_type == "player_color":
                    self.player_color = message.get("color")

                if message_type == "start_game":
                    print("We have officially began the risk game.")
                    if not self.demo:
                        self.demo = message.get("demo")
                        self.create_board(self.demo)
                    self.territory_information = message.get("territory_info")
                    self.current_player = message.get("current_player")
                    print(message.get("territory_info"))
                    self.update_local_board()
                    self.game_state = "print_board"

                if message_type == "reselect_territory":
                    print("I need to reselect my territory")
                    self.prev_game_state = "None"
                    self.game_state = "select_territory"
                    self.player_message = message.get("message")

                if message_type == "edit_board":
                    if message.get("out") == "True":
                        self.game_stage = "out_of_game"
                    if message.get("win") == "True":
                        self.game_stage = "win_phase"
                    self.territory_information = message.get("territory_info")
                    self.prev_player = self.current_player
                    self.current_player = message.get("current_player")
                    self.update_local_board()
                    self.game_state = "print_board"

                if message_type == "end_game":
                    self.game_state = "end_game"
                    self.game_ended = True

                if message_type == "saves":
                    self.saves = message.get("saves")
                    self.game_state = "pick_saves"

                if message_type == "player_options":
                    self.player_options = message.get("player_options")
                    self.game_state = "pick_save_player_options"

                if message_type == "continue_game":
                    states = message.get("stage")
                    self.game_stage = states[0]
                    self.game_state = states[1]
                    self.player_message = states[2]

                if message_type == "get_info_for_save":
                    self.saved_game_state = self.game_state
                    self.game_state = "pick_save_name"

                if message_type == "turn_message":
                    print("It is my turn")
                    if message.get("turn_type") == "initial_territory_selection":
                        self.player_message = f"{self.player_name}, please select a territory"
                        self.game_state = "select_territory"
                        self.game_stage = "initial_territories"
                    elif message.get("turn_type") == "initial_soldier_addition":
                        self.player_message = f"{self.player_name}, please select a territory that you own to add a soldier to:"
                        self.game_state = "select_territory"
                        self.game_stage = "initial_soldiers"
                    elif message.get("turn_type") == "receiving_reinforcements":
                        self.player_message = f"{self.player_name}, you have {message.get("number")} soldiers remaining. Please select another territory to place a soldier in."
                        if message.get("first_time") == "True":
                            self.player_message = f"{self.player_name}, you have been awarded {message.get("number")} soldiers to place.\n please select one of your territories to add a reinforcement to: "
                        self.game_state = "select_territory"
                        self.game_stage = "receiving_reinforcements"
                    elif message.get("turn_type") == "select_attacking_territory":
                        self.player_message = f"{self.player_name}, please select a territory you would like to attack with"
                        self.game_state = "select_territory"
                        self.game_stage = "attacking_territory"
                    elif message.get("turn_type") == "select_attacking_soldiers":
                        self.player_message = "Select number of soldiers to send:"
                        self.number = message.get("number")
                        self.game_state = "select_soldiers"
                        self.game_stage = "attacking_territory_soldiers"
                    elif message.get("turn_type") == "select_defending_territory":
                        self.player_message = "Please select an enemy territory you would like to attack"
                        self.game_state = "select_territory"
                        self.game_stage = "defending_territory"
                    elif message.get("turn_type") == "select_transfer_soldiers":
                        self.attacker_dice = message.get("attacker_dice")
                        self.defender_dice = message.get("defender_dice")
                        self.player_message = "Please select how many soldiers you will move over"
                        self.number = message.get("transfer_options")
                        self.game_state = "select_soldiers"
                        self.game_stage = "transferring_territory_soldiers"
                    elif message.get("turn_type") == "attack_results":
                        self.attacker_dice = message.get("attacker_dice")
                        self.defender_dice = message.get("defender_dice")
                        self.player_message = f"You rolled: {self.attacker_dice}; {message.get("defender")} rolled: {self.defender_dice}"
                        self.can_attack = message.get("can_attack")
                        self.game_state = "select_soldiers"
                        self.game_stage = "attack_summary"
                    elif message.get("turn_type") == "fortify_position":
                        self.player_message = "Would you like to fortify your position?"
                        self.game_state = "select_soldiers"
                        self.game_stage = "select_if_fortify"
                    elif message.get("turn_type") == "select_fortify_territory":
                        self.player_message = "Please select one of your territories to move soldiers from: "
                        self.game_state = "select_territory"
                        self.game_stage = "fortify_territory_home"
                    elif message.get("turn_type") == "select_fortify_territory_soldier_number":
                        self.player_message = "Please select how many soldiers to send to the new territory"
                        self.number = message.get("transfer_options")
                        self.game_state = "select_soldiers"
                        self.game_stage = "select_fortify_soldiers"
                    elif message.get("turn_type") == "select_fortify_territory_new_home":
                        self.player_message = "Please select which territory you want to fortify"
                        self.game_state = "select_territory"
                        self.game_stage = "fortify_territory_new_home"
                    elif message.get("turn_type") == "card_turn_in":
                        self.player_message = f"Would you like to turn in a card set for {message.get("number")} additional reinforcements?"
                        self.number = message.get("forced")
                        self.game_state = "select_soldiers"
                        self.game_stage = "card_series"
                    elif message.get("turn_type") == "round_summary":
                        self.player_message = "Round Summary"
                        self.number = [message.get("territories_conquered"), message.get("cards")]
                        self.game_state = "select_soldiers"
                        self.game_stage = "round_summary"
        except Exception as e:
            print(f"Error in client: {e}")

    def select_territory(self):
        selection_valid = False
        selected_territory = None
        while not selection_valid and self.game_ended is False:
            for event in pygame.event.get():
                if self.game_ended:
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for territory_name, territory in self.board.territories.items():
                        if territory.click(mouse_pos):
                            selected_territory = territory
                            selection_valid = True
                        save_btn = pygame.Rect(800, 550, 150, 50)
                        if save_btn.collidepoint(mouse_pos):
                            self.get_player_input(screen, "save_name", False)
                            return None
                        if self.game_stage == "attacking_territory" or self.game_stage == "defending_territory":
                            button_rect = pygame.Rect(625, 550, 150, 50)
                            if button_rect.collidepoint(mouse_pos):
                                selected_territory = None
                                selection_valid = True
        return selected_territory

    def choose_demo(self, screen):
        pygame.font.init()
        yes_button = pygame.Rect(400, 350, 200, 40)
        no_button = pygame.Rect(400, 450, 220, 40)
        font = pygame.font.Font(None, 32)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == MOUSEBUTTONDOWN:
                    if yes_button.collidepoint(event.pos):
                        self.create_board(True)
                        return
                    if no_button.collidepoint(event.pos):
                        self.create_board(False)
                        return
            screen.fill((194, 236, 237))
            draw_text("Demo?", font, (0, 0, 0), screen,
                      100, 250)
            color = pygame.Color('green')

            pygame.draw.rect(screen, color, yes_button)
            pygame.draw.rect(screen, color, no_button)
            text = font.render("Yes", True, (255, 255, 255))
            text_rect = text.get_rect(center=yes_button.center)
            screen.blit(text, text_rect)

            text = font.render("No", True, (255, 255, 255))
            text_rect = text.get_rect(center=no_button.center)
            screen.blit(text, text_rect)
            pygame.display.flip()

    def game_options(self, screen, has_host):
        pygame.font.init()
        if has_host:
            join_game_button = pygame.Rect(400, 350, 200, 40)
        else:
            new_game_button = pygame.Rect(400, 350, 200, 40)
            load_game_button = pygame.Rect(400, 450, 220, 40)
        text = ''
        font = pygame.font.Font(None, 32)
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == MOUSEBUTTONDOWN:
                    if has_host:
                        if join_game_button.collidepoint(event.pos):
                            self.get_player_input(screen, "code", False)
                            return
                    else:
                        if new_game_button.collidepoint(event.pos):
                            self.choose_demo(screen)
                            self.get_player_input(screen, "name", False)
                            return
                        if load_game_button.collidepoint(event.pos):
                            message = {"type": "get_saves"}
                            self.client_socket.sendall(pickle.dumps(message))
                            return
            screen.fill((194, 236, 237))
            draw_text("Welcome, would you like to start a new game or load an existing game?", font, (0, 0, 0), screen, 100, 250)
            color = pygame.Color('green')

            # Render the submit button
            if has_host:
                pygame.draw.rect(screen, color, join_game_button)
                text = font.render("Join Game", True, (255, 255, 255))
                text_rect = text.get_rect(center=join_game_button.center)
                screen.blit(text, text_rect)
            else:
                pygame.draw.rect(screen, color, new_game_button)
                pygame.draw.rect(screen, color, load_game_button)
                text = font.render("New Game", True, (255, 255, 255))
                text_rect = text.get_rect(center=new_game_button.center)
                screen.blit(text, text_rect)

                text = font.render("Load Local Game", True, (255, 255, 255))
                text_rect = text.get_rect(center=load_game_button.center)
                screen.blit(text, text_rect)
            pygame.display.flip()

    def get_player_input(self, screen, input_type, retry):
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
                        message = ""
                        if input_type == "name":
                            self.player_name = text
                            message = {"type": "name_selection", "name": self.player_name, "demo": self.demo}
                        elif input_type == "code":
                            message = {"type": "game_code", "code": text}
                        elif input_type == "save_name":
                            saved_state = self.game_state
                            if self.saved_game_state:
                                saved_state = self.saved_game_state
                            message = {"type": "save_game", "save_name": text, "stage": [self.game_stage, saved_state, self.player_message]}
                            self.game_state = "end_game"
                        self.client_socket.sendall(pickle.dumps(message))
                        return
                    color = color_active if active else color_inactive
                if event.type == KEYDOWN:
                    if active:
                        if event.key == K_RETURN:
                            # Send the entered name to the server
                            message = ""
                            if input_type == "name":
                                self.player_name = text
                                message = {"type": "name_selection", "name": self.player_name, "demo": self.demo}
                            elif input_type == "code":
                                message = {"type": "game_code", "code": text}
                            elif input_type == "save_name":
                                saved_state = self.game_state
                                if self.saved_game_state:
                                    saved_state = self.saved_game_state
                                message = {"type": "save_game", "save_name": text, "stage": [self.game_stage, saved_state, self.player_message]}
                                self.game_state = "end_game"
                            self.client_socket.sendall(pickle.dumps(message))
                            return
                        elif event.key == K_BACKSPACE:
                            text = text[:-1]
                        else:
                            text += event.unicode

            screen.fill((194, 236, 237))
            # Render the welcome message.
            if input_type == "name":
                draw_text("Welcome, please enter your name!", font, (0, 0, 0), screen, 300, 250)
            elif input_type == "code":
                if retry:
                    draw_text("Incorrect game code, please enter again.", font, (0, 0, 0), screen, 300, 250)
                else:
                    draw_text("Welcome, please enter the game code!", font, (0, 0, 0), screen, 300, 250)
            elif input_type == "save_name":
                draw_text("Please enter a name for your local save:", font, (0, 0, 0), screen, 300, 250)
            txt_surface = font.render(text, True, color)
            width = max(200, txt_surface.get_width() + 10)
            input_box.w = width
            screen.blit(txt_surface, (input_box.x + 5, input_box.y + 5))
            pygame.draw.rect(screen, color, input_box, 2)

            pygame.draw.rect(screen, color_submit, submit_button)
            draw_text("Submit", font, (255, 255, 255), screen, 370, 360)

            pygame.display.flip()

    def host_wait_screen(self, screen):
        font = pygame.font.Font(None, 36)  # Font for rendering text
        print("flipflopflipflop")

        screen.fill((194, 236, 237))  # Fill the screen with white color

        if self.game_code is not None:
            draw_text(f"Room Code: {self.game_code}", font, (0, 0, 0), screen, 300, 20)

        # Display title
        draw_text("Players in the Lobby:", font, (0, 0, 0), screen, 300, 75)

        # Display player names
        for i, player_name in enumerate(self.player_list):
            draw_text(player_name, font, (0, 0, 0), screen, 300, 125 + i * 40)

        # Check if the client is the host and there are at least three clients including the host
        if self.is_host:
            if (self.saved_game and len(self.player_list) == self.save_game_count) or (
                    self.saved_game is False and len(self.player_list) >= 2):
                start_button = pygame.Rect(250, 150 + len(self.player_list) * 40, 200, 50)
                pygame.draw.rect(screen, (0, 255, 0), start_button)
                draw_text("Start Game", font, (0, 0, 0), screen, start_button.x + 50, start_button.y + 15)

    def spectator_wait_screen(self, screen):
        font = pygame.font.Font(None, 36)
        print("flipflopflipflop")

        screen.fill((194, 236, 237))
        draw_text("Waiting for game to begin...", font, (0, 0, 0), screen, 300, 75)


    def start_game(self):
        message = {"type": "start_game"}
        self.client_socket.sendall(pickle.dumps(message))
        print("Start game message sent to server")

    def start_saved_game(self):
        message = {"type": "start_saved_game"}
        self.client_socket.sendall(pickle.dumps(message))

    def end_game(self, screen):
        screen.fill((194, 236, 237))
        font = pygame.font.Font(None, 36)
        draw_text("The game has been ended by host", font, (0, 0, 0), screen, 300, 50)
        pygame.display.flip()
        pygame.time.Clock().tick(30)

    def update_local_board(self):
        for territory_name, territory_info in self.territory_information.items():
            self.board.territories[territory_name].soldierNumber = territory_info[0]
            self.board.territories[territory_name].owner = territory_name

    def present_saves(self, screen, saves, save_type):

        font = pygame.font.Font(None, 36)
        small_font = pygame.font.Font(None, 24)

        save_buttons = []

        if save_type == "saves":
            for idx, (game_code, save_name) in enumerate(saves):
                rect = pygame.Rect(100, 150 + 75 * idx, 250, 40)
                save_buttons.append((rect, (game_code, save_name)))
        elif save_type == "players":
            for idx, player_name in enumerate(saves):
                rect = pygame.Rect(100, 150 + 75 * idx, 150, 40)
                save_buttons.append((rect, player_name))

        running = True
        while running:
            for event in pygame.event.get():
                if event.type == QUIT:
                    pygame.quit()
                if event.type == MOUSEBUTTONDOWN:
                    print("whwhwhwh")
                    for button, save in save_buttons:
                        if button.collidepoint(event.pos):
                            message = ""
                            print("oisjdofisjdofi")
                            if save_type == "saves":
                                message = {"type": "selected_save", "save": save[0]}
                            elif save_type == "players":
                                self.player_name = save
                                message = {"type": "selected_player", "save": save}
                            self.client_socket.sendall(pickle.dumps(message))
                            return

            screen.fill((194, 236, 237))
            color = pygame.Color('green')

            if save_type == "saves":
                draw_text("Please select a game save: ", font, (0, 0, 0), screen, 300, 100)
            elif save_type == "players":
                draw_text("Select your name: ", font, (0, 0, 0), screen, 300, 100)



            for rect, _ in save_buttons:
                pygame.draw.rect(screen, color, rect)

            if save_type == "saves":
                for rect, (game_code, save_name) in save_buttons:
                    text = font.render(f"{save_name} (Code: {game_code})", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)
            elif save_type == "players":
                for rect, player_name in save_buttons:
                    text = font.render(f"{player_name}", True, (255, 255, 255))
                    text_rect = text.get_rect(center=rect.center)
                    screen.blit(text, text_rect)

            pygame.display.flip()

        pygame.quit()

    def create_board(self, demo):
        if demo:
            self.demo = True
            self.board = Board(True)
        else:
            self.demo = False
            self.board = Board(False)

    def edit_screen(self, screen, message=None):
        # Clear the screen
        screen.fill((194, 236, 237))  # Fill with white background

        # Draw the territories
        for territory_name, territory in self.board.territories.items():
            territory.draw(screen, (self.territory_information[territory_name])[1])
            territory.draw_lines_to_neighbors(screen)

        # Add text to the button
        if self.game_stage == "attacking_territory" or self.game_stage == "defending_territory":
            button_rect = pygame.Rect(625, 550, 200, 50)  # Button position and size
            pygame.draw.rect(screen, (0, 0, 255), button_rect)  # Draw the button
            font = pygame.font.SysFont(None, 30)
            text = font.render("End Combat Phase", True, (255, 255, 255))
            text_rect = text.get_rect(center=button_rect.center)
            screen.blit(text, text_rect)

        if self.game_state == "select_territory":
            save_btn = pygame.Rect(850, 550, 150, 50)
            pygame.draw.rect(screen, (0, 0, 255), save_btn)
            font = pygame.font.SysFont(None, 30)
            text = font.render("Save Game", True, (255, 255, 255))
            text_rect = text.get_rect(center=save_btn.center)
            screen.blit(text, text_rect)


        if message:
            font = pygame.font.SysFont(None, 30)
            text_surface = font.render(message, True, (0, 0, 0))
            screen.blit(text_surface, (width // 2 - text_surface.get_width() // 2, 20))

        # Update the display
        pygame.display.flip()

        # Control the frame rate
        pygame.time.Clock().tick(30)

    def create_popup(self, screen, text, options, added_results=None):
        # Determine popup size based on content
        popup_width = 400
        option_height = 40

        # Adjust popup height based on number of options
        max_options_per_column = 10
        num_columns = -(-len(options) // max_options_per_column)  # Ceiling division
        num_rows = min(len(options), max_options_per_column)
        popup_height = 200 + num_rows * option_height

        if added_results:
            popup_height += 150  # Additional height for dice results

        popup_x = (width - popup_width) // 2
        popup_y = (height - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Draw the popup window
        pygame.draw.rect(screen, (200, 200, 200), popup_rect)
        pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)

        # Add text to the popup
        font = pygame.font.SysFont(None, 30)
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(
            center=(popup_x + popup_width // 2, popup_y + 40))  # Adjusted vertical position
        screen.blit(text_surface, text_rect)

        # Calculate vertical spacing for options
        total_option_height = num_rows * option_height
        start_y = popup_y + 100 + (popup_height - 100 - total_option_height) // 2

        # Calculate number of options per column
        options_per_column = (len(options) + num_columns - 1) // num_columns

        # Add buttons for each option
        button_width = min(120, popup_width // num_columns - 20)  # Adjust button width dynamically
        for i, option in enumerate(options):
            column_index = i // options_per_column
            row_index = i % options_per_column
            button_x = popup_x + (popup_width // num_columns) * column_index + (
                        popup_width // num_columns - button_width) // 2
            button_y = start_y + row_index * option_height
            button_rect = pygame.Rect(button_x, button_y, button_width, option_height)
            pygame.draw.rect(screen, (100, 100, 255), button_rect)
            text_surface = font.render(option, True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

        # Return the index of the selected option
        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for i, option in enumerate(options):
                        column_index = i // options_per_column
                        row_index = i % options_per_column
                        button_x = popup_x + (popup_width // num_columns) * column_index + (
                                    popup_width // num_columns - button_width) // 2
                        button_y = start_y + row_index * option_height
                        button_rect = pygame.Rect(button_x, button_y, button_width, option_height)
                        if button_rect.collidepoint(mouse_pos):
                            return i

    def create_summary(self, screen, text, added_results):
        popup_width = 400
        popup_height = 500
        option_height = 40

        width, height = screen.get_size()  # Get screen size to calculate popup position
        popup_x = (width - popup_width) // 2
        popup_y = (height - popup_height) // 2
        popup_rect = pygame.Rect(popup_x, popup_y, popup_width, popup_height)

        # Draw the popup window
        pygame.draw.rect(screen, (200, 200, 200), popup_rect)
        pygame.draw.rect(screen, (0, 0, 0), popup_rect, 2)

        font = pygame.font.SysFont(None, 30)

        # Render the main text
        text_surface = font.render(text, True, (0, 0, 0))
        text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 40))
        screen.blit(text_surface, text_rect)

        if self.game_stage == "round_summary":
            result_surface = font.render(f"Conquered territories: {added_results[0]}", True, (0, 0, 0))
            result_rect = result_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 100 + option_height))
            screen.blit(result_surface, result_rect)

            result_surface = font.render(f"Infantry cards: {added_results[1]["infantry"]}", True, (0, 0, 0))
            result_rect = result_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 100 + 2 * option_height))
            screen.blit(result_surface, result_rect)

            result_surface = font.render(f"Cavalry cards: {added_results[1]["cavalry"]}", True, (0, 0, 0))
            result_rect = result_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 100 + 3 * option_height))
            screen.blit(result_surface, result_rect)

            result_surface = font.render(f"Artillery cards: {added_results[1]["artillery"]}", True, (0, 0, 0))
            result_rect = result_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 100 + 4 * option_height))
            screen.blit(result_surface, result_rect)

            button_rect = pygame.Rect(popup_x + popup_width // 2, popup_y + 100 + 5 * option_height, 100, option_height)
            pygame.draw.rect(screen, (100, 100, 255), button_rect)
            text_surface = font.render("End Turn", True, (255, 255, 255))
            text_rect = text_surface.get_rect(center=button_rect.center)
            screen.blit(text_surface, text_rect)

        pygame.display.flip()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    if button_rect.collidepoint(mouse_pos):
                        return


if __name__ == "__main__":
    HOST = "192.168.86.250"
    PORT = 8080
    client = RiskClient(HOST, PORT)
    client.start()
