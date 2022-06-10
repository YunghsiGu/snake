import torch
import random
import numpy as np
from collections import deque   # Doubly Ended Queue 可以從兩端操作的 list
from main import Snake, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" # 在 Anaconda 及 pyTorch 中有相同的檔案，會出現 OMP#15 警告

MAX_MEMORY = 100_000
BATCH_SIZE = 1000
LR = 0.001          # Learing rate

class Agent:
    def __init__(self):
        self.num_games = 0  # number of game
        self.epsilon = 0    # control randomness
        self.gamma = 0.9    # discount rate, must < 1
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)

    def get_state(self, game) -> np.ndarray:
        head = game.snakeBodys[0]
        point_l = Point(head.x - 20, head.y)    # 蛇頭往左一格的點
        point_r = Point(head.x + 20, head.y)    # 右
        point_u = Point(head.x, head.y - 20)    # 上
        point_d = Point(head.x, head.y + 20)    # 下
        
        dir_l = game.direction == Direction.LEFT    # 方向左
        dir_r = game.direction == Direction.RIGHT   # 右
        dir_u = game.direction == Direction.UP      # 上
        dir_d = game.direction == Direction.DOWN    # 下

        # 紀錄當前遊戲狀態，包括往哪走會掛掉、目前移動方向、食物在哪，以 boolean 表示
        state = [
            # Danger straight (若繼續直走，遊戲結束)
            (dir_r and game.is_collision(point_r)) or 
            (dir_l and game.is_collision(point_l)) or 
            (dir_u and game.is_collision(point_u)) or 
            (dir_d and game.is_collision(point_d)),

            # Danger right (若往當前方向順時針移轉一次的方向走，遊戲結束)
            (dir_u and game.is_collision(point_r)) or 
            (dir_d and game.is_collision(point_l)) or 
            (dir_l and game.is_collision(point_u)) or 
            (dir_r and game.is_collision(point_d)),

            # Danger left (若往當前方向逆時針移轉一次的方向走，遊戲結束)
            (dir_d and game.is_collision(point_r)) or 
            (dir_u and game.is_collision(point_l)) or 
            (dir_r and game.is_collision(point_u)) or 
            (dir_l and game.is_collision(point_d)),

            # move direction (當前移動方向)
            dir_l, dir_r, dir_u, dir_d,

            # food location (食物之於蛇頭的方位)
            game.foodPosition.x < game.snakePosition.x,  # food left
            game.foodPosition.x > game.snakePosition.x,  # food right
            game.foodPosition.y < game.snakePosition.y,  # food up
            game.foodPosition.y > game.snakePosition.y  # food down
        ]

        return np.array(state, dtype=int)   # 把 state 變成 numpy array 且以 1 或 0 表示

    # 紀錄
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            # 選取樣本, 相同的樣本會被刪除
            mini_sample = random.sample(self.memory, BATCH_SIZE)    # list of tuples
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        states = np.array(states, int)  # 用 tuple 做 tensor 太慢, 所以轉成 ndarray
        actions = np.array(actions, int)
        next_states = np.array(next_states, int)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        """ equils to this
        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done) 
        """

    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    # determine the next direction
    def get_action(self, state):        
        # if num_games >= 100, it will use its data to judge direction
        self.epsilon = 100 - self.num_games

        # the determination, only one of index is 1
        final_move = [0, 0, 0]

        # random moves: tradeoff exploration
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model(state0)
            move = torch.argmax(prediction).item()  # find the max
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []        # 記錄每次分數 (繪圖用)
    plot_mean_scores = []   # 記錄平均分數
    total_score = 0
    record = 0
    agent = Agent()
    game = Snake()
    while True:
        # get_old_state
        state_old = agent.get_state(game)

        # get_move
        final_move = agent.get_action(state_old)
        final_move = np.array(final_move, int)

        # perform move and get new state
        reward, done, score = game.start(final_move)
        state_new = agent.get_state(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)

        if done:    # game over
            # train long memory, plot result
            game.reset()
            agent.num_games += 1
            agent.train_long_memory()

            if score > record:  # 更新紀錄
                record = score
                agent.model.save()

            print('Game', agent.num_games, 'Score', score, 'Record', record)

            plot_scores.append(score)
            total_score += score
            mean_score = total_score / agent.num_games
            plot_mean_scores.append(mean_score)
            plot(plot_scores, plot_mean_scores)

if __name__ == '__main__':
    train()