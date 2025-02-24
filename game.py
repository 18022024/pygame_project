import os
from collections import deque
import sys
import maps
import pygame
import classes
import constants
import pyautogui
from PIL import ImageFilter

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


def get_direction(click_pos, target_pos):
    x1, y1 = click_pos
    x2, y2 = target_pos

    directions = []

    if x1 < x2:
        if abs(y1 - y2) <= 35:
            return 'l'
        directions.append('l')
    else:
        if abs(y1 - y2) <= 35:
            return 'r'
        directions.append('r')

    if y1 < y2:
        if abs(x1 - x2) <= 35:
            return 'u'
        directions.append('u')
    else:
        if abs(x1 - x2) <= 35:
            return 'd'
        directions.append('d')

    return ''.join(directions)


def is_valid(x, y, matrix, visited):
    return 0 <= x < len(matrix) and 0 <= y < len(matrix[0]) and matrix[x][y] != '#' and not visited[x][y]


def bfs(matrix, start, end):
    rows, cols = len(matrix), len(matrix[0])
    visited = [[False for _ in range(cols)] for _ in range(rows)]

    directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

    queue = deque([(start, [start])])
    visited[start[0]][start[1]] = True

    while queue:
        (curr_x, curr_y), path = queue.popleft()

        if (curr_x, curr_y) == end:
            return path

        for dx, dy in directions:
            new_x, new_y = curr_x + dx, curr_y + dy

            if is_valid(new_x, new_y, matrix, visited):
                visited[new_x][new_y] = True
                queue.append(((new_x, new_y), path + [(new_x, new_y)]))

    return []


def find_start_and_end(matrix):
    start = end = None
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            if matrix[i][j] == '!':
                start = (i, j)
            elif matrix[i][j] == '@':
                end = (i, j)
    return start, end


