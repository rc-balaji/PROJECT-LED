


import machine
from ds3231 import DS3231
import time

from file_opertaions import read_config



class Constants:
    def __init__(self):
        self.sda_pin = machine.Pin(21)
        self.scl_pin = machine.Pin(22)

        self.i2c = machine.I2C(0, scl=self.scl_pin, sda=self.sda_pin)


        time.sleep(0.5)

        self.rtc = DS3231(self.i2c)


        self.Local = read_config()


        self.KIT_NO = self.Local.get("KIT_NO", "")
        self.STATIC_NO = self.Local.get("STATIC_NO", "")
        if self.STATIC_NO == "":
            self.STATIC_IP = self.KIT_NO

        self.SERVER_NO = self.Local.get("SERVER_NO", 0)
        self.SSID = self.Local.get("SSID", "")
        self.PASSWORD = self.Local.get("PASSWORD", "")


        

        
    
    

