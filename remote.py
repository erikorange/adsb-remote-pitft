import sys
import signal
import time
import re
import socket
import enum
from display import Display
from adsb import Adsb
from util import Util

class Mode(enum.Enum): 
    CallsignOnly = 1
    FlightNumeric = 2
    FlightRadar = 3


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


def isMilCallsign(cs):
    # starts with at least 4 letters, then at least 2 numbers; or starts with RCH or TOPCAT; or is GOTOFMS.  Remove spaces for VADER xx
    match = re.search(r'(^[A-Z]{4,}[0-9]{2,}$)|(^RCH)|(^TOPCAT)|(GOTOFMS)', cs.replace(' ',''))
    if match:
        return 1
    else:
        return 0


signal.signal(signal.SIGTERM, shutdownEvent)
signal.signal(signal.SIGINT, shutdownEvent)
signal.signal(signal.SIGTSTP, shutdownEvent)

HOME_LAT, HOME_LON = getHomeLatLon("home-lat-lon.txt")

dsp = Display()
dsp.setupAdsbDisplay()
adsb = Adsb()

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.bind(('', 49001))
sck.setblocking(0)

currentMode = Mode.CallsignOnly
lastId = ''
lastCallSign = ''

adsbIdx=1

dsp.defineRadarPoints(250,220,90)

while True:
    try:
        data, address = sck.recvfrom(256)
    except socket.error:
        pass
    else:
        adsb.loadData(data.decode('utf-8'))
        currentId = adsb.ICAOid
        currentCallsign = adsb.callsign

        if (currentMode == Mode.CallsignOnly and currentCallsign != ""):
            dsp.displayCallsign(currentCallsign, isMilCallsign(currentCallsign))
            dsp.displayLastSeen(adsb)
            dsp.displayFlightData(adsb, False)

            lastCallSign = currentCallsign
            lastId = currentId

            
        if (currentMode == Mode.FlightNumeric and (currentId == lastId)):
            dsp.displayCallsign(lastCallSign, isMilCallsign(lastCallSign))
            dsp.displayLastSeen(adsb)
            dsp.displayFlightData(adsb, True)

            if (adsb.lat != "" and adsb.lon != ""):
                dist = Util.haversine(HOME_LON, HOME_LAT, float(adsb.lon), float(adsb.lat)) * 0.62137 # convert km to mi
                bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsb.lat), float(adsb.lon))
                dsp.displayDistance(dist, bearing)
                adsb.lastDist = dist
                adsb.lastBearing = bearing
            elif (not adsb.lastDist is None):
                dsp.displayDistance(adsb.lastDist, adsb.lastBearing)

        if (currentMode == Mode.FlightRadar):
            #TODO - check if there's a dist,bearing

            dsp.drawRadarLine(250, 220, 90, adsb.lastBearing, adsb.lastDist, 190)
            #dsp.displayDistance(dist, bearing)

            if (currentId == lastId):
                if (adsb.lat != "" and adsb.lon != ""):
                    dist = Util.haversine(HOME_LON, HOME_LAT, float(adsb.lon), float(adsb.lat)) * 0.62137 # convert km to mi
                    bearing = Util.calculateBearing(HOME_LAT, HOME_LON, float(adsb.lat), float(adsb.lon))
                    
                    adsb.lastDist = dist
                    adsb.lastBearing = bearing
                elif (not adsb.lastDist is None):
                    #remove!  maybe whole elif
                    zzz=4
                    #dsp.displayDistance(adsb.lastDist, adsb.lastBearing)

        #TODO - ensure this is the only update
        dsp.refreshDisplay()
  
    if (dsp.checkTap()):
        if (currentMode == Mode.CallsignOnly):
            currentMode = Mode.FlightNumeric

        elif (currentMode == Mode.FlightNumeric):
            currentMode = Mode.FlightRadar

        else:
            currentMode = Mode.CallsignOnly
            dsp.clearDistance()
            adsb.clearLastFlightData()


#TODO - remove?
#dsp.displayHoldMode(holdMode)

    

