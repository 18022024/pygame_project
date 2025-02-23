import math

import pygame
import game
import pytmx
import constants
import random


# copypaste is a live


class Inventory(pygame.sprite.Sprite):
    def __init__(self, all_group, image, inv):
        super().__init__(all_group)
        if not inv['heal'] and not inv['bullet']:
            self.item_now = None
        else:
            self.item_now = 'heal' if inv['heal'] else 'bullet'
        self.all_items = inv
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.image.set_alpha(150)
        self.rect = self.image.get_rect().move(constants.SIZE[0] - 500, constants.SIZE[1] - 300)

    def change_item(self):
        self.item_now = [it for it in self.all_items if it != self.item_now][0]

    def get(self, item):
        self.item_now = item

    def update(self):
        self.all_items = constants.INVENTORY


class Item(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, image, pos, type):
        super().__init__(single_group, all_group)
        self.type = type
        self.anim = 0
        self.x = pos[0]
        self.y = pos[1]
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect().move(self.x + 15, self.y - 30)

    def update(self):
        self.anim += 1
        if self.anim == 6 or self.anim == 12:
            self.rect.y += 2
        if self.anim == 18 or self.anim == 24:
            self.rect.y -= 2
        if self.anim == 24:
            self.anim = 0


class Chest(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, image, pos):
        super().__init__(single_group, all_group)
        self.items = ['heal', 'bullet', 'heal']
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.x = pos[0]
        self.y = pos[1]
        self.rect = self.image.get_rect().move(self.x * 96, self.y * 96)
        self.con = 'closed'

    def open(self):
        self.con = 'open'
        self.image = game.load_image('open_chest.png')
        self.image.set_colorkey(self.image.get_at((0, 0)))

    def is_closed(self):
        return self.con == 'closed'

    def get_item(self):
        return random.choice(self.items)


class Health(pygame.sprite.Sprite):
    def __init__(self, all_group, image, pos, count):
        super().__init__(all_group)
        self.image = image
        self.count = count
        self.x = pos[0] + 15
        self.y = pos[1]
        self.rect = self.image.get_rect().move(self.x, self.y)

    def update_health(self, x, y):
        self.rect.x = x + 15
        self.rect.y = y - 15

    def damage(self):
        constants.HEALTH -= 1

    def update(self):
        self.count = constants.HEALTH
        if self.count == 6:
            self.image = game.load_image('health_1.png')
        if self.count == 5:
            self.image = game.load_image('health_1_damage.png')
        if self.count == 4:
            self.image = game.load_image('health_2.png')
        if self.count == 3:
            self.image = game.load_image('health_2_damage.png')
        if self.count == 2:
            self.image = game.load_image('health_3.png')
        if self.count == 1:
            self.kill()


class Enemy_health(pygame.sprite.Sprite):
    def __init__(self, all_group, single_group, image, pos, count, atack_mode):
        super().__init__(single_group, all_group)
        self.image = image
        self.count = count
        self.type_enemy = atack_mode
        self.health_cd = 0
        self.x = pos[0] + 15
        self.y = pos[1]
        self.rect = self.image.get_rect().move(self.x, self.y)

    def update_health(self, x, y):
        if self.type_enemy == 'melee':
            self.rect.x = x + 40
            self.rect.y = y + 60
        else:
            self.rect.x = x + 45
            self.rect.y = y - 15

    def damage(self):
        self.count -= 1

    def update(self):
        if self.count == 4:
            self.image = game.load_image('enemy_health_1.png')
        if self.count == 3:
            self.image = game.load_image('enemy_health_damage_1.png')
        if self.count == 2:
            self.image = game.load_image('enemy_health_2.png')
        if self.count == 1:
            self.kill()


