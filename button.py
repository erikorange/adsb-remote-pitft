import pygame

class Button():
    def __init__(self, screen, posX, posY, sizeX, sizeY, font, btnColor, textColor, text, onCallback, offCallback):

        self.__screen = screen
        self.__posX = posX
        self.__posY = posY
        self.__sizeX = sizeX
        self.__sizeY = sizeY
        self.__font = font
        self.__btnColorOff = pygame.Color(btnColor)
        self.__btnColorOn = pygame.Color(btnColor).correct_gamma(0.25)
        self.__textColorOff = pygame.Color(textColor)
        self.__textColorOn = pygame.Color(textColor).correct_gamma(0.25)
        self.__text = text
        self.__onCallback = onCallback
        self.__offCallback = offCallback
        
        self.__state = False
        self.drawButton(self.__state)

    def drawButton(self, state):
        if (state):
            bgColor = self.__btnColorOn
            txtColor = self.__textColorOn
        else:
            bgColor = self.__btnColorOff
            txtColor = self.__textColorOff

        self.__buttonRect = pygame.draw.rect(self.__screen, bgColor, (self.__posX, self.__posY, self.__sizeX, self.__sizeY), border_radius=10)
        txt = self.__font.render(self.__text, 1, txtColor)
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
