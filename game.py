import pygame
from frog import Frog
from car import Car
from log import Log
from turtl import Turtle
from level import level_configs
from settings import TILE_SIZE, SCORE_PER_TILE
import os

class Game:
    def __init__(self, screen):
        self.game_state = 0  # 0: Menu, 1: Level, 2-4: Death states
        self.timer = 0
        self.screen = screen
        self.frog = Frog(7 * TILE_SIZE, 14 * TILE_SIZE)
        self.selected_option = 0 # 0: Game Start, 1: Leaderboard, 2: Credits
        self.key_pressed = False  # Bandera para rastrear si una tecla ya está presionada
        self.game_over = False  # Variable para ver si el juego terminó
        self.game_over_option = 0  # 0: Try Again, 1: Back to Menu
        self.paused = False  # Indica si el juego está pausado
        self.finished_slots = [False, False, False, False, False]

        self.time_limit = 60  # 60 segundos para completar la jugada
        self.time_remaining = self.time_limit  # Inicialmente igual al límite
        self.time_bar_width = 6*TILE_SIZE  # Ancho de la barra de tiempo
        self.time_bar_height = 6  # Altura de la barra
        self.time_bar_x = 12*(TILE_SIZE//2)  # Posición X de la barra
        self.time_bar_y = 31*(TILE_SIZE//2)  # Posición Y de la barra
        self.time_last_update = pygame.time.get_ticks()  # Última vez que se actualizó el tiempo

        # Varibales para las puntaciones
        self.frog_previous_position = self.frog.rect.y
        self.checked_for_high_score = False

        self.current_level = 0  # Nivel inicial
        self.level_configs = level_configs
        self.init_level()

        # Cargar recursos gráficos y de sonido
        self.menu = pygame.image.load('assets/images/background/menu.png')
        self.background = pygame.image.load('assets/images/background/background.png')
        self.leaderboard = pygame.image.load('assets/images/background/leaderboard.png')
        self.font_images = self.load_font_images()
        self.car_hit = pygame.mixer.Sound('assets/sounds/car_hit.mp3')
        self.game_over_sound = pygame.mixer.Sound('assets/sounds/death_sound.mp3')

        # Puntuaciones y vidas
        self.score = 0
        self.high_score = 1000
        self.lives = 3
        self.leaderboard_scores = [self.high_score]

        # Cargar imágenes de letras y números
        self.font_images = self.load_font_images()

        # Cargar efectos de sonidos
        self.car_hit = pygame.mixer.Sound('assets/sounds/car_hit.mp3')
        self.log_sound = pygame.mixer.Sound('assets/sounds/log_landing.mp3')
        self.turtle_sound = pygame.mixer.Sound('assets/sounds/turtle_landing.mp3')

        # Variable para verificar si la rana ya está sobre un tronco
        self.on_log = False

        if self.game_over:
            self.paused = True  # Pausa el juego

    def init_level(self):
        # Si llega al ultimo nivel, se repite
        current_level_index = min(self.current_level, len(self.level_configs)-1)
        """Inicializa los objetos del nivel actual."""
        config = self.level_configs[current_level_index]

        # Configuración de autos
        self.cars = [Car(x * TILE_SIZE, y * TILE_SIZE, speed, direction, image) for x, y, speed, direction, image in config["cars"]]

        # Configuración de troncos
        self.logs = []
        for start_x, y, length, speed in config["logs"]:
            for i in range(length):
                if i == 0:
                    image = 'log_left.png'
                elif i == length - 1:
                    image = 'log_right.png'
                else:
                    image = 'log_middle.png'
                self.logs.append(Log((start_x + i) * TILE_SIZE, y * TILE_SIZE, speed, 1, image))

        # Configuración de tortugas
        self.turtles = [Turtle(x * TILE_SIZE, y * TILE_SIZE, 1, 0) for x, y in config["turtles"]]

    def next_level(self):
        """Avanza al siguiente nivel."""
        self.current_level += 1
        self.init_level()  # Re-inicializa los objetos con el nuevo nivel

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
                    self.lives -= 1  # Resta una vida al chocar con un coche
                    if self.lives > 0:
                        self.game_state = 2  # Muerte por golpe con coche
                    else:
                        self.game_over = True  # Si las vidas se acaban, se activa el Game Over
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

                if self.frog.is_ground or (not self.frog.is_ground and self.frog.direction in [2, 3]):
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

                
                if self.frog.is_ground or (not self.frog.is_ground and self.frog.direction in [2, 3]):
                    # Actualizar la posición de la rana basada en la velocidad de la tortuga
                    frog.rect.x -= turtle.speed
                break  # Sal del bucle si la rana colisiona con una tortuga

        # Actualizar la variable de estado de las tortugas
        self.on_turtle = is_on_turtle

        # Verificar si la rana cae al agua
        if frog.rect.y < 8 * TILE_SIZE and self.frog.is_ground and not (is_on_log or is_on_turtle):
            # La rana está en la zona del río y no está sobre un tronco ni una tortuga
            self.lives -= 1  # Resta una vida si la rana cae al agua
            if self.lives > 0:
                self.game_state = 3  # Muerte por ahogamiento
            else:
                self.game_over = True  # Si las vidas se acaban, se activa el Game Over
            self.timer = 0  # Reiniciar el temporizador para la animación de muerte

    def reset_frog(self):
        self.frog.rect.topleft = (7 * TILE_SIZE, 14 * TILE_SIZE)
        self.game_state = 1
        self.timer = 0
        self.frog.is_ground = True
        self.frog.image = self.frog.images['ground_up']
        self.time_remaining = self.time_limit  # Reiniciar el tiempo
        self.time_last_update = pygame.time.get_ticks()  # Reiniciar la última actualización del tiempo

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

    def handle_game_over_input(self):
        """Maneja la entrada del usuario en la pantalla de Game Over."""
        keys = pygame.key.get_pressed()

        if keys[pygame.K_r]:  # Volver a intentar
            self.reset_game(1)
        elif keys[pygame.K_m]:  # Volver al menú
            self.reset_game(0)
            self.game_state = 0

    def reset_game(self, state):
        self.lives = 3
        self.score = 0
        self.game_state = state
        self.game_over = False
        self.paused = False  # Despausar el juego
        self.current_level = 0
        self.finished_slots = [False] * len(self.finished_slots)
        self.init_level()
        self.reset_frog()
        self.reset_previous_y_frog_position()
        self.checked_for_high_score = False

    def check_y_frog_position(self):
        if self.frog_previous_position > self.frog.rect.y:
            self.score += SCORE_PER_TILE
            self.frog_previous_position = self.frog.rect.y
    
    def reset_previous_y_frog_position(self):
        self.frog_previous_position = self.frog.rect.y

    def check_for_high_score(self):
        """ Verifica si la puntuación actual es mayor que la puntuación más alta. """
        if len(self.leaderboard_scores) < 5:
            self.leaderboard_scores.append(self.score)
            self.leaderboard_scores.sort(reverse=True)
            self.high_score = self.leaderboard_scores[0]
            return 
        
        copy_leaderboard_scores = self.leaderboard_scores.copy()
        is_higher_than_any_highscore = list(map(lambda x: self.score > x,copy_leaderboard_scores))
        print(is_higher_than_any_highscore)

        if any(is_higher_than_any_highscore):
            idx_leaderboard = is_higher_than_any_highscore.index(True)
            self.leaderboard_scores.insert(idx_leaderboard, self.score)
            self.leaderboard_scores.pop()
            self.leaderboard_scores.sort(reverse=True)
            self.high_score = self.leaderboard_scores[0]

    def update(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                exit()

        if self.game_over:
            ###############
            # Aquí se debe llamar a la función para verificar si la puntuación actual es mayor que la puntuación más alta
            if not self.checked_for_high_score:
                self.check_for_high_score()
                self.checked_for_high_score = True
            self.handle_game_over_input()  # Manejar la entrada para el Game Over
            return  # Detener el resto de las actualizaciones cuando el juego ha terminado

        if self.game_state == 0:
            self.handle_menu_input()
        elif self.game_state == 5:
            self.handle_leaderboard_input()
        elif self.game_state == 6:
            self.handle_credits_input()

        if self.game_state == 1:

            # Actualizar el tiempo restante
            current_time = pygame.time.get_ticks()
            if current_time - self.time_last_update >= 1000:  # Actualizar cada segundo
                self.time_remaining -= 1
                self.time_last_update = current_time

            # Verificar si el tiempo se ha acabado
            if self.time_remaining <= 0:
                self.game_state = 4  # Estado de "muerte por tiempo agotado"
                self.lives -= 1
                self.game_over_sound.play()
                self.timer = 0

            # Juego normal, actualizar colisiones y objetos en movimiento
            self.check_collision(self.frog)
            for car in self.cars:
                car.update()
            for log in self.logs:
                log.update()
            for turtle in self.turtles:
                turtle.update()

            self.frog.update()

            #check for the frog position
            self.check_y_frog_position()

            # Llegada del sapo
            if self.frog.rect[1] == 32 and self.frog.rect[0] >= 0 and self.frog.rect[0] <= 16:
                self.frog.rect[0] = 8
                self.finished_slots[0] = True
                self.reset_frog()
                self.score+=200
                self.reset_previous_y_frog_position()
            elif self.frog.rect[1] == 32 and self.frog.rect[0] >= 48 and self.frog.rect[0] <= 64:
                self.frog.rect[0] = 56
                self.finished_slots[1] = True
                self.reset_frog()
                self.score+=200
                self.reset_previous_y_frog_position()

            elif self.frog.rect[1] == 32 and self.frog.rect[0] >= 96 and self.frog.rect[0] <= 112:
                self.frog.rect[0] = 104
                self.finished_slots[2] = True
                self.reset_frog()
                self.score+=200
                self.reset_previous_y_frog_position()

            elif self.frog.rect[1] == 32 and self.frog.rect[0] >= 144 and self.frog.rect[0] <= 160:
                self.frog.rect[0] = 152
                self.finished_slots[3] = True
                self.reset_frog()
                self.score+=200
                self.reset_previous_y_frog_position()

            elif self.frog.rect[1] == 32 and self.frog.rect[0] >= 192 and self.frog.rect[0] <= 208:
                self.frog.rect[0] = 200
                self.finished_slots[4] = True
                self.reset_frog()
                self.score+=200
                self.reset_previous_y_frog_position()
            
            # Verificar si todos los slots están completos
            if all(self.finished_slots):
                self.finished_slots = [False] * len(self.finished_slots)
                self.next_level()  # Avanza al siguiente nivel
                self.reset_frog()  # Reinicia la rana para el nuevo nivel


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
                    self.game_over_sound.play()
                    self.timer = 0
                    self.game_state = 4
                elif self.game_state == 4:
                    self.reset_frog()
                    self.time_remaining = self.time_limit  # Reiniciar el tiempo
                    self.reset_previous_y_frog_position()

    def draw(self):
        if self.game_state == 0:
            self.screen.blit(self.menu, (0, 0))
            options = ['GAME START', 'LEADERBOARD', 'CREDITS']
            self.render_text('USA LAS FLECHAS PARA', 2 * (TILE_SIZE // 2), 23 * (TILE_SIZE // 2), (189, 81, 90))
            self.render_text('MOVERSE', 2 * (TILE_SIZE // 2), 24 * (TILE_SIZE // 2), (189, 81, 90))
            self.render_text('PRESIONA S O ENTER PARA', 2 * (TILE_SIZE // 2), 26 * (TILE_SIZE // 2), (189, 81, 90))
            self.render_text('SELECCIONAR UNA OPCION', 2 * (TILE_SIZE // 2), 27 * (TILE_SIZE // 2), (189, 81, 90))
            for i, option in enumerate(options):
                color = (243, 208, 64) if i == self.selected_option else (242, 242, 240)
                self.render_text(option, 2 * (TILE_SIZE // 2), (18 + i) * (TILE_SIZE // 2) + (4 * i), color)

        elif self.game_state == 5:
            self.screen.blit(self.leaderboard, (0, 0))
            self.render_text('HI-SCORES:', 2 * (TILE_SIZE // 2), 2 * TILE_SIZE, (243, 208, 64))
            #Here is where in have to do the logic for displaying the high scores
            for idx, score in enumerate(self.leaderboard_scores):
                self.render_text(f'{idx + 1}. SCORE: {score}', 2 * (TILE_SIZE // 2), (4 + idx) * TILE_SIZE, (242, 242, 240))
            self.render_text('PRESIONA S PARA VOLVER', 2 * (TILE_SIZE // 2), 18 * (TILE_SIZE // 2), (243, 208, 64))

        elif self.game_state == 6:
            self.screen.blit(self.leaderboard, (0, 0))
            credits = ['GONZALO VICENTE', 'JOSE MORALES', 'MATIAS MUNOZ', 'JOSE QUEIROLO']
            self.render_text('CREDITS:', 2 * (TILE_SIZE // 2), 2 * TILE_SIZE, (243, 208, 64))
            for i, name in enumerate(credits):
                self.render_text(name, 2 * (TILE_SIZE // 2), (4 + i) * TILE_SIZE, (242, 242, 240))
            self.render_text('PRESIONA S PARA VOLVER', 2 * (TILE_SIZE // 2), 18 * (TILE_SIZE // 2), (243, 208, 64))

        elif self.game_over:
            # Pantalla de Game Over
            self.screen.fill((35, 33, 61))
            self.render_text('GAME OVER', 5 * TILE_SIZE, 5 * TILE_SIZE, (189, 81, 90))
            self.render_text('TU PUNTAJE ES', 3 * TILE_SIZE, 7 * TILE_SIZE, (243, 208, 64))
            self.render_text(str(self.score), 10 * TILE_SIZE, 7 * TILE_SIZE, (242, 242, 240))
            self.render_text('GRACIAS POR JUGAR', 3 * TILE_SIZE, 9 * TILE_SIZE, (243, 208, 64))
            self.render_text('PRESS R TO TRY AGAIN', 2 * TILE_SIZE, 11 * TILE_SIZE, (242, 242, 240))
            self.render_text('PRESS M TO RETURN TO MENU', 1 * TILE_SIZE, 13 * TILE_SIZE, (242, 242, 240))

        elif self.game_state in [1, 2, 3, 4]:
            self.screen.blit(self.background, (0, 0))
            for log in self.logs:
                log.draw(self.screen)
            for turtle in self.turtles:
                turtle.draw(self.screen)
            self.frog.draw(self.screen)
            
            for car in self.cars:
                car.draw(self.screen)

            for idx, slot in enumerate(self.finished_slots):
                if idx == 0 and slot == True:
                    self.screen.blit(self.frog.images['winner'], (8, 32))
                if idx == 1 and slot == True:
                    self.screen.blit(self.frog.images['winner'], (56, 32))
                if idx == 2 and slot == True:
                    self.screen.blit(self.frog.images['winner'], (104, 32))
                if idx == 3 and slot == True:
                    self.screen.blit(self.frog.images['winner'], (152, 32))
                if idx == 4 and slot == True:
                    self.screen.blit(self.frog.images['winner'], (200, 32))

            # Dibujar puntaje, hi-score y vidas
            self.render_text('1-UP', 4 * (TILE_SIZE // 2), 0, (242, 242, 240))
            self.render_text(str(self.score), 4 * (TILE_SIZE // 2), TILE_SIZE // 2, (189, 81, 90))
            self.render_text('HI-SCORE', 10 * (TILE_SIZE // 2), 0, (242, 242, 240))
            self.render_text(str(self.high_score), 10 * (TILE_SIZE // 2), TILE_SIZE // 2, (189, 81, 90))

            self.render_text('TIME', 24 * (TILE_SIZE // 2), 31 * (TILE_SIZE // 2), (243, 208, 64))
            # Dibujar la barra de tiempo
            time_ratio = self.time_remaining / self.time_limit
            current_width = int(self.time_bar_width * time_ratio)
            # Dibujar la barra desde la izquierda y reducir su ancho hacia la derecha
            pygame.draw.rect(self.screen, (243, 208, 64), (self.time_bar_x, self.time_bar_y, current_width, self.time_bar_height))
    
            self.render_text('LIVES', 0 * (TILE_SIZE // 2), 30 * (TILE_SIZE // 2), (243, 208, 64))
            self.render_text(str(self.lives), 6 * (TILE_SIZE // 2), 30 * (TILE_SIZE // 2), (242, 242, 240))    
            self.render_text('LEVEL', 0 * (TILE_SIZE // 2), 31 * (TILE_SIZE // 2), (243, 208, 64))
            self.render_text(str(self.current_level+1), 6 * (TILE_SIZE // 2), 31 * (TILE_SIZE // 2), (242, 242, 240))

            