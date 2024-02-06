import pygame
pygame.init()
pygame.font.init()


class Territory:
    def __init__(self, name, x, y, image_location):
        self.name = name
        self.soldierNumber = 0
        self.owner = None
        self.neighbors = []
        original_image = pygame.image.load(image_location)
        self.image = pygame.transform.scale(original_image, (100, 100))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = (x, y)

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, (255, 0, 0) if self.owner is None else self.owner.color,
                         (self.coordinates[0], self.coordinates[1], 50, 50))
        font = pygame.font.Font(None, 36)
        text = font.render(str(self.soldierNumber), True, (0, 0, 0))
        screen.blit(text, (self.coordinates[0] + 10, self.coordinates[1] + 10))

    def check_neighbors(self, player):
        flag = False
        for neighbor in self.neighbors:
            if neighbor.owner != player:
                flag = True
        return flag

    def draw_lines_to_neighbors(self, screen):
        for neighbor in self.neighbors:
            pygame.draw.line(screen, (0, 0, 0), self.coordinates, neighbor.coordinates, 2)
