# 此為簡化版遊戲，供訓練AI使用。

import random, pygame
from pygame.locals import *

'''enum是Python裡用來建立枚舉形態的標準函式庫。
enum算是比較新的標準函式庫，特性為
1. 不同的 enum class 雖然有相同的 enum value，但比較結果是不相同的。
2. 透過 enum class 可以取得 enum member。
3. 透過 enum member 可以取得 name 或是 value。
4. 可以改用 enum 來比對型態。
enum適合用來1. 改寫以前單獨使用const variable的狀況。 2. 當資料數量不適合使用tuple，但用class卻太多的時候，可以考慮使用enum。'''
from enum import Enum
from collections import namedtuple
import numpy as np
'''os模組是關於作業系統操作呼叫的相關模組。它提供了一些系統級別的操作，例如對檔案進行重新命名、刪除等一系列操作。'''
import os

# 初始化 pygame
pygame.init()

# 定義字體的函式
def font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font(os.path.join('assets', 'font.ttf'), size)

# 方向
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# 一個 tuple, 用 x, y 來表示 index
Point = namedtuple('Point', 'x, y')

# 設定蛇的身體顏色、食物顏色、並定義黑色及黃色的色碼
SNAKE_BODY_COLOR = pygame.Color(0, 255, 0) 
FOOD_COLOR = pygame.Color(255, 0, 0)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)

class Snake_G:    # 對應到 SnakeGame。Snake_G負責綠蛇(Green Snake)的操作。
    # 初始化設定值
    def __init__(self, w=1280, h=720):
        # 設定遊戲畫面大小(寬度、高度)
        self.w = w
        self.h = h

        # init display
        self.screen = pygame.display.set_mode((self.w, self.h))   # 設定視窗與邊界大小
        pygame.display.set_caption("Snake") # 視窗標題

        self.clock = pygame.time.Clock()
        self.speed = 60 # 設定FPS為60
        self.snake_y = Snake_Y()

        # 使用reset()函式
        self.reset()

    def reset(self):
        # 初始化(部分)遊戲設定值
        self.direction = Direction.RIGHT

        self.snakePosition = Point(200, 200) # 蛇的頭部位置           
        self.snakeBodys = [self.snakePosition, Point(180, 200), Point(160, 200)]
        self.foodPosition = Point(500, 500) # 食物位置
        self._place_food() # 設置食物
        self.is_animating = True    # 判斷是否繼續執行 start()

        self.score = 0 # 重設綠蛇的分數為0
        self.frame_iteration = 0

        self.snake_y.reset()
        
    def _place_food(self):
        # 食物長在邊界有點過分所以調了一下 XDD
        x = random.randint(1, (self.w - 20) // 20 - 1)
        y = random.randint(1, (self.h - 20) // 20 - 1)
        self.foodPosition = Point(x * 20, y * 20)       
        if self.foodPosition in self.snakeBodys or self.foodPosition in self.snake_y.snakeBodys:
            self._place_food() 
    
    # 蛇蛇遊戲本身
    def start(self, action, action_y):    # 對應到 play_step
        self.frame_iteration += 1
        self.snake_y.frame_iteration += 1
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # 2. move
        self._move(action) # update the head
        self.snakeBodys.insert(0, self.snakePosition)
        self.snake_y._move(action_y)
        self.snake_y.snakeBodys.insert(0, self.snake_y.snakePosition)

        # 3. check if game over
        self.reward = 0
        self.snake_y.reward = 0
        self.is_animating = True
        if len(self.snakeBodys) > len(self.snake_y.snakeBodys):
            max = len(self.snakeBodys)
        else:
            max = len(self.snake_y.snakeBodys)
        if self.frame_iteration > 100 * max or self.snake_y.frame_iteration > 100 * max:
            self.is_animating = False
            self.reward = 0
            self.snake_y.reward = 0
            return self.reward, not self.is_animating, self.score, self.snake_y.reward, self.snake_y.score
        elif self.is_collision() and self.opponent_collision():
            self.is_animating = False
            self.reward = -10
            self.snake_y.reward = -10
            return self.reward, not self.is_animating, self.score, self.snake_y.reward, self.snake_y.score
        elif self.is_collision():
            self.is_animating = False
            self.reward = -10
            self.snake_y.reward = 10
            return self.reward, not self.is_animating, self.score, self.snake_y.reward, self.snake_y.score
        elif self.opponent_collision():
            self.is_animating = False
            self.reward = 10
            self.snake_y.reward = -10
            return self.reward, not self.is_animating, self.score, self.snake_y.reward, self.snake_y.score

        # 4. place new food or just move
        if self.snakePosition == self.foodPosition:
            self.score += 1
            self.reward = 10
            self.snake_y.snakeBodys.pop()
            self._place_food()
        elif self.snake_y.snakePosition == self.foodPosition:
            self.snake_y.score += 1
            self.snake_y.reward = 10
            self.snakeBodys.pop()
            self._place_food()
        else:
            self.snakeBodys.pop()
            self.snake_y.snakeBodys.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # 6. return is_animating and score
        return self.reward, not self.is_animating, self.score, self.snake_y.reward, self.snake_y.score
    
    # 判斷自己有沒有撞到
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snakePosition
        # hits boundary
        if pt.x > self.w - 20 or pt.x < 0:
            return True
        elif pt.y > self.h - 20 or pt.y < 0:
            return True
        # hits itself
        elif pt in self.snakeBodys[1:]:
            return True
        # hits the other
        elif pt in self.snake_y.snakeBodys:
            return True
        else:
            return False
        
    # 判斷對手(黃蛇)有沒有撞到
    def opponent_collision(self, pt=None):
        if pt is None:
            pt = self.snake_y.snakePosition
        # hits boundary
        if pt.x > self.w - 20 or pt.x < 0:
            return True
        elif pt.y > self.h - 20 or pt.y < 0:
            return True
        # hits itself
        elif pt in self.snake_y.snakeBodys[1:]:
            return True
        elif pt in self.snakeBodys:
            return True
        else:
            return False

    # 更新畫面
    def _update_ui(self):
        self.screen.fill(BLACK)

        for position in self.snakeBodys:
            pygame.draw.rect(self.screen, SNAKE_BODY_COLOR, Rect(position.x, position.y, 20, 20))
            pygame.draw.rect(self.screen, FOOD_COLOR, Rect(self.foodPosition.x, self.foodPosition.y, 20, 20))
        
        for position in self.snake_y.snakeBodys:
            pygame.draw.rect(self.screen, YELLOW, Rect(position.x, position.y, 20, 20))
        
        pygame.display.flip()

    # 移動
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):   # no change
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]): # turn right
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:                                   # turn left
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        # Point 裡的值不能做調整, 所以用 x, y 來暫存, 之後修改 snakePosition
        x = self.snakePosition.x
        y = self.snakePosition.y

        if self.direction == Direction.RIGHT:
            x += 20
        elif self.direction == Direction.LEFT:
             x -= 20         
        elif self.direction == Direction.UP:
            y -= 20
        elif self.direction == Direction.DOWN:
            y += 20

        self.snakePosition = Point(x, y)

