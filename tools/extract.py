import argparse

def getICAOid(squitter):
    dataVals = squitter.split(",")
    return(dataVals[4])

parser = argparse.ArgumentParser()
parser.add_argument('--idlist', action='store', type=str, nargs="*", help="only use these ICAO IDs")
parser.add_argument("file", type=str, help="squitter filename")
args = parser.parse_args()

idx = 0
total = sum(1 for line in open(args.file))
print("{:,} squitters".format(total))

with open ('extract.txt', 'w') as f:
    for line in open(args.file):
        if (getICAOid(line) in args.idlist):
            f.write(line)
    
        idx += 1
        print("{:,}\r".format(idx), end="")
    