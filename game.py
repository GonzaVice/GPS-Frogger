import pygame
from frog import Frog
from car import Car
from log import Log
from turtl import Turtle
from settings import TILE_SIZE
import os

class Game:
    def __init__(self, screen):
        self.game_state = 0
        # 0: Menu
        # 1: Level
        # 2: Leaderboard

        self.screen = screen
        self.frog = Frog(7 * TILE_SIZE, 14 * TILE_SIZE) # 16x16 pixeles

        self.cars = []
        self.cars.append(Car(5 * TILE_SIZE, 13 * TILE_SIZE, 1, 0, 'car1.png'))
        self.cars.append(Car(7 * TILE_SIZE, 12 * TILE_SIZE, 0.25, 1, 'car2.png'))
        self.cars.append(Car(9 * TILE_SIZE, 11 * TILE_SIZE, 1.5, 0, 'car3.png'))
        self.cars.append(Car(11 * TILE_SIZE, 10 * TILE_SIZE, 2, 1, 'car4.png'))
        self.cars.append(Car(11 * TILE_SIZE, 9 * TILE_SIZE, 0.75, 0, 'truck.png'))

        self.logs = []
        self.logs.append(Log(4 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log1.png'))
        self.logs.append(Log(5 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(6 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log3.png'))
        self.logs.append(Log(9 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log1.png'))
        self.logs.append(Log(10 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(11 * TILE_SIZE, 6 * TILE_SIZE, 1, 1, 'log3.png'))
        
        self.logs.append(Log(1 * TILE_SIZE, 5 * TILE_SIZE, 2, 1, 'log1.png'))
        self.logs.append(Log(2 * TILE_SIZE, 5 * TILE_SIZE, 2, 1, 'log2.png'))
        self.logs.append(Log(3 * TILE_SIZE, 5 * TILE_SIZE, 2, 1, 'log2.png'))
        self.logs.append(Log(4 * TILE_SIZE, 5 * TILE_SIZE, 2, 1, 'log2.png'))
        self.logs.append(Log(5 * TILE_SIZE, 5 * TILE_SIZE, 2, 1, 'log3.png'))

        self.logs.append(Log(1 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log1.png'))
        self.logs.append(Log(2 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(3 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(4 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log3.png'))
        self.logs.append(Log(7 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log1.png'))
        self.logs.append(Log(8 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(9 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log2.png'))
        self.logs.append(Log(10 * TILE_SIZE, 3 * TILE_SIZE, 1, 1, 'log3.png'))

        self.turtles = []
        self.turtles.append(Turtle(6 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(7 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(8 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(11 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(12 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(13 * TILE_SIZE, 7 * TILE_SIZE, 1, 0))
        
        self.turtles.append(Turtle(1 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(2 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(5 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(6 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(9 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))
        self.turtles.append(Turtle(10 * TILE_SIZE, 4 * TILE_SIZE, 1, 0))

        self.menu = pygame.image.load('assets/images/background/menu.png')
        self.background = pygame.image.load('assets/images/background/background.png')
        self.leaderboard = pygame.image.load('assets/images/background/leaderboard.png')

        # Puntuaciones
        self.score = 0
        self.high_score = 1000
        self.lives = 3

        # Cargar imágenes de letras y números
        self.font_images = self.load_font_images()

        # Cargar efectos de sonidos
        self.car_hit = pygame.mixer.Sound('assets/sounds/car_hit.mp3')
        self.log_sound = pygame.mixer.Sound('assets/sounds/log_landing.mp3')

        # Variable para verificar si la rana ya está sobre un tronco
        self.on_log = False

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
                # Aplica el color al carácter
                colored_image = self.tint_image(char_image, color)
                self.screen.blit(colored_image, (x + index * colored_image.get_width(), y))

    def check_collision(self, frog, cars, logs, turtles):
        for car in cars:
            if frog.rect.colliderect(car.rect):
                # Lógica cuando la rana es golpeada por un coche
                self.car_hit.play()
                frog.is_ground = True
                frog.rect.topleft = (7 * TILE_SIZE, 14 * TILE_SIZE)  # Posición inicial de la rana
                return  # Termina la función si la rana colisiona con un coche

        # Verificar si la rana está sobre un tronco
        is_on_log = False  # Para verificar si la rana está en un tronco en este cuadro
        new_log = None  # Guardar referencia al nuevo tronco

        for log in logs:
            if frog.rect.colliderect(log.rect):
                is_on_log = True  # La rana está en un tronco
                new_log = log  # Guardar el tronco actual

                # Si no estaba en un tronco antes, pero ahora sí, reproducir el sonido
                if not self.on_log or self.on_log != new_log:
                    self.log_sound.play()

                # Actualizar la posición de la rana basada en la velocidad del tronco
                frog.rect.x += log.speed
                break  # Sal del bucle si la rana colisiona con un tronco

        # Actualizar la variable de estado para saber en qué tronco está la rana
        self.on_log = new_log if is_on_log else None

        for turtle in turtles:
            if frog.rect.colliderect(turtle.rect):
                frog.rect.x -= turtle.speed  # Actualiza la posición de la rana basada en la velocidad de la tortuga
                break  # Sal del bucle si la rana colisiona con una tortuga


    def update(self):
        keys = pygame.key.get_pressed()

        if self.game_state == 0:
            if keys[pygame.K_s]:
                self.game_state = 1

        elif self.game_state == 1:
            self.check_collision(self.frog, self.cars, self.logs, self.turtles)
            self.frog.update()
            for car in self.cars:
                car.update()
            for log in self.logs:
                log.update()
            for turtle in self.turtles:
                turtle.update()

    def draw(self):
        if self.game_state == 0:
            self.screen.blit(self.menu, (0, 0))
            self.render_text(f'PRESIONA S PARA COMENZAR', 2*(int(TILE_SIZE/2)), 18*(int(TILE_SIZE/2)), (243, 208, 64))


        elif self.game_state == 1:
            self.screen.blit(self.background, (0, 0))

            # Dibujar troncos y autos
            for log in self.logs:
                log.draw(self.screen)
            for turtle in self.turtles:
                turtle.draw(self.screen)
            self.frog.draw(self.screen)
            for car in self.cars:
                car.draw(self.screen)

            # Dibujar puntaje, hi-score y vidas
            self.render_text(f'1-UP', 4*(int(TILE_SIZE/2)), 0*(int(TILE_SIZE/2)), (242, 242, 240))
            self.render_text(f'{self.score}', 4*(int(TILE_SIZE/2)), 1*(int(TILE_SIZE/2)), (189, 81, 90))
            self.render_text(f'HI-SCORE', 10*(int(TILE_SIZE/2)), 0*(int(TILE_SIZE/2)), (242, 242, 240))
            self.render_text(f'{self.high_score}', 10*(int(TILE_SIZE/2)), 1*(int(TILE_SIZE/2)), (189, 81, 90))
            self.render_text(f'TIME', 24*(int(TILE_SIZE/2)), 31*(int(TILE_SIZE/2)), (243, 208, 64))