class Snake_Y:    # 對應到 SnakeGame。Snake_Y負責黃蛇(Yellow Snake)的操作。
    # 初始化設定值
    def __init__(self):
        # 使用reset()函式
        self.reset()

    # 定義reset()函式
    def reset(self):
        # 預設移動方向為向左
        self.direction = Direction.LEFT

        self.snakePosition = Point(880, 320) # 蛇的頭部位置         
        self.snakeBodys = [self.snakePosition, Point(900, 320), Point(920, 320)] 

        self.score = 0 # 重設黃蛇的分數為0
        self.frame_iteration = 0    
        self.reward = 0
    
    # 有沒有撞到
    def is_collision(self, pt=None):
        if pt is None:
            pt = self.snakePosition
        # hits boundary
        if pt.x > self.w - 20 or pt.x < 0:
            return True
        elif pt.y > self.h - 20 or pt.y < 0:
            return True
        # hits itself
        elif pt in self.snakeBodys[1:]:
            return True
        else:
            return False

    # 移動
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]):   # no change
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]): # turn right
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:                                   # turn left
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.direction = new_dir

        # Point 裡的值不能做調整, 所以用 x, y 來暫存, 之後修改 snakePosition
        x = self.snakePosition.x
        y = self.snakePosition.y

        if self.direction == Direction.RIGHT:
            x += 20
        elif self.direction == Direction.LEFT:
             x -= 20         
        elif self.direction == Direction.UP:
            y -= 20
        elif self.direction == Direction.DOWN:
            y += 20

        self.snakePosition = Point(x, y)
