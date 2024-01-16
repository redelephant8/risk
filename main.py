import pygame
import sys

from territory import Territory
from board import Board

width, height = 800, 600
screen = pygame.display.set_mode((width, height))
pygame.display.set_caption("Risk")


board = Board()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()


        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mouse_pos = pygame.mouse.get_pos()

            # Check if any territory is clicked
            for territory_name, territory in board.pieces.items():
                if territory.click(mouse_pos):
                    print(f"Number of soldiers on {territory_name}: {territory.soldierNumber}")

    # Clear the screen
    screen.fill((255, 255, 255))  # Fill with white background

    # Draw the butterfly
    board.pieces["qatar"].draw(screen)
    board.pieces["afghanistan"].draw(screen)
    board.pieces["saudi_arabia"].draw(screen)

    # Update the display
    pygame.display.flip()

    # Control the frame rate
    pygame.time.Clock().tick(60)
