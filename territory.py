import pygame
pygame.init()
pygame.font.init()


class Territory:
    def __init__(self, name, lower_name, continent, x, y, image_location):
        self.name = name
        self.lower_name = lower_name
        self.continent = continent
        self.soldierNumber = 0
        self.owner = None
        self.neighbors = []
        original_image = pygame.image.load(image_location)
        self.image = pygame.transform.scale(original_image, (50, 50))
        self.rect = self.image.get_rect(topleft=(x, y))
        self.coordinates = (x, y)

    def click(self, mouse_pos):
        return self.rect.collidepoint(mouse_pos)

    def draw(self, screen, color=(255, 0, 0)):
        screen.blit(self.image, self.rect)
        pygame.draw.rect(screen, color,
                         (self.coordinates[0], self.coordinates[1], 25, 25))
        font = pygame.font.Font(None, 20)
        text = font.render(str(self.soldierNumber), True, (0, 0, 0))
        screen.blit(text, (self.coordinates[0] + 10, self.coordinates[1] + 10))

    def check_neighbors(self, player):
        flag = False
        for neighbor in self.neighbors:
            if neighbor.owner != player:
                flag = True
        return flag

    def check_neighbors_for_player(self, player):
        flag = False
        for neighbor in self.neighbors:
            if neighbor.owner == player:
                flag = True
        return flag

    def neighbor_list_player(self, player):
        neighbor_list = []
        for neighbor in self.neighbors:
            if neighbor.owner == player:
                neighbor_list.append(neighbor)
        return neighbor_list

    def draw_lines_to_neighbors(self, screen):
        for neighbor in self.neighbors:
            pygame.draw.line(screen, (0, 0, 0), self.coordinates, neighbor.coordinates, 2)
