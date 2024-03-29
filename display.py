import os
import pygame
from pygame.locals import *
import datetime
from util import Util


class Display():
        
    def __init__(self, winFlag):
        self.__winFlag = winFlag

        self.__screenWidth = 800
        self.__screenHeight = 480
        
        self.__dataFlipLEDs = False
        self.__dataLED1x = 10
        self.__dataLED2x = 23
        self.__dataLEDy = 10

        self.__initDisplay()
        self.__initFonts()
        self.__initColors()
    
    def __initDisplay(self):
        pygame.init()

        if (self.__winFlag):
            self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight))
        else:
            pygame.mouse.set_visible(False)
            flags = pygame.FULLSCREEN | pygame.DOUBLEBUF | pygame.HWSURFACE
            self.__lcd = pygame.display.set_mode((self.__screenWidth, self.__screenHeight), flags)

    @property
    def lcd(self):
        return self.__lcd

    def __initFonts(self):
        if (self.__winFlag):
            sansFont = "microsoftsansserif"
            monoFont = "couriernew"
        else:
            sansFont = "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
            monoFont = "/usr/share/fonts/truetype/freefont/FreeMono.ttf"

        self.__idFont           = self.__defineFont(self.__winFlag, monoFont, 40) # ICAO ID
        self.__idFontBig        = self.__defineFont(self.__winFlag, monoFont, 130) # ICAO ID
        self.__csFont           = self.__defineFont(self.__winFlag, sansFont, 52) # callsign
        self.__csFontBig        = self.__defineFont(self.__winFlag, sansFont, 155) # callsign
        self.__fltFont          = self.__defineFont(self.__winFlag, monoFont, 35) # flight data
        self.__lastSeenFont     = self.__defineFont(self.__winFlag, sansFont, 25) # time last seen
        self.__lastSeenFontBig  = self.__defineFont(self.__winFlag, sansFont, 50) # time last seen
        self.__distFont         = self.__defineFont(self.__winFlag, sansFont, 37) # distance and bearing
        self.__recentHeaderFont = self.__defineFont(self.__winFlag, sansFont, 30) # headers for civ and mil recents
        self.__recentFont       = self.__defineFont(self.__winFlag, sansFont, 25) # civ and mil recents
        self.__infoFont         = self.__defineFont(self.__winFlag, sansFont, 35) # info page
        self.btnFont            = self.__defineFont(self.__winFlag, sansFont, 30) # buttons
        self.btnRadarFont       = self.__defineFont(self.__winFlag, monoFont, 50) # radar +/- buttons

    def __defineFont(self, winflag, fontFamily, size):
        if (self.__winFlag):
            return pygame.font.SysFont(fontFamily, size)
        else:
            return pygame.font.Font(fontFamily, size)

    def __initColors(self):
        self.__black        = (0,0,0)
        self.__red          = (255,0,0)
        self.__medRed       = (128,0,0)
        self.__darkRed      = (64,0,0)
        self.__medOrange    = (255,120,0)
        self.__darkOrange   = (128,60,0)
        self.__yellow       = (255,255,0)
        self.__medYellow    = (128,128,0)
        self.__green        = (0,255,0)
        self.__medGreen     = (0,128,0)
        self.__blue         = (0,0,255)
        self.__mediumBlue   = (100,149,237)
        self.__cyan         = (0,128,128)
        self.__medPurple    = (128,0,128)
        self.__darkPurple   = (64,0,64)
        self.__white        = (255,255,255)
        self.__easyWhite    = (200,200,200)
        self.__gray         = (128,128,128)
        
    def drawDataLEDs(self):
        pygame.draw.circle(self.__lcd, self.__medRed, (self.__dataLED1x,self.__dataLEDy), 5, 0)
        pygame.draw.circle(self.__lcd, self.__medRed, (self.__dataLED2x,self.__dataLEDy), 5, 0)

    def flipDataLEDs(self):
        if (self.__dataFlipLEDs):
            LED1 = self.__medGreen
            LED2 = self.__medRed
        else:
            LED1 = self.__medRed
            LED2 = self.__medGreen

        pygame.draw.circle(self.__lcd, LED1, (self.__dataLED1x,self.__dataLEDy), 5, 0)
        pygame.draw.circle(self.__lcd, LED2, (self.__dataLED2x,self.__dataLEDy), 5, 0)
        
        self.__dataFlipLEDs = not self.__dataFlipLEDs
        return

    def clearDisplayArea(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,0,self.__screenWidth,427))

    def drawInfoPane(self):
        labels = [("civilian:", 20), ("military:", 65), ("squitters:", 110), ("data/sec:", 155), ("cpu temp:", 200)]

        for l in labels:
            txt = self.__infoFont.render(l[0], 1, self.__mediumBlue)
            txtRect = txt.get_rect()
            txtRect.right = 155
            txtRect.y = l[1]
            self.__lcd.blit(txt, txtRect)

        self.refreshDisplay()

    def updateInfoPane(self, civCount, milCount, squitterCount, squitterRate, cpuTemp):
        x = 160
        pygame.draw.rect(self.__lcd, self.__black, (x-1,20,self.__screenWidth-550,220))
        
        civCnt = "{:,}".format(civCount)
        milCnt = "{:,}".format(milCount)
        sqCnt = "{:,}".format(squitterCount)
        #uptime = Util.getUptime()

        txt = self.__infoFont.render(civCnt, 1, self.__easyWhite)
        self.__lcd.blit(txt, (x, 20))
        txt = self.__infoFont.render(milCnt, 1, self.__easyWhite)
        self.__lcd.blit(txt, (x, 65))
        txt = self.__infoFont.render(sqCnt, 1, self.__easyWhite)
        self.__lcd.blit(txt, (x, 110))
        txt = self.__infoFont.render(str(squitterRate), 1, self.__easyWhite)
        self.__lcd.blit(txt, (x, 155))
        txt = self.__infoFont.render(cpuTemp, 1, self.__easyWhite)
        self.__lcd.blit(txt, (x, 200))
        #txt = self.__infoFont.render(uptime, 1, self.__easyWhite)
        #self.__lcd.blit(txt, (x, 310))

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
        pygame.draw.rect(self.__lcd, self.__black, (40,0,self.__screenWidth/2-40,39))

    def displayICAOidBig(self, id):
        txt = self.__idFontBig.render(id, 1, self.__yellow)
        xpos = (self.__screenWidth - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 20))

    def clearICAOidBig(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,40,self.__screenWidth,100))

    def displayCallsign(self, cs, isMil):
        txt = self.__csFont.render(cs, 1, self.__yellow)
        xpos = ((self.__screenWidth/2) - txt.get_width())/2
        if (isMil):
            pygame.draw.rect(self.__lcd, self.__medRed, (0,43,self.__screenWidth/2,55))
        
        self.__lcd.blit(txt, (xpos, 43))

    def clearCallsign(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,43,self.__screenWidth/2,55))

    def displayCallsignBig(self, cs, isMil):
        txt = self.__csFontBig.render(cs, 1, self.__yellow)
        xpos = (self.__screenWidth - txt.get_width())/2
        if (isMil):
            pygame.draw.rect(self.__lcd, self.__medRed, (0,160,self.__screenWidth,150))
        
        self.__lcd.blit(txt, (xpos, 148))

    def clearCallsignBig(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,160,self.__screenWidth,150))

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
            delta = abs((cur_dt - lst_dt).total_seconds())
        except ValueError:
            delta = 0

        if (delta > 180.0):                   # older than 3 minutes
            lsColor = self.__red
            
        elif (delta > 60.0):                   # older than 1 minute
            lsColor = self.__medYellow

        else:
            lsColor = self.__medGreen
    
        self.clearLastSeen()
        txt = self.__lastSeenFont.render("Last seen:  " + formattedTime + "  " + formattedDate, 1, lsColor)
        xpos = ((self.__screenWidth/2) - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 105))

    def clearLastSeen(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,105,self.__screenWidth/2,27))

    def displayLastSeenBig(self, lastSeen):
        # check if lastSeen hasn't been populated yet upon startup
        if (not lastSeen):
            return

        dateParts = lastSeen[0].split("/")
        formattedDate = dateParts[1] + "-" + dateParts[2] + "-" + dateParts[0]
        formattedTime = lastSeen[1].split(".")[0]

        cur_dt = datetime.datetime.now()
        try:
            lst_dt = datetime.datetime.strptime(lastSeen[0] + " " + lastSeen[1], "%Y/%m/%d %H:%M:%S.%f")
            delta = abs((cur_dt - lst_dt).total_seconds())
        except ValueError:
            delta = 0

        if (delta > 180.0):                   # older than 3 minutes
            lsColor = self.__red
            
        elif (delta > 60.0):                   # older than 1 minute
            lsColor = self.__medYellow

        else:
            lsColor = self.__medGreen
    
        self.clearLastSeenBig()
        txt = self.__lastSeenFontBig.render("Last seen:  " + formattedTime + "  " + formattedDate, 1, lsColor)
        xpos = (self.__screenWidth - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 340))

    def clearLastSeenBig(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,340,self.__screenWidth,60))
        
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
        txt = self.__fltFont.render(f'Alt: {altitude}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos))
        txt = self.__fltFont.render(f'Lat: {lat}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer))
        txt = self.__fltFont.render(f'Lon:{lon}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*2))
        txt = self.__fltFont.render(f'VRt: {verticalRate}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*3))
        txt = self.__fltFont.render(f'GSp: {Util.getGndSpeedText(groundSpeed)}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*4))
        txt = self.__fltFont.render(f'Sqk: {squawk}', 1, self.__mediumBlue)
        self.__lcd.blit(txt, (xpos, ypos+spacer*5))

    def clearFlightData(self):
        pygame.draw.rect(self.__lcd, self.__black, (79,190,300,210))

    def displayDistance(self, dist, bearing):
        self.clearDistance()
        s = "{0:0.1f}".format(dist) + " mi   " + "{0:0.1f}".format(bearing) + u'\N{DEGREE SIGN}' + " " + Util.getCompassDir(bearing)
        txt = self.__distFont.render(s, 1, self.__medOrange)
        xpos = (self.__screenWidth/2 - txt.get_width())/2
        self.__lcd.blit(txt, (xpos, 135))

    def clearDistance(self):
        pygame.draw.rect(self.__lcd, self.__black, (0,135,self.__screenWidth/2-2,42))

    def refreshDisplay(self):
        pygame.display.update()