def start_game(screen):
    running = True
    screen.fill((0, 0, 0))
    clock = pygame.time.Clock()

    cursor = pygame.image.load('data/cros.png')
    cursor.set_colorkey(cursor.get_at((0, 0)))

    all_sprites = pygame.sprite.Group()
    player_group = pygame.sprite.Group()
    enemy_group = pygame.sprite.Group()
    enemy_health = pygame.sprite.Group()
    en_bullet_group = pygame.sprite.Group()
    bullet_group = pygame.sprite.Group()
    chests = pygame.sprite.Group()
    items = pygame.sprite.Group()

    map, arr_map = maps.choose_map()
    map = classes.Map(map, [255, 254])
    health_cd = 0
    y = 0
    all_enemies = list()

    for elem in arr_map:
        y += 1
        if '@' in elem:
            player = classes.Player(player_group, all_sprites, load_image('player_static_left_1.png'),
                                    [elem.index('@'), y - 1])
        if '*' in elem:
            classes.Chest(chests, all_sprites, load_image('close_chest.png'), [elem.index('*'), y - 1])
        if '!' in elem:
            enemy = classes.Enemy(enemy_group, all_sprites, load_image('enemy_melee_right_1.png'),
                                  [elem.index('!'), y - 1], 'left')
            en_health = classes.Enemy_health(all_sprites, enemy_health, load_image('enemy_health_1.PNG'),
                                             [enemy.rect.x, enemy.rect.y],
                                             enemy.hp, enemy.attack_mode)
            all_enemies.append([enemy, en_health])

    health = classes.Health(all_sprites, load_image('health_1.PNG'), [player.rect.x, player.rect.y], constants.HEALTH)
    range_cd_time = 0
    melee_cd_time = 0
    timer = 0
    death_time = 0
    dir = 'l'
    inventory = classes.Inventory(all_sprites, load_image('inventory.png'), constants.INVENTORY)

    matrix = list()
    for x in arr_map:
        matrix.append([el for el in x])

    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if in_game_settings(screen):
                        return
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    if player.attack_mode == 'melee' and not melee_cd_time:
                        player.is_attack_melee = True
                        melee_cd_time += 1
                        for enemy in all_enemies:
                            if pygame.sprite.spritecollideany(enemy[0], player_group):
                                enemy[0].is_damage = True
                    if player.attack_mode == 'range' and not range_cd_time and player.alive:
                        player.is_attack_range = True
                        range_cd_time += 1
                        player_pos = [player.rect.x, player.rect.y]
                        fire_pos = event.pos
                        dir = get_direction(event.pos, [player.rect.x + player.image.get_size()[0] // 2,
                                                        player.rect.y + player.image.get_size()[1] // 2])
                        if dir == 'r':
                            player_pos = [player_pos[0] + player.image.get_size()[0],
                                          player_pos[1] + player.image.get_size()[1] // 2]
                        elif dir == 'l':
                            player_pos = [player_pos[0], player_pos[1] + player.image.get_size()[1] // 2]
                        elif dir == 'u':
                            player_pos = [player_pos[0] + player.image.get_size()[0] // 2, player_pos[1]]
                        elif dir == 'd':
                            player_pos = [player_pos[0] + player.image.get_size()[0] // 2,
                                          player_pos[1] + player.image.get_size()[1] // 2]
                        elif dir == 'rd':
                            player_pos = [player_pos[0] + player.image.get_size()[0] - player.image.get_size()[0] // 6,
                                          player_pos[1] + player.image.get_size()[1] // 3 * 2]
                        elif dir == 'ru':
                            player_pos = [player_pos[0] + player.image.get_size()[0] - player.image.get_size()[0] // 6,
                                          player_pos[1] + player.image.get_size()[1] // 3]
                        elif dir == 'ld':
                            player_pos = [player_pos[0] + player.image.get_size()[0] // 6,
                                          player_pos[1] + player.image.get_size()[1] // 1.5]
                        elif dir == 'lu':
                            player_pos = [player_pos[0] + player.image.get_size()[0] // 6,
                                          player_pos[1] + player.image.get_size()[1] // 2.5]
                        classes.Bullet(bullet_group, all_sprites, player_pos, fire_pos, player.bullet_mode, dir)

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 3 and player.alive:
                    inventory.change_item()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    player.attack_mode = 'melee'

                if event.key == pygame.K_3:
                    player.attack_mode = 'range'

                if event.key == pygame.K_w or event.key == pygame.K_s or event.key == pygame.K_a or event.key == pygame.K_d:
                    timer = 0

                if event.key == pygame.K_e and player.alive:
                    for sprite in items:
                        if pygame.sprite.spritecollideany(sprite, player_group):
                            inventory.get(sprite.type)
                            constants.INVENTORY[inventory.item_now] += 1
                            sprite.kill()
                    for sprite in chests:
                        if pygame.sprite.spritecollideany(sprite, player_group) and sprite.is_closed():
                            sprite.open()
                            x = sprite.rect.x
                            y = sprite.rect.y
                            p = sprite.get_item()
                            item = classes.Item(items, all_sprites, load_image(f'{p}.png'), [x, y], p)
                    if map.get_tile_id([player.map_x_l, player.map_y_top]) == 254 or map.get_tile_id(
                            [player.map_x_r, player.map_y_bot]) == 254:
                        return True

                if event.key == pygame.K_SPACE and player.alive:
                    if inventory.item_now:
                        if inventory.item_now == 'heal':
                            if constants.HEALTH == 6:
                                pass
                            else:
                                constants.HEALTH += 2
                                constants.INVENTORY[inventory.item_now] -= 1
                                if not inventory.all_items[inventory.item_now]:
                                    if not inventory.all_items['bullet']:
                                        inventory.item_now = None
                                    else:
                                        inventory.item_now = 'bullet'
                                        inventory.item_now = 'bullet'
                        elif inventory.item_now == 'bullet':
                            player.bullet_mode = 'bust'
                            constants.INVENTORY[inventory.item_now] -= 1
        for bullet in bullet_group:
            try:
                if (not map.is_free([(bullet.rect.x + bullet.image.get_size()[0] // 2 - 50) // constants.TILE_WIDTH,
                                     (bullet.rect.y + bullet.image.get_size()[
                                         1] // 2 - 50) // constants.TILE_WIDTH])) and (
                        bullet.dir == 'd' or bullet.dir == 'r' or bullet.dir == 'rd') or (
                        not map.is_free([(bullet.rect.x + bullet.image.get_size()[0] // 2 + 50) // constants.TILE_WIDTH,
                                         (bullet.rect.y + bullet.image.get_size()[
                                             1] // 2 + 50) // constants.TILE_WIDTH])) and (
                        bullet.dir == 'u' or bullet.dir == 'l' or bullet.dir == 'lu') or (
                        not map.is_free([(bullet.rect.x + bullet.image.get_size()[0] // 2 - 50) // constants.TILE_WIDTH,
                                         (bullet.rect.y + bullet.image.get_size()[
                                             1] // 2 + 50) // constants.TILE_WIDTH])) and bullet.dir == 'ru' or (
                        not map.is_free([(bullet.rect.x + bullet.image.get_size()[0] // 2 + 50) // constants.TILE_WIDTH,
                                         (bullet.rect.y + bullet.image.get_size()[
                                             1] // 2 - 50) // constants.TILE_WIDTH])) and bullet.dir == 'ld':
                    bullet.kill()
            except Exception:
                bullet.kill()

        if player.bullet_mode == 'bust':
            player.bust_time += 1
            if player.bust_time >= 201:
                player.bust_time = 0
                player.bullet_mode = 'simple'

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

        for enemy in all_enemies:
            if not enemy[0].is_attack and enemy[0].alive:
                enemy[0].x = (enemy[0].rect.x + enemy[0].image.get_size()[0] // 2) // constants.TILE_WIDTH
                enemy[0].y = (enemy[0].rect.y + enemy[0].image.get_size()[1] // 2) // constants.TILE_WIDTH

                start, end = ((enemy[0].y, enemy[0].x), (player.y, player.x))
                answer = list()
                path = bfs(matrix, start, end)
                for i in range(1, len(path)):
                    if path[i - 1][0] - path[i][0] < 0:
                        answer.append('down')
                    elif path[i - 1][0] - path[i][0] > 0:
                        answer.append('up')
                    elif path[i - 1][1] - path[i][1] > 0:
                        answer.append('left')
                    elif path[i - 1][1] - path[i][1] < 0:
                        answer.append('right')
                enemy[0].path = answer
                try:
                    if answer[0] == 'left':
                        enemy[0].rect.x -= 5
                        enemy[0].direction = 'left'
                    elif answer[0] == 'right':
                        enemy[0].rect.x += 5
                        enemy[0].direction = 'right'
                    elif answer[0] == 'up':
                        enemy[0].rect.y -= 5
                    elif answer[0] == 'down':
                        enemy[0].rect.y += 5
                except Exception:
                    enemy[0].is_attack = True

                enemy[0].timer += 1
                enemy[0].update_move()
            elif enemy[0].can_attack and enemy[0].alive:
                enemy[0].attack()
                enemy[0].attack_time += 1
            if enemy[0].make_dmg:
                player.is_damage = True
                enemy[0].make_dmg = False
            enemy[1].update_health(enemy[0].rect.x, enemy[0].rect.y)

            if pygame.sprite.spritecollideany(enemy[0], bullet_group):
                for b in bullet_group:
                    if pygame.sprite.spritecollideany(b, enemy_group):
                        b.kill()
                        if player.bullet_mode == 'simple':
                            enemy[0].is_damage = True
                        else:
                            enemy[0].alive = False
                            enemy[1].count = 0

            if enemy[0].is_damage:
                enemy[1].health_cd += 1
                if enemy[1].health_cd == 9:
                    enemy[1].damage()
                if enemy[1].health_cd == 18:
                    enemy[1].damage()
                    enemy[1].health_cd = 0
                    enemy[0].is_damage = False

            if enemy[1].count <= 0:
                enemy[1].kill()
                enemy[0].alive = False

            if not enemy[0].alive:
                enemy[0].death_time += 1
                enemy[0].death(enemy[0].death_time)
                if enemy[0].death_time >= 72:
                    all_enemies.remove([enemy[0], enemy[1]])

            enemy[0].range_attack_cd += 1
            if enemy[0].range_attack_cd >= 120 and enemy[0].alive:
                if enemy[0].attack_mode == 'range':
                    enemy[0].is_attack = True
                    player_pos = [player.rect.x + player.image.get_size()[0] // 2,
                                  player.rect.y + player.image.get_size()[1] // 2 - 20]
                    en_pos = [enemy[0].rect.x, enemy[0].rect.y]
                    en_pos = [en_pos[0], en_pos[1]]
                    classes.Enemy_bullet(en_bullet_group, all_sprites, en_pos, player_pos, enemy[0].direction)
                enemy[0].range_attack_cd = 0

        for en_bullet in en_bullet_group:
            try:
                if en_bullet.dir == 'left' and not map.is_free(
                        [en_bullet.rect.x // constants.TILE_WIDTH, en_bullet.rect.y // constants.TILE_WIDTH]):
                    en_bullet.kill()
            except Exception:
                en_bullet.kill()

        if pygame.sprite.spritecollideany(player, en_bullet_group):
            for b in en_bullet_group:
                if pygame.sprite.spritecollideany(b, player_group):
                    b.kill()
            player.is_damage = True

        if player.is_attack_melee:
            player.attack_melee(dir)
            player.attack_time += 1
        elif player.is_attack_range:
            direction = None
            if dir == 'r':
                direction = 'right'
            if dir == 'l':
                direction = 'left'
            if dir == 'd':
                direction = 'down'
            if dir == 'ld':
                direction = 'left_down'
            if dir == 'rd':
                direction = 'right_down'
            if dir == 'u':
                direction = 'up'
            if dir == 'lu':
                direction = 'up_left'
            if dir == 'ru':
                direction = 'up_right'
            player.attack_range(direction)
            player.attack_time += 1
        elif player.alive:
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

        if player.is_damage:
            health_cd += 1
            if health_cd == 9:
                health.damage()
            if health_cd == 18:
                health.damage()
                health_cd = 0
                player.is_damage = False
            if health.count <= 1:
                player.alive = False

        screen.fill((255, 255, 255))

        map.render(screen)
        all_sprites.draw(screen)
        if range_cd_time:
            range_cd_time += 1
            color = (255, 255, 255) if player.bullet_mode == 'simple' else (255, 255, 0)
            pygame.draw.rect(screen, color,
                             [health.rect.x, health.rect.y + health.image.get_size()[1] + 5, range_cd_time * 2.4, 5])
            if range_cd_time >= 61:
                range_cd_time = 0

        if melee_cd_time:
            melee_cd_time += 1
            if melee_cd_time >= 31:
                melee_cd_time = 0

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

        if not player.alive:
            death_time += 1
            player.death(death_time)
            if death_time >= 160:
                fade(screen)
                return
        player.x = (player.rect.x + player.image.get_size()[0] // 2) // constants.TILE_WIDTH
        player.y = (player.rect.y + player.image.get_size()[1] // 2) // constants.TILE_WIDTH

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

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
    global music_vol

    audio_inter_but = classes.Button(250, constants.SIZE[1] // 2 + 200, 800, 600,
                                     'Звук интерфейса', 'button.png', 'hover_button.png', 'button_sound.mp3')
    audio_music_but = classes.Button(1850, constants.SIZE[1] // 2 + 200, 800, 600,
                                     'Музыка', 'button.png', 'hover_button.png', 'button_sound.mp3')
    back_but = classes.Button(1050, constants.SIZE[1] - 200, 800, 600,
                              'Назад', 'button.png', 'hover_button.png', 'button_sound.mp3')
    buttons = [audio_inter_but, audio_music_but, back_but]

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


def in_game_settings(screen):
    screenshot = pyautogui.screenshot()
    blurred_screenshot = screenshot.filter(ImageFilter.GaussianBlur(10))
    blurred_screenshot.save("data/screenshot.png")
    bg_image = pygame.image.load("data/screenshot.png")
    cursor = pygame.image.load('data/cursor.png')
    cursor.set_colorkey(cursor.get_at((0, 0)))
    clicked_cursor = pygame.image.load('data/cursor_clicked.png')
    clicked_cursor.set_colorkey(clicked_cursor.get_at((0, 0)))

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
                in_game_audio(screen)

            if event.type == pygame.USEREVENT and event.button == exit_but:
                constants.INVENTORY = {'heal': 0, 'bullet': 0}
                constants.HEALTH = 6
                return 1

        for button in buttons:
            button.check_mouse(pygame.mouse.get_pos())
            if button.is_hover:
                cursor = clicked_cursor
            button.show(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

        pygame.display.flip()


def in_game_audio(screen):
    bg_image = pygame.image.load("data/screenshot.png")
    cursor = pygame.image.load('data/cursor.png')
    cursor.set_colorkey(cursor.get_at((0, 0)))
    clicked_cursor = pygame.image.load('data/cursor_clicked.png')
    clicked_cursor.set_colorkey(clicked_cursor.get_at((0, 0)))

    global inter_vol
    global game_vol

    back_but = classes.Button(1050, constants.SIZE[1] - 800, 800, 600,
                              'Вернуться', 'button.png', 'hover_button.png', 'button_sound.mp3')
    audio_inter_but = classes.Button(1050, constants.SIZE[1] - 500, 800, 600,
                                     'Звук интерфейса', 'button.png', 'hover_button.png', 'button_sound.mp3')
    game_eff_but = classes.Button(1050, constants.SIZE[1] - 200, 800, 600,
                                  'Звук игры', 'button.png', 'hover_button.png', 'button_sound.mp3')
    buttons = [audio_inter_but, back_but, game_eff_but]

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

            if event.type == pygame.USEREVENT and event.button == audio_inter_but:
                if inter_vol >= 1.0:
                    inter_vol = 0
                inter_vol += 0.1

            if event.type == pygame.USEREVENT and event.button == game_eff_but:
                if game_vol >= 1.0:
                    game_vol = 0
                game_vol += 0.1
                pygame.mixer.music.set_volume(game_vol)

        for button in buttons:
            button.check_mouse(pygame.mouse.get_pos())
            if button.is_hover:
                cursor = clicked_cursor
            button.show(screen)

        x, y = pygame.mouse.get_pos()
        screen.blit(cursor, (x - 2, y - 2))

        pygame.display.flip()
