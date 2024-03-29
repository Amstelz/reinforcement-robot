import torch
import random
import numpy as np
from collections import deque
from game import SnakeGameAI, Direction, Point
from model import Linear_QNet, QTrainer, DQNet
from helper import plot

MAX_MEMORY = 1000_000
BATCH_SIZE = 1000
LR = 0.001

# MAX_MEMORY = 10000
# BATCH_SIZE = 32
# LR = 0.000001

class Agent:

    def __init__(self):
        self.n_games = 0
        self.epsilon = 0 # randomness
        self.gamma = 0.9 # discount rate
        self.memory = deque(maxlen=MAX_MEMORY) # popleft()
        self.model = Linear_QNet(11, 256, 3)
        # self.model = DQNet(1600, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    # old get_state
    def get_state(self, game):
        head = game.snake[0]
        point_l = Point(head.x - 32, head.y)
        point_r = Point(head.x + 32, head.y)
        point_u = Point(head.x, head.y - 32)
        point_d = Point(head.x, head.y + 32)

        dir_l = game.direction == Direction.LEFT
        dir_r = game.direction == Direction.RIGHT
        dir_u = game.direction == Direction.UP
        dir_d = game.direction == Direction.DOWN

        state = [
            # Danger straight
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),
            
            # Move direction
            dir_l,
            dir_r,
            dir_u,
            dir_d,
            
            # Food location 
            game.food.x < game.head.x,  # food left
            game.food.x > game.head.x,  # food right
            game.food.y < game.head.y,  # food up
            game.food.y > game.head.y,  # food down

            # head location 
            # int(head.y//game.block_size),
            # int(head.x//game.block_size),

            # body length
            # len(game.snake)
            ]

        return np.array(state, dtype=int)

    # def get_state(self, game):
    #     head = game.snake[0]
    #     body = game.snake[1:]
    #     world = game.world
    #     food = game.food

    #     head_matrix = np.zeros((game.world_size, game.world_size))
    #     head_matrix[int(head.y//game.block_size), int(head.x//game.block_size)] = 1

    #     body_matrix = np.zeros((game.world_size, game.world_size))
    #     for b in body:
    #         body_matrix[int(b.y//game.block_size), int(b.x//game.block_size)] = 1

    #     world_matrix = np.zeros((game.world_size, game.world_size))
    #     for i in range(game.world_size):
    #         for j in range(game.world_size):
    #             if world[i][j] == "=":
    #                 world_matrix[i][j] = 1

    #     food_matrix = np.zeros((game.world_size, game.world_size))
    #     food_matrix[int(food.y//game.block_size), int(food.x//game.block_size)] = 1

    #     state = np.array([head_matrix, body_matrix, world_matrix, food_matrix])
    #     state = state.reshape((1,1600))

    #     return state
    
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        # print('train long memory')
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE) # list of tuples
        else:
            mini_sample = self.memory

        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        #for state, action, reward, nexrt_state, done in mini_sample:
        #    self.trainer.train_step(state, action, reward, next_state, done)

    def train_short_memory(self, state, action, reward, next_state, done):
        # print('train short memory')
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploitation
        self.epsilon = 80 - self.n_games
        final_move = [0,0,0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move


def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = SnakeGameAI()
    while True:
        # get old state
        state_old = agent.get_state(game)

        # get move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.play_step(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:
            # train long memory, plot result
            game.reset()
            agent.n_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                agent.model.save()

            print('Game', agent.n_games, 'Score', score, 'Record:', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.n_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)


if __name__ == '__main__':
    train()