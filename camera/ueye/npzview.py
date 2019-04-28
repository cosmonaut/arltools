# Author: Nicholas Nell
# nicholas.nell@colorado.edu
#
# View npz format images saved by custom ueye software.


import sys
import numpy as np
import imageio
import matplotlib.pyplot as mp




def stack(flist):
    im = imageio.imread(flist[0])
    z = np.zeros(np.shape(im), dtype = np.uint32)
                           
    for fn in flist:
        im = imageio.imread(fn)
        z = z + im

    mp.imshow(z)
    mp.show()

def main(fname):
    im = imageio.imread(fname)
    mp.imshow(im)
    mp.show()

    # could also save as fits etc...

if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: npzview.py <filename>")
        exit()

    if (len(sys.argv) == 2):
        main(sys.argv[1])
    else:
        stack(sys.argv[1:])

