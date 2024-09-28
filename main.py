import pygame
from game import Game
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, TITLE

# Multiplicador del tamaño de la ventana
SCALE_FACTOR = 3

def main():
    pygame.init()
    
    # Crea la ventana con el tamaño escalado
    screen = pygame.display.set_mode((SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    # Crea una superficie interna con el tamaño original del juego
    game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
    game = Game(game_surface)

    # Configurar la música de fondo
    pygame.mixer.music.load('assets/music/background_music.mp3')
    pygame.mixer.music.play(-1)


    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        # Actualiza el estado del juego
        game.update()

        # Dibuja en la superficie del juego
        game.draw()

        # Escala la superficie del juego al tamaño de la ventana
        scaled_surface = pygame.transform.scale(game_surface, (SCREEN_WIDTH * SCALE_FACTOR, SCREEN_HEIGHT * SCALE_FACTOR))

        # Dibuja la superficie escalada en la ventana
        screen.blit(scaled_surface, (0, 0))
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()

if __name__ == "__main__":
    main()