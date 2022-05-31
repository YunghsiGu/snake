# 引入random、pygame、sys、time、button、json模組，並利用button模組引入button.py檔案(class Button())
import random, pygame, sys, time
from pygame.locals import *
from button import Button


# 初始化pygame與專門處理音樂播放的pygame.mixer
pygame.init()
pygame.mixer.init()

button_sfx = pygame.mixer.Sound("SAOmenubutton.wav")
quit_sfx = pygame.mixer.Sound("SAOalert.wav")
# 載入名為Last Day On Earth OST - Global Map Theme的mp3檔，並儲存於soundwav2裡
background_music = pygame.mixer.Sound("Last Day On Earth OST - Global Map Theme.mp3")
#無限循環撥放background_music(註：只撥放一次為()；無限循環撥放則為(-1))
background_music.play(-1)

# 初始化設定值
name = ""
selection_image = 2
point_on = pygame.image.load("assets/Change Rect Hover.png")
point_start = pygame.image.load("assets/Start Rect Hover.png")
point_option = pygame.image.load("assets/Option Rect Hover.png")
point_quit = pygame.image.load("assets/Quit Rect Hover.png")
point_ok = pygame.image.load("assets/Ok Hover.png")
point_cancel = pygame.image.load("assets/Cancel Hover.png")
point_paste = pygame.image.load("assets/Paste Hover.png")
point_remove = pygame.image.load("assets/Remove Hover.png")
animating = True
# 設定視窗與邊界大小(原版為width = 600, height = 700)，依照長度=width，寬度(高度)=height來創建畫面
screen = pygame.display.set_mode((1280, 720))
# 將視窗標題訂為Snake
pygame.display.set_caption("Snake")
clock = pygame.time.Clock()

ring = pygame.image.load("assets/ring.png").convert_alpha()
RW, RH = ring.get_width(), ring.get_height()
arc1 = pygame.image.load("assets/arc1.png").convert_alpha()
arc1 = pygame.transform.scale(arc1, (RW * 1.5, RH * 1.5))
arc2 = pygame.image.load("assets/arc2.png").convert_alpha()
arc2 = pygame.transform.scale(arc2, (RW * 2, RH * 2))



# Store the original center position of the surface.
pivot = [640, 360]
# This offset vector will be added to the pivot point, so the
# resulting rect will be blitted at `rect.topleft + offset`.
offset = pygame.math.Vector2(50, 0)
ring_angle = 0
arc1_angle = 0
arc2_angle = 0

paste_flag = 0
remove_flag = 0

# 設定主畫面字型為assets資料夾內的font.ttf字型檔案
def get_font(size):  # Returns Press-Start-2P in the desired size
    return pygame.font.Font("assets/font.ttf", size)

def rotate(surface, angle, pivot, offset):
    """Rotate the surface around the pivot point.

    Args:
        surface (pygame.Surface): The surface that is to be rotated.
        angle (float): Rotate by this angle.
        pivot (tuple, list, pygame.math.Vector2): The pivot point.
        offset (pygame.math.Vector2): This vector is added to the pivot.
    """
    rotated_image = pygame.transform.rotozoom(surface, -angle, 1)  # Rotate the image.
    rect = rotated_image.get_rect(center=pivot)
    return rotated_image, rect  # Return the rotated image and shifted rect.

def background_display():
    global ring_angle
    global arc1_angle
    global arc2_angle
    ring_angle += 1
    arc1_angle += 1.5
    arc2_angle += 1.25
    
    # IMPORTANT! MUST UPDATE THE BACKGROUND BEFORE BLITTING THE PNG IMAGE!
    BG = pygame.image.load("assets/Background.jpg")
    BG = pygame.transform.scale(BG, (1280, 720))
    screen.blit(BG, (0, 0))
    
    # Rotated version of the image and the shifted rect.
    rotated_image, rect = rotate(ring, ring_angle, pivot, offset)
    screen.blit(rotated_image, rect)  # Blit the rotated image.
    
    # Rotated version of the image and the shifted rect.
    rotated_image, rect = rotate(arc1, arc1_angle, pivot, offset)
    screen.blit(rotated_image, rect)  # Blit the rotated image.
    
    # Rotated version of the image and the shifted rect.
    rotated_image, rect = rotate(arc2, arc2_angle, pivot, offset)
    screen.blit(rotated_image, rect)  # Blit the rotated image.
    clock.tick(75)

