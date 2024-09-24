import pygame
from settings import TILE_SIZE

class Car:
    def __init__(self, x, y, speed, direction):
        self.image = pygame.image.load('assets/images/car/car_test.png')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = speed
        self.direction = direction # 0: Izquierda, 1: Derecha

    def update(self):
        # Dirección izquierda
        if self.direction <= 0:
            # Velocidad por cada frame
            self.rect.x -= self.speed
            # De derecha a izquierda
            if self.rect.x <= -TILE_SIZE:
                self.rect.x = 15 * TILE_SIZE
        # Dirección derecha
        else:
            # Velocidad por cada frame
            self.rect.x += self.speed
            # De derecha a izquierda
            if self.rect.x >= 15 * TILE_SIZE:
                self.rect.x = -TILE_SIZE

    def draw(self, surface):
        # Dibuja el vehiculo en la superficie proporcionada.
        surface.blit(self.image, self.rect)