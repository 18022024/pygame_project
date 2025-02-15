import os
import sys
import pytmx
import pygame
import classes
import constants
import random


def load_level(filename):
    filename = "maps/" + filename
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]
    return level_map


maps = {
    1: ['map1.tmx', load_level('map1.txt'), [2, 2], [[24, 7], [23, 7], [24, 8], [23, 8]]]
}


def choose_map():
    return maps[random.choice([i for i in maps])]
