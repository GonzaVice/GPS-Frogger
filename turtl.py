import pygame
from settings import TILE_SIZE

class Turtle:
    def __init__(self, x, y, speed, direction):
        self.images = [
            pygame.image.load('assets/images/turtle/turtle1.png'),
            pygame.image.load('assets/images/turtle/turtle2.png'),
            pygame.image.load('assets/images/turtle/turtle3.png')
        ]
        self.current_image_index = 0
        self.image = self.images[self.current_image_index]
        
        self.rect = self.image.get_rect(topleft=(x, y))
        self.x_float = float(x)  # Mantiene la posición en decimal
        self.speed = float(speed)
        self.direction = direction # 0: Izquierda, 1: Derecha

        self.frame_counter = 0

    def update(self):
        # Animación de la tortuga cada 20 frames
        self.frame_counter += 1
        if self.frame_counter >= 20:
            self.frame_counter = 0
            self.current_image_index = (self.current_image_index + 1) % len(self.images)
            self.image = self.images[self.current_image_index]
        
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
        # Dibuja el tronco en la superficie proporcionada.
        surface.blit(self.image, self.rect)