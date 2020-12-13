import sys
import socket
import time
import argparse

def sendToSocket(sck, msg):
    retry = True
    while (retry):
        try:
            sck.send(msg)
        except ConnectionRefusedError:
            time.sleep(1)
        except:
            time.sleep(1)
        else:
            retry = False

def getICAOid(squitter):
    dataVals = squitter.split(",")
    return(dataVals[4])

def convertToUpper(list):
    if (list != None):
        return [x.upper() for x in list]

parser = argparse.ArgumentParser()
parser.add_argument('--filter', action='store', type=str, nargs="*", help="only use these ICAO IDs")
parser.add_argument("--replace", nargs=2, action="store", help="substitute one callsign with another callsign")
parser.add_argument("--loop", action="store_true", help="keep replaying squitter file")
parser.add_argument("file", type=str, help="squitter filename")
args = parser.parse_args()

args.filter = convertToUpper(args.filter)
args.replace = convertToUpper(args.replace)

total = sum(1 for line in open(args.file))
print("{:,} simulated squitters".format(total))

sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.connect(('127.0.0.1', 49001))


squitterFile = open(args.file, 'r')
while True:
    idx = 0
    for line in squitterFile:
        if (args.filter == None):               # no filtering, process everything
            process = True
        elif (getICAOid(line) in args.filter):  # some filter was specified, check if a match and process is found
            process = True
        else:
            process = False                     # skip this record

        if (process):
            if (args.replace):
                if args.replace[0] in line:
                    line = line.replace(args.replace[0], args.replace[1])
            msg = bytes(line.strip(), 'utf-8')
            sendToSocket(sck, msg)
            time.sleep(0.01)
            
        idx +=1
        print("{:,}\r".format(idx), end="")

    if (not args.loop):
        break

squitterFile.close()
