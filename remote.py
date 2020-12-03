import sys
import signal
import time
import re
import socket
import enum
import pygame
import collections

from display import Display
from button import Button
from adsb import Adsb
from util import Util

class State(enum.Enum): 
    CIV_MIL = 1
    CIV_MIL_HOLD = 2
    CIV_MIL_BIG = 3
    MIL_ONLY = 4
    MIL_ONLY_HOLD = 5
    MIL_ONLY_BIG = 6
    STATS = 7


def shutdownEvent(signal, frame):
    sys.exit(0)

def getHomeLatLon(filename):
    try:
        f = open(filename, "r")
    except:
        return 41.499741, -81.693726

    lat = float(f.readline())
    lon = float(f.readline())
    f.close()
    return lat, lon


def exitSystem():
    sys.exit(0)


def zoomIn():
    global posList, radarScale
    radarScale -= 5
    if (radarScale < 5):
        radarScale = 5
    
    dsp.clearRadar()
    dsp.drawRadar(600,195,165,radarScale)
    for coord in posList:
        dsp.drawRadarBlip(coord[2], coord[3])

def zoomOut():
    global posList, radarScale
    radarScale += 5
    if (radarScale > 150):
        radarScale = 150
    
    dsp.clearRadar()
    dsp.drawRadar(600,195,165,radarScale)
    for coord in posList:
        dsp.drawRadarBlip(coord[2], coord[3])


def holdOn():
    global curState, adsbObj, posList, radarScale
    if (curState == State.CIV_MIL):
        milBtn.drawButton(Button.State.DISABLED)
        curState = State.CIV_MIL_HOLD

    elif (curState == State.MIL_ONLY):
        curState = State.MIL_ONLY_HOLD

    adsbObj.clearLastFlightData()
    dsp.clearLastSeen()
    dsp.clearRecentsPane()
    radarScale = 50
    dsp.drawRadar(600,195,165,radarScale)
    plusBtn.drawButton(Button.State.ON)
    minusBtn.drawButton(Button.State.ON)
    posList=[]
    
def holdOff():
    global curState, adsbObj, currentCallsign, lastSeenDateTime
    if (curState == State.CIV_MIL_HOLD):
        curState = State.CIV_MIL
        milBtn.drawButton(Button.State.OFF)

    elif (curState == State.MIL_ONLY_HOLD):
        curState = State.MIL_ONLY

    plusBtn.drawButton(Button.State.HIDDEN)
    minusBtn.drawButton(Button.State.HIDDEN)

    adsbObj.clearLastCallsignAndID()
    adsbObj.clearLastFlightData()
    dsp.clearDistance()
    dsp.clearFlightData()
    dsp.clearRadar()
    dsp.drawRecentsPane()
    dsp.displayCivRecents(civRecents, currentCallsign)
    dsp.displayMilRecents(milRecents, currentCallsign)
    lastSeenDateTime = ()
    
    #TODO - Hold and Mil on, then mil off -> undefined state
def milOn():
    global curState, lastSeenDateTime
    curState = State.MIL_ONLY
    dsp.clearICAOid()
    dsp.clearCallsign()
    dsp.clearFlightData()
    dsp.clearLastSeen()
    lastSeenDateTime = ()

def milOff():
    global curState, lastSeenDateTime

    if (curState == State.MIL_ONLY_HOLD):
        curState = State.CIV_MIL_HOLD

    else:
        curState = State.CIV_MIL
        dsp.clearICAOid()
        dsp.clearCallsign()
        dsp.clearFlightData()
        dsp.clearLastSeen()
        lastSeenDateTime = ()

def bigOn():
    return

def bigOff():
    return

def dataOn():
    return

def dataOff():
    return

def addToRecents(callsign, que):
    try:
        x = list(que).index(callsign)
    except ValueError:
        que.appendleft(callsign)
    return que


signal.signal(signal.SIGTERM, shutdownEvent)
signal.signal(signal.SIGINT, shutdownEvent)
signal.signal(signal.SIGTSTP, shutdownEvent)

HOME_LAT, HOME_LON = getHomeLatLon("home-lat-lon.txt")

dsp = Display()
dsp.setupAdsbDisplay()
adsbObj = Adsb()

civRecents = collections.deque(maxlen=10)
civList = set()
milRecents = collections.deque(maxlen=10)
milList = set()
holdMode = False
milMode = False
currentID = ''
currentCallsign = ''
lastSeenDateTime = ()
posList=[]
radarScale=50
hasCallsign = False
isMilCallsign = False
adsbCount=0
curState = State.CIV_MIL


medRed = (80,0,0)
medPurple = (80,0,80)
medBlue = (0,0,80)
gray = (128,128,128)
darkGreen=(0,32,0)
dataColor=(0,32,32)
white=(255,255,255)

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.bind(('', 49001))
sck.setblocking(0)

