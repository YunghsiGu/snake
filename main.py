# 做 AI 用的簡化版遊戲
# 引入模組, 並利用 button 模組引入 button.py 檔案(class Button())
import random, pygame
from pygame.locals import *
from enum import Enum
from collections import namedtuple
import numpy as np

# 初始化 pygame
pygame.init()

# 字體
def font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

# 方向
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# 呃應該是一個 tuple, 用 x, y 來表示 index
Point = namedtuple('Point', 'x, y')

# color
SNAKE_BODY_COLOR = pygame.Color(0, 255, 0) 
FOOD_COLOR = pygame.Color(255, 0, 0)
BLACK = (0,0,0)

class Snake:    # 對應到 SnakeGame
    # 初始化設定值
    def __init__(self, w=1280, h=660):  # 因為螢幕大小的關係，我有調過
        # 遊戲畫面大小
        self.w = w
        self.h = h

        # init display
        self.screen = pygame.display.set_mode((self.w, self.h))   # 設定視窗與邊界大小
        pygame.display.set_caption("Snake") # 視窗標題

        self.clock = pygame.time.Clock()

        # init game state
        self.reset()

    def reset(self):
        # init game state
        self.direction = Direction.RIGHT

        self.snakePosition = Point(200, 200) # head             
        self.snakeBodys = [self.snakePosition, Point(180, 200), Point(160, 200)] 
        """ snakeBodys:
        self.head, 
        Point(self.head.x - BLOCK_SIZE, self.head.y),
        Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)
        """
        self.foodPosition = Point(500, 500) # 食物位置
        self._place_food()
        self.is_animating = True    # 是否繼續執行 start()

        self.score = 0
        self.foodNumber = 1     # 隨著遊戲進展加速用       
        self.speed = 40         # 我很爛所以調很慢, 你們可以改
        self.frame_iteration = 0
        
    def _place_food(self):
        # 食物長在邊界有點過分所以調了一下 XDD
        x = random.randint(0, (self.w-20 )//20 )
        y = random.randint(0, (self.h-20 )//20 )
        self.foodPosition = Point(x * 20, y * 20)       
        if self.foodPosition in self.snakeBodys:
            self._place_food() 
    
    # 蛇蛇遊戲本身
    def start(self, action):    # 對應到 play_step
        self.frame_iteration += 1

        # speed up
        if self.foodNumber % 5 == 0:
            self.speed += 1
            self.foodNumber = 1
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()

        # 2. move
        self._move(action) # update the head
        self.snakeBodys.insert(0, self.snakePosition)

        # 3. check if game over
        reward = 0
        self.is_animating = True
        if self.is_collision() or self.frame_iteration > 100 * len(self.snakeBodys):
            self.is_animating = False
            reward = -10
            return reward, not self.is_animating, self.score

        # 4. place new food or just move
        if self.snakePosition == self.foodPosition:
            self.score += 1
            self.foodNumber += 1
            reward = 10
            self._place_food()
        else:
            self.snakeBodys.pop()

        # 5. update ui and clock
        self._update_ui()
        self.clock.tick(self.speed)

        # 6. return is_animating and score
        return reward, not self.is_animating, self.score
    
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

    # 更新畫面
    def _update_ui(self):
        self.screen.fill(BLACK)

        for position in self.snakeBodys:
            pygame.draw.rect(self.screen, SNAKE_BODY_COLOR, Rect(position.x, position.y, 20, 20))
            pygame.draw.rect(self.screen, FOOD_COLOR, Rect(self.foodPosition.x, self.foodPosition.y, 20, 20))
        
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
        else:   # turn left
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

        
    