def tutorial():
    tutorial_animating = True
    while tutorial_animating:
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        
        T0 = pygame.image.load("assets/Alert.png")
        T0 = pygame.transform.scale(T0, (800, 535))
        screen.blit(T0, (240, 80))
        TUTORIAL0_TEXT = get_font(50).render("Tutorial", True, "Black")
        TUTORIAL0_RECT = TUTORIAL0_TEXT.get_rect(center=(640, 155))
        screen.blit(TUTORIAL0_TEXT, TUTORIAL0_RECT)
        TUTORIAL1_TEXT = get_font(25).render("1. Click the white box and wait until it becomes green, then insert the URL and press enter.", True, "Black")
        TUTORIAL1_RECT = TUTORIAL1_TEXT.get_rect(center=(640, 250))
        screen.blit(TUTORIAL1_TEXT, TUTORIAL1_RECT)
        TUTORIAL2_TEXT = get_font(25).render("2. After inserting the URL, choose one of the functions below to execute.", True, "Black")
        TUTORIAL2_RECT = TUTORIAL2_TEXT.get_rect(center=(640, 285))
        screen.blit(TUTORIAL2_TEXT, TUTORIAL2_RECT)
        TUTORIAL3_TEXT = get_font(25).render('''3. You can also use the "paste" and "delete" buttons to make the process easier;''', True, "Black")
        TUTORIAL3_RECT = TUTORIAL3_TEXT.get_rect(center=(640, 320))
        screen.blit(TUTORIAL3_TEXT, TUTORIAL3_RECT)
        TUTORIAL4_TEXT = get_font(25).render('''once you clicked those buttons, the text is ready to be pasted or removed.''', True, "Black")
        TUTORIAL4_RECT = TUTORIAL4_TEXT.get_rect(center=(640, 345))
        screen.blit(TUTORIAL4_TEXT, TUTORIAL4_RECT)
        TUTORIAL5_TEXT = get_font(25).render('''Press the space bar to confirm the action.''', True, "Black")
        TUTORIAL5_RECT = TUTORIAL5_TEXT.get_rect(center=(640, 370))
        screen.blit(TUTORIAL5_TEXT, TUTORIAL5_RECT)
        TUTORIAL6_TEXT = get_font(25).render("4. To watch this tutorial again, please go to the settings.", True, "Black")
        TUTORIAL6_RECT = TUTORIAL6_TEXT.get_rect(center=(640, 405))
        screen.blit(TUTORIAL6_TEXT, TUTORIAL6_RECT)
        
        OK_BUTTON = Button(image=pygame.image.load("assets/Ok Normal.png"), pos=(440, 520),
                                text_input=None, font=get_font(55), base_color="Black", hovering_color="Green")
        OK_BUTTON.update(MENU_MOUSE_POS, point_ok, screen)
        CANCEL_BUTTON = Button(image=pygame.image.load("assets/Cancel Normal.png"), pos=(840, 520),
                               text_input=None, font=get_font(55), base_color="Black", hovering_color="Green")
        CANCEL_BUTTON.update(MENU_MOUSE_POS, point_cancel, screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    button_sfx.play()
                    tutorial_animating = False
                    start()
                if CANCEL_BUTTON.checkForInput(MENU_MOUSE_POS):
                    button_sfx.play()
                    tutorial_animating = False
        pygame.display.flip()
        clock.tick(30)

def start():
    animating = True
    
    snakeBody_color = pygame.Color(0, 255, 0) 
    food_color = pygame.Color(255, 0, 0) 
    snakePosition = [200, 200]                       
    snakeBodys = [[200, 200], [180, 200], [160, 200]] 
    foodPosition = [500, 500]        
    foodTotal = 1                   
    foodNumber = 1                  
    direction = 'right'             
    changeDirection = direction     
    speed = 4
    
    while animating:

        # 將主畫面背景設為asset資料夾內的Background2.jpg，並自動調整為視窗大小
        if selection_image == 2:
            BG = pygame.image.load("assets/Background2.jpg")
            BG = pygame.transform.scale(BG, (1280, 720))
            screen.blit(BG, (0, 0))
        elif selection_image == 1:
            BG = pygame.image.load("assets/Background.jpg")
            BG = pygame.transform.scale(BG, (1280, 720))
            screen.blit(BG, (0, 0))
        
        # 更新畫面
        pygame.display.update()

        # 獲得滑鼠的位置
        PLAY_MOUSE_POS = pygame.mouse.get_pos()
        
        '''# 將Start視窗的內容標題訂為"Insert the URL at here"並將文字顏色設定為#AE8F00，文字中心座標位於(640, 100)，字體大小為75
        PLAY_TEXT = get_font(75).render("Insert the URL at here", True, "#AE8F00")
        PLAY_RECT = PLAY_TEXT.get_rect(center=(640, 100))
        screen.blit(PLAY_TEXT, PLAY_RECT)'''

        PLAY_BACK = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(1100, 630),
                           text_input="BACK", font=get_font(55), base_color="Black", hovering_color="Green")
        PLAY_BACK.update(PLAY_MOUSE_POS, point_quit, screen)

        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                animating = False
                pygame.quit()
                sys.exit()
            # 使用者開始輸入
            if event.type == pygame.KEYDOWN:
                # escape鍵以退出動畫
                if event.key == pygame.K_ESCAPE:
                    animating = False
                    pygame.quit()
                    sys.exit()
                if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                    changeDirection = 'right'

                if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                    changeDirection = 'left'
                    
                if event.key == pygame.K_UP or event.key == pygame.K_w:
                    changeDirection = 'up'
                    
                if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                    changeDirection = 'down'
            if event.type == pygame.MOUSEBUTTONDOWN:
                if PLAY_BACK.checkForInput(PLAY_MOUSE_POS):
                    button_sfx.play()
                    animating = False
        
        if changeDirection == 'right' and not direction == 'left':
            direction = changeDirection
            
        if changeDirection == 'left' and not direction == 'right':
            direction = changeDirection
            
        if changeDirection == 'up' and not direction == 'down':
            direction = changeDirection
            
        if changeDirection == 'down' and not direction == 'up':
            direction = changeDirection

        
        if direction == 'right':
            snakePosition[0] += 20
            
        if direction == 'left':
            snakePosition[0] -= 20
            
        if direction == 'up':
            snakePosition[1] -= 20
            
        if direction == 'down':
            snakePosition[1] += 20

        snakeBodys.insert(0, list(snakePosition))  
        
        
        if snakePosition[0] == foodPosition[0] and snakePosition[1] == foodPosition[1]:
            foodTotal = 0
        else:
            snakeBodys.pop()  

        
        if foodTotal == 0:
            x = random.randrange(1, 64)
            y = random.randrange(1, 36)
            foodPosition = [int(x * 20), int(y * 20)]
            foodTotal = 1
            foodNumber += 1    
            
        
        for body in snakeBodys[1:]:
            if foodPosition[0] == body[0] and foodPosition[1] == body[1]:
                foodTotal = 0
                foodNumber -=1

        
        if foodNumber % 5 ==0:
            speed += 1
            foodNumber = 1

        for position in snakeBodys:
            pygame.draw.rect(screen, snakeBody_color, Rect(position[0], position[1], 20, 20))
            pygame.draw.rect(screen, food_color, Rect(foodPosition[0], foodPosition[1], 20, 20))

        pygame.display.flip() 

        
        if snakePosition[0] > 1279 or snakePosition[0] < 0:
            animating = False
            pygame.quit()
            sys.exit()
            
        elif snakePosition[1] > 719 or snakePosition[1] < 0:
            animating = False
            pygame.quit()
            sys.exit()
            
        for body in snakeBodys[1:]:
            if snakePosition[0] == body[0] and snakePosition[1] == body[1]:
                animating = False
                pygame.quit()
                sys.exit()

        pygame.display.flip()
        clock.tick(30)

