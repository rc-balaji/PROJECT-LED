import gc
import machine
from neopixel import NeoPixel
import time
import ujson
from machine import Timer
import urequests
import network
from ds3231 import DS3231

# Define I2C pins for SDA and SCL for DS3231 RTC
sda_pin = machine.Pin(21)
scl_pin = machine.Pin(22)

# Initialize I2C
i2c = machine.I2C(0, scl=scl_pin, sda=sda_pin)
time.sleep(0.5)  # Short delay to ensure I2C is ready

# Initialize the DS3231 RTC module
rtc = DS3231(i2c)

config_file_path = '/config.json'

def read_config(file_path):
    """Reads JSON configuration from the specified file."""
    try:
        with open(file_path, 'r') as file:
            config = ujson.load(file)
            return config
    except OSError:
        return {}

Local = read_config(config_file_path)
KIT_NO = Local.get("KIT_NO", "")
STATIC_NO = Local.get("STATIC_NO", "")
if STATIC_NO == "":
    STATIC_IP = KIT_NO

SERVER_NO = Local.get("SERVER_NO", 0)
SSID = Local.get("SSID", "")
PASSWORD = Local.get("PASSWORD", "")

def get_data():
    """Reads JSON configuration from the specified file."""
    try:
        with open('/data.json', 'r') as file:
            config = ujson.load(file)
            return config
    except OSError:
        return {}

def set_data(new_data):
    with open('/data.json', 'w') as file:
        ujson.dump(new_data, file)

data = get_data()
rack_id = data.get("rack_id", "")
bins_config = data.get("bins", [])

bin_queue = {index: [] for index in range(len(bins_config))}

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

bin_manager = BinManager()

class Bin:
    def __init__(self, bin_config, index, rack_id):
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
        bin_manager.add_to_active_bins(self.rack_id, self.index, self.color)

    def turn_off_leds(self):
        for i in range(self.num_leds):
            self.np[i] = (0, 0, 0)
        self.np.write()
        print("LEDs turned off.")
        bin_manager.remove_from_active_bins(self.rack_id, self.index)

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

            self.turn_off_leds()
            self.send_message(self.index, 'click-change')

           
            if bin_queue[self.index]:
                next_color = bin_queue[self.index].pop(0)
                self.color = next_color
                self.change_led_color()
            else:
                self.turn_off_leds()
                self.clicked = True

            bin_manager.check_and_update_buzzer_relay()

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

bins = [Bin(bin_cfg, idx, rack_id) for idx, bin_cfg in enumerate(bins_config)]

import _thread
import time

def check_schedules():
    while True:
        # Get current time from DS3231 RTC
        current_time = rtc.get_time()
        current_hour = current_time[3]
        current_minute = current_time[4]

        print(f"Current Time: {current_hour:02}:{current_minute:02}")
        data = get_data()

        for index, _bin in enumerate(data['bins']):
            for schedule in _bin['schedules']:
                if schedule['enabled']:
                    schedule_hour, schedule_minute = map(int, schedule['time'].split(":"))
                    if current_hour == schedule_hour and current_minute == schedule_minute:
                        if bins[index].clicked:
                            bins[index].color = tuple(schedule['color'])
                            bins[index].change_led_color()
                            bins[index].clicked = False
                            bins[index].active_schedules.append(schedule)
                        else:
                            bin_queue[index].append(tuple(schedule['color']))
                            print(f"Schedule missed for bin {index}, color added to queue")

        gc.collect()
        time.sleep(60)

# Connect to Wi-Fi
def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    max_attempts = 10
    attempt = 0
    while not wlan.isconnected() and attempt < max_attempts:
        print(f"Connecting to WiFi... Attempt {attempt + 1}/{max_attempts}")
        time.sleep(1)
        attempt += 1
    
    if wlan.isconnected():
        print("Connected to WiFi")
        print("IP Address: ", wlan.ifconfig()[0])
        return True, wlan.ifconfig()[0]
    else:
        print("Failed to connect to WiFi")
        return False, None

def parse_iso_time(iso_string):
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

def get_time_from_server(ip):
    try:
        url = "http://" + ip + ":5000/get-time1"
        response = urequests.get(url)
        if response.status_code == 200:
            time_data = response.json().get('time')
            print(f"Received time from server: {time_data}")
            year, month, day, hour, minute, second = parse_iso_time(time_data)
            rtc.set_time(year, month, day, hour, minute, second,0,0)
            print(f"RTC updated to: {year}-{month}-{day} {hour}:{minute}:{second}")
        else:
            print("Failed to get time from server")
    except Exception as e:
        print(f"Error fetching time: {e}")

# Dynamically generate the server IP address based on local IP
def generate_server_ip(local_ip, server_no):
    ip_parts = local_ip.split('.')
    ip_parts[-1] = str(server_no)  # Replace the last byte with SERVER_NO
    return '.'.join(ip_parts)

# Example usage
wifi_connected, local_ip = connect_to_wifi(SSID, PASSWORD)
if wifi_connected:
    server_ip = generate_server_ip(local_ip, SERVER_NO)
    print(f"Dynamically generated server IP: {server_ip}")
    get_time_from_server(server_ip)
else:
    print("Could not fetch time due to WiFi connection failure.")

_thread.start_new_thread(check_schedules, ())

print("System initialized and running.")
