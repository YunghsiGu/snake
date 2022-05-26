import pygame
import sys
import random
from pygame.locals import *
pygame.init()
pygame.mixer.init()
#----------------------------------------------------
playSurface = pygame.display.set_mode((1280, 720))
pygame.display.set_caption("貪吃蛇")
#--------------------------------------------
pygame.mixer.music.load("snakeoff.mp3")
pygame.mixer.music.play(-1)
#--------------------------------------------
def gameover():
    pygame.quit()
    sys.exit()
#------------------------------------------
snakeBody_color = pygame.Color(0, 255, 0) 
food_color = pygame.Color(255, 0, 0) 
#----------------------------------------
def main():

    time_clock = pygame.time.Clock() 
    
    
    snakePosition = [200, 200]                       
    snakeBodys = [[200, 200], [180, 200], [160, 200]] 
    foodPosition = [500, 500]        
    foodTotal = 1                   
    foodNumber = 1                  
    direction = 'right'             
    changeDirection = direction     

    speed = 4  

    while True:
        for event in pygame.event.get():   

            
            if event.type == QUIT:
                pygame.quit()
                sys.exit()

            
            elif event.type == KEYDOWN:
                if event.key == K_RIGHT or event.key == K_d:
                    changeDirection = 'right'

                if event.key == K_LEFT or event.key == K_a:
                    changeDirection = 'left'
                    
                if event.key == K_UP or event.key == K_w:
                    changeDirection = 'up'
                    
                if event.key == K_DOWN or event.key == K_s:
                    changeDirection = 'down'

                if event.key == K_ESCAPE:
                    pygame.event.post(pygame.event.Event(QUIT))

        
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
            x = random.randrange(1, 40)
            y = random.randrange(1, 40)
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
            
        
        background = pygame.image.load("background.jpg")
        playSurface.blit(background,(0,0))
        pygame.display.update()

        
        for position in snakeBodys:
            pygame.draw.rect(playSurface, snakeBody_color, Rect(position[0], position[1], 20, 20))
            pygame.draw.rect(playSurface, food_color, Rect(foodPosition[0], foodPosition[1], 20, 20))

        pygame.display.flip() 

        
        if snakePosition[0] > 800 or snakePosition[0] < 0:
            gameover()
            
        elif snakePosition[1] > 800 or snakePosition[1] < 0:
            gameover()
            
        
        for body in snakeBodys[1:]:
            if snakePosition[0] == body[0] and snakePosition[1] == body[1]:
                gameover()

        
        time_clock.tick(speed)

        
if __name__ == "__main__":
    main()