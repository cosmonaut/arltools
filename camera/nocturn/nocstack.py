# Author: Nicholas Nell
# nicholas.nell@colorado.edu
#
# Stack Nocturn pgm images...

import sys
import numpy as np
import pgmread
import matplotlib.pyplot as mp


def main(flist):
    im = pgmread.read_noc_pgm(flist[0])
    z = np.zeros(im.shape, dtype = np.uint32)

    for name in flist:
        im = pgmread.read_noc_pgm(name)
        z = z + im

    mp.imshow(z)
    mp.show()

    # details...
    exit()
    mp.plot(z[53])
    mp.plot(z[:,79])
    mp.show()

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("usage: nocstack.py <file 1> <file 2> etc")
        exit()

    flist = sys.argv[1:]
    main(flist)
