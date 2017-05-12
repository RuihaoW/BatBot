#Batbot Echo Client protocol
#Created by Brandon Nguyen

#Standard libraries
import socket
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
from scipy.signal import butter, lfilter, freqz

fs = 250000 #Hz
#lowcut = 20000 #Hz
lowcut = 50000
highcut = 100000 #Hz

def butter_bandpass(lowcut, highcut, fs, order = 5):
	nyq = 0.5*fs
	low = lowcut/nyq
	high = highcut/nyq
	b, a = butter(order, [low, high], btype = 'band')
	return b, a
	
def butter_bandpass_filter(data, lowcut, highcut, fs, order = 5):
	b, a = butter_bandpass(lowcut, highcut, fs, order = order)
	y = lfilter(b, a, data)
	return y

tic = time.time()

#Check for command line arguments
if len(sys.argv) >= 2:
	iterations = int(sys.argv[1])
	if len(sys.argv) == 5:
		host = str(sys.argv[2])
		username = str(sys.argv[3])
		password = str(sys.argv[4])
	else:
		host = "BatBotRPi.local"
		username = "pi"
		password = "123"	
else:
	iterations = 20
	host = "BatBotRPi.local"
	username = "pi"
	password = "123"	
	
host = "BatBotRPi.local"
#username = "pi"
#password = "branches"

print("Finding IPV6 address...")
system_result = subprocess.run("ping -n 1 " + host, stdout = subprocess.PIPE)
stdout = str(system_result.stdout)
ip_frontbound = stdout.index('[')
ip_backbound = stdout.index(']')
ipv6_addr = stdout[ip_frontbound + 1 : ip_backbound]
print(ipv6_addr)

cwd = os.getcwd()
port = 50420

#Socket client setup
s = socket.socket(socket.AF_INET6, socket.SOCK_STREAM)
s.connect((ipv6_addr, port))

print("Running for " + str(iterations) + " iterations...")

maketimevec = True
t = []
lp_total = []
rp_total = []
lp_raw = []
plt.ion()

file_counter = 0
		
while file_counter < iterations:
	
	try:
	
		file_counter = file_counter + 1
		lp_current = []
		rp_current = []
		tic1 = time.time()
		
		print("Sending run command to Pi.")
		s.send(b'run') #Tells Pi to run the sbRIO loop!
		data = s.recv(1024).decode().strip() #Read data from Pi
		
		tic2 = time.time()

		if data == "fileready":
			#Can definitely be faster if we bypass writing the datafile.dat here
			tic_obtain = time.time()
			print("Obtaining file #" + str(file_counter))
			with open('datafile.dat', 'wb') as fid: 
				line = 1
				while (line):
					line = s.recv(1024)
					#line_str = line.decode().strip()
					#print(line_str)
					#if not line_str:
					if b'done' in line:
						#print(line.decode())
						#line_str = line.decode().strip()
						#line = line_str.replace("done", "").encode()
						#fid.write(line)
						#Remove 'done' from line here
						fid.write(line)
						print("done!")
						break
					fid.write(line)
			
			print("Obtained! Time: " + str(time.time() - tic_obtain))	
			#time.sleep(0.05) #??
			#Removes 'done' from the EOF
			
			print("Editing file...")
			with open('datafile.dat', 'rb+') as f:
				f.seek(0, 2) #End of file
				size = f.tell() #Tells position of pointer, so entire 'size' of file
				f.truncate(size - 4) #Truncates the file to 4 from the end, deleting the last 4 chars

			tic_edit = time.time()
			
			for line in csv.reader(open('datafile.dat'), delimiter = '\t', skipinitialspace = True):
				lp_current.append(line[1])
				rp_current.append(line[2])
			
			print("Time to edit data: " + str(time.time() - tic_edit))
			
			tic_plotting = time.time()
			
			if maketimevec == True: #Runs once
				for line in csv.reader(open('datafile.dat'), delimiter = '\t', skipinitialspace = True):
					t.append(line[0]) 
						
				lp_total.append(t)
				rp_total.append(t)
				lp_raw.append(t)
				
				lp_current_array = np.float64(lp_current)
				rp_current_array = np.float64(rp_current)
					
				#Filter here
				lp_current_filtered = butter_bandpass_filter(lp_current_array, lowcut, highcut, fs, order = 2)
				rp_current_filtered = butter_bandpass_filter(rp_current_array, lowcut, highcut, fs, order = 2)
				
				y1 = lp_current_filtered
				y2 = rp_current_filtered
				
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
				lp_plot, = ax.plot(t, lp_current_filtered, label = "L", color = 'r', linestyle = '-')
				rp_plot, = ax1.plot(t, rp_current_filtered, label = "R", color = 'b', linestyle = '-')
				
				maketimevec = False
			
			lp_current_array = np.float64(lp_current)
			rp_current_array = np.float64(rp_current)
				
			#Filter here
			lp_current_filtered = butter_bandpass_filter(lp_current_array, lowcut, highcut, fs, order = 2)
			rp_current_filtered = butter_bandpass_filter(rp_current_array, lowcut, highcut, fs, order = 2)
			
			lp_plot.set_ydata(lp_current_filtered)
			rp_plot.set_ydata(rp_current_filtered)
			
			lp_total.append(lp_current_filtered)
			rp_total.append(rp_current_filtered)
			lp_raw.append(lp_current)
			
			#fig.canvas.draw()
			plt.pause(0.00001)
			
			os.remove(cwd + "\datafile.dat")
			print("Time to plot: " + str(time.time() - tic_plotting))
			print("Loop time: " + str(time.time() - tic1))	

	except KeyboardInterrupt:
		s.send(b'quit')
		
		
			#except KeyboardInterrupt:
	#	print("Force Stopped.")
		#Stop program on the Pi: \x003
	
#File making; starts post while loop
lp_total_zipped = list(zip(*lp_total))
rp_total_zipped = list(zip(*rp_total))

print("Creating files for " + str(file_counter) + " iterations...")

date_time = time.strftime("%d_%m_%Y_%H%M%S")

with open('raw.dat', 'w', newline = '') as csvfile:
	datawriter = csv.writer(csvfile, delimiter = '\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	for j in range(len(lp_total_zipped)):
		datawriter.writerow(lp_total_zipped[j])
	
with open('lp_' + date_time + '.dat', 'w', newline = '') as csvfile:
	datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	#for j in range(len(lp_total_zipped)):
	#	datawriter.writerow(lp_total_zipped[j])
	for item in lp_total_zipped:
		for j in range(len(item)):
			csvfile.write("%.6f\t" % float(item[j]))
		csvfile.write("\n")
		
with open('rp_' + date_time + '.dat', 'w', newline = '') as csvfile:
	datawriter = csv.writer(csvfile, delimiter='\t', quotechar='|', quoting=csv.QUOTE_MINIMAL)
	#for k in range(len(rp_total_zipped)):
	#	datawriter.writerow(rp_total_zipped[k])
	for item in rp_total_zipped:
		for k in range(len(item)):
			csvfile.write("%.6f\t" % float(item[k]))
		csvfile.write("\n")
		
s.send(b'quit')

print("Files created!")

print("Overall program time: " + str(time.time() - tic))
s.close()