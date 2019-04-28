#===========================================================================#
#                                                                           #
#  Copyright (C) 2006 - 2018                                                #
#  IDS Imaging Development Systems GmbH                                     #
#  Dimbacher Str. 6-8                                                       #
#  D-74182 Obersulm, Germany                                                #
#                                                                           #
#  The information in this document is subject to change without notice     #
#  and should not be construed as a commitment by IDS Imaging Development   #
#  Systems GmbH. IDS Imaging Development Systems GmbH does not assume any   #
#  responsibility for any errors that may appear in this document.          #
#                                                                           #
#  This document, or source code, is provided solely as an example          #
#  of how to utilize IDS software libraries in a sample application.        #
#  IDS Imaging Development Systems GmbH does not assume any responsibility  #
#  for the use or reliability of any portion of this document or the        #
#  described software.                                                      #
#                                                                           #
#  General permission to copy or modify, but not for profit, is hereby      #
#  granted, provided that the above copyright notice is included and        #
#  reference made to the fact that reproduction privileges were granted     #
#  by IDS Imaging Development Systems GmbH.                                 #
#                                                                           #
#  IDS Imaging Development Systems GmbH cannot assume any responsibility    #
#  for the use or misuse of any portion of this software for other than     #
#  its intended diagnostic purpose in calibrating and testing IDS           #
#  manufactured cameras and software.                                       #
#                                                                           #
#===========================================================================#

# Modified by Nicholas Nell
# nicholas.nell@colorado.edu
# 
# Key controls added for exposure and integration time
# = increase frame rate
# - decrease frame rate
# ] increase exposure time
# [ decrease exposure time
# q quit
# c capture single frame
# a capture long series of frames
# r toggle reticle display

# Requires ueye library to be installed and usb daemon to be enabled
# in order to detect and interact with camera.

#Libraries
from pyueye import ueye
import numpy as np
# for saving an image...
from scipy import misc
#from scipy import imageio
import imageio
import cv2
import sys
import math


#------------------------------------------

#Variables
hCam = ueye.HIDS(0)             #0: first available camera;  1-254: The camera with the specified camera ID
sInfo = ueye.SENSORINFO()
cInfo = ueye.CAMINFO()
pcImageMemory = ueye.c_mem_p()
MemID = ueye.int()
rectAOI = ueye.IS_RECT()
pitch = ueye.INT()
#nBitsPerPixel = ueye.INT(24)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
nBitsPerPixel = ueye.INT(8)    #24: bits per pixel for color mode; take 8 bits per pixel for monochrome
channels = 3                    #3: channels for color mode(RGB); take 1 channel for monochrome
m_nColorMode = ueye.INT()		# Y8/RGB16/RGB24/REG32
bytes_per_pixel = int(nBitsPerPixel / 8)
#---------------------------------------------------------------------------------------------------------------------------------------

