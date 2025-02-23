import pygame
import constants
import game


def main():
    while True:
        pygame.init()
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
        game.main_menu(screen)
        game.transition(screen, 0)
        pygame.mixer.music.load('data/game_music.mp3')
        pygame.mixer.music.play(-1)
        pygame.mixer.music.set_volume(constants.MUSIC_VOL)
        s = game.start_game(screen)
        while s:
            game.fade(screen)
            s = game.start_game(screen)


if __name__ == '__main__':
    main()
