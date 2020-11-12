import os
import pygame
from pygame.locals import *
import math
from util import Util

class Display():

    def __init__(self):
        self.__screenWidth = 800
        self.__screenHeight = 480

        self.__radarLineAngle=0
        self.__radarBlipGamma=255
        self.__compassPoints=[]
        self.__crosshatchLines=[]
        self.__concentricRadii=[]
        self.__radarBox=None

        self.__initDisplay()
        self.__initFonts()
        self.__initColors()
    
    def __initDisplay(self):
        os.putenv('SDL_FBDEV', '/dev/fb1')
                
        pygame.init()
        pygame.mouse.set_visible(False)
        flags = FULLSCREEN | DOUBLEBUF | HWSURFACE
        self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight), flags)
        self.lcd = self.__lcd

    def __initFonts(self):
        fontDir="/usr/share/fonts/truetype/freefont/"
        self.__csFont = pygame.font.Font(fontDir + "FreeSans.ttf", 80) # callsign
        self.__lastSeenFont = pygame.font.Font(fontDir + "FreeSans.ttf", 28) # time last seen
        self.__fltFont = pygame.font.Font(fontDir + "FreeMono.ttf", 65) # flight data
        self.__distFont = pygame.font.Font(fontDir + "FreeSans.ttf", 45) # distance and bearing


        self.__btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 13)
        self.__recentFont= pygame.font.Font(fontDir + "FreeSans.ttf", 13)
        self.__statsFont= pygame.font.Font(fontDir + "FreeSans.ttf", 14)
        self.__optsFont = pygame.font.Font(fontDir + "FreeSans.ttf", 17)
        self.__titleFont= pygame.font.Font(fontDir + "FreeSans.ttf", 18)
        self.__radarFont = pygame.font.Font(fontDir + "FreeSans.ttf", 18)
        self.btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 30)


    def __initColors(self):
        self.__green = (0,255,0)
        self.__black = (0,0,0)
        self.__yellow = (255,255,0)
        self.__mediumBlue = (100,149,237)
        self.__cyan = (0,255,255)
        self.__darkRed = (64,0,0)
        self.__medRed = (128,0,0)
        self.__darkPurple=(64,0,64)
        self.__medPurple=(128,0,128)
        self.__medOrange=(255,120,0)
        self.__darkOrange=(128,60,0)
        self.__white = (255,255,255)
        self.__gray = (128,128,128)
        self.__red = (255,0,0)

    def setupAdsbDisplay(self):
        self.__lcd.fill(self.__black)
        pygame.display.update()
        pygame.event.clear()    # clear all initial events

    def displayCallsign(self, cs, isMil):
        pygame.draw.rect(self.__lcd, self.__black, (5,5,self.__screenWidth-10,76))
        if (isMil):
            pygame.draw.rect(self.__lcd, self.__medRed, (5,6,self.__screenWidth-10,75))
        txt = self.__csFont.render(cs, 1, self.__yellow)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 0))
        pygame.display.update((5,5,self.__screenWidth-10,94))

    def displayLastSeen(self, adsbObj):
        pygame.draw.rect(self.__lcd, self.__black, (5,82,self.__screenWidth-10,25))
        dateParts = adsbObj.theDate.split("/")
        formattedDate = dateParts[1] + "-" + dateParts[2] + "-" + dateParts[0]
        formattedTime = adsbObj.theTime.split(".")[0]
        txt = self.__lastSeenFont.render(formattedTime + "  " + formattedDate, 1, self.__cyan)
        self.__lcd.blit(txt, ((self.__screenWidth - txt.get_width())/2, 79))

    def displayFlightData(self, adsbObj, persist):
        altitude = adsbObj.altitude
        lat = adsbObj.lat
        lon = adsbObj.lon

        if (persist):
            if (altitude == ""):
                altitude = adsbObj.lastAltitude
            else:
                adsbObj.lastAltitude = altitude

            if (lat == ""):
                lat = adsbObj.lastLat
            else:
                adsbObj.lastLat = lat

            if (lon == ""):
                lon = adsbObj.lastLon
            else:
                adsbObj.lastLon = lon

        xpos = 60
        ypos = 115
        spc = 49
        self.clearFlightData()
        #only render altitude if there is one, to prevent lone '
        if (altitude != ""):
            txt = self.__fltFont.render("  " + altitude + "'", 1, self.__mediumBlue)
            self.__lcd.blit(txt, (xpos, ypos))
        txt = self.__fltFont.render(" " + lat, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spc))
        txt = self.__fltFont.render(lon, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+(spc*2)))

    def clearFlightData(self):
        pygame.draw.rect(self.__lcd, self.__black, (60,115,350,152))

    def displayDistance(self, dist, bearing):
        self.clearDistance()
        s = "{0:0.1f}".format(dist) + " mi   " + "{0:0.1f}".format(bearing) + u'\N{DEGREE SIGN}' + " " + Util.getCompassDir(bearing)
        txt = self.__distFont.render(s, 1, self.__yellow)
        self.__lcd.blit(txt, (30, 270))

    def clearDistance(self):
        pygame.draw.rect(self.__lcd, self.__black, (30,270,420,43))








    def defineRadarPoints(self, radarX, radarY, radarRadius):
        #crosshatches
        chAngle=0
        for a in range(0, 4):
            chAngle=a*45
            self.__crosshatchLines.append([self.circleXY(radarX, radarY, chAngle, radarRadius), self.circleXY(radarX, radarY, chAngle+180, radarRadius)])
        
        #concentric circles
        f=0.25
        for a in range(0, 3):
            self.__concentricRadii.append(int(radarRadius*f))
            f=f+0.25

        #points on circumference
        for a in range(0, 360):
            lineEndX = radarX + math.cos(math.radians(a)) * (radarRadius-1)
            lineEndY = radarY + math.sin(math.radians(a)) * (radarRadius-1)
            self.__compassPoints.append((lineEndX, lineEndY))
        
        self.__radarBox=(radarX-radarRadius, radarY-radarRadius, radarRadius*2, radarRadius*2)

    def drawRadarLine(self,radarX,radarY,radarRadius,blipAngle,blipDistance,maxBlipDistance):
        radarColor=(0,50,0)
        radarLineColor=(0,255,0)
        
        #clear rectangle bounded by circle
        pygame.draw.rect(self.__lcd, self.__black, self.__radarBox, 0)

        #draw radar circle
        pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), radarRadius, 1)
 
        #crosshatches
        for a in range(0, len(self.__crosshatchLines)):
            pygame.draw.line(self.__lcd, radarColor, self.__crosshatchLines[a][0], self.__crosshatchLines[a][1])
       
        # concentric circles
        for a in range(0, len(self.__concentricRadii)):
            pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), self.__concentricRadii[a], 1)
    
        #draw radar line
        #TODO - int got a NONE
        pygame.draw.line(self.__lcd, radarLineColor, (radarX, radarY), self.__compassPoints[self.__radarLineAngle], 1)

        #keep blip inside circle radius
        #TODO - error ">" not supported between instances of str and int
        if (blipDistance > maxBlipDistance-6):
            blipDistance = maxBlipDistance-6

        #transform blip distance proportionally from mileage to circle radius
        blipRatio=maxBlipDistance/radarRadius
        blipRadius=int(blipDistance/blipRatio)

        #calculate blip (x,y)
        blipX=blipRadius*math.cos(math.radians(blipAngle))
        blipY=blipRadius*math.sin(math.radians(blipAngle))

        #transform the coordinates from Unit Circle to Mathematics Circle
        plotX=blipY
        plotY=-blipX

        #reset blip intensity if anything has changed
        if ((blipDistance != self.__oldBlipDistance) | (blipAngle != self.__oldBlipAngle)):
            self.__oldBlipAngle = blipAngle
            self.__oldBlipDistance = blipDistance
            self.__radarBlipGamma = 255

        #plot the blip
        pygame.draw.circle(self.__lcd, (self.__radarBlipGamma, self.__radarBlipGamma,0), (radarX+int(plotX),radarY+int(plotY)), 2)

        #fade the blip
        self.__radarBlipGamma-=1
        if (self.__radarBlipGamma < 75):
            self.__radarBlipGamma = 75

        #advance the radar arm
        self.__radarLineAngle+=1
        if (self.__radarLineAngle == 360):
            self.__radarLineAngle=0

        pygame.display.update(self.__radarBox)
        clock = pygame.time.Clock()
        clock.tick(60)


    def circleXY(self, cX, cY, angle, radius):
        x = cX + radius * math.cos(math.radians(angle))
        y = cY + radius * math.sin(math.radians(angle))
        return(int(x),int(y))








    def displayHoldMode(self, mode):
        if (mode):
            txt = self.__lastSeenFont.render('Hold', 1, self.__red)
            self.__lcd.blit(txt, (10, 280))
        else:
            pygame.draw.rect(self.__lcd, self.__black, (10,280,60,30))

        pygame.display.update()


    def checkTap(self):
        if (pygame.event.peek()):
            for event in pygame.event.get():
                if(event.type == pygame.MOUSEBUTTONUP):
                    return True
                else:
                    return False
        else:
            return False

    









    
    def updateCallsignCount(self, civCnt, milCnt):
        pygame.draw.rect(self.__lcd, self.__black, (3,203,143,16))
        lab = self.__statsFont.render("civ:", 1, self.__cyan)
        self.__lcd.blit(lab, (5,203))
        num = self.__statsFont.render("{:,}".format(civCnt), 1, self.__white)
        self.__lcd.blit(num, (5 + lab.get_width() + 1,203))

        lab = self.__statsFont.render("mil:", 1, self.__cyan)
        self.__lcd.blit(lab, (79,203))
        num = self.__statsFont.render("{:,}".format(milCnt), 1, self.__white)
        self.__lcd.blit(num, (79 + lab.get_width() + 1,203))

    

    
 
    def refreshDisplay(self):
        pygame.display.update()



    def drawRadar(self, radarX, radarY, radarRadius, maxBlipDistance):
        #crosshatches
        chAngle=0
        for a in range(0, 4):
            chAngle=a*45
            self.__crosshatchLines.append([self.circleXY(radarX, radarY, chAngle, radarRadius), self.circleXY(radarX, radarY, chAngle+180, radarRadius)])
        
        #concentric circles
        f=0.25
        for a in range(0, 3):
            self.__concentricRadii.append(int(radarRadius*f))
            f=f+0.25

        self.__radarBox=(radarX-radarRadius, radarY-radarRadius, radarRadius*2, radarRadius*2)

        radarColor=(0,50,0)
        
        #clear rectangle bounded by circle
        pygame.draw.rect(self.__lcd, self.__black, self.__radarBox, 0)

        #draw radar circle
        pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), radarRadius, 1)
 
        #crosshatches
        for a in range(0, len(self.__crosshatchLines)):
            pygame.draw.line(self.__lcd, radarColor, self.__crosshatchLines[a][0], self.__crosshatchLines[a][1])
       
        # concentric circles
        for a in range(0, len(self.__concentricRadii)):
            pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), self.__concentricRadii[a], 1)

        textOffset = 12
        # compass directions
        txt = self.__radarFont.render("N", 1, self.__green)
        txtCenterX = radarX
        txtCenterY = radarY - radarRadius - textOffset
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("S", 1, self.__green)
        txtCenterX = radarX
        txtCenterY = radarY + radarRadius + textOffset
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("W", 1, self.__green)
        txtCenterX = radarX - radarRadius - textOffset
        txtCenterY = radarY
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__radarFont.render("E", 1, self.__green)
        txtCenterX = radarX + radarRadius + textOffset
        txtCenterY = radarY
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        # radar distance
        pygame.draw.line(self.__lcd, radarColor, (radarX - radarRadius, radarY + radarRadius + (textOffset*3)), (radarX + radarRadius,  radarY + radarRadius + (textOffset*3)), width=1)
        pygame.draw.line(self.__lcd, radarColor, (radarX - radarRadius, radarY + radarRadius + (textOffset*3)-10), (radarX - radarRadius,  radarY + radarRadius + (textOffset*3)+10), width=1)
        pygame.draw.line(self.__lcd, radarColor, (radarX + radarRadius, radarY + radarRadius + (textOffset*3)-10), (radarX + radarRadius,  radarY + radarRadius + (textOffset*3)+10), width=1)

        txt = self.__radarFont.render(" " + str(maxBlipDistance) + " mi ", 1, radarColor, self.__black)
        txtCenterX = radarX
        txtCenterY = radarY + radarRadius + (textOffset*3)
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        self.__oldBlipAngle=0
        self.__oldBlipDistance=0
        self.__oldPlotX = 0
        self.__oldPlotY = 0

    def drawRadarBlip(self,radarX,radarY,radarRadius,blipAngle,blipDistance,maxBlipDistance):
        if ((blipDistance != self.__oldBlipDistance) | (blipAngle != self.__oldBlipAngle)):

            self.__oldBlipAngle = blipAngle
            self.__oldBlipDistance = blipDistance


            if (blipDistance > maxBlipDistance-1):
                blipDistance = maxBlipDistance-1

            #transform blip distance proportionally from mileage to circle radius
            blipRatio=maxBlipDistance/radarRadius
            blipRadius=int(blipDistance/blipRatio)
            #calculate blip (x,y)
            blipX=blipRadius*math.cos(math.radians(blipAngle))
            blipY=blipRadius*math.sin(math.radians(blipAngle))

            #transform the coordinates from Unit Circle to Mathematics Circle
            plotX=blipY
            plotY=-blipX

            #overwrite the old blip, if there is one
            if ((self.__oldPlotX != 0) & (self.__oldPlotY != 0)):
                pygame.draw.circle(self.__lcd, (200,0,200), (radarX+int(self.__oldPlotX),radarY+int(self.__oldPlotY)), 2)
                
            #plot the blip
            pygame.draw.circle(self.__lcd, (255,255,0), (radarX+int(plotX),radarY+int(plotY)), 2)
            self.__oldPlotX = plotX
            self.__oldPlotY = plotY

            pygame.display.update(self.__radarBox)


