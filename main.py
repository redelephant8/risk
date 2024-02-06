import pygame
import sys

from territory import Territory
from player import Player
from board import Board

game_state = 0
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Risk")

def edit_screen():
    # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white background

    # Draw the territories
    # Draw the territories
    game.board.territories["qatar"].draw(screen)
    game.board.territories["qatar"].draw_lines_to_neighbors(screen)

    game.board.territories["afghanistan"].draw(screen)
    game.board.territories["afghanistan"].draw_lines_to_neighbors(screen)

    game.board.territories["saudi_arabia"].draw(screen)
    game.board.territories["saudi_arabia"].draw_lines_to_neighbors(screen)

    game.board.territories["iran"].draw(screen)
    game.board.territories["iran"].draw_lines_to_neighbors(screen)

    game.board.territories["egypt"].draw(screen)
    game.board.territories["egypt"].draw_lines_to_neighbors(screen)

    # Draw the button
    button_rect = pygame.Rect(600, 500, 150, 50)  # Button position and size
    pygame.draw.rect(screen, (0, 0, 255), button_rect)  # Draw the button

    # Add text to the button
    font = pygame.font.SysFont(None, 30)
    text = font.render("End Combat", True, (255, 255, 255))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)



class Game:
    def __init__(self):
        player1 = Player("Red", "Elad")
        player2 = Player("Blue", "Ben")
        player3 = Player("Green", "Orian")
        self.players = [player1, player2, player3]
        self.current_player = self.players[0]
        self.current_player_index = 0
        self.board = Board()
        self.game_state = 0

    def change_current_player(self):
        i = self.current_player_index
        if i+1 >= len(self.players):
            self.current_player = self.players[0]
            self.current_player_index = 0
        else:
            self.current_player = self.players[i+1]
            self.current_player_index = i+1

    def add_territories(self, current_player, selected_territory):
        current_player.territories.append(selected_territory)
        selected_territory.owner = current_player
        selected_territory.soldiers += 1

    def choosing_initial_territories(self):
        territories_remaining = 5
        while territories_remaining > 0:
            for player in self.players:
                if territories_remaining > 0:
                    mouse_pos = pygame.mouse.get_pos()
                    for territory_name, territory in self.board.territories.items():
                        if territory.click(mouse_pos):
                            territory.owner = player
                            player.territories.append(territory)
                            print(f"{player.name} picked {territory_name}")
                            territories_remaining -= 1

game = Game()
running = True

