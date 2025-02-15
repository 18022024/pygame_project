import pygame
import constants
import game


def main():
    while True:
        pygame.init()
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        game.main_menu(screen)
        game.transition(screen, 0)
        game.start_game(screen)


if __name__ == '__main__':
    main()
