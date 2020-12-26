import pygame
import pygame.gfxdraw
import math
from util import Util

class Radar():

    def __init__(self, lcd):
        self.__lcd = lcd
        self.__crosshatchLines=[]
        self.__concentricRadii=[]
        self.__ticMarks=[]
        self.__SCALEMIN = 5
        self.__SCALEMAX = 150
        self.__radarX = 600
        self.__radarY = 195
        self.__radarRadius = 165
        self.__radarMaxDist = 50
        self.__posList = []
        self.__radarColor = (0,80,0)
        self.__green = (0,255,0)
        self.__black = (0,0,0)
        self.__darkOrange = (128,60,0)
        self.__red = (255,0,0)
        self.__winFlag = Util.isWindows()

        if (self.__winFlag):
            sansFont = "microsoftsansserif"
            monoFont = "couriernew"
        else:
            sansFont = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            monoFont = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"

        self.__radarFont = self.__defineFont(self.__winFlag, sansFont, 20) # NSEW letters
        self.__rangeFont = self.__defineFont(self.__winFlag, sansFont, 20) # radar "out of range"

        #crosshatches
        chAngle=0
        for a in range(0, 4):
            chAngle=a*45
            self.__crosshatchLines.append([self.__circleXY(self.__radarX, self.__radarY, chAngle, self.__radarRadius), self.__circleXY(self.__radarX, self.__radarY, chAngle+180, self.__radarRadius)])
        
        #concentric circles
        f=0.25
        for a in range(0, 3):
            self.__concentricRadii.append(int(self.__radarRadius*f))
            f=f+0.25

        # tic marks
        for a in range(0, 360, 10):
            if a % 10 == 0:
                ticLen = 6
            else:
                ticLen = 3

            self.__ticMarks.append([self.__circleXY(self.__radarX, self.__radarY, a, self.__radarRadius), self.__circleXY(self.__radarX, self.__radarY, a, self.__radarRadius-ticLen)])
        

    def __defineFont(self, winflag, fontFamily, size):
        if (Util.isWindows()):
            return pygame.font.SysFont(fontFamily, size)
        else:
            return pygame.font.Font(fontFamily, size)

    def clearPosList(self):
        self.__posList = []

    def addToPosList(self, lat, lon, dist, bearing):
        self.__posList.append((lat, lon, dist, bearing))

    def drawRadarScreen(self):
        #draw radar circle
        pygame.draw.circle(self.__lcd, self.__radarColor, (self.__radarX, self.__radarY), self.__radarRadius, 1)
 
        #crosshatches
        for a in range(0, len(self.__crosshatchLines)):
            pygame.draw.line(self.__lcd, self.__radarColor, self.__crosshatchLines[a][0], self.__crosshatchLines[a][1])
       
        # concentric circles
        for a in range(0, len(self.__concentricRadii)):
            pygame.draw.circle(self.__lcd, self.__radarColor, (self.__radarX, self.__radarY), self.__concentricRadii[a], 1)

        # ticmarks
        for a in range(0, len(self.__ticMarks)):
            pygame.draw.line(self.__lcd, self.__radarColor, self.__ticMarks[a][0], self.__ticMarks[a][1])
            
        textOffset = 13
        # compass directions
        txt = self.__radarFont.render("N", 1, self.__green)
        txtCenterX = self.__radarX
        txtCenterY = self.__radarY - self.__radarRadius - textOffset
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("S", 1, self.__green)
        txtCenterX = self.__radarX
        txtCenterY = self.__radarY + self.__radarRadius + textOffset
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("W", 1, self.__green)
        txtCenterX = self.__radarX - self.__radarRadius - textOffset
        txtCenterY = self.__radarY
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("E", 1, self.__green)
        txtCenterX = self.__radarX + self.__radarRadius + textOffset
        txtCenterY = self.__radarY
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        # radar distance
        pygame.draw.line(self.__lcd, self.__radarColor, (self.__radarX - self.__radarRadius, self.__radarY + self.__radarRadius + (textOffset*3)), (self.__radarX + self.__radarRadius,  self.__radarY + self.__radarRadius + (textOffset*3)), width=1)
        pygame.draw.line(self.__lcd, self.__radarColor, (self.__radarX - self.__radarRadius, self.__radarY + self.__radarRadius + (textOffset*3)-10), (self.__radarX - self.__radarRadius,  self.__radarY + self.__radarRadius + (textOffset*3)+10), width=1)
        pygame.draw.line(self.__lcd, self.__radarColor, (self.__radarX + self.__radarRadius, self.__radarY + self.__radarRadius + (textOffset*3)-10), (self.__radarX + self.__radarRadius,  self.__radarY + self.__radarRadius + (textOffset*3)+10), width=1)

        txt = self.__radarFont.render(" " + str(self.__radarMaxDist*2) + " mi ", 1, self.__green, self.__black)
        txtCenterX = self.__radarX
        txtCenterY = self.__radarY + self.__radarRadius + (textOffset*3)
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        self.__oldBlipAngle=0
        self.__oldBlipDistance=0
        self.__oldPlotX = 0
        self.__oldPlotY = 0

    def decreaseScale(self):
        self.__radarMaxDist -= 5
        if (self.__radarMaxDist < self.__SCALEMIN):
            self.__radarMaxDist = self.__SCALEMIN

    def increaseScale(self):
        self.__radarMaxDist += 5
        if (self.__radarMaxDist > self.__SCALEMAX):
            self.__radarMaxDist = self.__SCALEMAX

    def refreshDisplay(self):
        self.clearRadar()
        self.drawRadarScreen()
        self.plotTotalPath()
    
    def plotTotalPath(self):
        for coord in self.__posList:
            self.plotCurrentPos(coord[2], coord[3])

    def __circleXY(self, cX, cY, angle, radius):
        x = cX + radius * math.cos(math.radians(angle))
        y = cY + radius * math.sin(math.radians(angle))
        return(int(x),int(y))

    def clearRadar(self):
        pygame.draw.rect(self.__lcd, self.__black, (400,0,400,416))

    def plotCurrentPos(self, blipDistance, blipAngle):
        if ((blipDistance != self.__oldBlipDistance) | (blipAngle != self.__oldBlipAngle)):
            self.__oldBlipAngle = blipAngle
            self.__oldBlipDistance = blipDistance
            if (blipDistance > self.__radarMaxDist):
                self.__drawOutOfRange(True)
                return False

            self.__drawOutOfRange(False)
            #transform blip distance proportionally from mileage to circle radius
            blipRatio = self.__radarMaxDist/self.__radarRadius
            blipRadius = int(blipDistance/blipRatio)
            #calculate blip (x,y)
            blipX = blipRadius*math.cos(math.radians(blipAngle))
            blipY = blipRadius*math.sin(math.radians(blipAngle))

            #transform the coordinates from Unit Circle to Mathematics Circle
            plotX=blipY
            plotY=-blipX

            #overwrite the old blip, if there is one
            if ((self.__oldPlotX != 0) & (self.__oldPlotY != 0)):
                pygame.draw.circle(self.__lcd, self.__darkOrange, (self.__radarX+int(self.__oldPlotX),self.__radarY+int(self.__oldPlotY)), 2)
                
            #plot the blip
            pygame.draw.circle(self.__lcd, self.__green, (self.__radarX+int(plotX),self.__radarY+int(plotY)), 2)
            self.__oldPlotX = plotX
            self.__oldPlotY = plotY

            return True

    def __drawOutOfRange(self, tooFarAway):
        if (tooFarAway):
            pygame.draw.rect(self.__lcd, self.__black, (675,5,125,25))
            txt = self.__rangeFont.render("Out of Range", 1, self.__red)
            self.__lcd.blit(txt, (675, 5))

        else:
            pygame.draw.rect(self.__lcd, self.__black, (675,5,125,25))
