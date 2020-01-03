import sys
import signal
import time
import re
import socket
from display import Display

def shutdownEvent(signal, frame):
    sys.exit(0)

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

dsp = Display()

dsp.setupAdsbDisplay()

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
addr = ('', 49001)
sck.bind(addr)

while True:
    data, address = sck.recvfrom(1024)
    txt = data.decode('utf-8')
    dataVals = txt.split(",")
    ICAOid = dataVals[4]
    callsign = dataVals[10]
    if (callsign != ""):
        dsp.clearCallsignAndID()
        dsp.displayICAOid(ICAOid)
        dsp.displayCallsign(callsign, isMilCallsign(callsign))
        dsp.refreshDisplay()





#while True:
#    p = dsp.check()
#    if (p is not None):
#        dsp.drawSquare(p)




