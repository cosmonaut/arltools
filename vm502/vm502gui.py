# Author: Nicholas Nell
# nicholas.nell@colorado.edu

import sys
import time
import serial
from serial.tools.list_ports import comports
import numpy as np
from PyQt5.uic import loadUiType
from PyQt5 import QtWidgets
from PyQt5 import QtCore
import vm502
import traceback

Ui_MainWindow, QMainWindow = loadUiType('vm502.ui')


class ComboBox(QtWidgets.QComboBox):
    def showPopup(self):
        # populate...
        c = comports()
        #print(c)
        self.clear()
        for row in c:
            #print(row)
            self.addItem(row[0])

        index = self.findText('/dev/ttyS0', QtCore.Qt.MatchFixedString)
        if (index >= 0):
            self.setCurrentIndex(index)

        super(ComboBox, self).showPopup()


class Main(QMainWindow, Ui_MainWindow):
    def __init__(self, ):
        super(Main, self).__init__()
        self.setupUi(self)

        self.setup_signal_slots()

        self.portcombobox = ComboBox()
        self.commbox.layout().addWidget(self.portcombobox, 0, 1)

        c = comports()

        for row in c:
            self.portcombobox.addItem(row[0])

        index = self.portcombobox.findText('/dev/ttyS0', QtCore.Qt.MatchFixedString)
        if (index >= 0):
            self.portcombobox.setCurrentIndex(index)

        
        self.commandbox.setEnabled(False)
        self.statusbox.setEnabled(False)

        self.button_connect.clicked.connect(self.serial_connect)
        self.button_disconnect.clicked.connect(self.serial_disconnect)
        
        self.button_disconnect.setEnabled(False)
        self.gotobutton.clicked.connect(self.goto)
        self.gratbutton.clicked.connect(self.set_grating)
        self.scanbutton.clicked.connect(self.scan)
        self.sratebutton.clicked.connect(self.set_srate)
        self.resetbutton.clicked.connect(self.reset)

        
    def serial_connect(self):

        port = self.portcombobox.currentText()
        print("Connectiong to port: " + str(port))

        try:
            self.ser = serial.Serial(port, vm502.VM502_BAUD, timeout = 5.0)
        except:
            print("Failed to open serial port...")
            traceback.print_exc()
            return
        
        self.button_disconnect.setEnabled(True)
        self.button_connect.setEnabled(False)
        self.portcombobox.setEnabled(False)

        self.commandbox.setEnabled(True)
        self.statusbox.setEnabled(True)

        #vm502.vm502_init(self.ser)
        g = vm502.vm502_get_grating(self.ser)
        self.gratbox.setText(str(g))
        #time.sleep(0.1)
        model = vm502.vm502_get_model(self.ser)
        self.modelbox.setText(model)
        #time.sleep(0.1)
        sernum = vm502.vm502_get_serial(self.ser)
        self.serialbox.setText(sernum)
        rate = vm502.vm502_get_rate(self.ser)
        self.ratebox.setText(rate)
        gratings = vm502.vm502_get_gratings(self.ser)
        #print(gratings)
        #print("testing..")
        gpermm = ''
        blaze = ''
        for line in gratings.split('\r\n'):
            line = line.lstrip(" ")
            if (len(line) > 0):
                gdata = line.split(" ")
                if (g == gdata[0]):
                    gpermm = gdata[1]
                    blaze = gdata[4]
            print(line)
            #print("asdf\r\n")
        self.blazebox.setText(blaze)
        self.groovebox.setText(gpermm)

        lam = vm502.vm502_get_lambda(self.ser)
        self.wavebox.setText(lam)

        self.log("Connected to monochromator")
            
    def serial_disconnect(self):
        if (self.ser):
            self.ser.close()
        
        self.button_connect.setEnabled(True)
        self.button_disconnect.setEnabled(False)
        self.portcombobox.setEnabled(True)

        self.commandbox.setEnabled(False)
        self.statusbox.setEnabled(False)

    
    

    def setup_signal_slots(self):
        self.actionQuit.triggered.connect(self.close)

    def goto(self):
        lamg = self.gotobox.value()
        slamg = str.format("{0:.4f}", lamg)
        #print(slamg)
        self.log(str.format("Slewing to {0:.4f}...", lamg))
        self.commandbox.setEnabled(False)
        QtWidgets.QApplication.processEvents()
        newlam = vm502.vm502_goto(self.ser, slamg)
        self.wavebox.setText(newlam)
        self.log("Slewed to " + newlam)
        self.log("Slew complete.")
        
        self.commandbox.setEnabled(True)

    def set_grating(self):
        self.log("Set grating Unimplemented")
        gnum = self.gratselbox.value()
        self.log("grating selection: " + str(gnum))

    def scan(self):
        #self.log("Scan Unimplemented")
        scanlam = self.scanbox.value()
        scanlam = str.format("{0:.4f}", scanlam)
        self.log(str.format("Scanning to {0:s}...", scanlam))
        self.commandbox.setEnabled(False)
        vm502.vm502_scan(self.ser, scanlam)
        while(True):
            done = vm502.vm502_done(self.ser)
            if (done[0] == '1'):
                break
            else:
                nm = vm502.vm502_get_lambda(self.ser)
                self.log(str.format("Current wavelength: {0:s}", nm))

            # Keep GUI alive-ish
            QtWidgets.QApplication.processEvents()
            time.sleep(0.5)

        nm = vm502.vm502_get_lambda(self.ser)
        self.log(str.format("Scan complete. Wavelength: {0:s}", nm))
        self.wavebox.setText(nm)
        self.commandbox.setEnabled(True)
        
        #self.log("scan wavelength: " + str(scanlam))

    def set_srate(self):
        #self.log("set srate unimplemented")
        srate = self.scanratebox.value()
        srate = str.format("{0:.2f}", srate)
        self.log(str.format("Setting scan rate to {0:s}...", srate))
        #self.log("srate: " + str(srate))
        nsrate = vm502.vm502_set_rate(self.ser, srate)
        self.ratebox.setText(nsrate)
        self.log(str.format("Scan rate set: {0:s}", nsrate))

    def reset(self):
        self.log("reset unimplemented")

    def log(self, m):
        self.textbox.appendPlainText(m)
        
    def close(self):
        print("closing...")

        # Close serial here...

        QtWidgets.qApp.quit()

    def closeEvent(self, event):
        # Close safely
        self.close()

        

def main():
    print("Starting VM502 gui...")

    app = QtWidgets.QApplication(sys.argv)
    main = Main()
    main.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
    
