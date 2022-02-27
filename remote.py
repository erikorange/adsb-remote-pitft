import sys
import signal
import time
import re
import socket
import enum
import pygame
import collections
import datetime

from display import Display
from button import Button
from adsb import Adsb
from radar import Radar
from util import Util

class State(enum.Enum): 
    CIV_MIL = 1
    CIV_MIL_HOLD = 2
    CIV_MIL_BIG = 3
    MIL_ONLY = 4
    MIL_ONLY_HOLD = 5
    MIL_ONLY_BIG = 6
    INFO = 7

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

def powerOff():
    Util.shutdownSystem()

def zoomBtnOut():
    radar.decreaseScale()
    radar.refreshDisplay()

def zoomBtnIn():
    radar.increaseScale()
    radar.refreshDisplay()

def holdBtnOn():
    global curState, adsbObj
    if (curState == State.CIV_MIL):
        curState = State.CIV_MIL_HOLD

    elif (curState == State.MIL_ONLY):
        curState = State.MIL_ONLY_HOLD

    adsbObj.clearLastFlightData()
    dsp.clearLastSeen()
    dsp.clearRecentsPane()
    radar.drawRadarScreen()
    radar.clearPosList()
    plusBtn.drawButton(Button.State.ON)
    minusBtn.drawButton(Button.State.ON)
    bigBtn.drawButton(Button.State.DISABLED)
    
def holdBtnOff():
    global curState, adsbObj, currentCallsign, lastSeenDateTime
    if (curState == State.CIV_MIL_HOLD):
        curState = State.CIV_MIL
        milBtn.drawButton(Button.State.OFF)

    elif (curState == State.MIL_ONLY_HOLD):
        curState = State.MIL_ONLY

    plusBtn.drawButton(Button.State.HIDDEN)
    minusBtn.drawButton(Button.State.HIDDEN)
    bigBtn.drawButton(Button.State.OFF)
    adsbObj.clearLastCallsignAndID()
    adsbObj.clearLastFlightData()
    dsp.clearDistance()
    dsp.clearFlightData()
    radar.clearRadar()
    dsp.drawRecentsPane()
    dsp.displayCivRecents(civRecents, currentCallsign)
    dsp.displayMilRecents(milRecents, currentCallsign)
    lastSeenDateTime = ()
    
def milBtnOn():
    global curState, lastSeenDateTime, adsbObj

    # if curstate = civ_mil_big then curstate=mil_big; if curcallsign isn't mil then clear everything

    if (curState == State.CIV_MIL_HOLD):
        holdBtn.drawButton(Button.State.OFF)
        plusBtn.drawButton(Button.State.HIDDEN)
        minusBtn.drawButton(Button.State.HIDDEN)
        adsbObj.clearLastCallsignAndID()
        adsbObj.clearLastFlightData()
        dsp.clearDistance()
        dsp.clearFlightData()
        radar.clearRadar()
        dsp.drawRecentsPane()
        dsp.displayCivRecents(civRecents, currentCallsign)
        dsp.displayMilRecents(milRecents, currentCallsign)
        lastSeenDateTime = ()

    curState = State.MIL_ONLY
    dsp.clearICAOid()
    dsp.clearCallsign()
    adsbObj.clearLastCallsignAndID()
    dsp.clearFlightData()
    dsp.clearLastSeen()
    lastSeenDateTime = ()
    

def milBtnOff():
    global curState, lastSeenDateTime

    # if curstate = mil_big then curstate=civ_mil_big;

    if (curState == State.MIL_ONLY_HOLD):
        holdBtn.drawButton(Button.State.OFF)
        plusBtn.drawButton(Button.State.HIDDEN)
        minusBtn.drawButton(Button.State.HIDDEN)
        adsbObj.clearLastCallsignAndID()
        adsbObj.clearLastFlightData()
        dsp.clearDistance()
        dsp.clearFlightData()
        radar.clearRadar()
        dsp.drawRecentsPane()
        dsp.displayCivRecents(civRecents, currentCallsign)
        dsp.displayMilRecents(milRecents, currentCallsign)
        lastSeenDateTime = ()

    else:
    # curState = State.MIL_ONLY
        dsp.clearICAOid()
        dsp.clearCallsign()
        dsp.clearFlightData()
        dsp.clearLastSeen()
        lastSeenDateTime = ()
    
    curState = State.CIV_MIL

