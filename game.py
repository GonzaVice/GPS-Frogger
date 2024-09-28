import pygame
from frog import Frog
from car import Car
from log import Log
from turtl import Turtle
from settings import TILE_SIZE
import os

class Game:
    def __init__(self, screen):
        self.game_state = 0  # 0: Menu, 1: Level, 2-4: Death states
        self.timer = 0
        self.screen = screen
        self.frog = Frog(7 * TILE_SIZE, 14 * TILE_SIZE)

        # Configuración de autos
        car_configs = [
            (5, 13, 1, 0, 'car1.png'),
            (7, 12, 0.25, 1, 'car2.png'),
            (9, 11, 1.5, 0, 'car3.png'),
            (11, 10, 2, 1, 'car4.png'),
            (11, 9, 0.75, 0, 'truck.png')
        ]
        self.cars = [Car(x * TILE_SIZE, y * TILE_SIZE, speed, direction, image) for x, y, speed, direction, image in car_configs]

        # Configuración de troncos
        self.logs = []

        log_positions = [
            # Format: (start_x, y, length, type)
            (4, 6, 3, 1),   # Logs at row 6
            (9, 6, 3, 1),   # Logs at row 6
            (1, 5, 5, 2),   # Logs at row 5
            (1, 3, 4, 1),   # Logs at row 3
            (7, 3, 4, 1),   # Logs at row 3
        ]

        for start_x, y, length, log_type in log_positions:
            for i in range(length):
                if i == 0:
                    image = 'log_left.png'
                elif i == length - 1:
                    image = 'log_right.png'
                else:
                    image = 'log_middle.png'
                
                self.logs.append(Log((start_x + i) * TILE_SIZE, y * TILE_SIZE, log_type, 1, image))


        # Configuración de tortugas
        turtle_positions = [
            (6, 7), (7, 7), (8, 7), (11, 7), (12, 7), (13, 7),
            (1, 4), (2, 4), (5, 4), (6, 4), (9, 4), (10, 4)
        ]
        self.turtles = [Turtle(x * TILE_SIZE, y * TILE_SIZE, 1, 0) for x, y in turtle_positions]

        # Cargar recursos gráficos y de sonido
        self.menu = pygame.image.load('assets/images/background/menu.png')
        self.background = pygame.image.load('assets/images/background/background.png')
        self.leaderboard = pygame.image.load('assets/images/background/leaderboard.png')
        self.font_images = self.load_font_images()
        self.car_hit = pygame.mixer.Sound('assets/sounds/car_hit.mp3')

        # Puntuaciones y vidas
        self.score = 0
        self.high_score = 1000
        self.lives = 3

    def load_font_images(self):
        """ Carga las imágenes de las letras y números desde la carpeta de assets. """
        font_images = {}
        font_path = 'assets/font/'
        for char in '-0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ':
            image_path = os.path.join(font_path, f'{char}.png')
            font_images[char] = pygame.image.load(image_path)
        return font_images

    def tint_image(self, image, color):
        """ Aplica un color de tinte a la imagen. """
        tinted_image = image.copy()
        tinted_image.fill(color, special_flags=pygame.BLEND_RGBA_MULT)
        return tinted_image

    def render_text(self, text, x, y, color=(255, 255, 255)):
        """ Renderiza el texto usando las imágenes de las letras y números, aplicando un tinte de color. """
        for index, char in enumerate(text):
            if char in self.font_images:
                char_image = self.font_images[char]
                colored_image = self.tint_image(char_image, color)
                self.screen.blit(colored_image, (x + index * colored_image.get_width(), y))

    def check_collision(self, frog):
        if self.game_state == 1:
            for car in self.cars:
                if frog.rect.colliderect(car.rect):
                    self.game_state = 2  # Muerte por golpe con coche
                    return

            for log in self.logs:
                if frog.rect.colliderect(log.rect):
                    frog.rect.x += log.speed
                    return

            for turtle in self.turtles:
                if frog.rect.colliderect(turtle.rect):
                    frog.rect.x -= turtle.speed
                    return

    def update(self):
        keys = pygame.key.get_pressed()

        if self.game_state == 0 and keys[pygame.K_s]:
            self.game_state = 1

        elif self.game_state in [1, 2, 3, 4]:
            self.check_collision(self.frog)
            for car in self.cars:
                car.update()
            for log in self.logs:
                log.update()
            for turtle in self.turtles:
                turtle.update()

            if self.game_state == 1:
                self.frog.update()
            elif self.game_state in [2, 3, 4]:
                if self.timer >= 30:
                    if self.game_state in [2, 3]:
                        self.timer = 0
                        self.game_state = 4
                    elif self.game_state == 4:
                        self.reset_frog()
                else:
                    self.timer += 1
                    if self.game_state == 2:
                        self.frog.image = self.frog.images['slam']
                    elif self.game_state == 3:
                        self.frog.image = self.frog.images['drown']
                    elif self.game_state == 4:
                        self.frog.image = self.frog.images['death']

    def reset_frog(self):
        self.frog.rect.topleft = (7 * TILE_SIZE, 14 * TILE_SIZE)
        self.game_state = 1
        self.timer = 0
        self.car_hit.play()
        self.frog.is_ground = True
        self.frog.image = self.frog.images['ground_up']

    def draw(self):
        if self.game_state == 0:
            self.screen.blit(self.menu, (0, 0))
            self.render_text('PRESIONA S PARA COMENZAR', 2 * (TILE_SIZE // 2), 18 * (TILE_SIZE // 2), (243, 208, 64))
        elif self.game_state in [1, 2, 3, 4]:
            self.screen.blit(self.background, (0, 0))
            for log in self.logs:
                log.draw(self.screen)
            for turtle in self.turtles:
                turtle.draw(self.screen)
            self.frog.draw(self.screen)
            for car in self.cars:
                car.draw(self.screen)

            # Dibujar puntaje, hi-score y vidas
            self.render_text('1-UP', 4 * (TILE_SIZE // 2), 0, (242, 242, 240))
            self.render_text(str(self.score), 4 * (TILE_SIZE // 2), TILE_SIZE // 2, (189, 81, 90))
            self.render_text('HI-SCORE', 10 * (TILE_SIZE // 2), 0, (242, 242, 240))
            self.render_text(str(self.high_score), 10 * (TILE_SIZE // 2), TILE_SIZE // 2, (189, 81, 90))
            self.render_text('TIME', 24 * (TILE_SIZE // 2), 31 * (TILE_SIZE // 2), (243, 208, 64))
