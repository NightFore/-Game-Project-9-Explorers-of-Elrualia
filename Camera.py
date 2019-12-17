import pygame

class Camera:
    def __init__(self, width, height, WIDTH, HEIGHT):
        self.camera = pygame.Rect(0, 0, width, height)
        self.width = width
        self.height = height
        self.WIDTH = WIDTH
        self.HEIGHT = HEIGHT

    def apply(self, entity):
        return entity.rect.move(self.camera.topleft)

    def apply_rect(self, rect):
        return rect.move(self.camera.topleft)

    def update(self, target):
        x = -target.rect.centerx + int(self.WIDTH / 2)
        y = -target.rect.centery + int(self.HEIGHT / 2)

        # Limit to map size
        x = min(0, x)  # Left
        x = max(-(self.width - self.WIDTH), x)  # Right
        y = min(0, y)  # Top
        y = max(-(self.height - self.HEIGHT), y)  # Bottom
        self.camera = pygame.Rect(x, y, self.width, self.height)