def bigOn():
    global curState, lastState, holdBtnState, milBtnState
    
    dsp.clearDisplayArea()
    lastState = curState
    # BIG is only available in these 2 states
    if (lastState == State.CIV_MIL):
        curState = State.CIV_MIL_BIG
    else:
        curState = State.MIL_ONLY_BIG

    # save button states
    holdBtnState = holdBtn.getState()
    milBtnState = milBtn.getState()
    holdBtn.drawButton(Button.State.HIDDEN)
    milBtn.drawButton(Button.State.HIDDEN)
    infoBtn.drawButton(Button.State.HIDDEN)

    return

def bigOff():
    global curState, lastState, holdBtnState, milBtnState, civRecents, milRecents, currentCallsign
    dsp.clearDisplayArea()
    curState = lastState
    holdBtn.drawButton(holdBtnState)
    milBtn.drawButton(milBtnState)
    infoBtn.drawButton(Button.State.OFF)

    dsp.displayICAOid(adsbObj.lastID)
    # mil mode might have been turned on, but a mil callsign hasn't been received yet.  Skip if no callsign:
    if (not (adsbObj.lastCallsign is None)):
        dsp.displayCallsign(adsbObj.lastCallsign, Util.isMilCallsign(adsbObj.lastCallsign))
    dsp.displayFlightData(adsbObj, True)

    dsp.drawRecentsPane()
    dsp.displayCivRecents(civRecents, currentCallsign)
    dsp.displayMilRecents(milRecents, currentCallsign)

    return


def infoOn():
    global curState, lastState, holdBtnState, milBtnState, startAgain, startTime, startCount, endTime, squitterRate, delta, cpuTemp, winFlag
    startAgain = True
    startTime = None
    endTime = None
    startCount = 0
    squitterRate = 0
    delta = 0

    if (winFlag):
        cpuTemp = "n/a"
    else:
        temp = Util.getCPUTemp()
        deg = u'\N{DEGREE SIGN}'
        cpuTemp = f'{temp}{deg}C'

    dsp.clearDisplayArea()
    lastState = curState
    curState = State.INFO
    # save button states
    holdBtnState = holdBtn.getState()
    milBtnState = milBtn.getState()
    holdBtn.drawButton(Button.State.HIDDEN)
    milBtn.drawButton(Button.State.HIDDEN)
    bigBtn.drawButton(Button.State.HIDDEN)
    #historyBtn.drawButton(Button.State.ON)

    if (lastState == State.MIL_ONLY_HOLD or lastState == State.CIV_MIL_HOLD):
        plusBtn.drawButton(Button.State.HIDDEN)
        minusBtn.drawButton(Button.State.HIDDEN)
        
    dsp.drawInfoPane()


def infoOff():
    global curState, lastState, holdBtnState, milBtnState, civRecents, milRecents, currentCallsign
    dsp.clearDisplayArea()
    curState = lastState
    holdBtn.drawButton(holdBtnState)
    milBtn.drawButton(milBtnState)
    bigBtn.drawButton(Button.State.OFF)
    #historyBtn.drawButton(Button.State.HIDDEN)

    if (curState == State.CIV_MIL_HOLD or curState == State.MIL_ONLY_HOLD):
        bigBtn.drawButton(Button.State.DISABLED)
        radar.drawRadarScreen()
        radar.plotTotalPath()
        plusBtn.drawButton(Button.State.ON)
        minusBtn.drawButton(Button.State.ON)
        dsp.displayICAOid(adsbObj.lastID)
        # mil mode might have been turned on, but a mil callsign hasn't been received yet.  Skip if no callsign:
        if (not (adsbObj.lastCallsign is None)):
            dsp.displayCallsign(adsbObj.lastCallsign, Util.isMilCallsign(adsbObj.lastCallsign))
        dsp.displayFlightData(adsbObj, True)

    elif (curState == State.CIV_MIL or curState == State.MIL_ONLY):
        dsp.drawRecentsPane()
        dsp.displayCivRecents(civRecents, currentCallsign)
        dsp.displayMilRecents(milRecents, currentCallsign)

def addItemToUniqueList(item, list):
    list.append(item) if item not in list else None


