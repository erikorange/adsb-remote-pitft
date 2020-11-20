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


def holdOn():
    global holdMode, adsbObj
    holdMode = True
    adsbObj.clearLastFlightData()
    dsp.clearLastSeen()
    dsp.clearRecentsPane()
    dsp.drawRadar(600,195,165,110)

def holdOff():
    global holdMode, adsbObj
    holdMode = False
    # Why clear this?
    adsbObj.clearLastCallsignID()
    adsbObj.clearLastFlightData()
    dsp.clearDistance()
    dsp.clearFlightData()
    dsp.clearRadar()
    dsp.drawRecentsPane()
    dsp.displayCivRecents(civRecents)
    dsp.displayMilRecents(milRecents)
    

def milOn():
    global milMode, dsp
    milMode = True
    dsp.clearICAOid()
    dsp.clearCallsign()
    dsp.clearFlightData()
    dsp.clearLastSeen()
    return

def milOff():
    global milMode
    milMode = False
    return

def bigOn():
    return

def bigOff():
    return

def dataOn():
    return

def dataOff():
    return

def addToRecents(callSign, que):
    try:
        x = list(que).index(callSign)
    except ValueError:
        que.appendleft(callSign)
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
lastID = ''
currentCallsign = ''
lastCallSign = ''
adsbIdx=1
medRed = (80,0,0)
medPurple = (80,0,80)
medBlue = (0,0,80)
gray = (128,128,128)
darkGreen=(0,32,0)
dataColor=(0,32,32)

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.bind(('', 49001))
sck.setblocking(0)

dsp.drawRecentsPane()

buttonList = []
holdBtn = Button(dsp.lcd, 5, 419, 100, 60, dsp.btnFont, medPurple, gray, "HOLD", holdOn, holdOff)
buttonList.append(holdBtn)
milBtn = Button(dsp.lcd, 120, 419, 100, 60, dsp.btnFont, darkGreen, gray, "MIL", milOn, milOff)
buttonList.append(milBtn)
bigBtn = Button(dsp.lcd, 235, 419, 100, 60, dsp.btnFont, medBlue, gray, "BIG", bigOn, bigOff)
buttonList.append(bigBtn)
dataBtn = Button(dsp.lcd, 350, 419, 100, 60, dsp.btnFont, dataColor, gray, "DATA", dataOn, dataOff)
buttonList.append(dataBtn)
exitBtn = Button(dsp.lcd, 695, 419, 100, 60, dsp.btnFont, medRed, gray, "EXIT", exitSystem, exitSystem)
buttonList.append(exitBtn)
pygame.display.update()

while True:
    try:
        data, address = sck.recvfrom(256)
    except socket.error:
        pass
    else:
        adsbObj.loadData(data.decode('utf-8'))
        currentID = adsbObj.ICAOid
        currentCallsign = adsbObj.callsign.strip()

        if (currentCallsign != ""):
            if (Util.isMilCallsign(currentCallsign)):
                milRecents = addToRecents(currentCallsign, milRecents)
                milList.add((currentID, currentCallsign))
                if (not holdMode):
                    dsp.displayMilRecents(milRecents)
                #dsp.displayMilCount(len(milList))
            else:
                civRecents = addToRecents(currentCallsign, civRecents)
                civList.add((currentID, currentCallsign))
                if (not holdMode):
                    dsp.displayCivRecents(civRecents)
                #dsp.displayCivCount(len(civList))


        if (holdMode and (currentID == lastID)):
            dsp.clearICAOid()
            dsp.clearCallsign()
            dsp.clearFlightData()
            dsp.displayICAOid(lastID)
            dsp.displayCallsign(lastCallSign, Util.isMilCallsign(lastCallSign))
            dsp.displayLastSeen(adsbObj)
            dsp.displayFlightData(adsbObj, True)

            if (adsbObj.lat != "" and adsbObj.lon != ""):
                dist = Util.haversine(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsbObj.lat), float(adsbObj.lon))
                dsp.displayDistance(dist, bearing)
                dsp.drawRadarBlip(bearing,dist)
                adsbObj.lastDist, adsbObj.lastBearing = (dist, bearing)
            elif (not adsbObj.lastDist is None):
                dsp.displayDistance(adsbObj.lastDist, adsbObj.lastBearing)

        elif (not holdMode and ((not milMode and currentCallsign != "") or (milMode and Util.isMilCallsign(currentCallsign)))):
            dsp.clearICAOid()
            dsp.clearCallsign()
            dsp.displayICAOid(currentID)
            dsp.displayCallsign(currentCallsign, Util.isMilCallsign(currentCallsign))
            dsp.displayLastSeen(adsbObj)
            dsp.displayFlightData(adsbObj, False)
            lastCallSign = currentCallsign
            lastID = currentID

    for event in pygame.event.get():
        if event.type == pygame.FINGERUP:
            for btn in buttonList:                
                if btn.isSelected():
                    btn.toggleButton()

    dsp.refreshDisplay()


#   WAS NORMAL MODE
#        if (currentMode == Mode.CallsignOnly and currentCallsign != ""):
#            dsp.displayCallsign(currentCallsign, Util.isMilCallsign(currentCallsign))
#            dsp.displayLastSeen(adsb)
#            dsp.displayFlightData(adsb, False)
#
#            lastCallSign = currentCallsign
#            lastId = currentId
#
#
#   WAS HOLD MODE            
#        if (currentMode == Mode.FlightNumeric and (currentId == lastId)):
#            dsp.displayCallsign(lastCallSign, Util.isMilCallsign(lastCallSign))
#            dsp.displayLastSeen(adsb)
#            dsp.displayFlightData(adsb, True)
#
#            if (adsb.lat != "" and adsb.lon != ""):
#                dist = Util.haversine(HOME_LON, HOME_LAT, float(adsb.lon), float(adsb.lat)) * 0.62137 # convert km to mi
#                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsb.lat), float(adsb.lon))
#                dsp.displayDistance(dist, bearing)
#                dsp.drawRadarBlip(640,247,120,bearing,dist,50)
#                adsb.lastDist = dist
#                adsb.lastBearing = bearing
#            elif (not adsb.lastDist is None):
#                dsp.displayDistance(adsb.lastDist, adsb.lastBearing)
