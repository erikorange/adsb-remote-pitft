import sys
import pygame

class Button():
    def __init__(self, screen, posX, posY, sizeX, sizeY, font, rgbColor, text, onCallback, offCallback):

        self.__screen = screen
        self.__posX = posX
        self.__posY = posY
        self.__sizeX = sizeX
        self.__sizeY = sizeY
        self.__font = font
        self.__colorOff = pygame.Color(rgbColor)
        self.__colorOn = pygame.Color(rgbColor).correct_gamma(0.25)
        self.__colorText = pygame.Color((255,255,255))
        self.__text = text
        self.__onCallback = onCallback
        self.__offCallback = offCallback
        
        self.__state = False
        self.drawButton(self.__state)

    def drawButton(self, state):
        if (state):
            bgColor = self.__colorOn
        else:
            bgColor = self.__colorOff

        self.__buttonRect = pygame.draw.rect(self.__screen, bgColor, (self.__posX, self.__posY, self.__sizeX, self.__sizeY), border_radius=10)
        txt = self.__font.render(self.__text, 1, self.__colorText)
        txtCenterX = self.__posX + (self.__sizeX/2)
        txtCenterY = self.__posY + (self.__sizeY/2)
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__screen.blit(txt, txtRect)

    def toggleButton(self):
        self.__state = not (self.__state)
        self.drawButton(self.__state)
        if (self.__state):
            self.__onCallback()
        else:
            self.__offCallback()

    def isSelected(self):
        return self.__buttonRect.collidepoint(pygame.mouse.get_pos())
        


def exitSystem():
    sys.exit(0)

def holdOn():
    pygame.draw.rect(lcd, (0,0,255), (200, 50, 80, 80))

def holdOff():
    pygame.draw.rect(lcd, (0,0,0), (200, 50, 80, 80))

pygame.init()
lcd = pygame.display.set_mode((800,480), pygame.FULLSCREEN)
pygame.mouse.set_visible(False)

fontDir="/usr/share/fonts/truetype/freefont/"
btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 30)
medRed = (80,0,0)
medPurple = (80, 0, 80)

buttonList = []
holdBtn = Button(lcd, 5, 400, 100, 60, btnFont, medPurple, "HOLD", holdOn, holdOff)
buttonList.append(holdBtn)
exitBtn = Button(lcd, 130, 400, 100, 60, btnFont, medRed, "EXIT", exitSystem, exitSystem)
buttonList.append(exitBtn)

pygame.display.update()

while True:
    for event in pygame.event.get():
        if event.type == pygame.FINGERUP:
            for btn in buttonList:                
                if btn.isSelected():
                    btn.toggleButton()
                    pygame.display.update()
    

