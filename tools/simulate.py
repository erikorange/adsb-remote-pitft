# --file <filename> required
# --feed | --summary

import sys
import socket
import time
import argparse
import re


def isMilCallsign(cs):
    # starts with at least 4 letters, then at least 2 numbers; or starts with RCH or TOPCAT; or is GOTOFMS.  Remove spaces for VADER xx
        match = re.search(r'(^(?!TEST)[A-Z]{4,}[0-9]{2,}$)|(^RCH)|(^TOPCAT)|(GOTOFMS)', cs.replace(' ',''))
        if match:
            return 1
        else:
            return 0

def summary(filename):
    civList = set()
    milList = set()
    civCnt = 0
    milCnt = 0
    idx = 0
    total = sum(1 for line in open(filename))

    for line in open(filename):
        l = line.strip()
        vals = l.split(",")
        cs = vals[10].strip()
        if (cs != ""):
            id = vals[4]
            if (isMilCallsign(cs)):
                milList.add((id,cs))
                milCnt += 1
            else:
                civList.add((id,cs))
                civCnt += 1

        idx += 1
        pct = idx/total*100
        print("{0:0.1f}% complete\r".format(pct), end="")

    print("Civilian: {:,}".format(civCnt))
    print("Military: {:,}".format(milCnt))
    

    return







parser = argparse.ArgumentParser()
parser.add_argument("file", type=str, help="squitter file")
group = parser.add_mutually_exclusive_group()
group.add_argument("--feeder", action="store_true", help="feed squitter file to remote head")
group.add_argument("--summary", action="store_true", help="display a summary of squitter file callsigns")
args = parser.parse_args()

if (args.feeder):
    print("feeder")
elif (args.summary):
    summary(args.file)

print("done.")
sys.exit(0)




filename = "C:\\Users\\Erik\\Documents\\adsb-scanner\\squittersss.txt"
print(filename)
f = open(filename, 'r')
sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sck.connect(('127.0.0.1', 49001))
count=0

while True: 
    line = f.readline() 
    if not line: 
        break
    
    msg = bytes(line.strip(), 'utf-8')
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
    count +=1
    time.sleep(0.01)
    print(str(count))

f.close()
print("done.")
