import pygame
import sys

from territory import Territory
from player import Player
from board import Board

game_state = 0
width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Risk")



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

    game.choosing_initial_territories()


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if any territory is clicked
            for territory_name, territory in game.board.territories.items():
                if territory.click(mouse_pos):
                    print(f"Number of soldiers on {territory_name}: {territory.soldierNumber}")

    # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white background

    # Draw the butterfly
    game.board.territories["qatar"].draw(screen)
    game.board.territories["afghanistan"].draw(screen)
    game.board.territories["saudi_arabia"].draw(screen)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
