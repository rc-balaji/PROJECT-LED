
import json

import urequests

bin_queue_file = '/bin_queue.json'
   
queue_file = "/queue.json"


MAX_RETRIES = 3  # Maximum number of retries for failed requests


def process_queue(server_ip, kit_no):
    """Process the request queue and send requests."""
    # Read the queue from the file
    try:
        with open(queue_file, 'r') as file:
            queue = json.load(file)
    except Exception:
        print("Queue file not found. Initializing a new queue.")
        queue = []  # Initialize an empty queue if the file does not exist

    if not queue:
        print("No pending requests in the queue.")
        return

    # New queue to hold requests that failed processing
    new_queue = []

    # Process requests until the queue is empty
    while queue:
        request = queue.pop(0)
        data = request.get("data")
        method = request.get("method", "GET").upper()
        # retries = request.get("retries", 0)  # Number of attempts made

        url = f"http://{server_ip}:5000/click/KT-{kit_no}"

        try:
            # Send the request
            if method == "GET":
                response = urequests.get(url)
            elif method == "POST":
                response = urequests.post(url, json=data)

            if response.status_code == 200:
                print(f"Successfully processed request to {kit_no}")
            else:
                print(f"Failed to process request to {url}. Status code: {response.status_code}")
                # request["retries"] = retries + 1
                new_queue.append(request)

            response.close()

        except Exception as e:
            print(f"Error processing request to {url}: {e}")
            # request["retries"] = retries + 1
            new_queue.append(request)

        

    # Update the queue file with failed requests
    set_queue(new_queue)

    print("Queue processing completed.")


def set_queue(queue):
    with open(queue_file, 'w') as file:
        json.dump(queue, file)

def add_to_queue(request_data):
    """Add a new request to the queue."""
    # Initialize the queue if the file does not exist
    try:
        with open(queue_file, 'r') as file:
            queue = json.load(file)
    except Exception:
        print("Queue file not found. Initializing a new queue.")
        queue = []

    # Initialize retries for the new request
    request_data["retries"] = 0

    # Add the new request to the queue
    queue.append(request_data)

    # Save the updated queue back to the file
    with open(queue_file, 'w') as file:
        json.dump(queue, file)

    print("Request added to the queue.")


# Example usage
# Uncomment the following lines to add requests to the queue
# add_to_queue({"url": "http://example.com/api", "data": {"key": "value"}, "method": "POST"})
# process_queue()



def get_bin_queue():
    print("Called2")
    try:
        with open('/bin_queue.json', 'r') as f:
            bin_queue = json.load(f)
            print(bin_queue)
            return bin_queue
    except Exception:
        # If the file does not exist, initialize an empty queue structure
        bin_queue = {index: [] for index in range(4)}
        set_bin_queue(bin_queue)


def set_bin_queue(queue):
    with open('/bin_queue.json', 'w') as f:
        json.dump(queue, f)

def read_config():

    try:
        with open('../config.json', 'r') as file:
            config = json.load(file)
            return config
    except OSError:
        return {}


def get_data():
    
    try:
        with open('/data.json', 'r') as file:
            config = json.load(file)
            return config
    except OSError:
        return {}

def set_data(new_data):
    with open('/data.json', 'w') as file:
        json.dump(new_data, file)

