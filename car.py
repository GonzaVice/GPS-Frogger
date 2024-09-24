import pygame
from settings import TILE_SIZE

class Car:
    def __init__(self, x, y, speed, direction):
        self.image = pygame.image.load('assets/images/car/car_test.png')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_float = float(x)  # Mantiene la posición en decimal
        self.speed = float(speed)
        self.direction = direction # 0: Izquierda, 1: Derecha

    def update(self):
        # Dirección izquierda
        if self.direction == 0:
            # Velocidad por cada frame
            self.x_float -= self.speed
            # Si sale por el lado izquierdo, reaparece por la derecha
            if self.rect.x <= -TILE_SIZE:
                self.x_float = 15 * TILE_SIZE
        # Dirección derecha
        elif self.direction == 1:
            # Velocidad por cada frame
            self.x_float += self.speed
            # Si sale por el lado derecho, reaparece por la izquierda
            if self.rect.x >= 15 * TILE_SIZE:
                self.x_float = -TILE_SIZE
        # Actualiza la posición del rectángulo (en entero)
        self.rect.x = int(self.x_float)

    def draw(self, surface):
        # Dibuja el vehiculo en la superficie proporcionada.
        surface.blit(self.image, self.rect)