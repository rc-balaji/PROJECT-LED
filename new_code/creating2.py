import os

file_data = {
    "station.py":"""

import network
import time
import urequests
from machine import RTC
import gc
import machine

from file_opertaions import get_data , set_data , process_queue , set_bin_queue , set_queue

class Station:
    def __init__(self, ssid, password, server_no, rtc,kit_id,static_no):
        self.ssid = ssid
        self.password = password
        self.server_no = server_no  # Added server number from constructor
        self.rtc = rtc
        self.local_ip = None
        self.server_ip = None
        self.wlan = network.WLAN(network.STA_IF)
        self.kit_id = kit_id
        self.static_no = static_no

    # Connect to Wi-Fi
    def connect_to_wifi(self):
        self.wlan.active(True)
        
        # Disconnect if already connected
        if self.wlan.isconnected():
            print("Already connected to WiFi. Disconnecting...")
            self.disconnect_wifi()
            machine.reset()

        self.wlan.connect(self.ssid, self.password)
        
        max_attempts = 10
        attempt = 0
        while not self.wlan.isconnected() and attempt < max_attempts:
            print(f"Connecting to WiFi... Attempt {attempt + 1}/{max_attempts}")
            time.sleep(1)
            attempt += 1
        
        if self.wlan.isconnected():
            # self.local_ip = self.wlan.ifconfig()[0]
            # print("Connected to WiFi")
            # print("IP Address: ", self.local_ip)


            ip_info = self.wlan.ifconfig()
            print("Current IP info:", ip_info)
            ip_address = ip_info[0]
            ip_parts = ip_address.split('.')

            if len(ip_parts) == 4:
                new_ip_address = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{self.static_no}"
                self.server_ip = f"{ip_parts[0]}.{ip_parts[1]}.{ip_parts[2]}.{self.server_no}"
            
                self.local_ip = new_ip_address
                # Reconfigure network interface
                self.wlan.ifconfig((new_ip_address, ip_info[1], ip_info[2], ip_info[3]))
            
                time.sleep(2)  # Short wait to ensure it's applied
                new_ip_info = self.wlan.ifconfig()
                print('Updated network configuration:', new_ip_info)
                if new_ip_info[0] == new_ip_address:
                    print("IP updated successfully.")
                else:
                    print("IP update failed.")
            else:
                print("Unexpected IP address format.")

            # self.generate_server_ip()


            # process_queue(self.server_ip , self.kit_id)

            return True, self.local_ip
        else:
            print("Failed to connect to WiFi")
            self.wlan.active(False)
            gc.collect()
            return False, None
    
    def isconnected(self):
        return self.wlan.isconnected()

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
                self.rtc.set_time(year, month, day, hour, minute, second, 0, 0)
                print(f"RTC updated to: {year}-{month}-{day} {hour}:{minute}:{second}")
            else:
                print("Failed to get time from server")
            response.close()  # Properly close the connection
        except Exception as e:
            print(f"Error fetching time: {e}")
        finally:
            gc.collect()  # Force garbage collection

    def update_data_from_server(self):

        not_found =     {
  "rack_id": "",
  "KIT_ID": "",
  "bins": [
    {
      "color": [255, 255, 255],
      "colorESP": [0, 0, 0],
      "led_pin": 12,
      "bin_id": "RC-1_01",
      "button_pin": 13,
      "schedules": [],
      "enabled": False,
      "clicked": True
    },
    {
      "color": [255, 255, 255],
      "colorESP": [0, 0, 0],
      "led_pin": 25,
      "bin_id": "RC-1_02",
      "button_pin": 14,
      "schedules": [],
      "enabled": False,
      "clicked": True
    },
    {
      "color": [255, 255, 255],
      "colorESP": [0, 0, 0],
      "led_pin": 26,
      "bin_id": "RC-1_03",
      "button_pin": 15,
      "schedules": [],
      "enabled": False,
      "clicked": True
    },
    {
      "color": [255, 255, 255],
      "colorESP": [0, 0, 0],
      "led_pin": 27,
      "bin_id": "RC-1_04",
      "button_pin": 16,
      "schedules": [],
      "enabled": False,
      "clicked": True
    }
  ]
}


        new_bin_q = {"1": [], "0": [], "3": [], "2": []}


        if not self.server_ip:
            print("Server IP is not set. Generate the server IP first.")
            return

        try:
            url = f"http://{self.server_ip}:5000/get-data/KT-{self.kit_id}"
            response = urequests.get(url)

            if response.status_code == 200:
                data = response.json()
                if 'message' in data and data['message'] == 'Rack not found':
                    print("Rack not found. Setting data to an empty object.")
                    set_data(not_found)
                    set_queue([])
                    set_bin_queue(new_bin_q)
                else:
                    set_data(data)
                    print("Update data from server: Success")
                    # Further processing can be done with the received data


            response.close()  # Properly close the connection

        except Exception as e:
            print(f"Error fetching data: {e}")
              # Set data to an empty object in case of error
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
# station = Station("your_ssid", "your_password", 1, RTC())  # Specify server number directly
# wifi_connected, local_ip = station.connect_to_wifi()

# if wifi_connected:
#     station.generate_server_ip()  # Automatically uses server_no from constructor
#     station.update_data_from_server()  # Fetch data from server

# # Disconnect and clean up when done
# station.cleanup()









    



""",

    "STA_MODE.py":"""

import _thread
import time

from Bins import BinManager
from file_opertaions import get_data, process_queue , get_bin_queue , set_bin_queue
from schedule import check_schedules
from Bin_Constants import BinConstants
from constants import Constants
from station import Station

import gc 

import urequests

from machine import Pin

from time import sleep


const = Constants()
bin_manager = BinManager()
sta = Station(const.SSID, const.PASSWORD, const.SERVER_NO, const.rtc, kit_id=const.KIT_NO,static_no=const.STATIC_NO)
sta.connect_to_wifi()
sta.update_data_from_server()


# Load configuration from JSON
data = get_data()
rack_id = data.get("rack_id", "")
bins_config = data.get("bins", [])





bin_obj = BinConstants(bins_config=bins_config, rack_id=rack_id, bin_manager=bin_manager,server_ip=sta.server_ip,kt_id=const.KIT_NO,sta=sta )

_thread.start_new_thread(check_schedules, (const.rtc, bin_obj))

def chech_buzzer_and_relay_state():

    while True:
        if bin_manager.check_state():
            bin_manager.turn_on_buzzer_and_relay()
        else:
            bin_manager.turn_off_buzzer_and_relay()
        print(bin_manager.time_queue)
        time.sleep(1)

_thread.start_new_thread(chech_buzzer_and_relay_state , ())
def get_click_data_from_server():
        if not sta.server_ip:
            print("Server IP is not set. Generate the server IP first.")
            return

        try:
            url = f"http://{sta.server_ip}:5000/get-click/KT-{const.KIT_NO}"
            response = urequests.get(url)

            if response.status_code == 200:
                click_data = response.json()
                print("Click Data:", click_data)

                bin_queue = get_bin_queue()


                for index in click_data:

                    current_bin = bin_obj.bins[index]
                    current_bin.turn_off_leds()

                    if bin_queue[str(index)]:
                        next_color = bin_queue[str(index)].pop(0)
                        current_bin.color = next_color
                        current_bin.change_led_color()
                    else:
                        current_bin.turn_off_leds()
                        current_bin.clicked = True
                    set_bin_queue(bin_queue)
                # print("Okii")  # Print "Okii" as requested
                
            else:
                print("No clicks found for the specified KIT_ID")
                # return None

            response.close()  # Properly close the connection

        except Exception as e:
            print(f"Error fetching click data: {e}")
            return None

        finally:
            gc.collect()  # Force garbage collection


print(sta.server_ip)

led = Pin(17, Pin.OUT)

# Function to blink the LED
def blink_led():
    led.on()   # Turn the LED on
    sleep(0.5) # Wait for 0.5 seconds
    led.off()  # Turn the LED off
    sleep(0.5) # Wait for 0.5 seconds

# Function to turn the LED on
def turn_on_led():
    led.on()





while True:
    if sta.isconnected():
        turn_on_led()
        process_queue(sta.server_ip , const.KIT_NO)
        sta.get_time_from_server()
        sta.update_data_from_server()
        get_click_data_from_server()
    else:
        print("Not Connecting With Wifi")
        blink_led() 
        sta.connect_to_wifi()
        
    time.sleep(10)
    
    

print("System initialized and running.")









"""


}


# Create the files with the corresponding code strings
for filename, content in file_data.items():
    with open(filename, 'w') as file:
        file.write(content)