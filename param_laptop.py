#Parameter adjustment script for the client side
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
	
hostname = "BatBotRPi.local"
username = "pi"
password = "123"	
port = 22	
	
system_result = subprocess.run("ping -n 1 " + hostname, stdout = subprocess.PIPE)
stdout = str(system_result.stdout)
ip_frontbound = stdout.index('[')
ip_backbound = stdout.index(']')
ipv6_addr = stdout[ip_frontbound + 1 : ip_backbound]

try:
	my_sesh = paramiko.Transport((ipv6_addr, port))
	my_sesh.connect(username = username, password = password)
	sftp = paramiko.SFTPClient.from_transport(my_sesh)
	
	ssh = paramiko.SSHClient()
	ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
	ssh.connect(hostname, username=username, password=password)

finally:
	pass

param_dict = {1:"Amplitude", 2:"Length", 3:"Initial Frequency", 4:"Final Frequency", 5:"Interpulse Time", 6:"Samples"}

if len(sys.argv) == 3:
	param_to_change = str(sys.argv[1])
	new_value = float(sys.argv[2])
	print("Attempting to change "+ param_dict[int(param_to_change)] + " to " + str(new_value) + "...")
else:
	ssh.exec_command("python /home/pi/param.py ")
	stdin, stdout, stderr = ssh.exec_command("python param.py") #Maybe?
	my_stdout = stdout.read().strip()
	print("1. Amplitude (V)")
	print("2. Length (ms)")
	print("3. Initial Freq [Hz]")
	print("4. Final Freq [Hz]")
	print("5. Interpulse Time [ms]")
	print("6. # of Samples to Read")
	#for items in my_stdout.splitlines():
	#	print(items.strip().decode())
	sys.exit()

stdin, stdout, stderr = ssh.exec_command("python param.py " + param_to_change + " " + str(new_value)) #Maybe?
my_stdout = stdout.read().strip()

for items in my_stdout.splitlines():
	print(items.strip().decode())


	