dsp.drawRecentsPane()

buttonList = []
holdBtn = Button(dsp.lcd, 5, 429, 100, 50, dsp.btnFont, medPurple, gray, "HOLD", holdOn, holdOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(holdBtn)
milBtn = Button(dsp.lcd, 120, 429, 100, 50, dsp.btnFont, darkGreen, gray, "MIL", milOn, milOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(milBtn)
bigBtn = Button(dsp.lcd, 235, 429, 100, 50, dsp.btnFont, medBlue, gray, "BIG", bigOn, bigOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(bigBtn)
dataBtn = Button(dsp.lcd, 350, 429, 100, 50, dsp.btnFont, dataColor, gray, "DATA", dataOn, dataOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(dataBtn)
exitBtn = Button(dsp.lcd, 695, 429, 100, 50, dsp.btnFont, medRed, gray, "EXIT", exitSystem, exitSystem, Button.State.OFF, Button.Type.STICKY)
buttonList.append(exitBtn)
plusBtn = Button(dsp.lcd, 545, 429, 50, 50, dsp.btnRadarFont, darkGreen, white, "+", zoomOut, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
buttonList.append(plusBtn)
minusBtn = Button(dsp.lcd, 605, 429, 50, 50, dsp.btnRadarFont, darkGreen, white, "-", zoomIn, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
buttonList.append(minusBtn)

pygame.display.update()

while True:
    try:
        data, address = sck.recvfrom(256)
    except socket.error:
        pass
    else:
        adsbObj.loadData(data.decode('utf-8'))
        adsbCount += 1
        currentID = adsbObj.ICAOid
        currentCallsign = adsbObj.callsign.strip()
    
        if (currentCallsign != ""):
            hasCallsign = True
            if (Util.isMilCallsign(currentCallsign)):
                isMilCallsign = True
                milRecents = addToRecents(currentCallsign, milRecents)
                milList.add((currentID, currentCallsign))
            else:
                isMilCallsign = False
                civRecents = addToRecents(currentCallsign, civRecents)
                civList.add((currentID, currentCallsign))
        else:
            hasCallsign = False
            isMilCallsign = False

#TODO - clear lastSeenDateTime() approproately in all state changes

        if ((curState == State.CIV_MIL and hasCallsign) or (curState == State.MIL_ONLY and isMilCallsign)):
            dsp.clearICAOid()
            dsp.clearCallsign()
            dsp.displayICAOid(currentID)
            dsp.displayCallsign(currentCallsign, isMilCallsign)
            dsp.displayFlightData(adsbObj, False)
            dsp.displayCivRecents(civRecents, currentCallsign)
            dsp.displayMilRecents(milRecents, currentCallsign)
            adsbObj.setLastCallsignAndID(currentCallsign, currentID)
            lastSeenDateTime = (adsbObj.theDate, adsbObj.theTime)
            # Here, last seen is the time for any airplace.  might not update quickly late at night.
                
        if ((curState == State.CIV_MIL_HOLD or curState == State.MIL_ONLY_HOLD) and (currentID == adsbObj.lastID)):
            dsp.clearICAOid()
            dsp.clearCallsign()
            dsp.clearFlightData()
            dsp.displayICAOid(adsbObj.lastID)
            dsp.displayCallsign(adsbObj.lastCallsign, Util.isMilCallsign(adsbObj.lastCallsign))
            dsp.displayFlightData(adsbObj, True)
            if (adsbObj.lat != "" and adsbObj.lon != ""):
                dist = Util.haversine(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                dsp.displayDistance(dist, bearing)
                dsp.drawRadarBlip(dist, bearing)
                posList.append((adsbObj.lat, adsbObj.lon, dist, bearing))
                #TODO make setters or 1 method
                adsbObj.lastDist, adsbObj.lastBearing = (dist, bearing)
            elif (not adsbObj.lastDist is None):
                dsp.displayDistance(adsbObj.lastDist, adsbObj.lastBearing)

            lastSeenDateTime = (adsbObj.theDate, adsbObj.theTime)
            # Here, last seen is the time for this held airplane.  Will age as airplane flies out of range.

        dsp.displayLastSeen((lastSeenDateTime))


    for event in pygame.event.get():
        if event.type == pygame.FINGERUP:
            for btn in buttonList:                
                if (btn.isSelected() and (not (btn.isDisabled() or btn.isHidden()))):
                    if (btn.getType() == Button.Type.STICKY):
                        btn.toggleButton()

                    if (btn.getType() == Button.Type.MOMENTARY):
                        btn.pushButton()

    dsp.refreshDisplay()
