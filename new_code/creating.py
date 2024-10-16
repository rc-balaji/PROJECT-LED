import os

# # Define the filenames and corresponding code strings
files_data = {
    "Bin_Constants.py": """

# Bin_Constants.py

import json

from Bins import Bin

class BinConstants:
    def __init__(self, rack_id, bins_config,bin_manager):
        self.bins = [Bin(bin_cfg, idx, rack_id,bin_manager=bin_manager) for idx, bin_cfg in enumerate(bins_config)]
        

    

    """,




    "Bins.py": """
# Bins.py
import machine
from neopixel import NeoPixel

from file_opertaions import get_data,set_data , get_bin_queue , set_bin_queue
import time



class BinManager:
    def __init__(self):
        self._active_bins = []
        self._buzzer_pin = 32
        self._relay_pin = 33
        self._buzzer = machine.Pin(self._buzzer_pin, machine.Pin.OUT)
        self._relay = machine.Pin(self._relay_pin, machine.Pin.OUT)

    def add_to_active_bins(self, rack_id, bin_index, color):
        if (rack_id, bin_index) not in [(b[0], b[1]) for b in self._active_bins]:
            self._active_bins.append((rack_id, bin_index, color))
            print(f"Added bin {bin_index} in rack {rack_id} with color {color} to active bins.")
        self.check_and_update_buzzer_relay()

    def remove_from_active_bins(self, rack_id, bin_index):
        self._active_bins = [b for b in self._active_bins if not (b[0] == rack_id and b[1] == bin_index)]
        print(f"Removed bin {bin_index} in rack {rack_id} from active bins.")
        self.check_and_update_buzzer_relay()

    def check_and_update_buzzer_relay(self):
        if self._active_bins:
            # self._buzzer.on()
            self._relay.on()
            print("Buzzer and Relay turned ON")
        else:
            # self._buzzer.off()
            self._relay.off()
            print("Buzzer and Relay turned OFF")




class Bin:
    def __init__(self, bin_config, index, rack_id,bin_manager):
        self.button_pin = bin_config['button_pin']
        self.led_pin = bin_config['led_pin']
        self.color = tuple(bin_config['color'])
        self.last_pressed_time = 0
        self.clicked = bin_config['clicked']
        self.index = index
        self.rack_id = rack_id
        self.schedules = bin_config.get("schedules", [])
        self.queued_color = None
        self.active_schedules = []
        self.bin_manager  = bin_manager

        self.button = machine.Pin(self.button_pin, machine.Pin.IN, machine.Pin.PULL_UP)
        self.num_leds = 10
        self.np = NeoPixel(machine.Pin(self.led_pin), self.num_leds)

        self.button.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.handle_button_press)
        print(f"Button configured on pin {self.button_pin}")

        self.initialize_leds()

    def change_led_color(self):
        for i in range(self.num_leds):
            self.np[i] = self.color
        self.np.write()
        print(f"LEDs changed to color: {self.color}")
        self.bin_manager.add_to_active_bins(self.rack_id, self.index, self.color)

    def turn_off_leds(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()
        print("LEDs turned off.")
        self.bin_manager.remove_from_active_bins(self.rack_id, self.index)

    def initialize_leds(self):
        if self.clicked:
            self.turn_off_leds()
        else:
            self.change_led_color()

    def handle_button_press(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_pressed_time) > 200:
            print(f"Button pressed for bin {self.button_pin}")
            self.last_pressed_time = current_time

            bin_queue = get_bin_queue()
            
            self.turn_off_leds()
            self.send_message(self.index, 'click-change')

           
            if bin_queue[self.index]:
                next_color = bin_queue[self.index].pop(0)
                self.color = next_color
                self.change_led_color()
            else:
                self.turn_off_leds()
                self.clicked = True

            set_bin_queue()
            self.bin_manager.check_and_update_buzzer_relay()

    def send_message(self, bin_index, operation):
        msg = {
            'rack_id': self.rack_id,
            'bin_idx': bin_index,
            'operation': operation
        }
        self.update_data_json_from_message(msg)

    def update_data_json_from_message(self, msg_data):
        try:
            data = get_data()
            rack_id = msg_data.get('rack_id')
            bin_idx = msg_data.get('bin_idx')

            if not rack_id or bin_idx is None:
                print("Error: Missing required fields in the message")
                return

            data["bins"][bin_idx]['clicked'] = True
            set_data(data)

            print("Data JSON updated based on received message")

        except Exception as err:
            print(f"Error updating JSON from message: {err}")

    """,





    "config.json": """
{
  "PASSWORD": "",
  "KIT_NO": "",
  "SSID": "",
  "SERVER_NO": "",
  "STATIC_NO": ""
}

    """,



    "constants.py": """


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


        

        
    
    """,




    "ds3231.py": """
# ds3231.py

import utime
import machine
import sys





DS3231_I2C_ADDR = 104

try:
    rtc = machine.RTC()
except:
    print('Warning: machine module does not support the RTC.')
    rtc = None

def bcd2dec(bcd):
    return (((bcd & 0xf0) >> 4) * 10 + (bcd & 0x0f))

def dec2bcd(dec):
    tens, units = divmod(dec, 10)
    return (tens << 4) + units

def tobytes(num):
    return num.to_bytes(1, 'little')

class DS3231:
    def __init__(self, i2c):
        self.ds3231 = i2c
        self.timebuf = bytearray(7)
        if DS3231_I2C_ADDR not in self.ds3231.scan():
            raise RuntimeError("DS3231 not found on I2C bus at %d" % DS3231_I2C_ADDR)

    def get_time(self, set_rtc=False):
        if set_rtc:
            self.await_transition()
        else:
            self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf)
        return self.convert(set_rtc)

    def convert(self, set_rtc=False):
        data = self.timebuf
        ss = bcd2dec(data[0])
        mm = bcd2dec(data[1])
        if data[2] & 0x40:
            hh = bcd2dec(data[2] & 0x1f)
            if data[2] & 0x20:
                hh += 12
        else:
            hh = bcd2dec(data[2])
        wday = data[3]
        DD = bcd2dec(data[4])
        MM = bcd2dec(data[5] & 0x1f)
        YY = bcd2dec(data[6])
        if data[5] & 0x80:
            YY += 2000
        else:
            YY += 1900
        result = YY, MM, DD, hh, mm, ss, wday - 1, 0
        if set_rtc:
            if rtc is None:
                secs = utime.mktime(result)
                utime.localtime(secs)
            else:
                rtc.datetime((YY, MM, DD, wday, hh, mm, ss, 0))
        return result

    def set_time(self, YY, MM, mday, hh, mm, ss, wday, yday):
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 0, tobytes(dec2bcd(ss)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 1, tobytes(dec2bcd(mm)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 2, tobytes(dec2bcd(hh)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 3, tobytes(dec2bcd(wday + 1)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 4, tobytes(dec2bcd(mday)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 5, tobytes(dec2bcd(MM)))
        self.ds3231.writeto_mem(DS3231_I2C_ADDR, 6, tobytes(dec2bcd(YY - 1900)))
    
    def await_transition(self):
        self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf)
        ss = self.timebuf[0]
        while ss == self.timebuf[0]:
            self.ds3231.readfrom_mem_into(DS3231_I2C_ADDR, 0, self.timebuf)
        return self.timebuf

    def get_temperature(self):
        t = self.ds3231.readfrom_mem(DS3231_I2C_ADDR, 0x11, 2)
        i = t[0] << 8 | t[1]
        return self._twos_complement(i >> 6, 10) * 0.25

    def _twos_complement(self, input_value: int, num_bits: int) -> int:
        mask = 2 ** (num_bits - 1)
        return -(input_value & mask) + (input_value & ~mask)


    """,



    "file_opertaions.py": """
import ujson

import json



bin_queue_file = 'bin_queue.json'
   

def get_bin_queue():
    try:
        with open(bin_queue_file, 'r') as f:
            bin_queue = json.load(f)
    except Exception:
        # If the file does not exist, initialize an empty queue structure
        bin_queue = {index: [] for index in range(4)}
        set_bin_queue(bin_queue)


def set_bin_queue(queue):
    with open(bin_queue_file, 'w') as f:
        json.dump(queue, f,)

def read_config():

    try:
        with open('/config.json', 'r') as file:
            config = json.load(file)
            return config
    except OSError:
        return {}


def get_data():
    try:
        with open('/data.json', 'r') as file:
            config = ujson.load(file)
            return config
    except OSError:
        return {}

def set_data(new_data):
    with open('/data.json', 'w') as file:
        ujson.dump(new_data, file)
    """,



    "schedule.py": """
import gc

import time

from file_opertaions import get_data , get_bin_queue , set_bin_queue
def check_schedules(rtc,bin_obj):
    while True:
        # Get current time from DS3231 RTC
        current_time = rtc.get_time()
        current_hour = current_time[3]
        current_minute = current_time[4]

        print(f"Current Time: {current_hour:02}:{current_minute:02}")
        data = get_data()
        bin_queue = get_bin_queue()
        for index, _bin in enumerate(data['bins']):
            for schedule in _bin['schedules']:
                if schedule['enabled']:
                    schedule_hour, schedule_minute = map(int, schedule['time'].split(":"))
                    if current_hour == schedule_hour and current_minute == schedule_minute:
                        if bin_obj.bins[index].clicked:
                            bin_obj.bins[index].color = tuple(schedule['color'])
                            bin_obj.bins[index].change_led_color()
                            bin_obj.bins[index].clicked = False
                            bin_obj.bins[index].active_schedules.append(schedule)
                        else:
                            bin_queue[index].append(tuple(schedule['color']))
                            print(f"Schedule missed for bin {index}, color added to queue")
        set_bin_queue(bin_queue)
        gc.collect()
        time.sleep(60)

    """,



    "STA_MODE.py": """

import _thread


from Bins import BinManager

from file_opertaions import get_data,set_data

from schedule import check_schedules

from Bin_Constants import BinConstants

from constants import Constants

from station import Station

config_file_path = '/config.json'




data = get_data()
rack_id = data.get("rack_id", "")
bins_config = data.get("bins", [])


const  = Constants()


bin_manager = BinManager()

bin_obj = BinConstants(bins_config=bins_config, rack_id=rack_id,bin_manager=bin_manager)


sta  = Station(const.SSID , const.PASSWORD , const.SERVER_NO,const.rtc)


sta.connect_to_wifi()


sta.get_time_from_server()


_thread.start_new_thread(check_schedules, (const.rtc  , bin_obj))

print("System initialized and running.")


    """,



    "station.py": """
import network
import time
import urequests
from machine import RTC
import gc

class Station:
    def __init__(self, ssid, password, server_no,rtc):
        self.ssid = ssid
        self.password = password
        self.server_no = server_no  # Added server number from constructor
        self.rtc = rtc
        self.local_ip = None
        self.server_ip = None
        self.wlan = network.WLAN(network.STA_IF)

    # Connect to Wi-Fi
    def connect_to_wifi(self):
        self.wlan.active(True)
        
        # Disconnect if already connected
        if self.wlan.isconnected():
            print("Already connected to WiFi. Disconnecting...")
            self.disconnect_wifi()

        self.wlan.connect(self.ssid, self.password)
        
        max_attempts = 10
        attempt = 0
        while not self.wlan.isconnected() and attempt < max_attempts:
            print(f"Connecting to WiFi... Attempt {attempt + 1}/{max_attempts}")
            time.sleep(1)
            attempt += 1
        
        if self.wlan.isconnected():
            self.local_ip = self.wlan.ifconfig()[0]
            print("Connected to WiFi")
            print("IP Address: ", self.local_ip)

            self.generate_server_ip()

            return True, self.local_ip
        else:
            print("Failed to connect to WiFi")
            self.wlan.active(False)
            gc.collect()
            return False, None

    # Disconnect from Wi-Fi
    def disconnect_wifi(self):
        if self.wlan.isconnected():
            self.wlan.disconnect()
            print("Disconnected from WiFi")
        self.wlan.active(False)
        gc.collect()

    # Parse ISO formatted time string
    def parse_iso_time(self, iso_string):
        date_time = iso_string.split("T")
        date_parts = date_time[0].split("-")
        year = int(date_parts[0])
        month = int(date_parts[1])
        day = int(date_parts[2])
        time_parts = date_time[1].split("+")[0].split(":")
        hour = int(time_parts[0])
        minute = int(time_parts[1])
        second = int(time_parts[2])
        return year, month, day, hour, minute, second

    # Get time from server
    def get_time_from_server(self):
        if not self.server_ip:
            print("Server IP is not set. Generate the server IP first.")
            return
        
        try:
            url = f"http://{self.server_ip}:5000/get-time1"
            response = urequests.get(url)
            if response.status_code == 200:
                time_data = response.json().get('time')
                print(f"Received time from server: {time_data}")
                year, month, day, hour, minute, second = self.parse_iso_time(time_data)
                self.rtc.datetime((year, month, day, 0, hour, minute, second, 0))
                print(f"RTC updated to: {year}-{month}-{day} {hour}:{minute}:{second}")
            else:
                print("Failed to get time from server")
            response.close()  # Properly close the connection
        except Exception as e:
            print(f"Error fetching time: {e}")
        finally:
            gc.collect()  # Force garbage collection

    # Dynamically generate the server IP address based on local IP
    def generate_server_ip(self):
        if not self.local_ip:
            print("Local IP is not set. Connect to WiFi first.")
            return None
        ip_parts = self.local_ip.split('.')
        ip_parts[-1] = str(self.server_no)  # Use the server_no from the constructor
        self.server_ip = '.'.join(ip_parts)
        return self.server_ip

    # Clean up the class instance (for memory management)
    def cleanup(self):
        self.disconnect_wifi()
        self.rtc = None
        self.local_ip = None
        self.server_ip = None
        self.wlan = None
        gc.collect()
        print("Resources cleaned up")

# Example usage
# station = Station("your_ssid", "your_password", 1)  # Specify server number directly
# wifi_connected, local_ip = station.connect_to_wifi()

# if wifi_connected:
#     server_ip = station.generate_server_ip()  # Automatically uses server_no from constructor
#     station.get_time_from_server()

# # Disconnect and clean up when done
# station.cleanup()

    """,



    "bin_queue.json": """
{
    "0": [],
    "1": [],
    "2": [],
    "3": []
}

    """,

    "data.json": """
{
    "rack_id": "_D13",
    "bins": [
      {
        "color": [65, 65, 65],
        "led_pin": 12,
        "bin_id": "_D13_01",
        "button_pin": 13,
        "schedules": [
          {
            "time": "13:13",
            "enabled": true,
            "color": [65, 0, 65]
          },
          {
            "time": "13:14",
            "enabled": true,
            "color": [65, 0, 0]
          },
          {
            "time": "13:18",
            "enabled": true,
            "color": [65, 0, 0]
          }
        ],
        "enabled": true,
        "clicked": true
      },
      {
        "color": [65, 65, 65],
        "led_pin": 25,
        "bin_id": "_D13_02",
        "button_pin": 14,
        "schedules": [],
        "enabled": true,
        "clicked": true
      },
      {
        "color": [65, 0, 0],
        "led_pin": 26,
        "bin_id": "_D13_03",
        "button_pin": 15,
        "schedules": [],
        "enabled": true,
        "clicked": true
      },
      {
        "color": [65, 65, 65],
        "led_pin": 27,
        "bin_id": "_D13_04",
        "button_pin": 16,
        "schedules": [
          {
            "time": "13:13",
            "enabled": true,
            "color": [0, 0, 0]
          },
          {
            "time": "13:18",
            "enabled": true,
            "color": [65, 0, 65]
          }
        ],
        "enabled": true,
        "clicked": true 
      } 
    ],
    "mac": [44, 188, 187, 7, 42, 116],
    "device_id": "KT-13"
  }
  
  

    """,



}



# Create the files with the corresponding code strings
for filename, content in files_data.items():
    with open(filename, 'w') as file:
        file.write(content)

print("Files have been created.")
