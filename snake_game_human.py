import os
import pygame
import random
from enum import Enum
from collections import namedtuple

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
SPEED = 5

char_to_image = {
    '.': os.path.join(ASSETS_PATH, 'dot.png'),
    '=': os.path.join(ASSETS_PATH, 'wall.png'),
    '*': os.path.join(ASSETS_PATH, 'power.png'),
}

class SnakeGame:
    
    def __init__(self, w=WIDTH, h=HEIGHT):
        self.w = w
        self.h = h
        self.world = []

        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption(TITLE)
        self.clock = pygame.time.Clock()
        
        # init game state
        self._load_level(1)
        self.direction = Direction.RIGHT
        
        self.head = Point(self.w/2 - BLOCK_SIZE, self.h/2 - BLOCK_SIZE) 
        self.snake = [self.head,
                      Point(self.head.x-BLOCK_SIZE, self.head.y),
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)]
        
        self.score = 0
        self.food = None

        self._place_food()
        
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
        if self.food == self.snake or self.world[y][x] == '=' or self.food in self.snake:
            self._place_food()
        else: 
            self.world[y][x] = '*'
    
    def play_step(self):
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_LEFT and self.direction != Direction.RIGHT:
                    self.direction = Direction.LEFT
                elif event.key == pygame.K_RIGHT and self.direction != Direction.LEFT:
                    self.direction = Direction.RIGHT
                elif event.key == pygame.K_UP and self.direction != Direction.DOWN:
                    self.direction = Direction.UP
                elif event.key == pygame.K_DOWN and self.direction != Direction.UP:
                    self.direction = Direction.DOWN
        
        # 2. move
        self._move(self.direction) # update the head
        self.snake.insert(0, self.head)

        # 3. check if game over
        game_over = False
        if self._is_collision():
            game_over = True
            return game_over, self.score
            
        # 4. place new food or just move
        if  self.head == self.food:
            self.score += 1
            self.world[self.food.y//BLOCK_SIZE][self.food.x//BLOCK_SIZE] = ''
            self._place_food()
        else:
            self.snake.pop()
        
        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(SPEED)

        # 6. return game over and score
        return game_over, self.score
    
    def _is_collision(self):
        # hits wall
        if self.world[int(self.head.y//BLOCK_SIZE)][int(self.head.x//BLOCK_SIZE)] == '=':
            return True 
        
        # hits itself
        if self.head in self.snake[1:]:
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
        
    def _move(self, direction):
        x = self.head.x
        y = self.head.y
        if direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif direction == Direction.UP:
            y -= BLOCK_SIZE
            
        self.head = Point(x, y)
            

if __name__ == '__main__':
    game = SnakeGame()
    
    # game loop
    while True:
        game_over, score = game.play_step()
        
        if game_over == True:
            break
        
    print('Final Score', score)
        
        
    pygame.quit()