# 此為控制按鈕的函式。

class Button:
    
    # 初始化設定值，包含圖檔、座標位置、字型、原色與游標指向時的呈色、文字方塊...等
    def __init__(self, image, pos, text_input, font, base_color, hovering_color):
        self.image = image
        self.x_pos = pos[0]
        self.y_pos = pos[1]
        self.font = font
        self.base_color, self.hovering_color = base_color, hovering_color
        self.text_input = text_input
        self.text = self.font.render(self.text_input, True, self.base_color)
        # 如果不想用任何圖片做成按鈕的話，則將圖片以文字本身代替做成文字按鈕
        if self.image is None:
            self.image = self.text
        self.rect = self.image.get_rect(center=(self.x_pos, self.y_pos))
        self.text_rect = self.text.get_rect(center=(self.x_pos + 35, self.y_pos + 3))
    
    # 檢查是否有輸入(按下按鈕)，判斷方式為偵測當按下滑鼠時(這部分的偵測寫在game.py裡)，游標的座標位於按鈕物件的邊界(也就是範圍)內。
    def checkForInput(self, position):
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            return True
        return False           
    
    # 定義更新的函式，負責在當滑鼠指著按鈕的時候，變化按鈕與文字的顏色及外觀型態，變成游標指著按鈕時的醒目提示狀態。
    def update(self, position, image, screen):
        # 將原本的圖檔備份存在backup內
        backup = self.image
        # 當游標指著的時候變換圖檔與文字型態
        if position[0] in range(self.rect.left, self.rect.right) and position[1] in range(self.rect.top, self.rect.bottom):
            self.text = self.font.render(self.text_input, True, self.hovering_color)
            self.image = image
            screen.blit(self.image, self.rect)
            screen.blit(self.text, self.text_rect)
        # 當游標不再指著的時候會變回原樣
        else:
            self.text = self.font.render(self.text_input, True, self.base_color)
            # 拿backup的備份把圖檔換回來
            self.image = backup
            screen.blit(self.image, self.rect)
            screen.blit(self.text, self.text_rect)
