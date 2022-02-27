class Adsb():

    def __init__(self):
        self.clearLastCallsignAndID()
        self.clearLastFlightData()

    def clearLastCallsignAndID(self):
        self.__lastCallsign = None
        self.__lastID = None

    def setLastCallsignAndID(self, callsign, id):
        self.__lastCallsign = callsign
        self.__lastID = id

    @property
    def lastID(self):
        return self.__lastID

    @lastID.setter
    def lastID(self, id):
        self.__lastID = id

    @property
    def lastCallsign(self):
        return self.__lastCallsign
	
    @lastCallsign.setter
    def lastCallsign(self, callsign):
        self.__lastCallsign = callsign

    
    def clearLastFlightData(self):
        self.lastDist = None
        self.lastBearing = ""
        self.lastLat = ""
        self.lastLon = ""
        self.lastAltitude = ""
        self.lastVerticalRate = ""
        self.lastGroundSpeed = ""
        self.lastSquawk = ""
        
    def isValidRec(self, rec):
        if rec.count(',') == 21:
            return 1
        return 0

    def loadData(self, rec):
        dataVals = rec.split(",")
        self.ICAOid = dataVals[4]
        self.theDate = dataVals[6]
        self.theTime = dataVals[7]
        self.callsign = dataVals[10].strip()
        self.altitude = dataVals[11]
        self.groundSpeed = dataVals[12]
        self.track = dataVals[13]
        self.lat = dataVals[14]
        self.lon = dataVals[15]
        self.verticalRate = dataVals[16]
        self.squawk = dataVals[17]

        