from socket import socket
import json
from threading import Thread
import time


def getDataFromJSON(jsonstr):
    try:
        packet = json.loads(jsonstr)
    except json.JSONDecodeError:
        return

    command = packet["command"]
    if "cnt;" in command:
        if "sa;" in command:
            ControlSignals.steeringAngle = float(packet["data"])
        elif "thr;" in command:
            ControlSignals.gasVal = float(packet["data"])
        elif "cmc;" in command:
            ControlSignals.cameraState = int(float(packet["data"]))
        elif "cmch;" in command:
            ControlSignals.controlState = int(float(packet["data"]))
            print(ControlSignals.controlState)
    elif "dbg;" in command:
        if "cmc;" in command:
            ControlSignals.cameraState = int(float(packet["data"]))



def connectSocket(addr):
    print("attempting to connect...")
    while True:
        try:
            ControlSignals.sock.connect(addr)
            print("connected!")
            break;
        except:
            time.sleep(1)
            print("Connection refused, trying again")


def startUpdateLoop():
    while True:
        
        packet = ControlSignals.sock.recv(1024).decode(encoding='UTF-8')
        if packet == "":
            continue
        updates = splitPacketsAndUpdate(packet)
        #print(updates)

        for update in updates:
            getDataFromJSON(update)

def splitPacketsAndUpdate(packets):
    updates = packets.split("}")
    formattedUpdates = [s + "}" for s in updates]
    return formattedUpdates[:-1]



def startListening():
    thread = Thread(target=initSock())
    thread.start()


def sendSuggestedAngle(angle):
    
    msg = "{\"command\":\"inf;sa;\", \"data\":\"" + str(angle) + "\", \"packetID\":\"null\", \"authID\":\"null\"}"
    print("sending suggested angle: ", msg)
    ControlSignals.sock.sendall(bytes(msg, 'utf-8'))


def initSock():
    if ControlSignals.sock is None:
        ControlSignals.sock = socket()
        connectSocket(ControlSignals.def_addr)
        thread = Thread(target=startUpdateLoop)
        thread.start()

def getState():
    return (ControlSignals.gasVal, ControlSignals.steeringAngle, ControlSignals.cameraState)

def getSteeringAngle():
    return ControlSignals.steeringAngle


def getDrivePower():
    return ControlSignals.gasVal


def getCameraState():
    return ControlSignals.cameraState

def getControlState():
    return ControlSignals.controlState


class ControlSignals:
    def_addr = ("localhost", 1103)
    isListening = False
    sock = None
    gasVal = 0 #0% throttle
    steeringAngle = 0 #0 degrees
    cameraState = 0 #Distorted mode
    controlState = 0 #Manual mode


if __name__ == "__main__":
    initSock()
    
