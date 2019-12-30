import sys
import signal
import time
from display import Display

def shutdownEvent(signal, frame):
    sys.exit(0)

signal.signal(signal.SIGTERM, shutdownEvent)
signal.signal(signal.SIGINT, shutdownEvent)
signal.signal(signal.SIGTSTP, shutdownEvent)

dsp = Display()
dsp.setupAdsbDisplay()

while True:
    p = dsp.check()
    if (p is not None):
        dsp.drawSquare(p)




