import network
import time
import urequests
from machine import RTC
import gc
import machine

from file_opertaions import get_data , set_data , process_queue

class Station:
    def __init__(self, ssid, password, server_no, rtc,kit_id):
        self.ssid = ssid
        self.password = password
        self.server_no = server_no  # Added server number from constructor
        self.rtc = rtc
        self.local_ip = None
        self.server_ip = None
        self.wlan = network.WLAN(network.STA_IF)
        self.kit_id = kit_id

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
            self.local_ip = self.wlan.ifconfig()[0]
            print("Connected to WiFi")
            print("IP Address: ", self.local_ip)

            self.generate_server_ip()


            process_queue()

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
                    set_data({})
                else:
                    set_data(data)
                    print("Update data from server: Success")
                    # Further processing can be done with the received data
            else:
                print("Failed to get data from server. Setting data to an empty object.")
                set_data({})

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