# 定義options清單的函式
def options():
    # 將變數selection_image設定為全域變數
    global selection_image
    while True:
        Flag = True
        # 偵測滑鼠游標位置
        OPTIONS_MOUSE_POS = pygame.mouse.get_pos()

        # 將主畫面背景設為asset資料夾內的Optionbackground.jpg，並自動調整為視窗大小
        BG_main = pygame.image.load("assets/Optionbackground.jpg")
        BG_main = pygame.transform.scale(BG_main, (1280, 720))
        screen.blit(BG_main, (0, 0))
        
        '''1.設定Options裡能夠更換背景的兩張圖片，其中背景圖片P1為Background.png，背景圖片P2為Background2.png
        2.設定好這些圖片後，利用pygame.transform.scale將原圖片大小調整成與視窗大小一致
        3.The screen object represents your game screen.
        screen.blit()is a thin wrapper around a Pygame surface that allows you 
        to easily draw images to the screen (“blit” them).'''
        P1 = pygame.image.load("Background.jpg")
        P1 = pygame.transform.scale(P1, (160 * 2, 90 * 2)) # 128 * 3, 72 * 3 --> 160 * 2, 90 * 2
        screen.blit(P1, (450, 80))

        P2 = pygame.image.load("Background2.jpg")
        P2 = pygame.transform.scale(P2, (160 * 2, 90 * 2)) # 128 * 3, 72 * 3 --> 160 * 2, 90 * 2
        screen.blit(P2, (800, 80))
        
        
        # 設定PLAY按鈕
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        PLAY_BUTTON = Button(image=pygame.image.load("assets/Option Rect.png"), pos=(610, 330),
                             text_input="change", font=get_font(55), base_color="Black", hovering_color="Green")
        PLAY_BUTTON.update(MENU_MOUSE_POS, point_option, screen)
        PLAY_BUTTON2 = Button(image=pygame.image.load("assets/Option Rect.png"), pos=(960, 330),
                              text_input="change", font=get_font(55), base_color="Black", hovering_color="Green")
        PLAY_BUTTON2.update(MENU_MOUSE_POS, point_option, screen)
        
        # 將Options視窗的內容標題訂為"Background Image"並將文字顏色設定為#00E3E3，文字中心座標位於(240, 90)，字體大小為50
        OPTIONS1_TEXT = get_font(50).render("Background Image", True, "#00E3E3")
        OPTIONS1_RECT = OPTIONS1_TEXT.get_rect(center=(240, 90))
        screen.blit(OPTIONS1_TEXT, OPTIONS1_RECT)
        
        OPTIONS2_TEXT = get_font(50).render("Watch tutorial", True, "#00E3E3")
        OPTIONS2_RECT = OPTIONS2_TEXT.get_rect(center=(217, 450))
        screen.blit(OPTIONS2_TEXT, OPTIONS2_RECT)
        
        options_watch_tutorial = Button(image=pygame.image.load("assets/Start Rect.png"), pos=(610, 450),
                             text_input="Watch", font=get_font(50), base_color="Black", hovering_color="Green")
        # 將Options視窗的按鈕上文字訂為"BACK"並將文字顏色設定為白色，文字中心座標位於(1100, 630)，字體大小為75，游標指向它時文字顏色會變成綠色
        OPTIONS_BACK = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(1100, 630),
                              text_input="BACK", font=get_font(55), base_color="Black", hovering_color="Green")
        
        options_watch_tutorial.update(MENU_MOUSE_POS, point_start, screen)
        OPTIONS_BACK.update(MENU_MOUSE_POS, point_quit, screen)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OPTIONS_BACK.checkForInput(OPTIONS_MOUSE_POS):
                    Flag = False
                    button_sfx.play()
                elif PLAY_BUTTON.checkForInput(MENU_MOUSE_POS):
                    selection_image = 1
                    button_sfx.play()
                elif PLAY_BUTTON2.checkForInput(MENU_MOUSE_POS):
                    selection_image = 2
                    button_sfx.play()
                elif options_watch_tutorial.checkForInput(MENU_MOUSE_POS):
                    button_sfx.play()
                    tutorial()

        pygame.display.update()

        if not Flag:
            break

