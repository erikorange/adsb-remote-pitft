import sys
import time
import argparse
import re


def isMilCallsign(callsign):
    # starts with at least 4 letters, then at least 2 numbers; or starts with RCH or TOPCAT; or is GOTOFMS.  Remove spaces for VADER xx
        match = re.search(r'(^(?!TEST)[A-Z]{4,}[0-9]{2,}$)|(^RCH)|(^TOPCAT)|(GOTOFMS)', callsign.replace(' ',''))
        if match:
            return 1
        else:
            return 0

def writeListToFile(list, filename):
    if (len(list) == 0):
        return
        
    with open (filename, 'w') as f:
        for row in list:
            f.write(f"{row[0]} {row[1]}\n")


parser = argparse.ArgumentParser()
parser.add_argument("sqFile", type=str, help="squitter filename")
args = parser.parse_args()

civList = set()
milList = set()

idx = 0
total = sum(1 for line in open(args.sqFile))
print("Analyzing {:,} rows".format(total))

for l in open(args.sqFile):
    line = l.strip()
    vals = line.split(",")
    callsign = vals[10].strip()

    if (callsign != ""):
        id = vals[4]
        if (isMilCallsign(callsign)):
            milList.add((id,callsign))
        else:
            civList.add((id,callsign))

    idx += 1
    pct = idx/total*100
    print("{0:0.1f}% complete\r".format(pct), end="")

print("")
print("Civilian: {:,}".format(len(civList)))
print("Military: {:,}".format(len(milList)))

writeListToFile(civList, "civilian.txt")
writeListToFile(milList, "military.txt")

  
