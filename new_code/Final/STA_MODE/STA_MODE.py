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

print("TP-1")
const = Constants()
bin_manager = BinManager()
sta = Station(const.SSID, const.PASSWORD, const.SERVER_NO, const.rtc, kit_id=const.KIT_NO,static_no=const.STATIC_NO)
print("TP-2")
sta.connect_to_wifi()
sta.update_data_from_server()


# Load configuration from JSON
data = get_data()
rack_id = data.get("rack_id", "")
bins_config = data.get("bins", [])





bin_obj = BinConstants(bins_config=bins_config, rack_id=rack_id, bin_manager=bin_manager,server_ip=sta.server_ip,kt_id=const.KIT_NO,sta=sta )

_thread.start_new_thread(check_schedules, (const.rtc, bin_obj))

# def chech_relay_state():

#     while True:
#         if bin_manager.check_state():
#             bin_manager.turn_on_buzzer_and_relay()
#         else:
#             bin_manager.turn_off_buzzer_and_relay()
#         print(bin_manager.time_queue)
#         time.sleep(1)

# _thread.start_new_thread(chech_relay_state , ())

def chech_buzzer_state():

    if bin_manager.check_state_buzzer():
        bin_manager.turn_on_buzzer()
    else:
        bin_manager.turn_off_buzzer()

def chech_relay_state():

    if bin_manager.check_state_relay():
        bin_manager.turn_on_relay()
    else:
        bin_manager.turn_off_relay()





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




print(sta.server_ip)
print(sta.local_ip)

while True:
    if sta.isconnected():
        turn_on_led()
        process_queue(sta.server_ip , const.KIT_NO)
        sta.get_time_from_server()
        sta.update_data_from_server()
        get_click_data_from_server()

        chech_buzzer_state()

        chech_relay_state()

    else:
        print("Not Connecting With Wifi")
        blink_led() 
        sta.connect_to_wifi()
        
    time.sleep(10)
    
    

print("System initialized and running.")