def quit():
    time.sleep(0.25)
    quit_sfx.play()
    quit_animating = True
    while quit_animating:
        MENU_MOUSE_POS = pygame.mouse.get_pos()
        
        A0 = pygame.image.load("assets/Alert.png")
        A0 = pygame.transform.scale(A0, (800, 535))
        screen.blit(A0, (240, 80))
        QUIT1_TEXT = get_font(50).render("Alert", True, "Black")
        QUIT1_RECT = QUIT1_TEXT.get_rect(center=(640, 155))
        screen.blit(QUIT1_TEXT, QUIT1_RECT)
        QUIT2_TEXT = get_font(50).render("Do you really want to quit?", True, "Black")
        QUIT2_RECT = QUIT2_TEXT.get_rect(center=(640, 330))
        screen.blit(QUIT2_TEXT, QUIT2_RECT)
        OK_BUTTON = Button(image=pygame.image.load("assets/Ok Normal.png"), pos=(440, 520),
                                text_input=None, font=get_font(55), base_color="Black", hovering_color="Green")
        OK_BUTTON.update(MENU_MOUSE_POS, point_ok, screen)
        CANCEL_BUTTON = Button(image=pygame.image.load("assets/Cancel Normal.png"), pos=(840, 520),
                               text_input=None, font=get_font(55), base_color="Black", hovering_color="Green")
        CANCEL_BUTTON.update(MENU_MOUSE_POS, point_cancel, screen)
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if OK_BUTTON.checkForInput(MENU_MOUSE_POS):
                    button_sfx.play()
                    quit_animating = False
                    pygame.quit()
                    sys.exit()
                if CANCEL_BUTTON.checkForInput(MENU_MOUSE_POS):
                    button_sfx.play()
                    quit_animating = False
        pygame.display.flip()
        clock.tick(30)

