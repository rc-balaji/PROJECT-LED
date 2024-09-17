# main.py

import json
import network
import usocket as socket

import machine
from neopixel import NeoPixel
import esp
import gc
gc.enable()

#Define the pin for the switch
switch_pin = machine.Pin(2, machine.Pin.IN)

curr_state = switch_pin.value()

print("Coming")
if curr_state == 1:
    print("TP-1")
    try:
        with open('AP_MODE.py', 'r') as file:
            code = file.read()
        exec(code)
    except Exception:
        
        machine.reset()

elif curr_state == 0:
    print("TP-2")
    try:
        with open('STA_MODE.py', 'r') as file:
            code = file.read()
        exec(code)
    except Exception as err:
        print(err)
        machine.reset()
        




