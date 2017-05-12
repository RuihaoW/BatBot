Notes:

-batbot_server.py and param.py belong on the Raspberry Pi. 
-batbot_client.py and param_laptop.py belong on your computer.

Make sure that on batbot_server.py, the serial port is initialized correctly. Also, make sure that the FTP address and login information are initialized correctly (these can be configured/changed on the sbRIO using NI Max). 

On batbot_client.py, adjust all instances of 'host' to the local hostname of the Raspberry Pi. 

In param.py, ensure that the serial port is correct.

In param_laptop.py make sure that the hostname, username, and password are all correct. 

For all cases, make sure that the Raspberry Pi is on the same network as your computer.

***To launch the server/client protocol***
1. Start batbot_server.py on the Raspberry Pi
2. Start batbot_client.py on your computer:
'python batbot_client.py __# OF ITERATIONS__'
The default number of iterations is 20

***To adjust parameters***
1. Run param_laptop.py once to obtain current values on the sbRIO
2. Run it again with the following syntax: 
'python param_laptop.py ___# OF VAR TO CHANGE___ ___NEW VALUE___'

Parameters: 1:"Amplitude", 2:"Length", 3:"Initial Frequency", 4:"Final Frequency", 5:"Interpulse Time", 6:"Samples"

***To set batbot_server.py to run on the Raspberry Pi @ start***
1. Create launcher script as shown below
2. Make it an executable by typing 'chmod 755 launcher.sh' 
3. Create a log directory: 'mkdir logs'
4. Open up Crontab for editing: 'sudo crontab -e'
5. In the crontab, enter the line shown below
6. Save and reboot the Pi

***LAUNCHER SCRIPT

#!/bin/sh
#launcher.sh

cd /home/pi/
sudo python batbot_server.py

***END LAUNCHER SCRIPT

***CRONTAB

@reboot sleep 30; sh /home/pi/launcher.sh > /home/pi/logs/cronlog 2>&1

***END CRONTAB