import os
import random
import sys
import maps
import pygame
import classes
import constants
import pyautogui
from PIL import ImageGrab, Image, ImageFilter


music_vol = constants.MUSIC_VOL
game_vol = constants.GAME_VOL
inter_vol = constants.INTER_VOL


def terminate():
    pygame.quit()
    sys.exit()


def load_image(name):
    fullname = os.path.join('data', name)
    image = pygame.image.load(fullname)
    return image


def fade(screen):
    clock = pygame.time.Clock()
    running = True
    alpha = 0

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        fade_screen = pygame.Surface(constants.SIZE)
        fade_screen.fill((0, 0, 0))
        fade_screen.set_alpha(alpha)
        screen.blit(fade_screen, (0, 0))

        alpha += 10
        if alpha >= 150:
            alpha = 255
            running = False

        clock.tick(constants.FPS)
        pygame.display.flip()


def start_game(screen):
    running = True
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    pygame.mixer.music.load('data/game_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(constants.MUSIC_VOL)

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    effect_group = pygame.sprite.Group()
    chests = pygame.sprite.Group()
    items = pygame.sprite.Group()
    map, arr_map, player_pos, finish_pos = maps.choose_map()
    map = classes.Map(map, [255], [254])
    health_cd = 0
    is_damage = False
    y = 0
    for elem in arr_map:
        y += 1
        if '@' in elem:
            player = classes.Player(player_group, all_sprites, load_image('player_static_left_1.png'),
                                    [elem.index('@'), y - 1])
        if '*' in elem:
            classes.Chest(chests, all_sprites, load_image('close_chest.png'), [elem.index('*'), y - 1])
    health = classes.Health(all_sprites, load_image('health_1.PNG'), [player.rect.x, player.rect.y])
    timer = 0
    dir = 'l'
    inventory = classes.Inventory(all_sprites, load_image('inventory.png'))

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    screenshot = pyautogui.screenshot()
                    blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(10))
                    blurred_screenshot.save("data/screenshot.png")
                    if in_game_settings(screen,  'data/screenshot.png'):
                        return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    atack = classes.Atack(effect_group, all_sprites, player.rect.x + player.rect.size[0], player.rect.y)
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_w or event.key == pygame.K_s or event.key == pygame.K_a or event.key == pygame.K_d:
                    timer = 0
                if event.key == pygame.K_z:
                    is_damage = True
                if event.key == pygame.K_e:
                    for sprite in items:
                        if pygame.sprite.spritecollideany(sprite, player_group):
                            inventory.get(sprite.type)
                            sprite.kill()
                    for sprite in chests:
                        if pygame.sprite.spritecollideany(sprite, player_group) and sprite.is_closed():
                            sprite.open()
                            x = sprite.rect.x
                            y = sprite.rect.y
                            p = sprite.get_item()
                            item = classes.Item(items, all_sprites, load_image(f'{p}.png'), [x, y], p)
                if event.key == pygame.K_SPACE:
                    if inventory.item_now:
                        if inventory.item_now == 'heal':
                            if health.count == 6:
                                pass
                            else:
                                health.count += 2
                                inventory.all_items[inventory.item_now] -= 1
                                if not inventory.all_items[inventory.item_now]:
                                    inventory.item_now = None
                                if sum([inventory.all_items[i] for i in inventory.all_items]):
                                    inventory.item_now = random.choice(
                                        [i for i in inventory.all_items if inventory.all_items[i]])
                        elif inventory.item_now == 'bullet':
                            pass
                            # для бафнутых пуль
        for sprite in chests:
            if pygame.sprite.spritecollideany(sprite, player_group) and sprite.is_closed():
                sprite.image = load_image('near_chest.png')
                sprite.image.set_colorkey(sprite.image.get_at((0, 0)))
            elif sprite.is_closed():
                sprite.image = load_image('close_chest.png')
                sprite.image.set_colorkey(sprite.image.get_at((0, 0)))
        for sprite in items:
            if pygame.sprite.spritecollideany(sprite, player_group):
                sprite.image = load_image(f'{sprite.type}_near.png')
                sprite.image.set_colorkey(sprite.image.get_at((0, 0)))
            else:
                sprite.image = load_image(f'{sprite.type}.png')
                sprite.image.set_colorkey(sprite.image.get_at((0, 0)))
        if pygame.key.get_pressed()[pygame.K_d] and pygame.key.get_pressed()[pygame.K_w]:
            player.update_right_up(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                            player.map_y_top]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                 player.map_y_top]):
                player.rect.x += 5
                player.rect.y -= 5
            else:
                pass
            dir = 'ru'
        elif pygame.key.get_pressed()[pygame.K_d] and pygame.key.get_pressed()[pygame.K_s]:
            player.update_right_down(timer)
            timer += 1
            if timer >= 31:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                            (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                 (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]):
                player.rect.x += 5
                player.rect.y += 5
            else:
                pass
            dir = 'rd'
        elif pygame.key.get_pressed()[pygame.K_a] and pygame.key.get_pressed()[pygame.K_w]:
            player.update_left_up(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                            player.map_y_top]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                 player.map_y_top]):
                player.rect.x -= 5
                player.rect.y -= 5
            else:
                pass
            dir = 'lu'
        elif pygame.key.get_pressed()[pygame.K_a] and pygame.key.get_pressed()[pygame.K_s]:
            player.update_left_down(timer)
            timer += 1
            if timer >= 31:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                            (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                 (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]):
                player.rect.x -= 5
                player.rect.y += 5
            else:
                pass
            dir = 'ld'
        elif pygame.key.get_pressed()[pygame.K_d]:
            player.update_right(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                            player.map_y_bot]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 + 15) // constants.TILE_WIDTH,
                 (player.rect.y + 55) // constants.TILE_WIDTH]):
                player.rect.x += 5
            else:
                pass
            dir = 'r'
        elif pygame.key.get_pressed()[pygame.K_a]:
            player.update_left(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                            player.map_y_bot]) and map.is_free(
                [(player.rect.x + player.rect.size[0] // 2 - 15) // constants.TILE_WIDTH,
                 (player.rect.y + 55) // constants.TILE_WIDTH]):
                player.rect.x -= 5
            else:
                pass
            dir = 'l'
        elif pygame.key.get_pressed()[pygame.K_w]:
            player.update_up(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([player.map_x_l, player.map_y_top]) and map.is_free([player.map_x_r, player.map_y_top]):
                player.rect.y -= 5
            else:
                pass
            dir = 'u'
        elif pygame.key.get_pressed()[pygame.K_s]:
            player.update_down(timer)
            timer += 1
            if timer >= 25:
                timer = 0
            if map.is_free([player.map_x_l,
                            (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]) and map.is_free(
                [player.map_x_r, (player.rect.y + player.rect.size[1] - 45) // constants.TILE_WIDTH]):
                player.rect.y += 5
            else:
                pass
            dir = 'd'
        else:
            player.update_afk(dir)
        player.map_x_r = (player.rect.x + player.rect.size[0] // 2 + 10) // constants.TILE_WIDTH
        player.map_y_top = (player.rect.y + 50) // constants.TILE_WIDTH
        player.map_x_l = (player.rect.x + player.rect.size[0] // 2 - 10) // constants.TILE_WIDTH
        player.map_y_bot = (player.rect.y + player.rect.size[1] - 50) // constants.TILE_WIDTH
        if is_damage:
            health_cd += 1
            if health_cd == 9:
                health.damage()
            if health_cd == 18:
                health.damage()
                health_cd = 0
                is_damage = False
        screen.fill((255, 255, 255))
        map.render(screen)
        all_sprites.draw(screen)
        if inventory.item_now:
            im = pygame.image.load(f'data/{inventory.item_now}.png')
            im = pygame.transform.scale(im, (100, 100))
            im.set_colorkey(im.get_at((0, 0)))
            im.set_alpha(150)
            font = pygame.font.Font(None, 100)
            text = font.render(str(inventory.all_items[inventory.item_now]), True, (200, 200, 200))
            screen.blit(text, [constants.SIZE[0] - inventory.rect.size[0] / 2 - 150,
                               constants.SIZE[1] - inventory.rect.size[1] + 40])
            screen.blit(im, [constants.SIZE[0] - inventory.rect.size[0] / 2 - 65,
                             constants.SIZE[1] - inventory.rect.size[1] + 20])
        all_sprites.update()
        health.update_health(player.rect.x, player.rect.y)
        clock.tick(constants.FPS)
        pygame.display.flip()


def main_menu(screen):
    pygame.mixer.music.load('data/menu_music.mp3')
    pygame.mixer.music.play(-1)
    pygame.mixer.music.set_volume(constants.MUSIC_VOL)
    bg_image = pygame.image.load(f'data/background.png')
    clicked_cursor = pygame.image.load('data/cursor_clicked.png')
    clicked_cursor.set_colorkey(clicked_cursor.get_at((0, 0)))
    pygame.mouse.set_visible(False)

    settings_but = classes.Button(200, constants.SIZE[1] - 200, 500, 300,
                                  'Настройки', 'button.png', 'hover_button.png', 'button_sound.mp3')
    game_but = classes.Button(1054, constants.SIZE[1] - 200, 500, 300,
                              'Начать игру', 'button.png', 'hover_button.png', 'button_sound.mp3')
    exit_but = classes.Button(1908, constants.SIZE[1] - 200, 500, 300,
                               'Выйти', 'button.png', 'hover_button.png', 'button_sound.mp3')
    buttons = [settings_but, game_but, exit_but]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        cursor = pygame.image.load('data/cursor.png')
        cursor.set_colorkey(cursor.get_at((0, 0)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.USEREVENT and event.button == game_but:
                return

            if event.type == pygame.USEREVENT and event.button == settings_but:
                fade(screen)
                settings(screen)

            if event.type == pygame.USEREVENT and event.button == exit_but:
                running = False
                terminate()

            for btn in buttons:
                btn.check_event(event, inter_vol)

        for button in buttons:
            button.check_mouse(pygame.mouse.get_pos())
            if button.is_hover:
                cursor = clicked_cursor
            button.show(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

        pygame.display.flip()


def settings(screen):
    bg_image = pygame.image.load(f'data/background_set.png')
    cursor = pygame.image.load('data/cursor.png')
    cursor.set_colorkey(cursor.get_at((0, 0)))
    clicked_cursor = pygame.image.load('data/cursor_clicked.png')
    clicked_cursor.set_colorkey(clicked_cursor.get_at((0, 0)))

    global inter_vol
    global game_vol
    global music_vol

    audio_inter_but = classes.Button(250, constants.SIZE[1] // 2 + 200, 800, 600,
                                  'Звук интерфейса', 'button.png', 'hover_button.png', 'button_sound.mp3')
    audio_music_but = classes.Button(1050, constants.SIZE[1] // 2 + 200, 800, 600,
                                     'Музыка', 'button.png', 'hover_button.png', 'button_sound.mp3')
    game_eff_but = classes.Button(1850, constants.SIZE[1] // 2 + 200, 800, 600,
                                     'Звук игры', 'button.png', 'hover_button.png', 'button_sound.mp3')
    back_but = classes.Button(1050, constants.SIZE[1] - 200, 800, 600,
                                  'Назад', 'button.png', 'hover_button.png', 'button_sound.mp3')
    buttons = [audio_inter_but, audio_music_but, game_eff_but, back_but]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        cursor = pygame.image.load('data/cursor.png')
        cursor.set_colorkey(cursor.get_at((0, 0)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    fade(screen)
                    running = False

            for btn in buttons:
                btn.check_event(event, inter_vol)

            if event.type == pygame.USEREVENT and event.button == back_but:
                fade(screen)
                running = False

            if event.type == pygame.USEREVENT and event.button == audio_music_but:
                if music_vol >= 1.0:
                    music_vol = 0
                music_vol += 0.1
                pygame.mixer.music.set_volume(music_vol)

            if event.type == pygame.USEREVENT and event.button == audio_inter_but:
                if inter_vol >= 1.0:
                    inter_vol = 0
                inter_vol += 0.1

            if event.type == pygame.USEREVENT and event.button == game_eff_but:
                pass
                # менять звуки игры

        for button in buttons:
            button.check_mouse(pygame.mouse.get_pos())
            if button.is_hover:
                cursor = clicked_cursor
            button.show(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

        pygame.display.flip()


def transition(screen, c):
    is_down = False
    pygame.mixer.music.stop()

    bg_image = pygame.image.load(f'data/background.png')
    trans = pygame.image.load('data/transition.png')
    clock = pygame.time.Clock()

    running = True
    pygame.mixer.Sound('data/plate.mp3').play()
    while running:
        if not is_down:
            screen.blit(bg_image, (0, 0))
        else:
            screen.fill((0, 0, 0))

        screen.blit(trans, (0, -1 * trans.get_size()[1] + c))
        if c > 1440:
            is_down = True
            pygame.time.wait(3000)
            pygame.mixer.Sound('data/plate.mp3').play()
        if not is_down:
            c += 10
        else:
            c -= 10
        if is_down and c <= 0:
            running = False

        cursor = pygame.image.load('data/cursor.png')
        cursor.set_colorkey(cursor.get_at((0, 0)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

        clock.tick(constants.FPS)
        pygame.display.flip()


def in_game_settings(screen, image):
    im = Image.open(image)
    bg_image = pygame.image.load(image)
    cursor = pygame.image.load('data/cursor.png')
    cursor.set_colorkey(cursor.get_at((0, 0)))
    clicked_cursor = pygame.image.load('data/cursor_clicked.png')
    clicked_cursor.set_colorkey(clicked_cursor.get_at((0, 0)))

    global inter_vol
    global game_vol
    global music_vol

    back_but = classes.Button(1050, constants.SIZE[1] - 800, 800, 600,
                                  'Вернуться', 'button.png', 'hover_button.png', 'button_sound.mp3')
    setting_but = classes.Button(1050, constants.SIZE[1] - 500, 800, 600,
                                  'Настройки', 'button.png', 'hover_button.png', 'button_sound.mp3')
    exit_but = classes.Button(1050, constants.SIZE[1] - 200, 800, 600,
                                  'Выйти', 'button.png', 'hover_button.png', 'button_sound.mp3')
    buttons = [setting_but, back_but, exit_but]

    running = True
    while running:
        screen.blit(bg_image, (0, 0))

        cursor = pygame.image.load('data/cursor.png')
        cursor.set_colorkey(cursor.get_at((0, 0)))

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False

            for btn in buttons:
                btn.check_event(event, inter_vol)

            if event.type == pygame.USEREVENT and event.button == back_but:
                running = False

            if event.type == pygame.USEREVENT and event.button == setting_but:
                pass

            if event.type == pygame.USEREVENT and event.button == exit_but:
                return 1

        for button in buttons:
            button.check_mouse(pygame.mouse.get_pos())
            if button.is_hover:
                cursor = clicked_cursor
            button.show(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

        pygame.display.flip()
