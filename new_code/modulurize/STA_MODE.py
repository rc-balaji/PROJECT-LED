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

# Load configuration from JSON
data = get_data()
rack_id = data.get("rack_id", "")
bins_config = data.get("bins", [])

const = Constants()
bin_manager = BinManager()
sta = Station(const.SSID, const.PASSWORD, const.SERVER_NO, const.rtc, kit_id=const.KIT_NO)
sta.connect_to_wifi()
# Check if data.json is empty or only contains an empty dictionary
if not data or data == {}:
    print("Configuration is empty. Starting WiFi request only.")
        
else:
    # Proceed if configuration is valid
    bin_obj = BinConstants(bins_config=bins_config, rack_id=rack_id, bin_manager=bin_manager,server_ip=sta.server_ip,kt_id=const.KIT_NO)

    # Start a new thread for schedule checking
    _thread.start_new_thread(check_schedules, (const.rtc, bin_obj))


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
                    current_bin.bin_manager.check_and_update_buzzer_relay()
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


while True:
    process_queue()
    sta.get_time_from_server()
    sta.update_data_from_server()
    get_click_data_from_server()
    time.sleep(10)
   
    

print("System initialized and running.")


