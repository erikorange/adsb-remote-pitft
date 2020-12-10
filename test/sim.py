import sys
import socket
import time

filename = "C:\\Users\\Erik\\Documents\\adsb-scanner\\squitters.txt"
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
