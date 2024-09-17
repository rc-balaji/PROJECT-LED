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


def set_default_color():
    pins = [12, 25, 26, 27]
    neopixels = [NeoPixel(machine.Pin(pin), 10) for pin in pins]
    for np in neopixels:
        for i in range(np.n):
            np[i] = (65, 0, 0)  
            np[i] = (0, 65, 0)  
            np[i] = (0, 0, 65)  
            np[i] = (0, 0, 0)  
        np.write()  

set_default_color()

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
        




