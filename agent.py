import torch
import random
import numpy as np
from collections import deque   # Doubly Ended Queue 可以從兩端操作的 list
from snakeAI import Snake_G, Direction, Point
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
        head = game.snakePosition
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
            game.foodPosition.x < head.x,  # food left
            game.foodPosition.x > head.x,  # food right
            game.foodPosition.y < head.y,  # food up
            game.foodPosition.y > head.y  # food down
        ]

        return np.array(state, dtype=int)   # 把 state 變成 numpy array 且以 1 或 0 表示

    def get_state_y(self, game) -> np.ndarray:
        head = game.snake_y.snakePosition
        point_l = Point(head.x - 20, head.y)    # 蛇頭往左一格的點
        point_r = Point(head.x + 20, head.y)    # 右
        point_u = Point(head.x, head.y - 20)    # 上
        point_d = Point(head.x, head.y + 20)    # 下
        
        dir_l = game.snake_y.direction == Direction.LEFT    # 方向左
        dir_r = game.snake_y.direction == Direction.RIGHT   # 右
        dir_u = game.snake_y.direction == Direction.UP      # 上
        dir_d = game.snake_y.direction == Direction.DOWN    # 下

        # 紀錄當前遊戲狀態，包括往哪走會掛掉、目前移動方向、食物在哪，以 boolean 表示
        state = [
            # Danger straight (若繼續直走，遊戲結束)
            (dir_r and game.opponent_collision(point_r)) or 
            (dir_l and game.opponent_collision(point_l)) or 
            (dir_u and game.opponent_collision(point_u)) or 
            (dir_d and game.opponent_collision(point_d)),

            # Danger right (若往當前方向順時針移轉一次的方向走，遊戲結束)
            (dir_u and game.opponent_collision(point_r)) or 
            (dir_d and game.opponent_collision(point_l)) or 
            (dir_l and game.opponent_collision(point_u)) or 
            (dir_r and game.opponent_collision(point_d)),

            # Danger left (若往當前方向逆時針移轉一次的方向走，遊戲結束)
            (dir_d and game.opponent_collision(point_r)) or 
            (dir_u and game.opponent_collision(point_l)) or 
            (dir_r and game.opponent_collision(point_u)) or 
            (dir_l and game.opponent_collision(point_d)),

            # move direction (當前移動方向)
            dir_l, dir_r, dir_u, dir_d,

            # food location (食物之於蛇頭的方位)
            game.foodPosition.x < head.x,  # food left
            game.foodPosition.x > head.x,  # food right
            game.foodPosition.y < head.y,  # food up
            game.foodPosition.y > head.y  # food down
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
        if random.randint(0, 300) < self.epsilon:
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
    game = Snake_G()

    plot_scores_y = []        # 記錄每次分數 (繪圖用)
    plot_mean_scores_y = []   # 記錄平均分數
    total_score_y = 0
    record_y = 0
    agent_y = Agent()

    while True:
        # get_old_state
        state_old = agent.get_state(game)
        state_old_y = agent_y.get_state_y(game)

        # get_move
        final_move = agent.get_action(state_old)
        final_move = np.array(final_move, int)
        final_move_y = agent_y.get_action(state_old_y)
        final_move_y = np.array(final_move_y, int)

        # perform move and get new state
        reward, done, score, reward_y, score_y = game.start(final_move, final_move_y)
        state_new = agent.get_state(game)
        state_new_y = agent_y.get_state_y(game)

        # train short memory
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent_y.train_short_memory(state_old_y, final_move_y, reward_y, state_new_y, done)

        # remember
        agent.remember(state_old, final_move, reward, state_new, done)
        agent_y.remember(state_old_y, final_move_y, reward_y, state_new_y, done)

        if done:    # game over
            # train long memory, plot result
            game.reset()
            agent.num_games += 1
            agent_y.num_games += 1
            agent.train_long_memory()
            agent_y.train_long_memory()

            if score > record:  # 更新紀錄
                record = score
                agent.model.save('green_snake.pth')
            
            if score_y > record_y:
                record_y = score_y
                agent_y.model.save('yellow_snake.pth')

            print('Game', agent.num_games)
            print('Green:\t', 'Score', score, 'Record', record)
            print('YELLOW:\t', 'Score', score_y, 'Record', record_y)

            plot_scores.append(score)
            plot_scores_y.append(score_y)
            total_score += score
            total_score_y += score_y
            mean_score = total_score / agent.num_games
            mean_score_y = total_score_y / agent_y.num_games
            plot_mean_scores.append(mean_score)
            plot_mean_scores_y.append(mean_score_y)
            plot(plot_scores, plot_mean_scores, 'GREEN')
            plot(plot_scores_y, plot_mean_scores_y, 'YELLOW')

if __name__ == '__main__':
    train()