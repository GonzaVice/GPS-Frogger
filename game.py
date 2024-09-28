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
        self.selected_option = 0 # 0: Game Start, 1: Leaderboard, 2: Credits
        self.key_pressed = False  # Bandera para rastrear si una tecla ya está presionada

        # Configuración de autos
        car_configs = [
            # Format: (x, y, speed, direction)
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
            # Format: (x, y, length, speed)
            (4, 6, 3, 1),   # Logs at row 6
            (9, 6, 3, 1),   # Logs at row 6
            (1, 5, 5, 2),   # Logs at row 5
            (1, 3, 4, 1),   # Logs at row 3
            (7, 3, 4, 1),   # Logs at row 3
        ]

        for start_x, y, length, speed in log_positions:
            for i in range(length):
                if i == 0:
                    image = 'log_left.png'
                elif i == length - 1:
                    image = 'log_right.png'
                else:
                    image = 'log_middle.png'
                
                self.logs.append(Log((start_x + i) * TILE_SIZE, y * TILE_SIZE, speed, 1, image))


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
        self.leaderboard_scores = [1500, 1200, 1000, 800, 500]  # Cinco puntajes máximos


        # Cargar imágenes de letras y números
        self.font_images = self.load_font_images()

        # Cargar efectos de sonidos
        self.car_hit = pygame.mixer.Sound('assets/sounds/car_hit.mp3')
        self.log_sound = pygame.mixer.Sound('assets/sounds/log_landing.mp3')
        self.turtle_sound = pygame.mixer.Sound('assets/sounds/turtle_landing.mp3')

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
                colored_image = self.tint_image(char_image, color)
                self.screen.blit(colored_image, (x + index * colored_image.get_width(), y))

    def check_collision(self, frog):
        if self.game_state == 1:
            # Verificar colisión con los coches
            for car in self.cars:
                if frog.rect.colliderect(car.rect):
                    self.car_hit.play()
                    self.game_state = 2  # Muerte por golpe con coche
                    self.timer = 0  # Reiniciar el temporizador para la animación de muerte
                    return

        # Verificar si la rana está sobre un tronco
        is_on_log = False  # Para verificar si la rana está en un tronco en este cuadro
        new_log = None  # Guardar referencia al nuevo tronco

        for log in self.logs:
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

        # Verificar si la rana está sobre una tortuga
        is_on_turtle = False  # Para verificar si la rana está en una tortuga en este cuadro
        for turtle in self.turtles:
            if frog.rect.colliderect(turtle.rect):
                is_on_turtle = True  # La rana está en una tortuga

                # Si no estaba en una tortuga antes, pero ahora sí, reproducir el sonido
                if not self.on_turtle:
                    self.turtle_sound.play()

                # Actualizar la posición de la rana basada en la velocidad de la tortuga
                frog.rect.x -= turtle.speed
                break  # Sal del bucle si la rana colisiona con una tortuga

        # Actualizar la variable de estado de las tortugas
        self.on_turtle = is_on_turtle

    def reset_frog(self):
        self.frog.rect.topleft = (7 * TILE_SIZE, 14 * TILE_SIZE)
        self.game_state = 1
        self.timer = 0
        self.frog.is_ground = True
        self.frog.image = self.frog.images['ground_up']

    def handle_menu_input(self):
        """Maneja la entrada del usuario para el menú."""
        keys = pygame.key.get_pressed()
        
        if not self.key_pressed:
            if keys[pygame.K_DOWN]:
                self.selected_option = (self.selected_option + 1) % 3
                self.key_pressed = True
            elif keys[pygame.K_UP]:
                self.selected_option = (self.selected_option - 1) % 3
                self.key_pressed = True
            elif keys[pygame.K_s] or keys[pygame.K_RETURN]:
                if self.selected_option == 0:
                    self.game_state = 1  # Start Game
                elif self.selected_option == 1:
                    self.game_state = 5  # Leaderboard
                elif self.selected_option == 2:
                    self.game_state = 6  # Credits
                self.key_pressed = True

        # Si ninguna de las teclas está presionada, restablecemos la bandera
        if not keys[pygame.K_DOWN] and not keys[pygame.K_UP] and not keys[pygame.K_s] and not keys[pygame.K_RETURN]:
            self.key_pressed = False

    def handle_leaderboard_input(self):
        """Maneja la entrada del usuario para el leaderboard."""
        keys = pygame.key.get_pressed()
        
        if not self.key_pressed:
            if keys[pygame.K_s] or keys[pygame.K_RETURN]:
                self.game_state = 0  # Regresar al menú principal
                self.key_pressed = True

        if not keys[pygame.K_s] and not keys[pygame.K_RETURN]:
            self.key_pressed = False

    def handle_credits_input(self):
        """Maneja la entrada del usuario para los créditos."""
        keys = pygame.key.get_pressed()
        
        if not self.key_pressed:
            if keys[pygame.K_s] or keys[pygame.K_RETURN]:
                self.game_state = 0  # Regresar al menú principal
                self.key_pressed = True

        if not keys[pygame.K_s] and not keys[pygame.K_RETURN]:
            self.key_pressed = False

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if self.game_state == 0:
            self.handle_menu_input()
        elif self.game_state == 5:
            self.handle_leaderboard_input()
        elif self.game_state == 6:
            self.handle_credits_input()

        if self.game_state == 1:
            # Juego normal, actualizar colisiones y objetos en movimiento
            self.check_collision(self.frog)
            for car in self.cars:
                car.update()
            for log in self.logs:
                log.update()
            for turtle in self.turtles:
                turtle.update()

            self.frog.update()

        elif self.game_state in [2, 3, 4]:
            # Manejar la animación de la muerte y la transición a la pantalla de reaparición
            if self.timer < 30:
                self.timer += 1
                if self.game_state == 2:
                    self.frog.image = self.frog.images['slam']  # Imagen de golpe por coche
                elif self.game_state == 3:
                    self.frog.image = self.frog.images['drown']  # Imagen de ahogamiento
                elif self.game_state == 4:
                    self.frog.image = self.frog.images['death']  # Imagen de muerte final
            else:
                # Después de 30 cuadros, resetear la rana y reanudar el juego
                if self.game_state in [2, 3]:
                    self.timer = 0
                    self.game_state = 4
                elif self.game_state == 4:
                    self.reset_frog()

    def draw(self):
        if self.game_state == 0:
            self.screen.blit(self.menu, (0, 0))
            options = ['GAME START', 'LEADERBOARD', 'CREDITS']
            for i, option in enumerate(options):
                color = (243, 208, 64) if i == self.selected_option else (255, 255, 255)
                self.render_text(option, 2 * (TILE_SIZE // 2), (18 + i) * (TILE_SIZE // 2) + (4 * i), color)

        elif self.game_state == 5:
            self.screen.blit(self.leaderboard, (0, 0))
            self.render_text('HI-SCORES:', 2 * (TILE_SIZE // 2), 2 * TILE_SIZE, (243, 208, 64))
            for i in range(5):
                self.render_text(f'{i + 1}. SCORE: {self.high_score - (i * 100)}', 2 * (TILE_SIZE // 2), (4 + i) * TILE_SIZE, (242, 242, 240))
            self.render_text('PRESIONA S PARA VOLVER', 2 * (TILE_SIZE // 2), 18 * (TILE_SIZE // 2), (243, 208, 64))

        elif self.game_state == 6:
            self.screen.blit(self.leaderboard, (0, 0))
            credits = ['GONZALO VICENTE', 'JOSE MORALES', 'MATIAS MUNOZ', 'JOSE QUEIROLO']
            self.render_text('CREDITS:', 2 * (TILE_SIZE // 2), 2 * TILE_SIZE, (243, 208, 64))
            for i, name in enumerate(credits):
                self.render_text(name, 2 * (TILE_SIZE // 2), (4 + i) * TILE_SIZE, (242, 242, 240))
            self.render_text('PRESIONA S PARA VOLVER', 2 * (TILE_SIZE // 2), 18 * (TILE_SIZE // 2), (243, 208, 64))

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


