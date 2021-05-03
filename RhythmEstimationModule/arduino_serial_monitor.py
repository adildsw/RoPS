from serial import Serial
from requests import get
from time import time

REQUEST_ADDRESS = "http://192.168.86.178:5000/addBPMTimestamp?data={}_{}"
arduino = Serial("/dev/cu.usbserial-1130", 9600, timeout=10)

while True:
    bpm = str(arduino.readline().decode().rstrip())
    if bpm != "":
        bpm = int(bpm.split(".")[0])
        print(bpm)
        get(REQUEST_ADDRESS.format(bpm, time()))