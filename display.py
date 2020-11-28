import os
import pygame
from pygame.locals import *
import math
import datetime
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

        self.__initDisplay()
        self.__initFonts()
        self.__initColors()
    
    def __initDisplay(self):
        pygame.init()
        pygame.mouse.set_visible(False)
        flags = FULLSCREEN | DOUBLEBUF | HWSURFACE
        self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight), flags)
        self.lcd = self.__lcd

    def __initFonts(self):
        fontDir="/usr/share/fonts/truetype/freefont/"
        self.__idFont = pygame.font.Font(fontDir + "FreeMono.ttf", 40) # ICAO ID
        self.__csFont = pygame.font.Font(fontDir + "FreeSans.ttf", 52) # callsign
        self.__fltFont = pygame.font.Font(fontDir + "FreeMono.ttf", 35) # flight data
        self.__lastSeenFont = pygame.font.Font(fontDir + "FreeSans.ttf", 25) # time last seen
        self.__distFont = pygame.font.Font(fontDir + "FreeSans.ttf", 40) # distance and bearing
        self.__btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 13)
        self.__recentFont= pygame.font.Font(fontDir + "FreeSans.ttf", 25)
        self.__statsFont= pygame.font.Font(fontDir + "FreeSans.ttf", 25)
        self.__optsFont = pygame.font.Font(fontDir + "FreeSans.ttf", 17)
        self.__titleFont= pygame.font.Font(fontDir + "FreeSans.ttf", 18)
        self.__radarFont = pygame.font.Font(fontDir + "FreeSans.ttf", 20)
        self.__recentHeaderFont = pygame.font.Font(fontDir + "FreeSans.ttf", 30)
        self.btnFont = pygame.font.Font(fontDir + "FreeSans.ttf", 30)

    def __initColors(self):
        self.__green = (0,255,0)
        self.__black = (0,0,0)
        self.__yellow = (255,255,0)
        self.__mediumBlue = (100,149,237)
        self.__cyan = (0,128,128)
        self.__darkRed = (64,0,0)
        self.__medRed = (128,0,0)
        self.__darkPurple=(64,0,64)
        self.__medPurple=(128,0,128)
        self.__medOrange=(255,120,0)
        self.__darkOrange=(128,60,0)
        self.__white = (255,255,255)
        self.__gray = (128,128,128)
        self.__red = (255,0,0)
        self.__blue = (0,0,255)

    def drawRecentsPane(self):
        ctrX = self.__screenWidth/2 + self.__screenWidth/4
        ctrTop = 30
        ctrBottom = 400
        leftEdge = self.__screenWidth/2+20
        rightEdge = self.__screenWidth-20
        horizLineY = 70
        pygame.draw.line(self.__lcd, self.__blue, (ctrX,ctrTop), (ctrX,ctrBottom), width=1)
        pygame.draw.line(self.__lcd, self.__blue, (leftEdge,horizLineY), (rightEdge,horizLineY), width=1)

        txt = self.__recentHeaderFont.render("Civilian", 1, self.__white)
        txtCenterX = leftEdge + (ctrX-leftEdge)/2
        txtCenterY = ctrTop + 15
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        txt = self.__recentHeaderFont.render("Military", 1, self.__white)
        txtCenterX = ctrX + (rightEdge-ctrX)/2
        txtCenterY = ctrTop + 15
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

    def displayCivRecents(self, recentCs, currentCs):
        xpos = 461
        yAnchor = 75
        ypos = yAnchor
        ctrX = self.__screenWidth/2 + self.__screenWidth/4
        leftEdge = self.__screenWidth/2+20
        pygame.draw.rect(self.__lcd, self.__black, (420,yAnchor,ctrX-leftEdge-1,322))
        for x in range(0, len(recentCs)):
            cs = recentCs[x]
            if (currentCs == cs):
                foreColor = self.__white
                backColor = self.__blue
            else:
                foreColor = self.__mediumBlue
                backColor = self.__black

            txt = self.__recentFont.render(cs[:8], 1, foreColor, backColor)
            self.__lcd.blit(txt, (xpos, ypos))
            ypos += 32
    
    def displayMilRecents(self, recentCs, currentCs):
        xpos = 641
        yAnchor = 75
        ypos = yAnchor
        ctrX = self.__screenWidth/2 + self.__screenWidth/4
        pygame.draw.rect(self.__lcd, self.__black, (603,yAnchor,self.__screenWidth-20-ctrX,322))
        for x in range(0, len(recentCs)):
            cs = recentCs[x]
            if (currentCs == cs):
                foreColor = self.__white
                backColor = self.__blue
            else:
                foreColor = self.__yellow
                backColor = self.__medRed

            txt = self.__recentFont.render(cs[:8], 1, foreColor, backColor)
            self.__lcd.blit(txt, (xpos, ypos))
            ypos += 32

    def clearRecentsPane(self):
        x = self.__screenWidth/2+20
        y = 30
        w = self.__screenWidth-19 - x
        h = 370
        pygame.draw.rect(self.__lcd, self.__black, (x,y,w,h))
        
    def setupAdsbDisplay(self):
        self.__lcd.fill(self.__black)
        pygame.display.update()
        pygame.event.clear()

    def displayICAOid(self, id):
        txt = self.__idFont.render(id, 1, self.__yellow)
        xpos = ((self.__screenWidth/2) - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 0))

    def clearICAOid(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,0,self.__screenWidth/2,39))

    def displayCallsign(self, cs, isMil):
        txt = self.__csFont.render(cs, 1, self.__yellow)
        xpos = ((self.__screenWidth/2) - txt.get_width())/2
        if (isMil):
            pygame.draw.rect(self.__lcd, self.__medRed, (0,43,self.__screenWidth/2,55))
        
        self.__lcd.blit(txt, (xpos, 43))

    def clearCallsign(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,43,self.__screenWidth/2,55))

    def displayLastSeen(self, lastSeen):
        # check if lastSeen hasn't been populated yet upon startup
        if (not lastSeen):
            return

        dateParts = lastSeen[0].split("/")
        formattedDate = dateParts[1] + "-" + dateParts[2] + "-" + dateParts[0]
        formattedTime = lastSeen[1].split(".")[0]

        cur_dt = datetime.datetime.now()
        try:
            lst_dt = datetime.datetime.strptime(lastSeen[0] + " " + lastSeen[1], "%Y/%m/%d %H:%M:%S.%f")
            delta = abs((cur_dt - lst_dt).seconds)
        except ValueError:
            delta = 0

        if (delta > 300):                   # older than 5 minutes
            lsColor = self.__red
        elif (delta > 120):                 # older than 2 minutes
            lsColor = self.__darkOrange
        else:
            lsColor = self.__cyan
    
        self.clearLastSeen()
        txt = self.__lastSeenFont.render("Last seen:  " + formattedTime + "  " + formattedDate, 1, lsColor)
        xpos = ((self.__screenWidth/2) - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 105))

    def clearLastSeen(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,105,self.__screenWidth/2,30))

        
    def displayFlightData(self, adsbObj, persist):
        self.clearFlightData()
        altitude = adsbObj.altitude
        groundSpeed = adsbObj.groundSpeed
        lat = adsbObj.lat
        lon = adsbObj.lon
        verticalRate = adsbObj.verticalRate
        squawk = adsbObj.squawk

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

            if (verticalRate == ""):
                verticalRate = adsbObj.lastVerticalRate
            else:
                adsbObj.lastVerticalRate = verticalRate

            if (groundSpeed == ""):
                groundSpeed = adsbObj.lastGroundSpeed
            else:
                adsbObj.lastGroundSpeed = groundSpeed

            if (squawk == ""):
                squawk = adsbObj.lastSquawk
            else:
                adsbObj.lastSquawk = squawk

        xpos = 0
        ypos = 190
        spacer = 35
        txt = self.__fltFont.render("Alt: " + altitude, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos))
        txt = self.__fltFont.render("Lat: " + lat, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer))
        txt = self.__fltFont.render("Lon:" + lon, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*2))
        txt = self.__fltFont.render("VRt: " + verticalRate, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*3))
        txt = self.__fltFont.render("GSp: " + groundSpeed, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*4))
        txt = self.__fltFont.render("Sqk: " + squawk, 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*5))

    def clearFlightData(self):
        pygame.draw.rect(self.__lcd, self.__black, (79,190,321,210))

    def displayDistance(self, dist, bearing):
        self.clearDistance()
        s = "{0:0.1f}".format(dist) + " mi   " + "{0:0.1f}".format(bearing) + u'\N{DEGREE SIGN}' + " " + Util.getCompassDir(bearing)
        txt = self.__distFont.render(s, 1, self.__medOrange)
        xpos = (self.__screenWidth/2 - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 135))

    def clearDistance(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,135,self.__screenWidth/2,42))

    def circleXY(self, cX, cY, angle, radius):
        x = cX + radius * math.cos(math.radians(angle))
        y = cY + radius * math.sin(math.radians(angle))
        return(int(x),int(y))

    def updateCallsignCount(self, adsbCnt,civCnt, milCnt):
        pygame.draw.rect(self.__lcd, self.__black, (0,391,self.__screenWidth/2,31))
        xpos = 0
        civLab = self.__statsFont.render("civ:", 1, self.__cyan)
        self.__lcd.blit(civLab, (xpos,393))
        civNum = self.__statsFont.render("{:,}".format(civCnt), 1, self.__white)
        xpos = xpos + civLab.get_width()+6
        self.__lcd.blit(civNum, (xpos,393))

        civRect = civNum.get_rect()
        xpos = xpos + civRect.right + 60
        milLab = self.__statsFont.render("mil:", 1, self.__cyan)
        self.__lcd.blit(milLab, (xpos,393))
        milNum = self.__statsFont.render("{:,}".format(milCnt), 1, self.__white)
        xpos = xpos + milLab.get_width()+6
        self.__lcd.blit(milNum, (xpos,393))

    def refreshDisplay(self):
        pygame.display.update()

    def drawRadar(self, radarX, radarY, radarRadius, maxBlipDistance):
        self.__radarX = radarX
        self.__radarY = radarY
        self.__radarRadius = radarRadius
        self.__maxBlipDistance = maxBlipDistance

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

        radarColor=(0,50,0)

        #draw radar circle
        pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), radarRadius, 1)
 
        #crosshatches
        for a in range(0, len(self.__crosshatchLines)):
            pygame.draw.line(self.__lcd, radarColor, self.__crosshatchLines[a][0], self.__crosshatchLines[a][1])
       
        # concentric circles
        for a in range(0, len(self.__concentricRadii)):
            pygame.draw.circle(self.__lcd, radarColor, (radarX,radarY), self.__concentricRadii[a], 1)

        textOffset = 13
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

        txt = self.__radarFont.render(" " + str(maxBlipDistance*2) + " mi ", 1, radarColor, self.__black)
        txtCenterX = radarX
        txtCenterY = radarY + radarRadius + (textOffset*3)
        txtRect = txt.get_rect(center=(txtCenterX, txtCenterY))
        self.__lcd.blit(txt, txtRect)

        self.__oldBlipAngle=0
        self.__oldBlipDistance=0
        self.__oldPlotX = 0
        self.__oldPlotY = 0

    def clearRadar(self):
        pygame.draw.rect(self.__lcd, self.__black, (400,0,400,416))

    def drawRadarBlip(self,blipAngle,blipDistance):
        if ((blipDistance != self.__oldBlipDistance) | (blipAngle != self.__oldBlipAngle)):
            self.__oldBlipAngle = blipAngle
            self.__oldBlipDistance = blipDistance
            if (blipDistance > self.__maxBlipDistance-1):
                #TODO - store in array, but don't plot (return?)
                blipDistance = self.__maxBlipDistance-1

            #transform blip distance proportionally from mileage to circle radius
            blipRatio=self.__maxBlipDistance/self.__radarRadius
            blipRadius=int(blipDistance/blipRatio)
            #calculate blip (x,y)
            blipX=blipRadius*math.cos(math.radians(blipAngle))
            blipY=blipRadius*math.sin(math.radians(blipAngle))

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

