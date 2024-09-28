import pygame

class Frog:
    def __init__(self, x, y):
        # Cargar las imágenes de la rana según su estado y dirección
        self.images = {
            'ground_up': pygame.image.load('assets/images/frog/frogger_ground_up.png'),
            'ground_down': pygame.image.load('assets/images/frog/frogger_ground_down.png'),
            'ground_left': pygame.image.load('assets/images/frog/frogger_ground_left.png'),
            'ground_right': pygame.image.load('assets/images/frog/frogger_ground_right.png'),
            'jump_up': pygame.image.load('assets/images/frog/frogger_jump_up.png'),
            'jump_down': pygame.image.load('assets/images/frog/frogger_jump_down.png'),
            'jump_left': pygame.image.load('assets/images/frog/frogger_jump_left.png'),
            'jump_right': pygame.image.load('assets/images/frog/frogger_jump_right.png'),
        }

        self.jump_sound = pygame.mixer.Sound('assets/sounds/frog_jump.mp3')

        # La imagen inicial es cuando está en el suelo mirando hacia arriba
        self.image = self.images['ground_up']
        self.rect = self.image.get_rect(topleft=(x, y))
        self.direction = 0  # 0 = up, 1 = down, 2 = left, 3 = right
        self.is_ground = True
        self.jump_speed = [3, 3, 2, 1, 2, 1, 0, 1, 1, 0, 1, 0, 0, 1, 0, 0]
        self.jump_speed_index = 0

    def start_jump(self, direction):
        self.direction = direction
        self.is_ground = False
        self.jump_speed_index = 0
        self.jump_sound.play()
        # Cambiar la imagen según la dirección del salto
        if self.direction == 0:
            self.image = self.images['jump_up']
        elif self.direction == 1:
            self.image = self.images['jump_down']
        elif self.direction == 2:
            self.image = self.images['jump_left']
        elif self.direction == 3:
            self.image = self.images['jump_right']

    def apply_jump(self):
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

        if self.jump_speed_index >= len(self.jump_speed):
            self.is_ground = True
            self.jump_speed_index = 0
            # Cambiar la imagen a la correspondiente en el suelo
            if self.direction == 0:
                self.image = self.images['ground_up']
            elif self.direction == 1:
                self.image = self.images['ground_down']
            elif self.direction == 2:
                self.image = self.images['ground_left']
            elif self.direction == 3:
                self.image = self.images['ground_right']

    def update(self):
        keys = pygame.key.get_pressed()

        if self.is_ground:
            if keys[pygame.K_UP]:
                self.start_jump(0)
            elif keys[pygame.K_DOWN]:
                self.start_jump(1)
            elif keys[pygame.K_LEFT]:
                self.start_jump(2)
            elif keys[pygame.K_RIGHT]:
                self.start_jump(3)
        else:
            self.apply_jump()

    def draw(self, surface):
        surface.blit(self.image, self.rect)