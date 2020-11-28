import pygame
import enum

class Button():

    class State(enum.Enum): 
        ON = 1
        OFF = 2
        DISABLED = 3

    def __init__(self, screen, posX, posY, sizeX, sizeY, font, btnColor, textColor, text, onCallback, offCallback, initialState):
        self.__screen = screen
        self.__posX = posX
        self.__posY = posY
        self.__sizeX = sizeX
        self.__sizeY = sizeY
        self.__font = font
        self.__btnColorOff = pygame.Color(btnColor)
        self.__btnColorOn = pygame.Color(btnColor).correct_gamma(0.25)
        self.__btnColorDisabled = pygame.Color((5,5,5))
        self.__textColorOff = pygame.Color(textColor)
        self.__textColorOn = pygame.Color(textColor).correct_gamma(0.25)
        self.__text = text
        self.__onCallback = onCallback
        self.__offCallback = offCallback
        self.drawButton(initialState)

    def drawButton(self, state):
        if (state == self.State.ON):
            self.__state = self.State.ON
            self.__renderButton(self.__btnColorOn, self.__textColorOn)
        
        if (state == self.State.OFF):
            self.__state = self.State.OFF
            self.__renderButton(self.__btnColorOff, self.__textColorOff)

        if (state == self.State.DISABLED):
            self.__state = self.State.DISABLED
            self.__renderButton(self.__btnColorDisabled, self.__textColorOff)

    def __renderButton(self, bgColor, txtColor):
        self.__buttonRect = pygame.draw.rect(self.__screen, bgColor, (self.__posX, self.__posY, self.__sizeX, self.__sizeY), border_radius=10)
        txt = self.__font.render(self.__text, 1, txtColor)
        txtCenterX = self.__posX + (self.__sizeX/2)
        txtCenterY = self.__posY + (self.__sizeY/2)
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__screen.blit(txt, txtRect)

    def toggleButton(self):
        if (self.__state == self.State.OFF):
            self.drawButton(self.State.ON)
            self.__onCallback()
        else:
            self.drawButton(self.State.OFF)
            self.__offCallback()

    def isDisabled(self):
        if (self.__state == self.State.DISABLED):
            return True
        else:
            return False

    def isSelected(self):
        return self.__buttonRect.collidepoint(pygame.mouse.get_pos())
