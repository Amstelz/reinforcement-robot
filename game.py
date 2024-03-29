import os
import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)
#font = pygame.font.SysFont('arial', 25)

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

# rgb colors
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

TITLE = 'Robot'
LEVEL_PATH = 'levels/'
ASSETS_PATH = 'assets/'

WORLD_SIZE = 20
BLOCK_SIZE = 32
WIDTH = WORLD_SIZE*BLOCK_SIZE
HEIGHT = WORLD_SIZE*BLOCK_SIZE
SPEED = 120
LEVEL = 1

char_to_image = {
    '.': os.path.join(ASSETS_PATH, 'dot.png'),
    '=': os.path.join(ASSETS_PATH, 'wall.png'),
    '*': os.path.join(ASSETS_PATH, 'power.png'),
}

class SnakeGameAI:

    def __init__(self, w=WIDTH, h=HEIGHT):
        self.w = w
        self.h = h
        self.world = []
        self.world_size = WORLD_SIZE
        self.block_size = BLOCK_SIZE

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        self.reset()


    def reset(self):
        # init game state
        self.world.clear()
        self._load_level(LEVEL)
        self.direction = Direction.RIGHT

        self.head = Point(self.w/2 - BLOCK_SIZE, self.h/2 - BLOCK_SIZE)
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None

        self._place_food()
        self.frame_iteration = 0

    def _load_level(self, number):
        file = os.path.join(LEVEL_PATH, f'level{number}.txt')
        with open(file) as f:
            for line in f:
                row = []
                for block in line:
                    row.append(block)
                self.world.append(row)

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )
        self.food = Point(x*BLOCK_SIZE , y*BLOCK_SIZE )
        if self.world[y][x] == '=' or self.food in self.snake:
            self._place_food()
        else: 
            self.world[y][x] = '*'


    def play_step(self, action):
        self.frame_iteration += 1
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
        
        # 2. move
        self._move(action) # update the head
        self.snake.insert(0, self.head)
        
        # 3. check if game over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -10
            return reward, game_over, self.score

        # 4. place new food or just move
        if self.head == self.food:
            self.score += 1
            reward = 10
            self.world[self.food.y//BLOCK_SIZE][self.food.x//BLOCK_SIZE] = ''
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return reward, game_over, self.score

    
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head

        # hits wall
        if int(pt.y//BLOCK_SIZE) >= WORLD_SIZE or int(pt.x//BLOCK_SIZE) >= WORLD_SIZE or int(pt.y//BLOCK_SIZE) < 0 or int(pt.x//BLOCK_SIZE) < 0:
            return True
        if self.world[int(pt.y//BLOCK_SIZE)][int(pt.x//BLOCK_SIZE)] == '=':
            return True 
        
        # hits itself
        if pt in self.snake[1:]:
            return True

        return False


    def _update_ui(self):
        self.display.fill(BLACK)
        # draw world
        for y, row in enumerate(self.world):
            for x, block in enumerate(row):
                image_path = char_to_image.get(block, None)
                if image_path:
                    image = pygame.image.load(image_path)
                    self.display.blit(image, (x*BLOCK_SIZE, y*BLOCK_SIZE))

        # draw snake
        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12))
        
        # draw score
        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()


    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] # no change
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx] # right turn r -> d -> l -> u
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx] # left turn r -> u -> l -> d

        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE

        self.head = Point(x, y)