def addToRecents(callsign, que):
    try:
        x = list(que).index(callsign)
    except ValueError:
        que.appendleft(callsign)
    return que


winFlag = Util.isWindows()
if (not winFlag):
    signal.signal(signal.SIGTERM, shutdownEvent)
    signal.signal(signal.SIGINT, shutdownEvent)
    signal.signal(signal.SIGTSTP, shutdownEvent)
    Util.setCurrentDir('/home/pi/adsb-remote')


HOME_LAT, HOME_LON = getHomeLatLon("home-lat-lon.txt")

dsp = Display(winFlag)
dsp.setupAdsbDisplay()
adsbObj = Adsb()
radar = Radar(dsp.lcd)

civRecents = collections.deque(maxlen=10)
civList = []
milRecents = collections.deque(maxlen=10)
milList = []
holdMode = False
milMode = False
currentID = ''
currentCallsign = ''
lastSeenDateTime = ()
hasCallsign = False
isMilCallsign = False
adsbCount=0
curState = State.CIV_MIL
lastState = None
holdBtnState = None
milBtnState = None
startAgain = True
startTime = None
endTime = None
startCount = 0
squitterRate = 0
delta = 0
cpuTemp = ''

medRed = (80,0,0)
medPurple = (80,0,80)
medBlue = (0,0,80)
green = (0,110,0)
gray = (128,128,128)
darkGreen=(0,32,0)
dataColor=(40,40,0)
white=(255,255,255)

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)   # added for simulator
sck.bind(('', 49001))
sck.setblocking(0)

dsp.drawRecentsPane()
dsp.drawDataLEDs()

