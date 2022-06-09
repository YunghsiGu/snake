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
        self.model = None   # TODO
        self.trainer = None # TODO

    def get_state(self, Snake):
        head = Snake.snakeBodys[0]
        point_l = Point(head.x - 20, head.y)    # 蛇頭往左一格的點
        point_r = Point(head.x + 20, head.y)    # 右
        point_u = Point(head.x, head.y - 20)    # 上
        point_d = Point(head.x, head.y + 20)    # 下

        dir_l = Snake.nextDirection == Direction.LEFT#方向左
        dir_r = Snake.nextDirection == Direction.RIGHT#右
        dir_u = Snake.nextDirection == Direction.UP#上
        dir_d = Snake.nextDirection == Direction.DOWN#下

        state = [     #紀錄當前遊戲狀態，包括往哪走會掛掉、目前移動方向、食物在哪，以boolean表示
            # danger straight(若繼續直走，遊戲結束)
            (dir_r and Snake.is_collision(point_r)) or
            (dir_l and Snake.is_collision(point_l)) or
            (dir_u and Snake.is_collision(point_u)) or
            (dir_d and Snake.is_collision(point_d)),

            # danger right(若往當前方向順時針移轉一次的方向走，遊戲結束)
            (dir_u and Snake.is_collision(point_r)) or
            (dir_d and Snake.is_collision(point_l)) or
            (dir_l and Snake.is_collision(point_u)) or
            (dir_r and Snake.is_collision(point_d)),

            # danger left(若往當前方向逆時針移轉一次的方向走，遊戲結束)
            (dir_d and Snake.is_collision(point_r)) or
            (dir_u and Snake.is_collision(point_l)) or
            (dir_r and Snake.is_collision(point_u)) or
            (dir_l and Snake.is_collision(point_d)),

            # move direction(當前移動方向)
            dir_l, dir_r, dir_u, dir_d,

            # food location(食物之於蛇頭的方位)
            Snake.foodPosition.x < Snake.snakePosition.x,   # food left
            Snake.foodPosition.x > Snake.snakePosition.x,   # food right
            Snake.foodPosition.y < Snake.snakePosition.y,   # food up
            Snake.foodPosition.y > Snake.snakePosition.y,   # food down
        ]

        return np.array(state, dtype=int)#把state變成numpy array且以1或0表示

    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # pop left if MAX_MEMORY is reached

    def train_long_memory(self):
        if len(self.memory) > BATCH_SIZE:
            mini_sample = random.sample(self.memory, BATCH_SIZE)    # list of tuples
        else:
            mini_sample = self.memory
        
        states, actions, rewards, next_states, dones = zip(*mini_sample)
        self.trainer.train_step(states, actions, rewards, next_states, dones)
        """ equils to this
        for state, action, reward, next_state, done in mini_sample:
            self.trainer.train_step(state, action, reward, next_state, done) 
        """


    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    def get_action(self, state):
        # random moves: tradeoff exploration / exploiration
        self.epsilon = 80 - self.num_games
        final_move = [0, 0, 0]
        if random.randint(0, 200) < self.epsilon:
            move = random.randint(0, 2)
            final_move[move] = 1
        else:
            state0 = torch.tensor(state, dtype=torch.float)
            prediction = self.model.predict(state0)
            move = torch.argmax(prediction).item()
            final_move[move] = 1

        return final_move

def train():
    plot_scores = []   #記錄每次分數(繪圖用)
    plot_mean_scores = []   #記錄平均分數
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

            if score > record:  #更新紀錄
                record = score 
                # agent.model.save()

            print('Game', agent.num_games, 'Score', score, 'Record', record)

            # TODO: plot

if __name__ == '__main__':
    train()
