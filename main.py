import datetime
import hashlib
import sys

import requests
from xml.etree import ElementTree as ET

"""
Enter your own configuration here

BOX - IP Adress of your Fritzbox
USER - Fritzbox User used to query the temperature
PW - Password of the user
AIN - ID of the device to query
SWUTCH - IP Address of the Delock 11827 WLAN Switch
OFF_TEMP - Temperature when Fan should be turned off
ON_TEMP - Temperature when Fan should turned on (must be below OFF_TEMP!!)
"""

BOX = "192.168.2.1"
USER = "fancontrol"
PW = "xxxxxxxxxx"
AIN: str = "09995 xxxxxxxx"
SWITCH = "192.168.2.40"

OFF_TEMP: float = 20.5
ON_TEMP: float = 18.0

"""
End of config section
"""


URL = "http://{box}/login_sid.lua"
URL2 = "http://{box}/login_sid.lua?username={username}&response={response}"
QUERY = "http://{box}/webservices/homeautoswitch.lua?ain={ain}&switchcmd={switchcmd}&sid={sid}"
SESSION_ID = "SID"
CHALLENGE = "Challenge"

URLSWITCH = "http://{switch}/cm?cmnd=Power%20{onoff}"


def getSessionId():
    global sessionId
    sessionId = None
    challenge = None
    result = requests.get(URL.format(box=BOX))
    tree = ET.ElementTree(ET.fromstring(result.content))
    for elem in tree.iter():
        if elem.tag == SESSION_ID:
            sessionId = elem.text
        if elem.tag == CHALLENGE:
            challenge = elem.text
    if sessionId == "0000000000000000":
        response = challenge + "-" + hashlib.md5((challenge + "-" + PW).encode("UTF-16LE")).hexdigest()
        result = requests.get(URL2.format(box=BOX, username=USER, response=response))
        tree = ET.ElementTree(ET.fromstring(result.content))
        for elem in tree.iter():
            if elem.tag == SESSION_ID:
                sessionId = elem.text
    return sessionId


def getTemperature(sessionId, ain):
    switchCmd = "gettemperature"
    result = requests.get(QUERY.format(box=BOX, ain=ain, switchcmd=switchCmd, sid=sessionId))
    strTmp = result.content.decode("UTF-8")
    if strTmp is None or len(strTmp)==0:
        return(-1000)
    else:
        return float(strTmp) / 10


def switchFan(onoff):
    result = requests.get(URLSWITCH.format(switch=SWITCH, onoff=onoff))


if __name__ == '__main__':
    retCode = 0
    now = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    print(f"[INF] Starting FanContol at {now}")
    if ON_TEMP >= OFF_TEMP:
        print(f"[ERR] Parameter ON_TEMP ({ON_TEMP}) must be lower than OFF_TEMP ({OFF_TEMP})")
        retCode = -1
    else:
        sessionId = getSessionId()
        if sessionId == "0000000000000000":
            print("[ERR] Error getting a valid sessionId, check your configuration")
            retCode = -1
        else:
            print(f"[INF] Got a valid session id from {BOX}")
            temp = getTemperature(sessionId, AIN)
            if temp == -1000:
                print(f"[ERR] Error reading a valid temperature, is your ain {AIN} valid?")
            else:
                print(f"[INF] ain {AIN} reports {temp} degrees celsius")
                if temp < ON_TEMP:
                    print("[INF] Switching fan ON")
                    switchFan("on")
                elif temp > OFF_TEMP:
                    print("[INF] Switching fan OFF")
                    switchFan("off")
                else:
                    print(f"[INF] Temperature is between on {ON_TEMP} and off {OFF_TEMP}. Doing nothing.")
    now = datetime.datetime.now().strftime("%d.%m.%Y, %H:%M:%S")
    print(f"[INF] Finishing FanContol at {now}")
    sys.exit(retCode)

