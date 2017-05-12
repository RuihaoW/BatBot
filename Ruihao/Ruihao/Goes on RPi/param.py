#Communication protocol for the RPi and sbRIO
#Created by Brandon Nguyen & Cody Earles

from ftplib import FTP
import time
import os
import thread
import threading
import serial
import sys

#Initialize serial
ser = serial.Serial('/dev/ttyUSB0',9600)
        
if len(sys.argv) == 3:
        param_to_change = str(sys.argv[1])
	new_value = float(sys.argv[2])
else:
        print("Please enter valid arguments: 'param.py [parameter #] [value]'")
        ser.write("a")
        time.sleep(2)
        ser.write("e")
	while ser.inWaiting():
		print(ser.readline().strip())
	sys.exit()
	
#Create data folder (if it doesnt exist) and navigate to its path
data_path = '/home/pi/DATA/'

if not os.path.exists(data_path):
	os.makedirs(data_path)

os.chdir(data_path)

ser.write("a")
time.sleep(2)
print("Current values: ")
while ser.inWaiting():
        print(ser.readline().strip())
if 0 < float(param_to_change) < 7:
        ser.write(param_to_change) #Write parameter # to sbRIO
        time.sleep(2)
        while ser.inWaiting():
                print(ser.readline().strip()) #Read parameter value from sbRIO
        ser.write(str(new_value))
        print("New parameters: ")
        time.sleep(2)
        ser.write("e")
        time.sleep(2)
        ser.write("e")
        time.sleep(2)
        while ser.inWaiting():
                print(ser.readline().strip())
else:
        print("Please enter a valid number.")