while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

        # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white background

    # Draw the territories
    game.board.territories["qatar"].draw(screen)
    game.board.territories["qatar"].draw_lines_to_neighbors(screen)

    game.board.territories["afghanistan"].draw(screen)
    game.board.territories["afghanistan"].draw_lines_to_neighbors(screen)

    game.board.territories["saudi_arabia"].draw(screen)
    game.board.territories["saudi_arabia"].draw_lines_to_neighbors(screen)

    game.board.territories["iran"].draw(screen)
    game.board.territories["iran"].draw_lines_to_neighbors(screen)

    game.board.territories["egypt"].draw(screen)
    game.board.territories["egypt"].draw_lines_to_neighbors(screen)


    # Draw the button
    button_rect = pygame.Rect(600, 500, 150, 50)  # Button position and size
    pygame.draw.rect(screen, (0, 0, 255), button_rect)  # Draw the button

    # Add text to the button
    font = pygame.font.SysFont(None, 30)
    text = font.render("End Combat", True, (255, 255, 255))
    text_rect = text.get_rect(center=button_rect.center)
    screen.blit(text, text_rect)

    # Update the display
    pygame.display.flip()

    game_state = 1
    territories_remaining = 5

    while game_state == 1 and territories_remaining > 0:
        for player in game.players:
            territory_selected = False
            if territories_remaining > 0:
                print(f"{player.name} please select a territory")
                while not territory_selected:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            for territory_name, territory in game.board.territories.items():
                                if territory.click(mouse_pos):
                                    if territory.owner is None:
                                        territory.owner = player
                                        player.territories.append(territory)
                                        territory.soldierNumber += 1  # Increment the number of soldiers
                                        player.soldiers_in_hand -= 1
                                        print(f"{player.name} picked {territory.name}")
                                        territories_remaining -= 1
                                        print(f"territories remaining: {territories_remaining}")
                                        territory_selected = True
                                        edit_screen()
                                        break
                                    elif territory.owner == player:
                                        print(f"You already own {territory.name}, please choose an empty territory")
                                        continue
                                    # elif territory.owner == player:
                                    #     territory.soldierNumber += 1
                                    #     print(f"{player.name} added a soldier to {territory.name}")
                                    #     territory_selected = True
                                    #     edit_screen()
                                    #     break
                                    else:
                                        print(f"{territory.name} has already been chosen by {territory.owner.name}")
                                        continue
                if territories_remaining == 0:
                    game_state = 2
                    break

    players_remaining = len(game.players)

    while game_state == 2:
        for player in game.players:
            territory_selected = False
            if player.soldiers_in_hand == 0:
                players_remaining -= 1
            if player.soldiers_in_hand > 0:
                print(f"{player.name}, please select a territory that you own to add a soldier to:")
                while not territory_selected:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            for territory_name, territory in game.board.territories.items():
                                if territory.click(mouse_pos):
                                    if territory.owner is player:
                                        territory.soldierNumber += 1
                                        player.soldiers_in_hand -= 1
                                        print(f"{player.name} added a soldier to {territory.name}")
                                        print(f"{player.name}, soldiers remaining: {player.soldiers_in_hand}")
                                        territory_selected = True
                                        edit_screen()
                                        break
                                    elif territory.owner is not player:
                                        print(f"{territory.name} is owned by {territory.owner.name}. You can not add soldiers to a territory you don't own")
                                        continue
            if players_remaining <= 0:
                game_state = 3
                break

    while game_state == 3:
        for player in game.players:
            print(f"It is {player.name}'s turn. Stage 1: Receiving and Placing Reinforcements")
            player.soldiers_in_hand = player.reinforcement_calculator()
            print(f"{player.name}, you have been awarded {player.soldiers_in_hand} to place")
            while player.soldiers_in_hand > 0:
                territory_selected = False
                print(f"{player.name}, please select a territory to add a soldier to.")
                while not territory_selected:
                    for event in pygame.event.get():
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            for territory_name, territory in game.board.territories.items():
                                if territory.click(mouse_pos):
                                    if territory.owner is player:
                                        territory.soldierNumber += 1
                                        player.soldiers_in_hand -= 1
                                        print(f"{player.name} added a soldier to {territory.name}")
                                        print(f"{player.name}, soldiers remaining: {player.soldiers_in_hand}")
                                        territory_selected = True
                                        edit_screen()
                                        break
                                    elif territory.owner is not player:
                                        print(
                                            f"{territory.name} is owned by {territory.owner.name}. You can not add soldiers to a territory you don't own")
                                        continue
            print("Stage 2: Combat")
            combat_stage = True
            while combat_stage:
                print(f"{player.name}, please select a territory you would like to attack with. If you would like to end the combat stage, press End Combat")
                territory_selected = False
                attacking_territory = None
                defending_territory = None
                while not territory_selected:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        mouse_pos = pygame.mouse.get_pos()
                        for territory_name, territory in game.board.territories.items():
                            if territory.click(mouse_pos):
                                if territory.owner is player:
                                    if territory.soldierNumber > 1:
                                        if territory.check_neighbors(player):
                                            attacking_territory = territory
                                            territory_selected = True
                                        else:
                                            print("There are no neighboring territories to attack")
                                    else:
                                        print("You can not attack with a territory that has less than 2 soldiers")
                                else:
                                    print("You must select one of your own territories to attack with")
                if attacking_territory is not None:
                    territory_selected = False
                    while not territory_selected:
                        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                            mouse_pos = pygame.mouse.get_pos()
                            for territory_name, territory in game.board.territories.items():
                                if territory.click(mouse_pos):
                                    if territory.owner in attacking_territory.neighbors:
                                        if territory.owner is not player:
                                            defending_territory = territory
                                            territory_selected = True
                                        else:
                                            print("You can't attack your own territory")
                                    else:
                                        print("You must attack a neighboring territory")
                    if defending_territory is not None:
                        print(f"New Battle: {player} is attacking {defending_territory.name} with {attacking_territory.name}")
                        print(f"Each side must now roll their dice to decide the outcome of this battle: ")




    # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white background

    # Draw the territories
    game.board.territories["qatar"].draw(screen)
    game.board.territories["afghanistan"].draw(screen)
    game.board.territories["saudi_arabia"].draw(screen)
    game.board.territories["iran"].draw(screen)
    game.board.territories["egypt"].draw(screen)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
