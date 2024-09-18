import pygame

class Frog:
    def __init__(self, x, y):
        self.image = pygame.image.load('assets/images/frog/frog_test.png')
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 0 # 0 = up, 1 = down, 2 = left, 3 = right
        self.is_ground = True
        self.jump_speed = [3, 3, 2, 1, 2, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0]
        self.jump_speed_index = 0 # Recorre la lista

    def start_jump(self, direction):
        # Inicia el salto al presionar una tecla de dirección.
        self.direction = direction
        self.is_ground = False
        self.jump_speed_index = 0

    def apply_jump(self):
        # Aplica el movimiento según la dirección y la velocidad de salto.
        movement = self.jump_speed[self.jump_speed_index]
        
        if self.direction == 0:  # UP
            self.rect.y -= movement
        elif self.direction == 1:  # DOWN
            self.rect.y += movement
        elif self.direction == 2:  # LEFT
            self.rect.x -= movement
        elif self.direction == 3:  # RIGHT
            self.rect.x += movement

        self.jump_speed_index += 1

        # Verifica si el salto ha terminado
        if self.jump_speed_index >= len(self.jump_speed):
            self.is_ground = True
            self.jump_speed_index = 0

    def update(self):
        # Actualiza el estado de la rana según las teclas presionadas.
        keys = pygame.key.get_pressed()

        if self.is_ground:
            if keys[pygame.K_UP]:
                #print(f'x = {self.rect.x}, y = {self.rect.y}')
                self.start_jump(0)  # UP
            elif keys[pygame.K_DOWN]:
                #print(f'x = {self.rect.x}, y = {self.rect.y}')
                self.start_jump(1)  # DOWN
            elif keys[pygame.K_LEFT]:
                #print(f'x = {self.rect.x}, y = {self.rect.y}')
                self.start_jump(2)  # LEFT
            elif keys[pygame.K_RIGHT]:
                #print(f'x = {self.rect.x}, y = {self.rect.y}')
                self.start_jump(3)  # RIGHT
        else:
            self.apply_jump()
    
    def draw(self, surface):
        # Dibuja la rana en la superficie proporcionada.
        surface.blit(self.image, self.rect)