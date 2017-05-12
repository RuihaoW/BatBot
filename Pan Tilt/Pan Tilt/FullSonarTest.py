#SSH protocol between laptop & Raspberry Pi for Batbot Sonar live streaming
#Created by Brandon Nguyen

#Standard libraries
import csv
import time
import sys
import os
import subprocess
import time

#External libraries	
import paramiko #SSH protocol
import matplotlib.pyplot as plt #Matlab-esque plotting
import numpy as np #Matlab-esque syntax/functions
from ptu import *

tic = time.time()

#Check for command line arguments
if len(sys.argv) >= 2:
	iterations = int(sys.argv[1])
	if len(sys.argv) == 5:
		hostname = str(sys.argv[2])
		username = str(sys.argv[3])
		password = str(sys.argv[4])
	else:
		hostname = "BatBotRPi.local"
		username = "pi"
		password = "123"	
else:
	iterations = 20
	hostname = "BatBotRPi.local"
	username = "pi"
	password = "123"	
	
#*********CHANGE THESE PARAMETERS**********
date_time = time.strftime("%d_%m_%Y_%H%M%S")
target = "test_target"
az_min = -90
az_max = 90
az_step = 10
pitch_min = 0
pitch_max = 0
pitch_step = 1
iterations = 50

cwd = os.getcwd()
port = 22
source = "/home/pi/DATA/datafile.dat"
	
#Find IPV6 address here. 
print("Finding IPV6 address...")
system_result = subprocess.run("ping -n 1 " + hostname, stdout = subprocess.PIPE)
stdout = str(system_result.stdout)
ip_frontbound = stdout.index('[')
ip_backbound = stdout.index(']')
ipv6_addr = stdout[ip_frontbound + 1 : ip_backbound]
print(ipv6_addr)

#Initialize the SFTP session
print("Connecting to " + hostname + "...")

connection_status = False

while connection_status == False: #Keeps trying to connect
	try:
		my_sesh = paramiko.Transport((ipv6_addr, port))
		my_sesh.connect(username = username, password = password)
		sftp = paramiko.SFTPClient.from_transport(my_sesh)
		
		ssh = paramiko.SSHClient()
		ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
		ssh.connect(hostname, username=username, password=password)
		connection_status = True
		print("Connected!")
		
		try:
			sftp.remove(source) #Remove file if it's already there
		except:
			pass
			
		try:
			os.remove(cwd + "\datafile.dat")
		except:
			pass
			
	except:
		print("Failed connection... Re-attempting to connect.")
	
	time.sleep(0.05)
	
#plink_cmd = 'plink -ssh {0}@{1} -pw {2} python autorun.py {3} 0 &'.format(username, hostname, password, iterations)
#subprocess.run(plink_cmd.strip())

initplots = True

for az in range(az_min, az_max + 1, az_step):
	for pitch in range(pitch_min, pitch_max + 1, pitch_step):
				
		tic2 = time.time()
		ptu.moveto(az, pitch)
		print("Moving pan tilt to ({}, {})".format(az, pitch))
		time.sleep(2)
		
		maketimevec = True
		t = []
		lp_total = []
		rp_total = []
		plt.ion()

		file_counter = 0

		#run autorun.py on Pi
			
		print("Running for " + str(iterations) + " iterations...")
				
		ssh.exec_command("python autorun.py " + str(iterations) +  " 0")

		print("Pi script started.")
		#ssh.exec_command("python /home/pi/DATA/makecopy.py " + str(iterations))
		#Obtain and remove data file from RPi:

		try:
			while file_counter < iterations:
				tic1 = time.time()
				#stdin, stdout, stderr = ssh.exec_command("python /home/pi/DATA/makecopy.py ")
				#stdin, stdout, stderr = ssh.exec_command("python autorun.py 1 0") #Maybe?
				#my_stdout = stdout
				lp_current = []
				rp_current = []
				
				try:
					sftp.get(source, cwd + "\datafile.dat")
					sftp.remove(source)
					file_counter = file_counter + 1
					print("Obtaining file #" + str(file_counter))
					print("Obtained!")	
							
					for line in csv.reader(open('datafile.dat'), delimiter = '\t', skipinitialspace = True):
						lp_current.append(line[1])
						rp_current.append(line[2])
					
					#Data parsing
					if maketimevec == True: #Runs once
						for line in csv.reader(open('datafile.dat'), delimiter = '\t', skipinitialspace = True):
							t.append(line[0]) 
								
						lp_total.append(t)
						rp_total.append(t)
						
						maketimevec = False
						
						if initplots == True:
							y1 = lp_current
							y2 = rp_current
							
							#Initialize figure
							fig = plt.figure()
							fig.subplots_adjust(hspace = 0.5) #Space between subplots
							plt.subplots_adjust(top = 0.85) #Space from top
							plt.suptitle('Live Data', fontsize = 20) #Overall title
							
							#Top subplot
							ax = fig.add_subplot(211)
							plt.title('Left Pinnae Live Data')
							plt.xlabel('Time [ms]')
							plt.ylabel('Amplitude [V]')
							axes1 = plt.gca() #Setting axis limits and tick size
							axes1.set_ylim([-3, 3])
							plt.yticks(np.arange(-3, 4, 1.0))
							
							#Bottom subplot
							ax1 = fig.add_subplot(212)
							plt.title('Right Pinnae Live Data')
							plt.xlabel('Time [ms]')
							plt.ylabel('Amplitude [V]')
							axes2 = plt.gca()
							axes2.set_ylim([-3, 3])
							plt.yticks(np.arange(-3, 4, 1.0))
							
							#Set & Initialize left and right pinnae plots
							lp_plot, = ax.plot(t, lp_current, label = "L", color = 'r', linestyle = '-')
							rp_plot, = ax1.plot(t, rp_current, label = "R", color = 'b', linestyle = '-')
					
							initplots = False
							
					lp_plot.set_ydata(lp_current)
					rp_plot.set_ydata(rp_current)
					
					lp_total.append(lp_current)
					rp_total.append(rp_current)
					
					#fig.canvas.draw()
					plt.pause(0.00001)
					
					os.remove(cwd + "\datafile.dat")
					
					print("Loop time: " + str(time.time() - tic1))
					
				except:
					pass
				time.sleep(0.05)
		except KeyboardInterrupt:
			print("Force Stopped.")
			#Stop program on the Pi: \x003
			
			
		#File making; starts post while loop
		lp_total_zipped = list(zip(*lp_total))
		rp_total_zipped = list(zip(*rp_total))
				
		print("Creating files for " + str(file_counter) + " iterations...")

		with open("{}_lp_{}_{}.dat".format(target, az, pitch), 'w', newline = '') as csvfile:
			datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for j in range(len(lp_total_zipped)):
				datawriter.writerow(lp_total_zipped[j])

		with open("{}_rp_{}_{}.dat".format(target, az, pitch), 'w', newline = '') as csvfile:
			datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
			for k in range(len(rp_total_zipped)):
				datawriter.writerow(rp_total_zipped[k])
						
		print("Files created!")
		print("Time for this az/pitch loop: " + str(time.time()-tic2))
		time.sleep(1)
	time.sleep(1)
print("Overall program time: " + str(time.time() - tic))
			
