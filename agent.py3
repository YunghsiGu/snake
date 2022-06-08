from matplotlib.pyplot import cla
import torch
import random
import numpy as np
from collections import deque   # struct
from copy import Snake, Direction, Point

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001          # Learing rate

class Agent:
    def __init__(self):
        self.num_games = 0  # number of game
        self.epsilon = 0    # control randomness
        self.gamma = 0      # discount rate
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        # TODO: model, trainer

    def get_state(self, Snake):
        head = Snake.snakeBodys[0]
        point_l = Point(head.x - 20, head.y)    # left
        point_r = Point(head.x + 20, head.y)    # right
        point_u = Point(head.x, head.y - 20)    # up
        point_d = Point(head.x, head.y + 20)    # down

        dir_l = Snake.nextDirection == Direction.LEFT
        dir_r = Snake.nextDirection == Direction.RIGHT
        dir_u = Snake.nextDirection == Direction.UP
        dir_d = Snake.nextDirection == Direction.DOWN

        state = [
            # danger straight
            (dir_r and Snake.is_collision(point_r)) or
            (dir_l and Snake.is_collision(point_l)) or
            (dir_u and Snake.is_collision(point_u)) or
            (dir_d and Snake.is_collision(point_d)),

            # danger right
            (dir_u and Snake.is_collision(point_r)) or
            (dir_d and Snake.is_collision(point_l)) or
            (dir_l and Snake.is_collision(point_u)) or
            (dir_r and Snake.is_collision(point_d)),

            # danger left
            (dir_d and Snake.is_collision(point_r)) or
            (dir_u and Snake.is_collision(point_l)) or
            (dir_r and Snake.is_collision(point_u)) or
            (dir_l and Snake.is_collision(point_d)),

            # move direction
            dir_l, dir_r, dir_u, dir_d,

            # food location
            Snake.foodPosition.x < Snake.snakePosition.x,   # food left
            Snake.foodPosition.x > Snake.snakePosition.x,   # food right
            Snake.foodPosition.y < Snake.snakePosition.y,   # food up
            Snake.foodPosition.y > Snake.snakePosition.y,   # food down
        ]

        return np.array(state, dtype=int)

    def remember(self, state, action, reward, next_state, done):
        pass

    def train_long_memory(self):
        pass

    def train_short_memory(self, state, action, reward, next_state, done):
        pass

    def get_action(self):
        pass

def train():
    plot_scores = []
    plot_mean_scores = []
    total_score = 0
    record = 0
    agent = Agent()
    game = Snake()
    while True:
        # get_old_state
        state_old = agent.get_state(game)

        # get_move
        final_move = agent.get_action(state_old)

        # perform move and get new state
        reward, done, score = game.start(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:    # game over
            game.reset()
            agent.num_games += 1
            agent.train_long_memory()

            if score > record:
                record = score
                # agent.model.save()

            print('Game', agent.num_games, 'Score', score, 'Record', record)

            # TODO: plot

if __name__ == '__main__':
    train()