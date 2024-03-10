import pygame
import sys
import random

from territory import Territory
from player import Player
from board import Board

game_state = 0
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Risk")

DICE_SIZE = 10
DICE_OFFSET_X = 50
DICE_OFFSET_Y = 50
DICE_IMAGES = {
    1: pygame.image.load("dice_white_1.png"),
    2: pygame.image.load("dice_white_2.png"),
    3: pygame.image.load("dice_white_3.png"),
    4: pygame.image.load("dice_white_4.png"),
    5: pygame.image.load("dice_white_5.png"),
    6: pygame.image.load("dice_white_6.png"),
}

def draw_dice(screen, value, x, y):
    screen.blit(DICE_IMAGES[value], (x, y))
    pygame.display.flip()


def edit_screen(message=None):
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

    if message:
        text_surface = font.render(message, True, (0, 0, 0))
        screen.blit(text_surface, (width // 2 - text_surface.get_width() // 2, 20))

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)

def create_popup(screen, text, options, dice_results=None):
    # Determine popup size based on content
    popup_width = 400
    option_height = 40
    popup_height = 200 + len(options) * option_height  # Adjusted spacing
    if dice_results:
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
    text_rect = text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 40))  # Adjusted vertical position
    screen.blit(text_surface, text_rect)

    # Calculate vertical spacing for options
    total_option_height = len(options) * option_height
    start_y = popup_y + 100 + (popup_height - 100 - total_option_height) // 2

    # Add buttons for each option
    button_width = 120
    for i, option in enumerate(options):
        button_x = popup_x + (popup_width - button_width) // 2
        button_y = start_y + i * option_height
        button_rect = pygame.Rect(button_x, button_y, button_width, option_height)
        pygame.draw.rect(screen, (100, 100, 255), button_rect)
        text_surface = font.render(option, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=button_rect.center)
        screen.blit(text_surface, text_rect)

    # Draw dice results
    if dice_results:
        dice_text = "Dice Results:"
        dice_text_surface = font.render(dice_text, True, (0, 0, 0))
        dice_text_rect = dice_text_surface.get_rect(center=(popup_x + popup_width // 2, popup_y + 150))
        screen.blit(dice_text_surface, dice_text_rect)

        dice_x = popup_x + (popup_width - DICE_SIZE * len(dice_results)) // 2
        dice_y = popup_y + popup_height - 120
        for i, result in enumerate(dice_results):
            draw_dice(screen, result, dice_x + i * (DICE_SIZE + 10), dice_y)

    pygame.display.flip()

    # Return the index of the selected option
    while True:
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                mouse_pos = pygame.mouse.get_pos()
                for i, option in enumerate(options):
                    button_rect = pygame.Rect(button_x, start_y + i * option_height, button_width, option_height)
                    if button_rect.collidepoint(mouse_pos):
                        return i

def end_combat_popup(screen):
    # Display a popup asking if the player wants to continue fighting
    options = ["Continue Fighting", "End Turn"]
    selection = create_popup(screen, "End of Combat Phase. What would you like to do?", options)
    return selection

class Game:
    def __init__(self):
        player1 = Player("Red", "Elad")
        player2 = Player("Indigo", "Ben")
        player3 = Player("Yellow", "Orian")
        self.players = [player1, player2, player3]
        self.player = self.players[0]
        self.player_index = 0
        self.board = Board()
        self.game_state = 0
        self.territory_selected = False
        self.combat_stage_flag = False



    def change_current_player(self):
        i = self.player_index
        if i+1 >= len(self.players):
            self.player = self.players[0]
            self.player_index = 0
        else:
            self.player = self.players[i+1]
            self.player_index = i+1

    def add_territories(self, current_player, selected_territory):
        current_player.territories.append(selected_territory)
        selected_territory.owner = current_player
        selected_territory.soldiers += 1

    def select_territory(self):
        selection_valid = False
        selected_territory = None
        while not selection_valid:
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    mouse_pos = pygame.mouse.get_pos()
                    for territory_name, territory in game.board.territories.items():
                        if territory.click(mouse_pos):
                            selected_territory = territory
                            selection_valid = True
                            edit_screen()
                        button_rect = pygame.Rect(600, 500, 150, 50)
                        if button_rect.collidepoint(mouse_pos) and self.combat_stage_flag is True:
                            selected_territory = None
                            selection_valid = True
                            print("BENSAVIRISBEHINDME")
                            edit_screen()
                            self.combat_stage_flag = False
        return selected_territory

    def choosing_initial_territories(self):
        edit_screen()
        territories_remaining = 5
        while territories_remaining > 0:
            self.territory_selected = False
            print(f"{self.player.name} please select a territory")
            edit_screen(f"{self.player.name} please select a territory")
            while not self.territory_selected:
                territory = self.select_territory()
                if territory.owner is None:
                    territory.owner = self.player
                    self.player.territories.append(territory)
                    territory.soldierNumber += 1  # Increment the number of soldiers
                    self.player.soldiers_in_hand -= 1
                    print(f"{self.player.name} picked {territory.name}")
                    territories_remaining -= 1
                    print(f"territories remaining: {territories_remaining}")
                    self.territory_selected = True
                    edit_screen()
                    self.change_current_player()
                elif territory.owner == self.player:
                    edit_screen(f"You already own {territory.name}. please choose an empty territory")
                    print(f"You already own {territory.name}. please choose an empty territory")
                    continue
                else:
                    edit_screen(f"{territory.name} has already been chosen by {territory.owner.name}")
                    print(f"{territory.name} has already been chosen by {territory.owner.name}")
                    continue
                edit_screen()

    def initial_additional_soldier_addition(self):
        self.player = self.players[0]
        self.player_index = 0
        players_remaining = len(self.players)
        while players_remaining > 0:
            print(f"{self.player.name} YOUR TURN MY GUY")
            print(f"{self.player.name}, is out: {self.player.isOut}")
            print("Players remaining: " + str(players_remaining))
            self.territory_selected = False
            if self.player.isOut is True:
                self.change_current_player()
            # if self.player.soldiers_in_hand < 1 and self.player.isOut is False:
            #     players_remaining -= 1
            #     self.player.isOut = True
            #     self.change_current_player()
            if self.player.soldiers_in_hand > 0:
                print(f"{self.player.name}, please select a territory that you own to add a soldier to:")
                edit_screen(f"{self.player.name}, please select a territory that you own to add a soldier to:")
                while not self.territory_selected:
                    territory = self.select_territory()
                    if territory.owner is self.player:
                        territory.soldierNumber += 1
                        self.player.soldiers_in_hand -= 1
                        print(f"{self.player.name} added a soldier to {territory.name}")
                        print(f"{self.player.name}, soldiers remaining: {self.player.soldiers_in_hand}")
                        self.territory_selected = True
                        if self.player.soldiers_in_hand <= 0:
                            players_remaining -= 1
                            self.player.isOut = True
                        edit_screen()
                        self.change_current_player()
                    elif territory.owner is not self.player:
                        edit_screen(f"{territory.name} is owned by {territory.owner.name}. You can not add soldiers to a territory you don't own")
                        print(
                            f"{territory.name} is owned by {territory.owner.name}. You can not add soldiers to a territory you don't own")
                        continue

    def receiving_placing_reinforcements(self):
        print(f"It is {self.player.name}'s turn. Stage 1: Receiving and Placing Reinforcements")
        self.player.soldiers_in_hand = self.player.reinforcement_calculator()
        print(f"{self.player.name}, you have been awarded {self.player.soldiers_in_hand} to place")
        edit_screen(f"{self.player.name}, you have been awarded {self.player.soldiers_in_hand} to place.\n please select one of your territories to add a reinforcement to: ")
        while self.player.soldiers_in_hand > 0:
            self.territory_selected = False
            print(f"{self.player.name}, please select one of your territories to add a reinforcement to: ")
            edit_screen(f"{self.player.name}, please select one of your territories to add a reinforcement to: ")
            while not self.territory_selected:
                territory = self.select_territory()
                if territory.owner is self.player:
                    territory.soldierNumber += 1
                    self.player.soldiers_in_hand -= 1
                    print(f"{self.player.name} added a soldier to {territory.name}")
                    print(f"{self.player.name}, soldiers remaining: {self.player.soldiers_in_hand}")
                    self.territory_selected = True
                    edit_screen()
                elif territory.owner is not self.player:
                    edit_screen(f"{territory.name} is owned by {territory.owner.name}. You cannot add soldiers to a territory you don't own")
                    print(f"{territory.name} is owned by {territory.owner.name}. You cannot add soldiers to a territory you don't own")

    def choose_attacking_territory(self):
        edit_screen(f"{self.player.name}, please select a territory you would like to attack with")
      #  print(f"{self.player.name}, please select a territory you would like to attack with. If you would like to end the combat stage, press End Combat")
        self.territory_selected = False
        while not self.territory_selected:
            territory = self.select_territory()
            if territory is None:
                return territory, 0
            if territory.owner is self.player:
                if territory.soldierNumber > 1:
                    if territory.check_neighbors(self.player):
                        print(f"Selected territory: {territory.name}")
                        num_soldiers_options = ["1 Soldier", "2 Soldiers", "3 Soldiers"]
                        if territory.soldierNumber == 2:
                            num_soldiers_options = ["1 Soldier"]
                        elif territory.soldierNumber == 3:
                            num_soldiers_options = ["1 Soldier", "2 Soldiers"]
                        num_soldiers_index = create_popup(screen, "Select number of soldiers to send:",
                                                          num_soldiers_options)
                        return territory, num_soldiers_index + 1  # Add 1 to convert index to number of soldiers
                    else:
                        edit_screen("There are no neighboring territories to attack")
                        print("There are no neighboring territories to attack")
                        continue
                else:
                    edit_screen("You cannot attack with a territory that has less than 2 soldiers")
                    print("You cannot attack with a territory that has less than 2 soldiers")
                    continue
            else:
                edit_screen("You must select one of your own territories to attack with")
                print("You must select one of your own territories to attack with")
                continue

    def choose_defending_territory(self, attacking_territory):
        edit_screen(f"{self.player.name}, please select an enemy territory you would like to attack")
        self.territory_selected = False
        while not self.territory_selected:
            territory = self.select_territory()
            if territory is None:
                return territory
            if territory in attacking_territory.neighbors:
                if territory.owner is not self.player:
                    return territory
                else:
                    edit_screen("You can't attack your own territory")
                    print("You can't attack your own territory")
                    continue
            else:
                edit_screen("You must attack a neighboring territory")
                print("You must attack a neighboring territory")
                continue

    def combat_stage(self):
        self.combat_stage_flag = True
        while self.combat_stage_flag:
            attacking_territory, num_attacking_soldiers = self.choose_attacking_territory()
            if attacking_territory is None:
                break
            defending_territory = self.choose_defending_territory(attacking_territory)
            if defending_territory is None:
                break
            print(f"New Battle: {self.player} is attacking {defending_territory.name} with {attacking_territory.name}")
            # Roll dice for attacker and defender
            attacker_dice = [random.randint(1, 6) for _ in
                             range(min(attacking_territory.soldierNumber - 1, num_attacking_soldiers))]
            defending_number = 2
            if defending_territory.soldierNumber == 1:
                defending_number = 1
            defender_dice = [random.randint(1, 6) for _ in range(min(defending_territory.soldierNumber, defending_number))]

            # Sort the dice rolls
            attacker_dice.sort(reverse=True)
            defender_dice.sort(reverse=True)

            print(f"{self.player.name} rolled: {attacker_dice}")
            print(f"{defending_territory.owner.name} rolled: {defender_dice}")

            attacker_losses, defender_losses = self.combat_losses(attacker_dice, defender_dice)
            attacking_territory.soldierNumber -= attacker_losses
            defending_territory.soldierNumber -= defender_losses
            if defending_territory.soldierNumber < 1:
                edit_screen()
                defending_territory.owner = attacking_territory.owner
                transfer_options = [str(i) for i in range(1, attacking_territory.soldierNumber)]
                transfer_result = create_popup(screen, "How many soldiers will you move over", transfer_options)
                defending_territory.soldierNumber = transfer_result + 1
                attacking_territory.soldierNumber -= transfer_result + 1
                edit_screen()
            edit_screen()

            # Draw attacker's dice
            for i, value in enumerate(attacker_dice):
                draw_dice(screen, value, DICE_OFFSET_X + i * DICE_SIZE, DICE_OFFSET_Y)

            # Draw defender's dice
            for i, value in enumerate(defender_dice):
                draw_dice(screen, value, width - DICE_OFFSET_X - (i + 1) * DICE_SIZE, DICE_OFFSET_Y)

            # Show combat results in a popup
            result_text = f"{self.player.name} rolled: {attacker_dice}\n{defending_territory.owner.name} rolled: {defender_dice}"
            result_options = ["Continue Fighting", "End Combat"]
            result_index = create_popup(screen, result_text, result_options,
                                        dice_results=attacker_dice + defender_dice)

            if result_index == 1:  # If "End Combat" is selected
                self.combat_stage_flag = False
                break

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



game = Game()
game.choosing_initial_territories()
game.initial_additional_soldier_addition()

while True:
    if len(game.player.territories) < 1:
        game.change_current_player()
        continue
    game.receiving_placing_reinforcements()
    game.combat_stage()
    game.change_current_player()