class Map:
    def __init__(self, filename, free_tile):
        self.map = pytmx.load_pygame(f'maps/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tile

    def render(self, screen):
        for y in range(self.height):
            for x in range(self.width):
                image = self.map.get_tile_image(x, y, 0)
                screen.blit(image, (x * self.tile_size, y * self.tile_size))
                try:
                    image = self.map.get_tile_image(x, y, 1)
                    screen.blit(image, (x * self.tile_size, y * self.tile_size))
                except Exception:
                    pass

    def get_tile_id(self, pos):
        return self.map.tiledgidmap[self.map.get_tile_gid(*pos, 0)] - 1

    def is_free(self, pos):
        return self.get_tile_id(pos) in self.free_tiles


class Enemy(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, image, pos, direction):
        super().__init__(single_group, all_group)
        self.direction = direction
        self.death_time = 0
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.x = pos[0]
        self.y = pos[1]
        self.rect = self.image.get_rect().move(self.x * 96, self.y * 96)
        self.attack_cd = 0
        self.is_damage = False
        self.can_attack = True
        self.timer = 0
        self.attack_time = 0
        self.is_attack = False
        self.range_attack_cd = 0
        self.attack_mode = random.choice(['melee', 'range', 'melee'])
        self.path = list()
        self.hp = 4
        self.make_dmg = False

    def update_move(self):
        if self.attack_mode == 'melee':
            if self.direction == 'right':
                if self.timer < 9:
                    self.image = game.load_image('enemy_melee_right_1.png')
                if self.timer == 17:
                    self.image = game.load_image('enemy_melee_right_2.png')
                if self.timer == 25:
                    self.image = game.load_image('enemy_melee_right_3.png')
                if self.timer == 33:
                    self.timer = 0
            else:
                if self.timer < 9:
                    self.image = game.load_image('enemy_melee_left_1.png')
                if self.timer == 17:
                    self.image = game.load_image('enemy_melee_left_2.png')
                if self.timer == 25:
                    self.image = game.load_image('enemy_melee_left_3.png')
                if self.timer == 33:
                    self.timer = 0
        else:
            if self.direction == 'right':
                if self.timer < 7:
                    self.image = game.load_image('enemy_range_right_1.png')
                if self.timer == 13:
                    self.image = game.load_image('enemy_range_right_2.png')
                if self.timer == 19:
                    self.image = game.load_image('enemy_range_right_3.png')
                if self.timer == 25:
                    self.image = game.load_image('enemy_range_right_4.png')
                if self.timer == 31:
                    self.timer = 0
            else:
                if self.timer < 7:
                    self.image = game.load_image('enemy_range_left_1.png')
                if self.timer == 13:
                    self.image = game.load_image('enemy_range_left_2.png')
                if self.timer == 19:
                    self.image = game.load_image('enemy_range_left_3.png')
                if self.timer == 25:
                    self.image = game.load_image('enemy_range_left_4.png')
                if self.timer == 31:
                    self.timer = 0

    def attack(self):
        if self.attack_time == 5:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_1.png')
        if self.attack_time == 10:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_2.png')
        if self.attack_time == 15:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_3.png')
        if self.attack_time == 20:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_4.png')
        if self.attack_time == 25:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_5.png')
        if self.attack_time == 30:
            self.image = game.load_image(f'enemy_{self.attack_mode}_attack_{self.direction}_6.png')
        if self.attack_time >= 36:
            self.attack_time = 0
            self.is_attack = False
            self.can_attack = True
            if self.attack_mode == 'melee':
                self.make_dmg = True

    def death(self, timer):
        if timer == 8:
            self.image = game.load_image(f'{self.attack_mode}_death_1.png')
        if timer == 16:
            self.image = game.load_image(f'{self.attack_mode}_death_2.png')
        if timer == 24:
            self.image = game.load_image(f'{self.attack_mode}_death_3.png')
        if timer == 32:
            self.image = game.load_image(f'{self.attack_mode}_death_4.png')
        if timer == 40:
            self.image = game.load_image(f'{self.attack_mode}_death_5.png')
        if timer == 48:
            self.image = game.load_image(f'{self.attack_mode}_death_6.png')
        if timer == 56:
            self.image = game.load_image(f'{self.attack_mode}_death_7.png')
            if self.attack_mode == 'range':
                self.kill()
        if timer == 64 and self.attack_mode == 'melee':
            self.image = game.load_image(f'{self.attack_mode}_death_8.png')
            self.kill()


class Player(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, image, pos):
        super().__init__(single_group, all_group)
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.x = pos[0]
        self.y = pos[1]
        self.map_x_r = 0
        self.map_y_top = 0
        self.map_x_l = 0
        self.map_y_bot = 0
        self.rect = self.image.get_rect().move(self.x * 96, self.y * 96)
        self.is_damage = False
        self.time_afk = 0
        self.attack_time = 0
        self.is_attack_melee = False
        self.is_attack_range = False
        self.attack_mode = 'melee'
        self.bullet_mode = 'simple'
        self.bust_time = 0
        self.alive = True

    def attack_melee(self, dir):
        if dir == 'r':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_right_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_right_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_right_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_right_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'l':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_left_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_left_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_left_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_left_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'd':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_down_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_down_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_down_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_down_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'ld':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_left_down_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_left_down_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_left_down_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_left_down_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'rd':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_right_down_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_right_down_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_right_down_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_right_down_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'u':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_up_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_up_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_up_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_up_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'lu':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_up_left_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_up_left_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_up_left_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_up_left_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False
        if dir == 'ru':
            if self.attack_time == 4:
                self.image = game.load_image('player_melee_up_right_1.png')
            if self.attack_time == 8:
                self.image = game.load_image('player_melee_up_right_2.png')
            if self.attack_time == 12:
                self.image = game.load_image('player_melee_up_right_3.png')
            if self.attack_time == 16:
                self.image = game.load_image('player_melee_up_right_4.png')
            if self.attack_time >= 20:
                self.attack_time = 0
                self.is_attack_melee = False

    def attack_range(self, direction):
        if self.attack_time == 6:
            self.image = game.load_image(f'player_range_{direction}_1.png')
        if self.attack_time == 12:
            self.image = game.load_image(f'player_range_{direction}_2.png')
        if self.attack_time == 18:
            self.image = game.load_image(f'player_range_{direction}_3.png')
        if self.attack_time >= 24:
            self.attack_time = 0
            self.is_attack_range = False

    def update_afk(self, dir):
        self.time_afk += 1
        if dir == 'l':
            if self.time_afk == 8:
                self.image = game.load_image('player_static_left_2.png')
            if self.time_afk == 16:
                self.image = game.load_image('player_static_left_3.png')
            if self.time_afk == 24:
                self.time_afk = 0
        if dir == 'r':
            if self.time_afk == 8:
                self.image = game.load_image('player_static_right_2.png')
            if self.time_afk == 16:
                self.image = game.load_image('player_static_right_3.png')
            if self.time_afk == 24:
                self.time_afk = 0
        if dir == 'd':
            if self.time_afk == 5:
                self.image = game.load_image('player_static_down_2.png')
            if self.time_afk == 10:
                self.image = game.load_image('player_static_down_3.png')
            if self.time_afk == 15:
                self.image = game.load_image('player_static_down_4.png')
            if self.time_afk == 20:
                self.image = game.load_image('player_static_down_5.png')
            if self.time_afk == 25:
                self.time_afk = 0
        if dir == 'ld':
            if self.time_afk == 8:
                self.image = game.load_image('player_static_down_left_2.png')
            if self.time_afk == 16:
                self.image = game.load_image('player_static_down_left_3.png')
            if self.time_afk == 24:
                self.time_afk = 0
        if dir == 'rd':
            if self.time_afk == 8:
                self.image = game.load_image('player_static_down_right_2.png')
            if self.time_afk == 16:
                self.image = game.load_image('player_static_down_right_3.png')
            if self.time_afk == 24:
                self.time_afk = 0
        if dir == 'u':
            if self.time_afk == 8:
                self.image = game.load_image('player_static_up_2.png')
            if self.time_afk == 16:
                self.image = game.load_image('player_static_up_3.png')
            if self.time_afk == 24:
                self.time_afk = 0
        if dir == 'lu':
            if self.time_afk == 6:
                self.image = game.load_image('player_static_up_left_2.png')
            if self.time_afk == 12:
                self.image = game.load_image('player_static_up_left_3.png')
            if self.time_afk == 18:
                self.image = game.load_image('player_static_up_left_4.png')
            if self.time_afk == 25:
                self.time_afk = 0
        if dir == 'ru':
            if self.time_afk == 6:
                self.image = game.load_image('player_static_up_right_2.png')
            if self.time_afk == 12:
                self.image = game.load_image('player_static_up_right_3.png')
            if self.time_afk == 18:
                self.image = game.load_image('player_static_up_right_4.png')
            if self.time_afk == 25:
                self.time_afk = 0

    def update_left(self, time):
        if not time:
            self.image = game.load_image('player_left_1.png')
        if time == 8:
            self.image = game.load_image('player_left_2.png')
        if time == 16:
            self.image = game.load_image('player_left_3.png')

    def update_right(self, time):
        if time < 8:
            self.image = game.load_image('player_right_1.png')
        if 8 <= time < 16:
            self.image = game.load_image('player_right_2.png')
        if 16 < time < 24:
            self.image = game.load_image('player_right_3.png')

    def update_down(self, time):
        if not time:
            self.image = game.load_image('player_down_1.png')
        if time == 6:
            self.image = game.load_image('player_down_2.png')
        if time == 12:
            self.image = game.load_image('player_down_1.png')
        if time == 18:
            self.image = game.load_image('player_down_3.png')

    def update_up(self, timer):
        if not timer:
            self.image = game.load_image('player_up_1.png')
        if timer == 8:
            self.image = game.load_image('player_up_2.png')
        if timer == 16:
            self.image = game.load_image('player_up_3.png')

    def update_left_down(self, time):
        if not time:
            self.image = game.load_image('player_down_left_1.png')
        if time == 6:
            self.image = game.load_image('player_down_left_2.png')
        if time == 12:
            self.image = game.load_image('player_down_left_3.png')
        if time == 18:
            self.image = game.load_image('player_down_left_4.png')
        if time == 24:
            self.image = game.load_image('player_down_left_5.png')

    def update_right_down(self, time):
        if not time:
            self.image = game.load_image('player_down_right_1.png')
        if time == 6:
            self.image = game.load_image('player_down_right_2.png')
        if time == 12:
            self.image = game.load_image('player_down_right_3.png')
        if time == 18:
            self.image = game.load_image('player_down_right_4.png')
        if time == 24:
            self.image = game.load_image('player_down_right_5.png')

    def update_right_up(self, time):
        if not time:
            self.image = game.load_image('player_up_right_1.png')
        if time == 6:
            self.image = game.load_image('player_up_right_2.png')
        if time == 12:
            self.image = game.load_image('player_up_right_3.png')
        if time == 18:
            self.image = game.load_image('player_up_right_4.png')

    def update_left_up(self, time):
        if not time:
            self.image = game.load_image('player_up_left_1.png')
        if time == 6:
            self.image = game.load_image('player_up_left_2.png')
        if time == 12:
            self.image = game.load_image('player_up_left_3.png')
        if time == 18:
            self.image = game.load_image('player_up_left_4.png')

    def death(self, timer):
        if timer == 8:
            self.image = game.load_image('player_death_1.png')
        if timer == 16:
            self.image = game.load_image('player_death_2.png')
        if timer == 24:
            self.image = game.load_image('player_death_3.png')
        if timer == 32:
            self.image = game.load_image('player_death_4.png')
        if timer == 40:
            self.image = game.load_image('player_death_5.png')
        if timer == 48:
            self.image = game.load_image('player_death_6.png')
        if timer == 56:
            self.image = game.load_image('player_death_7.png')
        if timer == 64:
            self.image = game.load_image('player_death_8.png')


class Button:
    def __init__(self, x, y, width, height, text, image, clicked_image=None, sound=None):
        self.x = x
        self.y = y
        self.width = width
        self.height = height
        self.text = text
        self.image = pygame.image.load(f'data/{image}')
        self.clicked_image = self.image
        if clicked_image:
            self.clicked_image = pygame.image.load(f'data/{clicked_image}')
        self.rect = self.image.get_rect().move(x, y)
        if sound:
            self.sound = pygame.mixer.Sound(f'data/{sound}')
        self.is_hover = False

    def show(self, screen):
        cur_image = self.clicked_image if self.is_hover else self.image
        screen.blit(cur_image, self.rect.topleft)
        font = pygame.font.Font(None, 36)
        scr_text = font.render(self.text, True, (255, 255, 255))
        text_rect = scr_text.get_rect(center=self.rect.center)
        screen.blit(scr_text, text_rect)

    def check_mouse(self, pos):
        self.is_hover = self.rect.collidepoint(pos)

    def check_event(self, event, vol):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 and self.is_hover:
            if self.sound:
                self.sound.play().set_volume(vol)
            pygame.event.post(pygame.event.Event(pygame.USEREVENT, button=self))


class Bullet(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, player_pos, fire_pos, type_of_bullet, dir):
        super().__init__(single_group, all_group)
        self.p_pos = player_pos
        self.f_pos = fire_pos
        self.type = type_of_bullet
        self.dx = player_pos[0] - fire_pos[0]
        self.dy = player_pos[1] - fire_pos[1]
        self.distance = math.hypot(self.dx, self.dy)
        self.dir = dir
        self.image = pygame.image.load('data/simple_bullet.png') if self.type == 'simple' else pygame.image.load('data/bust_bullet.png')
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect().move(self.p_pos[0], self.p_pos[1])
        if self.distance > 0:
            self.dx /= self.distance
            self.dy /= self.distance

    def update(self):
        self.rect.x -= self.dx * 30
        self.rect.y -= self.dy * 30


class Enemy_bullet(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, en_pos, player_pos, dir):
        super().__init__(single_group, all_group)
        self.p_pos = player_pos
        self.en_pos = en_pos
        self.dx = en_pos[0] - player_pos[0]
        self.dy = en_pos[1] - player_pos[1]
        self.distance = math.hypot(self.dx, self.dy)
        self.dir = dir
        self.image = pygame.image.load('data/en_bullet.png')
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect().move(self.en_pos[0], self.en_pos[1])
        if self.distance > 0:
            self.dx /= self.distance
            self.dy /= self.distance
        self.map_x_r = 0
        self.map_y_top = 0
        self.map_x_l = 0
        self.map_y_bot = 0

    def update(self):
        self.rect.x -= self.dx * 20
        self.rect.y -= self.dy * 20