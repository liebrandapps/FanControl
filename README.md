# FanControl
Python Script to control a WLAN Swtich for turining on / off ventilation based on temperature in the room

Purpose of the script is to read temperature from a Fritzbox that has smart home temperature sensor attached. The temperature is used to turn on / turn off a smart plug (Delock 11827).

Installation
+ copy the script (main.py) into you python 3 environment
+ configure the variables at the top of the script (BOX, USER, PW) 
+ run the script python 3 main.py

For automation run the script from a crontab:

*/5 * * * * python3 /home/pi/main.py 2>&1 /tmp/fanctrl.log