buttonList = []
holdBtn = Button(dsp.lcd, 5, 438, 100, 40, dsp.btnFont, medPurple, gray, "HOLD", holdBtnOn, holdBtnOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(holdBtn)
milBtn = Button(dsp.lcd, 115, 438, 100, 40, dsp.btnFont, darkGreen, gray, "MIL", milBtnOn, milBtnOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(milBtn)
infoBtn = Button(dsp.lcd, 225, 438, 100, 40, dsp.btnFont, medBlue, gray, "INFO", infoOn, infoOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(infoBtn)
bigBtn = Button(dsp.lcd, 335, 438, 100, 40, dsp.btnFont, dataColor, gray, "BIG", bigOn, bigOff, Button.State.OFF, Button.Type.STICKY)
buttonList.append(bigBtn)
exitBtn = Button(dsp.lcd, 695, 438, 100, 40, dsp.btnFont, medRed, gray, "EXIT", exitSystem, None, Button.State.OFF, Button.Type.MOMENTARY)
buttonList.append(exitBtn)
#offBtn = Button(dsp.lcd, 695, 429, 100, 50, dsp.btnFont, medRed, gray, "OFF", powerOff, None, Button.State.OFF, Button.Type.MOMENTARY)
#buttonList.append(offBtn)

plusBtn = Button(dsp.lcd, 545, 438, 40, 40, dsp.btnRadarFont, darkGreen, white, "+", zoomBtnOut, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
buttonList.append(plusBtn)
minusBtn = Button(dsp.lcd, 605, 438, 40, 40, dsp.btnRadarFont, darkGreen, white, "-", zoomBtnIn, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
buttonList.append(minusBtn)
#historyBtn = Button(dsp.lcd, 5, 40, 100, 50, dsp.btnFont, green, white, "LIST", historyOn, None, Button.State.HIDDEN, Button.Type.MOMENTARY)
#buttonList.append(historyBtn)


pygame.display.update()

while True:
    try:
        data, address = sck.recvfrom(256)
    except socket.error:
        pass
    else:
        adsbObj.loadData(data.decode('utf-8'))
        adsbCount += 1

        if (adsbCount % 10 == 0):
            dsp.flipDataLEDs()

        currentID = adsbObj.ICAOid
        currentCallsign = adsbObj.callsign.strip()
    
        # Determine if we have a callsign, and if so, what type.  Then add to the corresponding lists.
        if (currentCallsign != ""):
            hasCallsign = True
            if (Util.isMilCallsign(currentCallsign)):
                isMilCallsign = True
                milRecents = addToRecents(currentCallsign, milRecents)
                addItemToUniqueList((currentID, currentCallsign), milList)
            else:
                isMilCallsign = False
                civRecents = addToRecents(currentCallsign, civRecents)
                addItemToUniqueList((currentID, currentCallsign), civList)
        else:
            hasCallsign = False
            isMilCallsign = False


        # Refresh the recents display if we have a callsign and if we're in a mode that displays them
        if (hasCallsign and (curState == State.CIV_MIL or curState == State.MIL_ONLY)):
            if (isMilCallsign):
                dsp.displayMilRecents(milRecents, currentCallsign)
            else:
                dsp.displayCivRecents(civRecents, currentCallsign)


        if ((curState == State.CIV_MIL and hasCallsign) or (curState == State.MIL_ONLY and isMilCallsign)):
            dsp.clearICAOid()
            dsp.clearCallsign()
            dsp.displayICAOid(currentID)
            dsp.displayCallsign(currentCallsign, isMilCallsign)
            dsp.displayFlightData(adsbObj, False)
            adsbObj.setLastCallsignAndID(currentCallsign, currentID)
            lastSeenDateTime = (adsbObj.theDate, adsbObj.theTime)

        if ((curState == State.CIV_MIL_BIG and hasCallsign) or (curState == State.MIL_ONLY_BIG and isMilCallsign)):
            dsp.clearICAOidBig()
            dsp.clearCallsignBig()
            dsp.displayICAOidBig(currentID)
            dsp.displayCallsignBig(currentCallsign, isMilCallsign)
            adsbObj.setLastCallsignAndID(currentCallsign, currentID)
            lastSeenDateTime = (adsbObj.theDate, adsbObj.theTime)

            # Here, last seen is the time for any airplace.  might not update quickly late at night.
        
        # keep gathering positions if we were in hold mode but now we're in info mode
        if (curState == State.INFO and ((lastState == State.CIV_MIL_HOLD or lastState == State.MIL_ONLY_HOLD) and currentID == adsbObj.lastID)):
            if (adsbObj.lat != "" and adsbObj.lon != ""):
                dist = Util.haversine(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                radar.addToPosList(adsbObj.lat, adsbObj.lon, dist, bearing)

        if ((curState == State.CIV_MIL_HOLD or curState == State.MIL_ONLY_HOLD) and currentID == adsbObj.lastID):
            dsp.displayFlightData(adsbObj, True)
            if (adsbObj.lat != "" and adsbObj.lon != ""):
                dist = Util.haversine(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                dsp.displayDistance(dist, bearing)
                radar.plotCurrentPos(dist, bearing)
                radar.addToPosList(adsbObj.lat, adsbObj.lon, dist, bearing)
                adsbObj.lastDist, adsbObj.lastBearing = (dist, bearing)
            elif (not adsbObj.lastDist is None):
                dsp.displayDistance(adsbObj.lastDist, adsbObj.lastBearing)

            lastSeenDateTime = (adsbObj.theDate, adsbObj.theTime)
            # Here, last seen is the time for this held airplane.  Will age as airplane flies out of range.

        if (curState != State.INFO  and currentCallsign != ""):
            if (curState == State.CIV_MIL_BIG or curState == State.MIL_ONLY_BIG):
                dsp.displayLastSeenBig((lastSeenDateTime))
            else:
                dsp.displayLastSeen((lastSeenDateTime))
        
        if (curState == State.INFO):
            if (startAgain):
                startTime = datetime.datetime.now()
                startCount = adsbCount
                startAgain = False
            
            endTime = datetime.datetime.now()
            delta = (endTime - startTime).total_seconds()
            if (delta >= 1.0):
                squitterRate = adsbCount - startCount
                startAgain = True

            dsp.updateInfoPane(len(civList), len(milList), adsbCount, squitterRate, cpuTemp)


    for event in pygame.event.get():
        if (event.type == pygame.FINGERUP or event.type == pygame.MOUSEBUTTONUP):
            for btn in buttonList:                
                if (btn.isSelected() and (not (btn.isDisabled() or btn.isHidden()))):
                    if (btn.getType() == Button.Type.STICKY):
                        btn.toggleButton()

                    if (btn.getType() == Button.Type.MOMENTARY):
                        btn.pushButton()

    dsp.refreshDisplay()
