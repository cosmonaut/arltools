# Author: Nicholas Nell
# nicholas.nell@colorado.edu
#
# Counter needs to be set up to print to serial port at 1 Hz.
#
# Line choices optimized for hollow cathode lamp with H/Ar mix and
# bare MCP detector.


import serial
import numpy as np
import sys
import vm502



# Wavelengths for scan (Lya removed)
LAMBDA = ['65.0', '87.9', '91.9', '93.1', '97.2', '102.5',
          '104.7', '106.6', '109.9', '111.5',
          '114.4', '116.0', '117.4', '119.8', 
          '125.0', '130.2', '65.0']

#              '121.4', '125.0', '65.0']

# # Wavelengths for scan
# LAMBDA = ['65.0', '87.9', '91.9', '93.1', '97.2', '102.5',
#           '104.7', '106.6', '109.9', '111.5',
#           '114.4', '116.0', '117.4', '119.8', '121.1', 
#           '121.4', '121.8', '125.0', '65.0']


# Number of samples to average per wavelength
#N = 10
N = 5


# Read N samples from counter and return average
def read_n_samples(s, n):
    s.reset_input_buffer()
    print(s.read_until())
    #print(s.read_until())

    l = []
    for i in range(n):
        v = s.read_until()
        #print(v)
        v = np.float(v.decode('ASCII').replace(',', ''))
        l.append(v)
        #l.append(float(s.read_until()))

    a = np.array(l)
    #return(np.average(a))
    return(np.average(a), np.std(a))



def main(mp, cp, fname):
    ms = serial.Serial(mp, 9600, timeout = 5.0)
    cs = serial.Serial(cp, 9600, timeout = 3.0)

    cs.reset_input_buffer()
    print(cs.read_until())

    cl = vm502.vm502_get_lambda(ms)
    print("Wavelength: {0:s}".format(cl))


    flux = []
    fstd = []
    
    for wav in LAMBDA:
        cl = vm502.vm502_goto(ms, wav)
        print("Wavelength: {0:s}".format(cl))
    
        f, fdev = read_n_samples(cs, N)
        flux.append(f)
        fstd.append(fdev)
        print("Flux: {0:f}, std: {1:f}".format(f, fdev))

    print(LAMBDA)
    print(flux)

    print(np.column_stack((LAMBDA,flux)))
    
    np.savetxt(fname, np.column_stack((LAMBDA, flux, fstd)), delimiter = ',', fmt = '%s')

    cl = vm502.vm502_goto(ms, '65.0')

    cs.close()
    ms.close()



if __name__ == '__main__':
    if (len(sys.argv) < 4):
        print("Usage: monohcscan.py <mono port> <counter port> filename")
        exit()

    mono_port = str(sys.argv[1])
    counter_port = str(sys.argv[2])
        
    print("Monochromator Port: {0:s}".format(mono_port))
    print("Counter Port: {0:s}".format(counter_port))

    fname = sys.argv[3]
    print("Saving to file: {0:s}".format(fname))

    main(mono_port, counter_port, fname)
