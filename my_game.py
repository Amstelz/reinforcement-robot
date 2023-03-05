import os
import pygame

pygame.init()

WIDTH = 640
HEIGHT = 640
TITLE = 'Pac-Man'
LEVEL_PATH = 'levels/'
ASSETS_PATH = 'assets/'
WORLD_SIZE = 20
BLOCK_SIZE = 32
WIDTH = WORLD_SIZE*BLOCK_SIZE
HEIGHT = WORLD_SIZE*BLOCK_SIZE

world = []

def load_level(number):
    file = os.path.join(LEVEL_PATH, f'level{number}.txt')
    with open(file) as f:
        for line in f:
            row = []
            for block in line:
                row.append(block)
            world.append(row)

load_level(1)

char_to_image = {
    '.': os.path.join(ASSETS_PATH, 'dot.png'),
    '=': os.path.join(ASSETS_PATH, 'wall.png'),
    '*': os.path.join(ASSETS_PATH, 'power.png'),
}

def draw():
    screen.clear()
    for y, row in enumerate(world):
        for x, block in enumerate(row):
            image = char_to_image.get(block, None)
            if image:
                pygame.screen.blit(char_to_image[block], (x*BLOCK_SIZE, y*BLOCK_SIZE))

# Our sprites
pacman = Actor('pacman_o.png', anchor=('left', 'top'))
pacman.x = pacman.y = 1*BLOCK_SIZE

def on_key_down(key):
    if key == keys.LEFT:
        pacman.x += -BLOCK_SIZE
    if key == keys.RIGHT:
        pacman.x += BLOCK_SIZE
    if key == keys.UP:
        pacman.y += -BLOCK_SIZE
    if key == keys.DOWN:
        pacman.y += BLOCK_SIZE
