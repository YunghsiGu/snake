# 引入模組, 並利用 button 模組引入 button.py 檔案(class Button())
import random, pygame
from pygame.locals import *
from enum import Enum
from collections import namedtuple
import numpy as np

# 初始化 pygame 與專門處理音樂播放的 pygame.mixer
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

'''
檔案載入, 除非我有寫錯不然可以不要看它
'''
# pictures
T0 = pygame.image.load("assets/Alert.png")
T0 = pygame.transform.scale(T0, (800, 535))
BG_main = pygame.image.load("assets/Optionbackground.jpg")
BG_main = pygame.transform.scale(BG_main, (1280, 720))
background1 = pygame.image.load("assets/Background.jpg")
background2 = pygame.image.load("assets/Background2.jpg")


# 初始畫面的字
menu_text = font(100).render("Snake", True, "#921AFF")
menu_rect = menu_text.get_rect(center=(640, 100))

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

        # original center position of the surface
        self.pivot = Point(640, 360)
        
        # init game state
        self.reset()

    def reset(self):
        # init game state
        self.currentDirection = Direction.RIGHT
        self.nextDirection = Direction.RIGHT

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
        self.speed = 20         # 我很爛所以調很慢, 你們可以改

        self.selection_image = 2 # Background image
        self.frame_iteration = 0
        
    def _place_food(self):
        # 食物長在邊界有點過分所以調了一下 XDD
        x = random.randrange(2, 63)
        y = random.randrange(2, 35)
        self.foodPosition = Point(x * 20, y * 20)       
        if self.foodPosition in self.snakeBodys:
            self._place_food() 
    
    # 蛇蛇遊戲本身
    def start(self, action):    # 對應到 play_step
        self.frame_iteration += 1

        # 設定主畫面背景調整為視窗大小
        if self.selection_image == 1:
            BG = background1
        elif self.selection_image == 2:
            BG = background2
        # 調整為視窗大小
        BG = pygame.transform.scale(BG, (self.w, self.h))
        self.screen.blit(BG, (0, 0))        
        self._update_ui()

        '''
        將Start視窗的內容標題訂為 "Insert the URL at here" 並將文字顏色設定為 #AE8F00,
        文字中心座標位於 (640, 100), 字體大小為 75
        PLAY_TEXT = font(75).render("Insert the URL at here", True, "#AE8F00")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 100))
        screen.blit(PLAY_TEXT, PLAY_RECT)
        '''
        
        # speed up
        if self.foodNumber % 5 == 0:
            self.speed += 1
            self.foodNumber = 1

        for position in self.snakeBodys:
            pygame.draw.rect(self.screen, SNAKE_BODY_COLOR, Rect(position.x, position.y, 20, 20))
            pygame.draw.rect(self.screen, FOOD_COLOR, Rect(self.foodPosition.x, self.foodPosition.y, 20, 20))
        self._update_ui()
        self.clock.tick(75)
        
        # 1. collect user input
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.is_animating = False
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
            return reward, self.is_animating, self.score

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
        return reward, self.is_animating, self.score
    
    # 有沒有撞到
    def is_collision(self, pt=None):
        if pt == None:
            pt = self.snakePosition

        # hits boundary
        if pt.x > 1279 or pt.x < 0:
            return True
        elif pt.y > 719 or pt.y < 0:
            return True
        else:
            return False

    # 更新畫面
    def _update_ui(self):
        pygame.display.flip()

    # 移動
    def _move(self, action):
        # [straight, right, left]

        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        idx = clock_wise.index(self.nextDirection)

        if np.array_equal(action, [1, 0, 0]):   # no change
            new_dir = clock_wise[idx]
        elif np.array_equal(action, [0, 1, 0]): # turn right
            next_idx = (idx + 1) % 4
            new_dir = clock_wise[next_idx]
        else:   # turn left
            next_idx = (idx - 1) % 4
            new_dir = clock_wise[next_idx]

        self.nextDirection = new_dir

        # Point 裡的值不能做調整, 所以用 x, y 來暫存, 之後修改 snakePosition
        x = self.snakePosition.x
        y = self.snakePosition.y

        if self.nextDirection == Direction.RIGHT and self.currentDirection != Direction.LEFT:
            is_change = True
        elif self.nextDirection == Direction.LEFT and self.currentDirection != Direction.RIGHT:
            is_change = True           
        elif self.nextDirection == Direction.UP and self.currentDirection != Direction.DOWN:
            is_change = True
        elif self.nextDirection == Direction.DOWN and self.currentDirection != Direction.UP:
            is_change = True
        else:
            is_change = False

        if is_change:
            self.currentDirection = self.nextDirection

        if self.currentDirection == Direction.RIGHT:
            x += 20
        elif self.currentDirection == Direction.LEFT:
            x -= 20
        elif self.currentDirection == Direction.UP:
            y -= 20
        elif self.currentDirection == Direction.DOWN:
            y += 20

        self.snakePosition = Point(x, y)
    
    # 播背景的, 應該不用理它
    def background_display(self):
        
        # IMPORTANT! MUST UPDATE THE BACKGROUND BEFORE BLITTING THE PNG IMAGE!
        BG = background1
        BG = pygame.transform.scale(BG, (self.w, self.h))
        self.screen.blit(BG, (0, 0))
        
    