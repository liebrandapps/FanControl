import hashlib

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
PW = "xxxxxxxxx"
AIN = "09995 0880000"
SWITCH = "192.168.2.10"

OFF_TEMP = 20.0
ON_TEMP = 18.0

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
    return int(strTmp) / 10

def switchFan(onoff):
    result = requests.get(URLSWITCH.format(switch=SWITCH, onoff=onoff))


if __name__ == '__main__':
    sessionId = getSessionId()
    temp = getTemperature(AIN)
    if temp <ON_TEMP:
        switchFan("on")
    elif temp > OFF_TEMP:
        switchFan("off")
