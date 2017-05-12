#Batbot Echo Server protocol
#Created by Brandon Nguyen

from ftplib import FTP
import socket
import time
import os
#import thread
#import threading
import serial
import sys

while True:

	host = ''  # Symbolic name meaning all available interfaces
	port = 50420 # Arbitrary non-privileged port

	#Initialize serial
	ser = serial.Serial('/dev/ttyUSB0',9600)

	#Create data folder (if it doesnt exist) and navigate to its path
	data_path = '/home/pi/DATA/'

	if not os.path.exists(data_path):
		os.makedirs(data_path)

	os.chdir(data_path)
	
	ftp_logged = False

	while ftp_logged == False:
		
		try:
			#FTP
			#******CHANGE BELOW PARAMETERS*********
			ftp = FTP('169.254.32.143') #IP address of host
			ftp.login('admin','bats123')

			ftp.cwd('/ni-rt/startup/') #Changes to specified ftp directory
			ftp_logged = True
			print("FTP connection established.")
			#************************************
		except:
			pass
		
		time.sleep(1)

	#Socket server setup
	s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
	print("Socket connected.")
	s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

	try:
		s.bind((host, port))
	except socket.error as msg:
		print(msg)

	print("Socket bound.")
	print("Listening for client(s)...")
	s.listen(1)
	conn, address = s.accept()
	print("Connected to {} @ {}".format(str(address[0]), str(address[1])))

	run = 0

	while True:
			#Receive command from client to:
			#Tell sbRIO to do things, receive/delete datafile from it
			time_total = time.time()
			data = conn.recv(1024).decode().strip()
			
			if data == "run":
					ser.write("o") #Run sbRIO loop once
					time_ready = time.time()
					ready_signal = ser.readline().strip() 
					print("Time for sbrio to finish: " + str(time.time() - time_ready))
					if ready_signal == "ready": #Reads "ready" from sbRIO
									time_retr = time.time()
									print("making file # " + str(run + 1))
									ftp.retrbinary('RETR sbrio_data', open('datafile.dat', 'wb').write) #Retrieve specified file from sbRIO
									print("deleting file")
									ftp.delete('sbrio_data') #Deletes specified file from sbRIO
									print("done: " + str(time.time() - time_retr))
									conn.send(b'fileready') #Tells client that the file is ready
									#time.sleep(0.05)
									time.filewrite = time.time()
									with open(data_path + 'datafile.dat', 'rb') as fid:
											for line in fid:
													conn.send(line)
											time.sleep(0.2)
											conn.send(b'done')

									run = run + 1
									print(run)
									print("Time to transfer file: " + str(time.time() - time.filewrite))
			
			elif data == "quit":
							break

			print("Total loop time: " + str(time.time() - time_total))
			time.sleep(0.05)
				
	ftp.quit()
	conn.close()
	time.sleep(1)
			
