import random


def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


maps = {
    #1: ['map1.tmx', load_level('map1.txt')],
    #2: ['map2.tmx', load_level('map2.txt')],
    #3: ['map3.tmx', load_level('map3.txt')],
    #4: ['map4.tmx', load_level('map4.txt')],
    5: ['map5.tmx', load_level('map5.txt')]
}


def choose_map():
    return maps[random.choice([i for i in maps])]
