# Author: Nicholas Nell
# nicholas.nell@colorado.edu
#
# Rapid setup for SISTINE Nocturn testing...

import sys
import serial
import time

# default Nocturn baud...
DEF_BAUD = 115200


IMGFMT = "imgfmt 0\r\n"
RETICLE = "dr c 1 640 512 25 2 0xff\r\n"
RET2 = "dr c 2 640 912 25 2 0xff\r\n"
RET3 = "dr c 3 294 712 25 2 0xff\r\n"
DRAWON = "dr enable 1\r\n"
DRAWCLR = "dr sc\r\n"
CONTRAST = "contrast 0\r\n"
AVON = "av power 1\r\n"


BUDRATE = "baudrate usb 921600\r\n"



CMD_LIST = [IMGFMT, DRAWCLR, RETICLE, RET2, RET3, DRAWON, CONTRAST, AVON]


def send_blk(s, b):
    b = bytes(b, 'ASCII')
    s.write(b)


def main(devname):
    s = serial.Serial(devname, baudrate = DEF_BAUD, timeout = 5.0)


    for cmd in CMD_LIST:
        print(cmd)
        send_blk(s, cmd)
        time.sleep(0.2)
        n = s.inWaiting()
        r = s.read(n)
        r = r.decode('ASCII')
        print(r)


    # time.sleep(0.2)
    # send_blk(s, BUDRATE)
    # s.close()

    # time.sleep(0.2)
    # s = serial.Serial(devname, baudrate = 921600, timeout = 5.0)

    # send_blk(s, IMGFMT)
    # time.sleep(0.2)
    # n = s.inWaiting()
    # r = s.read(n).decode('ASCII')
    # print(r)

        
    exit()


    
    s.write(IMGFMT)
    time.sleep(0.1)
    #r = s.read_until("\n")
    n = s.inWaiting()
    print(n)
    r = s.read(n)
    print(r)


    s.close()
    exit()
    
    s.write(DRAWCLR)
    time.sleep(0.1)
    s.write(RETICLE)
    time.sleep(0.1)
    s.write(DRAWON)
    time.sleep(0.1)
    s.write(CONTRAST)
    time.sleep(0.1)

    s.write(AVON)
    time.sleep(0.1)
    

    s.close()

    time.sleep(0.5)

    s = serial.Serial(devname, baudrate = 921600)

    s.write()

    s.close()
    

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("usb device required...")

    main(sys.argv[1])