def main(fname, ncap):
    print("START")
    print()

    if (ncap > 300):
        print("Warning, requested more than 300 frames stacked, set to 300")
        ncap = 300

    # Starts the driver and establishes the connection to the camera
    nRet = ueye.is_InitCamera(hCam, None)
    if nRet != ueye.IS_SUCCESS:
        print("is_InitCamera ERROR")

    # Reads out the data hard-coded in the non-volatile camera memory and writes it to the data structure that cInfo points to
    nRet = ueye.is_GetCameraInfo(hCam, cInfo)
    if nRet != ueye.IS_SUCCESS:
        print("is_GetCameraInfo ERROR")

    # You can query additional information about the sensor type used in the camera
    nRet = ueye.is_GetSensorInfo(hCam, sInfo)
    if nRet != ueye.IS_SUCCESS:
        print("is_GetSensorInfo ERROR")
        
    nRet = ueye.is_ResetToDefault( hCam)
    if nRet != ueye.IS_SUCCESS:
        print("is_ResetToDefault ERROR")
            
    # Set display mode to DIB
    nRet = ueye.is_SetDisplayMode(hCam, ueye.IS_SET_DM_DIB)

    # Set the right color mode
    if int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_BAYER:
        # setup the color depth to the current windows setting
        ueye.is_GetColorDepth(hCam, nBitsPerPixel, m_nColorMode)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_BAYER: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()

    elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_CBYCRY:
        # for color camera models use RGB32 mode
        m_nColorMode = ueye.IS_CM_BGRA8_PACKED
        nBitsPerPixel = ueye.INT(32)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_CBYCRY: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()
    
    elif int.from_bytes(sInfo.nColorMode.value, byteorder='big') == ueye.IS_COLORMODE_MONOCHROME:
        # for color camera models use RGB32 mode
        m_nColorMode = ueye.IS_CM_MONO8
        nBitsPerPixel = ueye.INT(8)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("IS_COLORMODE_MONOCHROME: ", )
        print("\tm_nColorMode: \t\t", m_nColorMode)
        print("\tnBitsPerPixel: \t\t", nBitsPerPixel)
        print("\tbytes_per_pixel: \t\t", bytes_per_pixel)
        print()
        
    else:
        # for monochrome camera models use Y8 mode
        m_nColorMode = ueye.IS_CM_MONO8
        nBitsPerPixel = ueye.INT(8)
        bytes_per_pixel = int(nBitsPerPixel / 8)
        print("else")

    # Can be used to set the size and position of an "area of interest"(AOI) within an image
    nRet = ueye.is_AOI(hCam, ueye.IS_AOI_IMAGE_GET_AOI, rectAOI, ueye.sizeof(rectAOI))
    if nRet != ueye.IS_SUCCESS:
        print("is_AOI ERROR")

    width = rectAOI.s32Width
    height = rectAOI.s32Height

    # Prints out some information about the camera and the sensor
    print("Camera model:\t\t", sInfo.strSensorName.decode('utf-8'))
    print("Camera serial no.:\t", cInfo.SerNo.decode('utf-8'))
    print("Maximum image width:\t", width)
    print("Maximum image height:\t", height)
    print()


    #-------------------------------------------------------------

    # Allocates an image memory for an image having its dimensions defined by
    # width and height and its color depth defined by nBitsPerPixel
    nRet = ueye.is_AllocImageMem(hCam, width, height, nBitsPerPixel, pcImageMemory, MemID)
    if nRet != ueye.IS_SUCCESS:
        print("is_AllocImageMem ERROR")
    else:
        # Makes the specified image memory the active memory
        nRet = ueye.is_SetImageMem(hCam, pcImageMemory, MemID)
        if nRet != ueye.IS_SUCCESS:
            print("is_SetImageMem ERROR")
        else:
            # Set the desired color mode
            nRet = ueye.is_SetColorMode(hCam, m_nColorMode)



    # Activates the camera's live video mode (free run mode)
    nRet = ueye.is_CaptureVideo(hCam, ueye.IS_DONT_WAIT)
    if nRet != ueye.IS_SUCCESS:
        print("is_CaptureVideo ERROR")
        
    # Enables the queue mode for existing image memory sequences
    nRet = ueye.is_InquireImageMem(hCam, pcImageMemory, MemID, width, height, nBitsPerPixel, pitch)
    if nRet != ueye.IS_SUCCESS:
        print("is_InquireImageMem ERROR")
    else:
        print("Press q to leave the programm")
        

    # NICO STUFF HERE
    frate = ueye.DOUBLE()
    frate = 10.0
    afrate = ueye.DOUBLE()
    nRet = ueye.is_SetFrameRate(hCam, frate, afrate)
    if nRet != ueye.IS_SUCCESS:
        print("is_SetFrameRate failed ERROR")
    print("FRAMERATE: {0:f}".format(float(afrate)))
    
    # This doesn't work for some reason... track with afrate.
    # nRet = ueye.is_GetFramesPerSecond(hCam, afrate)
    # if nRet != ueye.IS_SUCCESS:
    #     print("is_GetFramesPerSecond failed ERROR")
    # print("FRAMERATE: {0:f}".format(float(afrate)))
    


    d = ueye.DOUBLE()
    nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_DEFAULT, d, 8)
    if (nRet != ueye.IS_SUCCESS):
        print("is_Exposure() failed...")
    print("Default exposure time {0:f} ms".format(float(d)))
    nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8)
    if (nRet != ueye.IS_SUCCESS):
        print("is_Exposure() failed...")
    print("Min exposure time {0:f} ms".format(float(d)))
    nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8)
    if (nRet != ueye.IS_SUCCESS):
        print("is_Exposure() failed...")
    print("Max exposure time {0:f} ms".format(float(d)))
    nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
    if (nRet != ueye.IS_SUCCESS):
        print("is_Exposure() failed...")
    print("Exposure time {0:f} ms".format(float(d)))
    
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_DEFAULT, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  default setting for the exposure time  %8.3f ms' % d)
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MIN, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  minimum exposure time                  %8.3f ms' % d)
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE_RANGE_MAX, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  maximum exposure time                  %8.3f ms' % d)
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  currently set exposure time            %8.3f ms' % d)
    # d =  ueye.double(25.0)
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  tried to changed exposure time to      %8.3f ms' % d)
    # ret = ueye.is_Exposure(self.cam.handle(), ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
    # if ret == ueye.IS_SUCCESS:
    # 	print('  currently set exposure time            %8.3f ms' % d)
    # #
    
    # frame rate
    # fps = ueye.DOUBLE()
    # nRet = ueye.is_GetFramesPerSecond(hCam, fps)
    # print("Frames: ")
    # print(nRet)
    # print(fps)
    # if nRet != ueye.IS_SUCCESS:
    #     print("FAIL FAIL FAIL")
    
    # END NICO SETUP
    
    #----------------------------------------------------------------------

    counter = 0
    filecounter = 0
    z = np.zeros((height.value, width.value), dtype = np.uint32)
    capflag = 0
    reticle = 0
    longav = 0
    lcnt = 0
    lfcnt = 0
    lcounter = 0
    
    # Continuous image display
    while(nRet == ueye.IS_SUCCESS):
        
        # In order to display the image in an OpenCV window we need to...
        # ...extract the data of our image memory
        array = ueye.get_data(pcImageMemory, width, height, nBitsPerPixel, pitch, copy=False)
        
        # bytes_per_pixel = int(nBitsPerPixel / 8)
        
        # ...reshape it in an numpy array...
        frame = np.reshape(array,(height.value, width.value, bytes_per_pixel))
        
        c = cv2.waitKey(20)
        if (c == ord('q')):
            break
        if (c == ord('c')):
            capflag = 1
            print("capturing...")
        if (c == ord('a')):
            # long average...
            longav = 1
            print("long average starting...")
        if(c == ord('r')):
            reticle = (reticle + 1) % 2
        if (c == ord('=')):
            frate = float(afrate + 0.5)
            #frate = float(int(float(afrate) + 2.0))
            print(frate)
            nRet = ueye.is_SetFrameRate(hCam, frate, afrate)
            if nRet != ueye.IS_SUCCESS:
                print("is_SetFrameRate failed ERROR")
            print("FRAMERATE: {0:f}".format(float(afrate)))
        if (c == ord('-')):
            frate = float(afrate - 0.5)
            print(frate)
            nRet = ueye.is_SetFrameRate(hCam, frate, afrate)
            if nRet != ueye.IS_SUCCESS:
                print("is_SetFrameRate failed ERROR")
            print("FRAMERATE: {0:f}".format(float(afrate)))
        if (c == ord(']')):
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            #print("Exposure time {0:f} ms".format(float(d)))
            d = ueye.double(d + 10.0)
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            #print("Exposure time {0:f} ms".format(float(d)))
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            print("Exposure time {0:f} ms".format(float(d)))
        if (c == ord('[')):
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            #print("Exposure time {0:f} ms".format(float(d)))
            d = ueye.double(d - 10.0)
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_SET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            #print("Exposure time {0:f} ms".format(float(d)))
            nRet = ueye.is_Exposure(hCam, ueye.IS_EXPOSURE_CMD_GET_EXPOSURE, d, 8)
            if (nRet != ueye.IS_SUCCESS):
                print("is_Exposure() failed...")
            print("Exposure time {0:f} ms".format(float(d)))
            
            
            
            
        if (capflag == 1):
            z = z + frame[:,:,0]
            #print(frame[:,:,0])
            counter = counter + 1
            #print(counter)
            if (counter == ncap):
                #print("A")
                #print(frame)
                #misc.imsave("nicowat.bmp", z)
                nfname = fname + "{0:03d}".format(filecounter) + ".npz"
                imageio.imwrite(nfname, z)
                print("Stored to {0:s}".format(nfname))
                filecounter = filecounter + 1
                
                print("Capture complete... ({0:d} frames)".format(ncap))
                z[:] = 0
                counter = 0
                capflag = 0

        
        if (longav == 1):
            lfcnt = lfcnt + 1
            if (lfcnt == 100):
                print("asdf")
                z = z + frame[:,:,0]
                lcnt = lcnt + 1
                lfcnt = 0
                if (lcnt == 60):
                    nfname = fname + "long" "{0:03d}".format(lcounter) + ".npz"
                    #imageio.imwrite("longim_nn_torque.npz", z)
                    imageio.imwrite(nfname, z)
                    lcounter = lcounter + 1
                    z[:] = 0
                    lfcnt = 0
                    lcnt = 0
                    longav = 0
                    print("longav done...")

            #longav = 0

            
            
        
        # ...resize the image by a half
        frame = cv2.resize(frame,(0,0),fx=0.6, fy=0.6)
        
        #---------------------------------------------
        #Include image data processing here
        
        #----------------------------------------------
        
        #...and finally display it
        
        if (reticle):
            cv2.circle(frame, (int(640*0.6), int(512*0.6)), 25, (255, 255, 255), 2)
            cv2.circle(frame, (int(640*0.6), int(112*0.6)), 25, (255, 255, 255), 2)
            cv2.circle(frame, (int(294*0.6), int(312*0.6)), 25, (255, 255, 255), 2)
        # display frame
        cv2.imshow("NICO", frame)
        

        # Press q if you want to end the loop
        #if cv2.waitKey(1) & 0xFF == ord('q'):
        #    break
        #---------------------------------------------
        
    # Releases an image memory that was allocated using is_AllocImageMem() and
    # removes it from the driver management
    ueye.is_FreeImageMem(hCam, pcImageMemory, MemID)

    # Disables the hCam camera handle and releases the data structures and
    # memory areas taken up by the uEye camera
    ueye.is_ExitCamera(hCam)

    # Destroys the OpenCv windows cv2.destroyAllWindows()
    
    print()
    print("END")


if __name__ == '__main__':
    if (len(sys.argv) < 2):
        print("Usage: edcamp.py <file prefix> <# of files to stack>")
        print("Defaultfile stack is 50")
        exit()

    if (len(sys.argv) == 3):
        N = int(sys.argv[2])
    else:
        N = 50

    fname = sys.argv[1]
        
    main(fname, N)


    
