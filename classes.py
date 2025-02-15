import pygame
import game
import pytmx
import constants
import random


class Inventory(pygame.sprite.Sprite):
    def __init__(self, all_group, image):
        super().__init__(all_group)
        self.item_now = None
        self.all_items = {'heal': 0, 'bullet': 0}
        self.image = image
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.image.set_alpha(150)
        self.rect = self.image.get_rect().move(constants.SIZE[0] - 500, constants.SIZE[1] - 300)

    def get(self, item):
        self.item_now = item
        self.all_items[item] += 1


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
    def __init__(self, all_group, image, pos):
        super().__init__(all_group)
        self.image = image
        self.count = 6
        self.x = pos[0] + 15
        self.y = pos[1]
        self.rect = self.image.get_rect().move(self.x, self.y)

    def update_health(self, x, y):
        self.rect.x = x + 15
        self.rect.y = y

    def damage(self):
        self.count -= 1

    def update(self):
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


class Map:

    def __init__(self, filename, free_tile, finish_tile):
        self.map = pytmx.load_pygame(f'maps/{filename}')
        self.height = self.map.height
        self.width = self.map.width
        self.tile_size = self.map.tilewidth
        self.free_tiles = free_tile
        self.finish_tile = finish_tile

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
        self.time_afk = 0

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


class Atack(pygame.sprite.Sprite):
    def __init__(self, single_group, all_group, pos_x, pos_y):
        super().__init__(single_group, all_group)
        self.atacks = ['atack_1.png', 'atack_2.png', 'atack_3.png']
        self.image = game.load_image(self.atacks[0])
        self.image.set_colorkey(self.image.get_at((0, 0)))
        self.rect = self.image.get_rect().move(pos_x, pos_y)
        self.time = 0
        self.x = pos_x
        self.y = pos_y

    def update(self):
        self.time += 1
        if self.time == 3:
            self.image = game.load_image(self.atacks[1])
        if self.time == 6:
            self.image = game.load_image(self.atacks[2])
        self.image.set_colorkey(self.image.get_at((0, 0)))
        if self.time == 9:
            self.kill()


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
