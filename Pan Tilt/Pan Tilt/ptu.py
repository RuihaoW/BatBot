import math
import time
import serial
import re

class ptu:
    # open serial port
    port = serial.Serial('COM8',9600)
    PR = 0
    TR = 0
    TN = 0
    PN = 0
    # set timeout so port doesn't hang
    port.timeout = 1
    time.sleep(1)

    def go(self, command):
        print('WRITING COMMAND: %s'% command)
        command = command + ' '
        # encode string command to byte array
        self.port.write(command.encode())
        print('PAN-TILT RESPONSE: ')
        # read in pan-tilt response and remove endline code
        x = self.port.readline().strip()
        # decode pan-tilt response from byte array to string
        y = x.decode("utf-8")
        print(y)
        time.sleep(1)
        return y

    def ls(self):
        print('----PTU SERIAL COMMANDS----')
        time.sleep(1)
        print('R = Reset')
        time.sleep(1)
        print('PR = Pan Resolution')
        time.sleep(1)
        print('TR = Tilt Resolution')
        time.sleep(1)
        print('PN = Pan Minimum')
        time.sleep(1)
        print('PX = Pan Maximum')
        time.sleep(1)
        print('TN = Tilt Minimum')
        time.sleep(1)
        print('TX = Tilt Maximum')
        time.sleep(1)
        print('ED = Disable host command echo')
        time.sleep(1)
        print('E = query echo mode')
        time.sleep(1)
        print('PP + number = pan position')
        time.sleep(1)
        print('TP + number = tilt position')
        time.sleep(1)
        print('END of COMMANDS LIST')

    def cmd(self):
        print('----PTU PYTHON COMMANDS----')
        time.sleep(1)
        print('go(COMMAND) = serial command')
        time.sleep(1)
        print('moveto(X,Y) = moves pan-tilt to X, Y')
        time.sleep(1)
        print('ls() = lists often used serial commands')
        time.sleep(1)
        print('END of COMMANDS LIST')
        
    def cart(self,angle,axis):
        if axis == 'x': #pan
            # convert angle to step count for ptu motors
            pos = (angle*3600)/self.PR
            pos = math.floor(pos)
        else: #tilt
            # convert angle to step count for ptu motors           
            pos = (angle*3600/self.TR)
            pos = math.floor(pos)
        return pos

    def moveto(self, az, el):
        az_pos = self.cart(float(az), 'x')
        el_pos = self.cart(float(el), 'y')

        self.go('PP%d'%az_pos)
        self.go('TP%d'%el_pos)
        
    @staticmethod
    def val(s, spec):
        # common specs
        # '\d+\.\d+' = float (positive)
        # '[-]\d+\.\d+' = float(negative)
        # '[-]\d+' = int(negative)
        # '\d+' = int(positive)
        ls = re.findall(spec, s) # find values of specification given in string
        num = float(ls[0])       # re.findall returns list, converts to float
        return num
        
    
    

ptu = ptu()
print('INITIALIZING PAN-TILT')
ptu.go('ED')
ptu.go('E')
ptu.go('TS256')
ptu.go('TS512')
ptu.PR = ptu.val(ptu.go('PR'), '\d+\.\d+')
ptu.TR = ptu.val(ptu.go('TR'), '\d+\.\d+')
ptu.TN = ptu.val(ptu.go('PN'), '[-]\d+')
ptu.PN = ptu.val(ptu.go('TN'), '[-]\d+')
ptu.TX = ptu.val(ptu.go('TX'), '\d+')
ptu.PX = ptu.val(ptu.go('PX'), '\d+')

    

