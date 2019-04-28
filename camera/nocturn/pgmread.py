# Author: Nicholas Nell
# nicholas.nell@colorado.edu
#
# Code to read PGM files from Nocturn camera. Files are either 8 or 10
# bit in 1024x1280 format.
#
# More info: http://netpbm.sourceforge.net/doc/pgm.html


import re
import numpy as np
import matplotlib.pyplot as mp
from matplotlib.colors import LogNorm
import sys



def read_noc_pgm(filename, byteorder = '<'):
    with open(filename, 'rb') as f:
        h1 = f.readline()
        h2 = f.readline()
        wh_vals = f.readline()

        wh_vals = wh_vals.decode("ASCII")
        wh_vals = wh_vals.strip('\r\n')
        wh_vals = wh_vals.split(' ')
        width = int(wh_vals[0])
        height = int(wh_vals[1])
        
        print(h1)
        print(h2)
        print("WIDTH: {0:d}".format(width))
        print("HEIGHT: {0:d}".format(height))

        # This is actually maxval (not bpp)
        bpp = ""
        # For some reason maxval doesn't get a \n terminator in the
        # nocturn... wtf mate.
        while(True):
            #for i in range(10):
            c = f.read(1)
            if (c != b'\r'):
                bpp += str(chr(c[0]))
            else:
                break

        # Now we've got hot bpp action
        bpp = int(bpp)
        print("BPP: {0:d}".format(bpp))

        # remaining payload.
        pload = f.read()

        print(len(pload))

        # inform numpy of proper pixel format...
        if (bpp < 256):
            noc_dtype = '>u1'
        else:
            noc_dtype = '>u2'
        
        im = np.frombuffer(pload, dtype=noc_dtype, count = width*height).reshape((height, width))
            
        return(im)


if __name__ == "__main__":

    if (len(sys.argv) < 2):
        print("need filename...")
        exit()

    fname = sys.argv[1]

    im = read_noc_pgm(fname)
    #mp.imshow(im, norm = LogNorm(vmin = 50))
    mp.imshow(im)
    mp.show()
    
