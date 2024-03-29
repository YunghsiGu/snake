# 此為完整的遊戲本體(純遊戲，不含AI部分)。

# 引入模組, 並利用 button 模組引入 button.py 檔案(class Button())
import random, pygame, time, os
from pygame.locals import *
from button import Button
from enum import Enum
from collections import namedtuple

# 初始化 pygame 與專門處理音樂播放的 pygame.mixer
pygame.init()
pygame.mixer.init()

# 字體
def font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font(os.path.join('assets', 'font.ttf'), size)   # 支援跨平台

# 時間
time_counter = 0
pygame.time.set_timer(pygame.USEREVENT, 1000)

# 方向
class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# 一個 tuple, 用 x, y 來表示 index
Point = namedtuple('Point', 'x, y')

# color
SNAKE_BODY_COLOR = pygame.Color(0, 255, 0) 
FOOD_COLOR = pygame.Color(255, 0, 0)

'''
檔案載入
'''
# music
button_sfx = pygame.mixer.Sound(os.path.join('sound', 'press.wav')) # 支援跨平台
quit_sfx = pygame.mixer.Sound(os.path.join('sound', 'quit.wav'))
background_music = pygame.mixer.Sound(os.path.join('sound', 'BGM.mp3'))
# 無限循環撥放 background_music (註：只撥放一次為()；無限循環撥放則為(-1))
background_music.play(-1)
# pictures
point_on = pygame.image.load(os.path.join('assets', 'ChangeRectHover.png'))
point_start = pygame.image.load(os.path.join('assets', 'StartRectHover.png'))
point_option = pygame.image.load(os.path.join('assets', 'OptionRectHover.png'))
point_quit = pygame.image.load(os.path.join('assets', 'QuitRectHover.png'))
point_ok = pygame.image.load(os.path.join('assets', 'OkHover.png'))
point_cancel = pygame.image.load(os.path.join('assets', 'CancelHover.png'))
point_paste = pygame.image.load(os.path.join('assets', 'PasteHover.png'))
point_remove = pygame.image.load(os.path.join('assets', 'RemoveHover.png'))
A0 = pygame.image.load(os.path.join('assets', 'Alert.png'))
T0 = pygame.transform.scale(A0, (800, 535))
bg_main = pygame.image.load(os.path.join('assets', 'Optionbackground.jpg'))
bg_main = pygame.transform.scale(bg_main, (1280, 720))
background1 = pygame.image.load(os.path.join('assets', 'Background.jpg'))
background2 = pygame.image.load(os.path.join('assets', 'Background2.jpg'))
ring = pygame.image.load(os.path.join('assets', 'ring.png'))
arc1 = pygame.image.load(os.path.join('assets', 'arc1.png'))
arc2 = pygame.image.load(os.path.join('assets', 'arc2.png'))
QuitRect = pygame.image.load(os.path.join('assets', 'QuitRect.png'))
OptionRect = pygame.image.load(os.path.join('assets', 'OptionRect.png'))
StartRect = pygame.image.load(os.path.join('assets', 'StartRect.png'))
CancelNormal = pygame.image.load(os.path.join('assets', 'CancelNormal.png'))
OkNormal = pygame.image.load(os.path.join('assets', 'OkNormal.png'))
icon = pygame.image.load(os.path.join('assets', 'icon.png'))

# 初始畫面的字
menu_text = font(100).render("Snake", True, "#921AFF")
menu_rect = menu_text.get_rect(center=(640, 100))

