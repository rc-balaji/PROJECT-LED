
import json

import urequests

bin_queue_file = '/bin_queue.json'
   
queue_file = "/queue.json"


MAX_RETRIES = 3  # Maximum number of retries for failed requests


def process_queue():
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

    # Try to send each request
    for request in queue:
        url = request.get("url")
        data = request.get("data")
        method = request.get("method", "GET").upper()
        retries = request.get("retries", 0)  # Number of attempts made

        # Attempt to process the request
        try:
            # Send the request
            if method == "GET":
                response = urequests.get(url)
            elif method == "POST":
                response = urequests.post(url, json=data)

            if response.status_code == 200:
                print(f"Successfully processed request to {url}")
            else:
                print(f"Failed to process request to {url}. Status code: {response.status_code}")
                # Increment the retry count and add back to new queue for later processing
                request["retries"] = retries + 1
                new_queue.append(request)

            response.close()

        except Exception as e:
            print(f"Error processing request to {url}: {e}")
            # Increment the retry count and add back to new queue for later processing
            request["retries"] = retries + 1
            new_queue.append(request)

        # Check if max retries have been reached
        if request["retries"] >= MAX_RETRIES:
            print(f"Max retries reached for request to {url}. Will retry later.")
            # Instead of dropping, just keep it in the new_queue to retry later
            new_queue.append(request)

    # Update the queue with all processed requests
    with open(queue_file, 'w') as file:
        json.dump(new_queue, file)

    print("Queue processing completed.")


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
        with open('/config.json', 'r') as file:
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
