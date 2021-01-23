import re
import os
from math import degrees, radians, cos, sin, asin, sqrt, atan2
from datetime import datetime
import platform

class Util:

    @staticmethod
    def calcPageRange(n, pageSize):
        endIdx = n*pageSize - 1
        bgnIdx = endIdx - (pageSize - 1)
        return(bgnIdx, endIdx)

    @staticmethod
    def getPage(pageNum, pageSize, theList):
        pageRange = Util.calcPageRange(pageNum, pageSize)

        rBegin = pageRange[0]
        rEnd = pageRange[1]
        listlen = len(theList)

        if (rBegin > listlen - 1):
            return None

        if (rEnd <= listlen - 1):
           endIdx = rEnd + 1
        else:
           endIdx = listlen

        result=[]
        for x in range(rBegin, endIdx):
            result.append(theList[x])

        return result

    @staticmethod
    def isWindows():
        if (platform.system() == 'Windows'):
            return True
        else:
            return False

    @staticmethod
    def shutdownSystem():
        sd = os.popen('sudo shutdown -h now').readline()
        return
        
    @staticmethod
    def setCurrentDir(dirpath):
        os.chdir(dirpath)
    
    @staticmethod
    def getGndSpeedText(kts_s):
        try:
            kts = int(kts_s)
        except ValueError:
            return ''
        
        mph = int(kts*1.151)
        return f'{mph} mph'


    @staticmethod
    def timestamp(txt):
        print(datetime.now().strftime("%Y-%m-%d %H:%M:%S") + ' ' + txt)

    @staticmethod
    def getCPUTemp():
        res = os.popen('vcgencmd measure_temp').readline()
        tempC = float(res.replace("temp=","").replace("'C\n",""))
        return "{0:0.1f}".format(tempC)
    
    @staticmethod
    def getUptime():
        ut = os.popen('uptime -p').readline()
        return ut.replace("\n","").replace("hours", "hr").replace("minutes", "min").replace("up ", "")

    @staticmethod
    def isMilCallsign(cs):
    # starts with at least 4 letters, then at least 2 numbers; or starts with RCH or TOPCAT; or is GOTOFMS.  Remove spaces for VADER xx
        match = re.search(r'(^(?!TEST)(?!RPPA)(?!RRPA)[A-Z]{4,}[0-9]{2,}$)|(^RCH)|(^TOPCAT)|(GOTOFMS)', cs.replace(' ',''))
        if match:
            return 1
        else:
            return 0

    @staticmethod
    def haversine(homeLat, homeLon, aircraftLat, aircraftLon):
        # convert decimal degrees to radians 
        homeLon, homeLat, aircraftLon, aircraftLat = map(radians, [homeLon, homeLat, aircraftLon, aircraftLat])

        # haversine formula 
        dlon = aircraftLon - homeLon 
        dlat = aircraftLat - homeLat
        a = sin(dlat/2)**2 + cos(homeLat) * cos(aircraftLat) * sin(dlon/2)**2
        c = 2 * asin(sqrt(a)) 
        r = 6371 # Radius of earth in kilometers is 6371.
        return c * r * 0.62137 # convert km to mi

    @staticmethod
    def calculateBearing(homeLat, homeLon, aircraftLat, aircraftLon):
        homeLat = radians(homeLat)
        aircraftLat = radians(aircraftLat)
        diffLong = radians(aircraftLon - homeLon)
        x = sin(diffLong) * cos(aircraftLat)
        y = cos(homeLat) * sin(aircraftLat) - (sin(homeLat) * cos(aircraftLat) * cos(diffLong))
        initial_bearing = atan2(x, y)
        initial_bearing = degrees(initial_bearing)
        compass_bearing = (initial_bearing + 360) % 360
        return compass_bearing

    @staticmethod
    def getCompassDir(bearing):
        tmp = round(bearing / 22.5)
        if (tmp == 1):
            return "NNE"
        elif (tmp == 2):
            return "NE"
        elif (tmp == 3):
            return "ENE"
        elif (tmp == 4):
            return "E"
        elif (tmp == 5):
            return "ESE"
        elif (tmp == 6):
            return "SE"
        elif (tmp == 7):
            return "SSE"
        elif (tmp == 8):
            return "S"
        elif (tmp == 9):
            return "SSW"
        elif (tmp == 10):
            return "SW"
        elif (tmp == 11):
            return "WSW"
        elif (tmp == 12):
            return "W"
        elif (tmp == 13):
            return "WNW"
        elif (tmp == 14):
            return "NW"
        elif (tmp == 15):
            return "NNW"
        else:
            return "N"