'''input_box1 = InputBox(80, 200, 960, 96) #160 200 960 96
input_boxes = [input_box1]'''

while True:
    
    background_display()
    
    menu_mouse_pos = pygame.mouse.get_pos()
    
    menu_text = get_font(100).render("Snake", True, "#921AFF")
    menu_rect = menu_text.get_rect(center=(640, 100))
    screen.blit(menu_text, menu_rect)
    
    start_button = Button(image=pygame.image.load("assets/Start Rect.png"), pos=(640, 250),
                         text_input="START", font=get_font(55), base_color="Black", hovering_color="Green")
    options_button = Button(image=pygame.image.load("assets/Option Rect.png"), pos=(640, 400),
                            text_input="OPTIONS", font=get_font(55), base_color="Black", hovering_color="Green")
    quit_button = Button(image=pygame.image.load("assets/Quit Rect.png"), pos=(640, 550),
                         text_input="QUIT", font=get_font(55), base_color="Black", hovering_color="Green")
    
    start_button.update(menu_mouse_pos, point_start, screen)
    options_button.update(menu_mouse_pos, point_option, screen)
    quit_button.update(menu_mouse_pos, point_quit, screen)
    
    

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()
        if event.type == pygame.MOUSEBUTTONDOWN:
            # 判斷是否按下的是PLAY按鈕
            if start_button.checkForInput(menu_mouse_pos):
                button_sfx.play()
                tutorial()
            # 判斷是否按下的是OPTIONS按鈕
            if options_button.checkForInput(menu_mouse_pos):
                button_sfx.play()
                options()
            # 判斷是否按下的是QUIT按鈕
            if quit_button.checkForInput(menu_mouse_pos):
                button_sfx.play()
                quit()
    pygame.display.update()