class Snake:    
    def __init__(self, w=1280, h=720): 
        # 遊戲畫面大小
        self.w = w
        self.h = h

        # init display
        self.screen = pygame.display.set_mode((self.w, self.h))     # 設定視窗與邊界大小
        pygame.display.set_caption("Snake") # 視窗標題
        pygame.display.set_icon(icon)       # 設定 icon
        # 在轉的那些圖片
        ring.convert_alpha()
        self.arc1 = pygame.transform.scale(arc1.convert_alpha(), (ring.get_width() * 1.5, ring.get_height() * 1.5))
        self.arc2 = pygame.transform.scale(arc2.convert_alpha(), (ring.get_width() * 2, ring.get_height() * 2))
        self.clock = pygame.time.Clock()

        # original center position of the surface
        self.pivot = Point(640, 360)

        # This offset vector will be added to the pivot point, so the
        # resulting rect will be blitted at `rect.topleft + offset`.
        self.offset = pygame.math.Vector2(50, 0)
        self.ring_angle = 0
        self.arc1_angle = 0
        self.arc2_angle = 0
        
        self.selection_image = 2 # Background image
        
        # init game state
        self.reset()

    def reset(self):
        # init game state
        self.reset_button()
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
        self.move_counter = 0
        self.foodNumber = 1     # 隨著遊戲進展加速用
        self.speed = 50    
        
    # 重設 button 們使用的圖片
    def reset_button(self):
        ''' button:
        按鈕圖像; 文字中心座標; 按鈕上文字; 字體大小; 文字顏色; 游標指向它時的文字顏色       
        '''
        self.PLAY_BACK = Button(image=QuitRect, pos=(1100, 630), text_input="BACK", font=font(55), 
            base_color="Black", hovering_color="Green")
        self.PLAY_BUTTON1 = Button(image=OptionRect, pos=(610, 330), text_input="change", font=font(55), 
            base_color="Black", hovering_color="Green")
        self.PLAY_BUTTON2 = Button(image=OptionRect, pos=(960, 330), text_input="change", font=font(55), 
            base_color="Black", hovering_color="Green")
        self.options_watch_tutorial = Button(image=StartRect, pos=(610, 450), text_input="Watch", font=font(50), 
            base_color="Black", hovering_color="Green")
        self.options_ai_activation = Button(image=StartRect, pos=(610, 570), text_input="Activate", font=font(50), 
            base_color="Black", hovering_color="Green")
        self.OPTIONS_BACK = Button(image=QuitRect, pos=(1100, 630), text_input="BACK", font=font(55), 
            base_color="Black", hovering_color="Green")
        self.OK_BUTTON = Button(image=OkNormal, pos=(440, 520), text_input=None, font=font(55), 
            base_color="Black", hovering_color="Green")
        self.CANCEL_BUTTON = Button(image=CancelNormal, pos=(840, 520), text_input=None, font=font(55), 
            base_color="Black", hovering_color="Green")
        self.start_button = Button(image=StartRect, pos=(640, 250),
            text_input="START", font=font(55), base_color="Black", hovering_color="Green")
        self.options_button = Button(image=OptionRect, pos=(640, 400),
            text_input="OPTIONS", font=font(55), base_color="Black", hovering_color="Green")
        self.quit_button = Button(image=QuitRect, pos=(640, 550),
            text_input="QUIT", font=font(55), base_color="Black", hovering_color="Green") 
        self.respawn_button = Button(image=StartRect, pos=(640, 550), text_input="Respawn", font=font(55), 
            base_color="Black", hovering_color="Green")

    def _place_food(self):
        # 食物長在邊界有點過分所以調了一下 XDD
        x = random.randrange(1, (self.w - 20) // 20 - 1)
        y = random.randrange(1, (self.h - 20) // 20 - 1)
        self.foodPosition = Point(x * 20, y * 20)       
        if self.foodPosition in self.snakeBodys:
            self._place_food()

    def you_died_display(self):
        you_died_animating = True

        while you_died_animating:
            MENU_MOUSE_POS = pygame.mouse.get_pos()

            DIED1_TEXT = font(100).render("YOU DIED!", True, "Red")
            DIED1_RECT = DIED1_TEXT.get_rect(center=(640, 155))
            self.screen.blit(DIED1_TEXT, DIED1_RECT)

            DIED2_TEXT = font(60).render("Score: " + str(self.score), True, "White")
            DIED2_RECT = DIED2_TEXT.get_rect(center=(640, 350))
            self.screen.blit(DIED2_TEXT, DIED2_RECT)
            
            self.respawn_button.update(MENU_MOUSE_POS, point_start, self.screen)
            
            # user input
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.respawn_button.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        you_died_animating = False
           
            self.reset_button()
            pygame.display.flip()
            self.clock.tick(40)
    
    # 蛇蛇遊戲本身
    def start(self):
        start_animating = True
        
        global time_counter
        
        while start_animating:
    
            # 設定主畫面背景調整為視窗大小
            if self.selection_image == 1:
                bg = background1
                # 調整為視窗大小
                bg = pygame.transform.scale(bg.convert_alpha(), (self.w, self.h))
                self.screen.blit(bg, (0, 0))        
            elif self.selection_image == 2:
                bg = background2
                # 調整為視窗大小
                bg = pygame.transform.scale(bg.convert_alpha(), (self.w, self.h))
                self.screen.blit(bg, (0, 0))        
        
            PLAY_MOUSE_POS = pygame.mouse.get_pos() # 獲得滑鼠的位置

            self.PLAY_BACK.update(PLAY_MOUSE_POS, point_quit, self.screen)
        
            START1_TEXT = font(60).render("Score: " + str(self.score), True, "White")
            START1_RECT = START1_TEXT.get_rect(center=(200, 100))
            self.screen.blit(START1_TEXT, START1_RECT)
        
            START2_TEXT = font(60).render("Time: " + str(time_counter), True, "White")
            START2_RECT = START2_TEXT.get_rect(center=(560, 100))
            self.screen.blit(START2_TEXT, START2_RECT)
        
            START3_TEXT = font(60).render("Moves: " + str(self.move_counter), True, "White")
            START3_RECT = START3_TEXT.get_rect(center=(920, 100))
            self.screen.blit(START3_TEXT, START3_RECT)
        
            # speed up
            if self.foodNumber % 5 == 0:
                self.speed += 1
                self.foodNumber = 1

            self._update_ui()
            self.clock.tick(75)
            
            # 1. collect user input
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_animating = False
                    pygame.quit()
                # counting time
                if event.type == pygame.USEREVENT: 
                    time_counter += 1
                # user input
                if event.type == pygame.KEYDOWN:         
                    if (event.key == pygame.K_RIGHT or event.key == pygame.K_d) and self.direction != Direction.LEFT:
                        self.direction = Direction.RIGHT
                        self.move_counter += 1
                    elif (event.key == pygame.K_LEFT or event.key == pygame.K_a) and self.direction != Direction.RIGHT:
                        self.direction = Direction.LEFT
                        self.move_counter += 1
                    elif (event.key == pygame.K_UP or event.key == pygame.K_w) and self.direction != Direction.DOWN:
                        self.direction = Direction.UP
                        self.move_counter += 1
                    elif (event.key == pygame.K_DOWN or event.key == pygame.K_s) and self.direction != Direction.UP:
                        self.direction = Direction.DOWN
                        self.move_counter += 1
                # backpage
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                        button_sfx.play()
                        self.is_animating = False
                        return self.is_animating, self.score
    
            # 2. move
            self._move(self.direction) # update the head
            self.snakeBodys.insert(0, self.snakePosition)
    
            # 3. check if game over
            self.is_animating = True
            if self._is_collision():
                self.is_animating = False
                time_counter = 0
                game.you_died_display()
                return self.is_animating, self.score
    
            # 4. place new food or just move
            if self.snakePosition == self.foodPosition:
                self.score += 1
                self.foodNumber += 1
                self._place_food()
            else:
                self.snakeBodys.pop()
    
            # 5. update ui and clock
            self.reset_button()
            self._update_ui()
            self.clock.tick(self.speed)
    
            # 6. return is_animating and score
            return self.is_animating, self.score
    
    # 有沒有撞到
    def _is_collision(self):
        # hits boundary
        if self.snakePosition.x > self.w - 1 or self.snakePosition.x < 0:
            return True
        elif self.snakePosition.y > self.h - 1 or self.snakePosition.y < 0:
            return True
        # hits itself
        elif self.snakePosition in self.snakeBodys[1:]:
            return True
        else:
            return False

    # 更新畫面
    def _update_ui(self):
        for position in self.snakeBodys:
            pygame.draw.rect(self.screen, SNAKE_BODY_COLOR, Rect(position.x, position.y, 20, 20))
            pygame.draw.rect(self.screen, FOOD_COLOR, Rect(self.foodPosition.x, self.foodPosition.y, 20, 20))

        pygame.display.flip()

    # 移動
    def _move(self, direction):
        # Point 裡的值不能做調整, 所以用 x, y 來暫存, 之後修改 snakePosition
        x = self.snakePosition.x
        y = self.snakePosition.y

        if direction == Direction.RIGHT and self.direction != Direction.LEFT:
            x += 20
        elif direction == Direction.LEFT and self.direction != Direction.RIGHT:
            x -= 20         
        elif direction == Direction.UP and self.direction != Direction.DOWN:
            y -= 20
        elif direction == Direction.DOWN and self.direction != Direction.UP:
            y += 20            

        self.snakePosition = Point(x, y)
        
    # 定義 options 清單的函式
    def options(self):

        while True:
            flag = True

            # 偵測滑鼠游標位置
            OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

            # 將主畫面背景設為 bg_main, 並調整為視窗大小
            self.screen.blit(bg_main, (0, 0))
            
            '''
            1. 設定 Options 裡能夠更換背景的兩張圖片, 其中背景圖片 background1 為 Background.png, 
            背景圖片 background2 為 Background2.png
            2. 設定好這些圖片後, 利用 pygame.transform.scale 將原圖片大小調整成與視窗大小一致
            3. The screen object represents your game screen.
            screen.blit() is a thin wrapper around a Pygame surface that allows you 
            to easily draw images to the screen ("blit" them).
            '''
            
            # 一堆按鍵
            # 圖片顯示與縮放
            bg1 = pygame.transform.scale(background1, (160 * 2, 90 * 2))
            # 128 * 3, 72 * 3 --> 160 * 2, 90 * 2
            self.screen.blit(bg1, (450, 80))
            bg2 = pygame.transform.scale(background2, (160 * 2, 90 * 2))
            # 128 * 3, 72 * 3 --> 160 * 2, 90 * 2
            self.screen.blit(bg2, (800, 80))
            
            MENU_MOUSE_POS = pygame.mouse.get_pos() # 取得游標位置

            # PLAY 按鈕們
            self.PLAY_BUTTON1.update(MENU_MOUSE_POS, point_option, self.screen)
            self.PLAY_BUTTON2.update(MENU_MOUSE_POS, point_option, self.screen)
            
            # 設定字體大小; 設定 Options 視窗的標題內容; 設定文字顏色為 #00E3E3
            OPTIONS1_TEXT = font(50).render("Background Image", True, "#00E3E3")
            # 文字中心座標位於 (240, 90)
            OPTIONS1_RECT = OPTIONS1_TEXT.get_rect(center=(240, 90))
            self.screen.blit(OPTIONS1_TEXT, OPTIONS1_RECT)
            
            OPTIONS2_TEXT = font(50).render("Watch tutorial", True, "#00E3E3")
            OPTIONS2_RECT = OPTIONS2_TEXT.get_rect(center=(217, 450))
            self.screen.blit(OPTIONS2_TEXT, OPTIONS2_RECT)
            
            OPTIONS3_TEXT = font(50).render("AI activation", True, "#00E3E3")
            OPTIONS3_RECT = OPTIONS3_TEXT.get_rect(center=(217, 570))
            self.screen.blit(OPTIONS3_TEXT, OPTIONS3_RECT)
            
            self.options_watch_tutorial.update(MENU_MOUSE_POS, point_start, self.screen)
            self.options_ai_activation.update(MENU_MOUSE_POS, point_start, self.screen)
            self.OPTIONS_BACK.update(MENU_MOUSE_POS, point_quit, self.screen)
            
            # 使用者輸入
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
               
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                        button_sfx.play()   # 播放音效
                        flag = False
                    elif self.PLAY_BUTTON1.checkForInput(MENU_MOUSE_POS):   # 更換背景
                        button_sfx.play()
                        self.selection_image = 1
                    elif self.PLAY_BUTTON2.checkForInput(MENU_MOUSE_POS):   # 更換背景
                        button_sfx.play()
                        self.selection_image = 2
                    elif self.options_watch_tutorial.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        self.tutorial()
                    elif self.options_ai_activation.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()

            self.reset_button()
            pygame.display.flip()

            if not flag:
                break

    def quit(self):
        time.sleep(0.25)
        quit_sfx.play()
        is_quit_animating = True

        while is_quit_animating:
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            
            # 一堆互動
            global A0
            A0 = pygame.transform.scale(A0, (800, 535))
            self.screen.blit(A0, (240, 80))

            QUIT1_TEXT = font(50).render("Alert", True, "Black")
            QUIT1_RECT = QUIT1_TEXT.get_rect(center=(640, 155))
            self.screen.blit(QUIT1_TEXT, QUIT1_RECT)

            QUIT2_TEXT = font(50).render("Do you really want to quit?", True, "Black")
            QUIT2_RECT = QUIT2_TEXT.get_rect(center=(640, 330))
            self.screen.blit(QUIT2_TEXT, QUIT2_RECT)
            
            self.OK_BUTTON.update(MENU_MOUSE_POS, point_ok, self.screen)
            self.CANCEL_BUTTON.update(MENU_MOUSE_POS, point_cancel, self.screen)
            
            # 使用者輸入
            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.OK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        is_quit_animating = False
                        pygame.quit()
                    if self.CANCEL_BUTTON.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        is_quit_animating = False
            self.reset_button()
            pygame.display.flip()
            self.clock.tick(40)
    
    # 負責轉圈圈的那個
    def rotate(self, surface, angle):
        """
        Rotate the surface around the pivot point.

        Args:
            surface (pygame.Surface): The surface that is to be rotated.
            angle (float): Rotate by this angle.
            pivot (tuple, list, pygame.math.Vector2): The pivot point.
            offset (pygame.math.Vector2): This vector is added to the pivot.
        """
        rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
        rect = rotated_image.get_rect(center=self.pivot)
        return rotated_image, rect  # Return the rotated image and shifted rect.
    
    # 播背景的
    def background_display(self):
        self.ring_angle += 1
        self.arc1_angle += 1.5
        self.arc2_angle += 1.25
        
        # IMPORTANT! MUST UPDATE THE BACKGROUND BEFORE BLITTING THE PNG IMAGE!
        bg = background1
        bg = pygame.transform.scale(bg.convert_alpha(), (self.w, self.h))
        self.screen.blit(bg, (0, 0))
        
        # Rotated version of the image and the shifted rect.
        rotated_image, rect = self.rotate(ring, self.ring_angle)
        self.screen.blit(rotated_image, rect)  # Blit the rotated image.
        
        # Rotated version of the image and the shifted rect.
        rotated_image, rect = self.rotate(self.arc1, self.arc1_angle)
        self.screen.blit(rotated_image, rect)  # Blit the rotated image.
        
        # Rotated version of the image and the shifted rect.
        rotated_image, rect = self.rotate(self.arc2, self.arc2_angle)
        self.screen.blit(rotated_image, rect)  # Blit the rotated image.
    
    # 一長串的教學內容
    def tutorial(self):
        is_tutorial_animating = True

        while is_tutorial_animating:
            MENU_MOUSE_POS = pygame.mouse.get_pos()
            
            self.screen.blit(T0, (240, 80))

            '''
            遊戲教學內容
            '''
            TUTORIAL0_TEXT = font(50).render("Tutorial", True, "Black")
            TUTORIAL0_RECT = TUTORIAL0_TEXT.get_rect(center=(640, 155))
            self.screen.blit(TUTORIAL0_TEXT, TUTORIAL0_RECT)
            TUTORIAL1_TEXT = font(25).render("1. Use WASD or arrow keys to move.", True, "Black")
            TUTORIAL1_RECT = TUTORIAL1_TEXT.get_rect(center=(640, 260))
            self.screen.blit(TUTORIAL1_TEXT, TUTORIAL1_RECT)
            TUTORIAL2_TEXT = font(25).render("2. Once the snake eats the food, it will become longer.", True, "Black")
            TUTORIAL2_RECT = TUTORIAL2_TEXT.get_rect(center=(640, 295))
            self.screen.blit(TUTORIAL2_TEXT, TUTORIAL2_RECT)
            TUTORIAL3_TEXT = font(25).render('''3. If the snake hits the wall or bites itself, then game over.''', True, "Black")
            TUTORIAL3_RECT = TUTORIAL3_TEXT.get_rect(center=(640, 330))
            self.screen.blit(TUTORIAL3_TEXT, TUTORIAL3_RECT)
            TUTORIAL4_TEXT = font(25).render('''4. Collect as much food as you can.''', True, "Black")
            TUTORIAL4_RECT = TUTORIAL4_TEXT.get_rect(center=(640, 365))
            self.screen.blit(TUTORIAL4_TEXT, TUTORIAL4_RECT)
                      
            # 使用者點選
            self.OK_BUTTON.update(MENU_MOUSE_POS, point_ok, self.screen)
            self.CANCEL_BUTTON.update(MENU_MOUSE_POS, point_cancel, self.screen)

            for event in pygame.event.get():
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if self.OK_BUTTON.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        is_tutorial_animating = False

                        while self.is_animating:
                            self.is_animating, self.score = self.start()
                            if self.is_animating == False:
                                game.reset()
                                break

                    if self.CANCEL_BUTTON.checkForInput(MENU_MOUSE_POS):
                        button_sfx.play()
                        is_tutorial_animating = False
            self.reset_button()
            pygame.display.flip()
            self.clock.tick(30)


'''
input_box1 = InputBox(80, 200, 960, 96) #160 200 960 96
input_boxes = [input_box1]
'''

if __name__ == '__main__':
    game = Snake()

    while True:
        game.background_display()   
        menu_mouse_pos = pygame.mouse.get_pos()
        
        game.reset_button()
        game.screen.blit(menu_text, menu_rect)
               
        game.start_button.update(menu_mouse_pos, point_start, game.screen)
        game.options_button.update(menu_mouse_pos, point_option, game.screen)
        game.quit_button.update(menu_mouse_pos, point_quit, game.screen)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                # 判斷是否按下 PLAY 按鈕
                if game.start_button.checkForInput(menu_mouse_pos):
                    button_sfx.play()
                    game.tutorial()

                # 判斷是否按下 OPTIONS 按鈕
                elif game.options_button.checkForInput(menu_mouse_pos):
                    button_sfx.play()
                    game.options()

                # 判斷是否按下 QUIT 按鈕
                elif game.quit_button.checkForInput(menu_mouse_pos):
                    button_sfx.play()
                    game.quit()

        pygame.display.flip()

