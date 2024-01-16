import pygame

class Territory:
    def __init__(self, name, x, y, image_location):
        self.name = name
        self.soldierNumber = 0
        self.owner = None
        self.neighbors = []
        original_image = pygame.image.load(image_location)
        self.image = pygame.transform.scale(original_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))

    def draw(self, screen):
        screen.blit(self.image, self.rect)

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)
