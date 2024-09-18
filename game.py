import pygame
from frog import Frog
from settings import TILE_SIZE

class Game:
    def __init__(self, screen):
        self.screen = screen
        self.frog = Frog(7 * TILE_SIZE, 14 * TILE_SIZE)
        # self.keys = pygame.key.get_pressed()

    def update(self):
        self.frog.update()

    def draw(self):
        self.screen.fill((0, 0, 0))
        self.frog.draw(self.screen)