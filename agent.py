# 此為AI主體，引入了snakeAI.py，model.py與helper.py程式。執行此程式將開始訓練AI貪食蛇。

# PyTorch為製作機器學習常用的模組。
import torch
import random
import numpy as np
from collections import deque   # Doubly Ended Queue 可以從兩端操作的 list
# 引入snakeAI.py、model.py與helper.py三個程式。
from snakeAI import Snake_G, Direction, Point
from model import Linear_QNet, QTrainer
from helper import plot
'''os模組是關於作業系統操作呼叫的相關模組。它提供了一些系統級別的操作，例如對檔案進行重新命名、刪除等一系列操作，
將程式碼改用os的模式撰寫可以支援跨平臺。'''
import os
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE" # 在 Anaconda 及 pyTorch 中有相同的檔案，會出現 OMP#15 警告

MAX_MEMORY = 100_000 # 最大記憶體限制
BATCH_SIZE = 1000 # 設 miniBatch 每個iteration以10筆做計算
LR = 0.001          # Learing rate (學習率)。當找到學習方向後，還要決定一次走多遠，這個由此數值決定。
''' Think of the learning rate as a way of how quickly a network abandons the former value for the new. 
If the learning rate is 1, the new estimate will be the new Q-value.'''

class Agent:
    # 初始化設定值
    def __init__(self):
        self.num_games = 0  # number of game (遊戲場次數)
        self.epsilon = 0    # control randomness (用來控制貪食蛇移動的隨機程度，也就是在隨機移動與以訓練數據為標準進行移動之間做出取捨)
        self.gamma = 0.9    # discount rate, must < 1
        self.memory = deque(maxlen=MAX_MEMORY)  # popleft()
        '''This is just a feed-forward neural net with an input layer, a hidden layer, and an output layer.
        For the input layer, it gets the state: as we have 11 different boolean values of the state, we need
        this size 11 at the beginning; then we can choose a hidden size, and for the output layer, we need three outputs
        because then we have to predict the action. Now we have to train the model.
        關於此model的詳細介紹，以及為什麼輸入層有11個布林值，輸出層有3個布林值，中間還有一個hidden layer，請看書面報告。'''
        self.model = Linear_QNet(11, 256, 3)
        self.trainer = QTrainer(self.model, lr=LR, gamma=self.gamma)
        
    # 定義獲取貪食蛇(綠蛇)狀態的函式
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
            game.foodPosition.x < head.x,  # food left (食物在左邊)
            game.foodPosition.x > head.x,  # food right (食物在右邊)
            game.foodPosition.y < head.y,  # food up (食物在上面)
            game.foodPosition.y > head.y  # food down (食物在下面)
        ]

        return np.array(state, dtype=int)   # 把 state 變成 numpy array 且以 1 或 0 表示

    # 定義獲取貪食蛇(黃蛇)狀態的函式
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
            game.foodPosition.x < head.x,  # food left (食物在左邊)
            game.foodPosition.x > head.x,  # food right (食物在右邊)
            game.foodPosition.y < head.y,  # food up (食物在上面)
            game.foodPosition.y > head.y  # food down (食物在下面)
        ]
        return np.array(state, dtype=int)   # 把 state 變成 numpy array 且以 1 或 0 表示


    # 紀錄
    def remember(self, state, action, reward, next_state, done):
        self.memory.append((state, action, reward, next_state, done)) # popleft if MAX_MEMORY is reached
        
    # 定義訓練長期記憶的函式
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
    
    # 定義訓練短期記憶的函式
    def train_short_memory(self, state, action, reward, next_state, done):
        self.trainer.train_step(state, action, reward, next_state, done)

    # 決定下一步怎麼走(determine the next direction)
    def get_action(self, state):        
        # 在訓練150次之後再開始讓蛇使用訓練資料
        # if num_games >= 150, it will use its data to judge direction
        self.epsilon = 150 - self.num_games

        # the determination, only one of index is 1
        final_move = [0, 0, 0]

        # 隨機移動
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

# 定義訓練的函式
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
        # 獲取綠蛇與黃蛇分別的舊狀態 (get_old_state)
        state_old = agent.get_state(game)
        state_old_y = agent_y.get_state_y(game)

        # 決定綠蛇與黃蛇分別如何移動 (get_move)
        final_move = agent.get_action(state_old)
        final_move = np.array(final_move, int)
        final_move_y = agent_y.get_action(state_old_y)
        final_move_y = np.array(final_move_y, int)

        # 進行移動並獲取綠蛇與黃蛇分別的新的狀態 (perform move and get new state)
        reward, done, score, reward_y, score_y = game.start(final_move, final_move_y)
        state_new = agent.get_state(game)
        state_new_y = agent_y.get_state_y(game)

        # 訓練短期記憶 (train short memory)
        agent.train_short_memory(state_old, final_move, reward, state_new, done)
        agent_y.train_short_memory(state_old_y, final_move_y, reward_y, state_new_y, done)

        # 記住 (remember)
        agent.remember(state_old, final_move, reward, state_new, done)
        agent_y.remember(state_old_y, final_move_y, reward_y, state_new_y, done)

        if done:    # 遊戲結束 (game over)
            # 訓練長期記憶 (train long memory, plot result)
            game.reset()
            agent.num_games += 1
            agent_y.num_games += 1
            agent.train_long_memory()
            agent_y.train_long_memory()

            if score > record:  # 更新綠蛇紀錄
                record = score
                agent.model.save('green_snake.pth')
                
            if score_y > record_y:  # 更新黃蛇紀錄
                record_y = score_y
                agent_y.model.save('yellow_snake.pth')

            # 以格式化形式輸出遊戲場次、綠蛇及黃蛇分別的分數與最高記錄。
            print('Game', agent.num_games)
            print('Green:\t', 'Score', score, 'Record', record)
            print('YELLOW:\t', 'Score', score_y, 'Record', record_y)

            # 儲存資料。
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
